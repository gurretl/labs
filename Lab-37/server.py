#!/usr/bin/env python3
"""
Strava MCP Server - A simplified MCP-inspired server for Strava activities.
Compatible with Python 3.8 - provides JSON-RPC interface for Strava data.
"""

import asyncio
import json
import os
import requests
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from oauth2_manager import OAuth2Manager

# Load environment variables
load_dotenv()

class StravaAPI:
    """Handles Strava API interactions with proper OAuth2 flow"""
    
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.base_url = "https://www.strava.com/api/v3"
        
        if not self.client_id or not self.client_secret:
            raise Exception("CLIENT_ID and CLIENT_SECRET must be configured in .env file")
        
        # Initialize OAuth2 manager
        self.oauth_manager = OAuth2Manager(self.client_id, self.client_secret)
        self.access_token = None
    
    async def ensure_valid_token(self):
        """Ensure we have a valid access token"""
        try:
            # This will handle the full OAuth2 flow if needed
            self.access_token = self.oauth_manager.get_valid_access_token()
            return self.access_token
        except Exception as e:
            raise Exception(f"OAuth2 authorization failed: {e}")
    
    async def get_activities(self, limit: int = 200, sport_type: Optional[str] = None):
        """Fetch activities from Strava API"""
        await self.ensure_valid_token()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        all_activities = []
        page = 1
        per_page = 200
        
        # Define date range for 2022-2025 (last 3 years including all of 2024)
        after_timestamp = int(datetime(2022, 1, 1).timestamp())
        before_timestamp = int(datetime(2025, 12, 31).timestamp())
        
        print(f"🔍 Fetching activities from 2022-2025 (including all of 2024)...", file=sys.stderr)
        
        # Get enough activities to see 2024 activities
        max_activities = min(400, limit * 2)  # Enough to go far back but not too much for communication
        
        while len(all_activities) < max_activities:
            params = {
                'per_page': min(per_page, max_activities - len(all_activities)),
                'page': page,
                'after': after_timestamp,
                'before': before_timestamp
            }
            
            response = requests.get(f"{self.base_url}/activities", headers=headers, params=params)
            
            if response.status_code == 200:
                activities = response.json()
                if not activities:  # No more activities
                    break
                
                # Filter by sport type if specified
                if sport_type:
                    activities = [a for a in activities if a.get('type', '').lower() == sport_type.lower()]
                
                all_activities.extend(activities)
                page += 1
                print(f"📈 Retrieved {len(all_activities)} activities...", file=sys.stderr)
                
                if len(activities) < per_page:  # Last page
                    break
            else:
                raise Exception(f"Strava API error: {response.status_code} - {response.text}")
        
        # Sort by date (most recent first)
        all_activities.sort(key=lambda x: x.get('start_date', ''), reverse=True)
        
        # Return requested limit or all if limit is higher
        return all_activities[:limit] if limit <= len(all_activities) else all_activities

# Initialize Strava API
strava_api = StravaAPI()

