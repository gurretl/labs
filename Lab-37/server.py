"""
Strava MCP Server - FastAPI backend for Strava activity data integration
=========================================================================

This FastAPI server provides a REST API interface to Strava's activity data.
It handles OAuth2 authentication with Strava and exposes endpoints for 
retrieving user activities filtered by date ranges (2024-2025).

Key Features:
- OAuth2 authentication flow with Strava
- Automatic token refresh handling
- Activity data retrieval with pagination
- Statistical analysis endpoints

Endpoints:
- GET /: Health check and welcome message
- GET /authorize: Initiate Strava OAuth flow
- GET /callback: Handle OAuth callback from Strava
- GET /activities: Retrieve user activities (2024-2025)

Environment Variables Required:
- CLIENT_ID: Strava application client ID
- CLIENT_SECRET: Strava application client secret
"""

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import os
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file
load_dotenv()

# Strava OAuth configuration
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"

# Initialize FastAPI application
app = FastAPI(
    title="Strava MCP Server",
    description="FastAPI server for Strava activity data integration",
    version="1.0.0"
)

# In-memory token storage (in production, use a database)
tokens = {}

@app.get("/")
def root():
    """
    Health check endpoint and welcome message.
    Returns basic server status and instructions.
    """
    return {"message": "MCP Server Strava Ready. Go to /authorize to start."}

@app.get("/authorize")
def authorize():
    """
    Initiate Strava OAuth2 authorization flow.
    Redirects user to Strava's authorization page.
    
    Returns:
        RedirectResponse: Redirects to Strava OAuth authorization URL
    """
    strava_auth_url = (
        f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}"
        f"&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope=activity:read_all"
    )
    return RedirectResponse(strava_auth_url)

@app.get("/callback")
def callback(request: Request):
    """
    Handle OAuth2 callback from Strava after user authorization.
    Exchanges authorization code for access and refresh tokens.
    
    Args:
        request: FastAPI request object containing query parameters
        
    Returns:
        JSONResponse: Success message or error details
    """
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "No code provided"}, status_code=400)

    # Exchange authorization code for access token
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        return JSONResponse({"error": "Failed to get token", "details": response.json()}, status_code=400)

    # Store tokens in memory (use database in production)
    token_data = response.json()
    tokens["access_token"] = token_data["access_token"]
    tokens["refresh_token"] = token_data["refresh_token"]

    return JSONResponse({"message": "Authorization successful. You can now call /activities."})

def refresh_access_token():
    """
    Refresh expired Strava access token using refresh token.
    
    Returns:
        bool: True if refresh successful, False otherwise
    """
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        return False

    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        return False

    # Update stored tokens
    token_data = response.json()
    tokens["access_token"] = token_data["access_token"]
    tokens["refresh_token"] = token_data["refresh_token"]
    return True

@app.get("/activities")
def get_activities():
    """
    Retrieve user's Strava activities filtered for 2024-2025 period.
    Handles pagination to fetch all activities and automatically refreshes
    expired tokens.
    
    Returns:
        JSONResponse: Activity data with total count and period information
    """
    access_token = tokens.get("access_token")
    if not access_token:
        return JSONResponse({"error": "No access token. Go to /authorize first."}, status_code=400)

    # Date range for 2024-2025 (Unix timestamps)
    start_2024 = int(datetime.datetime(2024, 1, 1).timestamp())
    end_2025 = int(datetime.datetime(2025, 12, 31, 23, 59, 59).timestamp())

    def fetch_activities_page(page_num):
        """Fetch a single page of activities from Strava API"""
        activities_url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        params = {
            'per_page': 200, 
            'page': page_num,
            'after': start_2024,   # Activities after Jan 1, 2024
            'before': end_2025     # Activities before Dec 31, 2025
        }
        return requests.get(activities_url, headers=headers, params=params)

    # Fetch all activities with pagination
    all_activities = []
    page_num = 1
    
    while True:
        response = fetch_activities_page(page_num)
        
        # Handle token expiration
        if response.status_code == 401:
            if refresh_access_token():
                response = fetch_activities_page(page_num)
            else:
                return JSONResponse({"error": "Failed to refresh token, please re-authorize."}, status_code=400)

        if response.status_code != 200:
            return JSONResponse({"error": "Failed to fetch activities", "details": response.json()}, status_code=400)

        activities_page = response.json()
        
        # If page is empty, we've fetched all activities
        if len(activities_page) == 0:
            break
            
        # Add activities from this page
        all_activities.extend(activities_page)
        page_num += 1
        
        # Safety limit: max 20 pages (4000 activities for 2024-2025)
        if page_num > 20:
            break

    # Simplify activity data structure for frontend consumption
    simplified = [
        {
            "name": a["name"],
            "distance": a["distance"],
            "moving_time": a["moving_time"],
            "type": a["type"],
            "start_date": a["start_date"],
            "total_elevation_gain": a.get("total_elevation_gain", 0),
            "average_speed": a.get("average_speed", 0)
        }
        for a in all_activities
    ]
    
    return JSONResponse({
        "total_activities": len(simplified),
        "activities": simplified,
        "period": "2024-2025"
    })