class SimpleMCPServer:
    """Simplified MCP server for Python 3.8"""
    
    def __init__(self):
        self.tools = [
            {
                "name": "get_activities",
                "description": "Retrieve user's Strava activities from 2022-2025 including all of 2024",
                "parameters": {
                    "limit": {"type": "integer", "default": 50},
                    "sport_type": {"type": "string", "optional": True}
                }
            },
            {
                "name": "get_activity_stats", 
                "description": "Get summary statistics for all activities including longest activity from 2022-2025",
                "parameters": {}
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id", 1)
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "simple-mcp-1.0",
                        "capabilities": {"tools": True}
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "result": {"tools": self.tools}
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "get_activities":
                    result = await self.get_activities_tool(arguments)
                elif tool_name == "get_activity_stats":
                    result = await self.get_stats_tool()
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id, 
                    "result": {"content": [{"type": "text", "text": result}]}
                }
            
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "error": {"code": -1, "message": str(e)}
            }
    
    async def get_activities_tool(self, arguments: Dict[str, Any]) -> str:
        """Get activities tool implementation"""
        limit = arguments.get("limit", 200)
        sport_type = arguments.get("sport_type")
        
        print(f"🛠️ Tool called: get_activities(limit={limit}, sport_type={sport_type})", file=sys.stderr)
        
        activities = await strava_api.get_activities(limit=limit, sport_type=sport_type)
        
        # Format activities for the LLM
        formatted_activities = []
        for i, activity in enumerate(activities):
            formatted_activity = {
                "index": i,
                "name": activity.get('name', 'Unknown'),
                "type": activity.get('type', 'Unknown'),
                "distance_km": round(activity.get('distance', 0) / 1000, 2),
                "moving_time_hours": round(activity.get('moving_time', 0) / 3600, 2),
                "elevation_gain_m": activity.get('total_elevation_gain', 0),
                "start_date": activity.get('start_date', ''),
                "average_speed_kmh": round(activity.get('average_speed', 0) * 3.6, 2) if activity.get('average_speed') else 0,
                "max_speed_kmh": round(activity.get('max_speed', 0) * 3.6, 2) if activity.get('max_speed') else 0
            }
            formatted_activities.append(formatted_activity)
        
        result = {
            "activities": formatted_activities,
            "total_count": len(formatted_activities),
            "period": "2022-2025",
            "sorted_by": "date_desc"
        }
        
        return json.dumps(result, indent=2)
    
    async def get_stats_tool(self) -> str:
        """Get activity stats tool implementation"""
        print("🛠️ Tool called: get_activity_stats", file=sys.stderr)
        
        activities = await strava_api.get_activities(limit=400)  # More activities for stats, including 2024
        
        # Calculate statistics
        total_distance = sum(a.get('distance', 0) for a in activities) / 1000  # km
        total_time = sum(a.get('moving_time', 0) for a in activities) / 3600  # hours
        total_elevation = sum(a.get('total_elevation_gain', 0) for a in activities)
        
        # Count by activity type
        activity_types = {}
        for activity in activities:
            activity_type = activity.get('type', 'Unknown')
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        
        # Find longest activity by distance
        longest_activity = max(activities, key=lambda x: x.get('distance', 0)) if activities else None
        
        stats = {
            "total_activities": len(activities),
            "total_distance_km": round(total_distance, 1),
            "total_time_hours": round(total_time, 1),
            "total_elevation_gain_m": total_elevation,
            "activity_types": activity_types,
            "period": "2022-2025",
            "average_distance_per_activity_km": round(total_distance / len(activities), 1) if activities else 0,
            "longest_activity": {
                "name": longest_activity.get('name', 'Unknown'),
                "distance_km": round(longest_activity.get('distance', 0) / 1000, 2),
                "date": longest_activity.get('start_date', ''),
                "type": longest_activity.get('type', 'Unknown'),
                "moving_time_hours": round(longest_activity.get('moving_time', 0) / 3600, 2),
                "elevation_gain_m": longest_activity.get('total_elevation_gain', 0)
            } if longest_activity else None
        }
        
        return json.dumps(stats, indent=2)

async def main():
    """Main server loop - reads JSON-RPC requests from stdin"""
    print("🚀 Starting Strava MCP Server...", file=sys.stderr)
    print("⚠️  Note: Please ensure you have valid Strava tokens configured", file=sys.stderr)
    
    server = SimpleMCPServer()
    
    # Read requests from stdin and write responses to stdout
    while True:
        try:
            line = input()
            if not line.strip():
                continue
                
            request = json.loads(line)
            response = await server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
            
        except EOFError:
            break
        except Exception as e:
            print(f"❌ Server error: {e}", file=sys.stderr)
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -1, "message": str(e)}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    print("🏃‍♂️ Strava MCP Server - Python 3.8 Compatible", file=sys.stderr)
    asyncio.run(main())
