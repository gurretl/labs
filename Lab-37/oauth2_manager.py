#!/usr/bin/env python3
"""
Strava OAuth2 Manager - Handles complete OAuth2 flow for Strava API
Compatible with Python 3.8
"""

import json
import os
import secrets
import urllib.parse
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Dict, Optional
import requests


class OAuth2Manager:
    """Manages OAuth2 flow for Strava API"""
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = "http://localhost:8080/callback"
        self.auth_url = "https://www.strava.com/oauth/authorize"
        self.token_url = "https://www.strava.com/oauth/token"
        self.token_file = ".strava_tokens.json"
        
        # OAuth2 state for security
        self.state = secrets.token_urlsafe(32)
        self.authorization_code = None
        self.server = None
        
    def get_authorization_url(self):
        """Generate the authorization URL for Strava OAuth2"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'approval_prompt': 'force',
            'scope': 'read,activity:read_all',
            'state': self.state
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"
    
    def start_callback_server(self):
        """Start local server to receive OAuth callback"""
        
        oauth_manager = self  # Store reference for the handler
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                # Parse the callback URL
                parsed_url = urllib.parse.urlparse(self.path)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                if 'code' in query_params and 'state' in query_params:
                    received_state = query_params['state'][0]
                    if received_state == oauth_manager.state:
                        oauth_manager.authorization_code = query_params['code'][0]
                        
                        # Send success response
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        success_html = """
                        <html>
                        <body>
                        <h1>✅ Authorization Successful!</h1>
                        <p>You can close this window and return to your terminal.</p>
                        <script>setTimeout(function(){window.close();}, 3000);</script>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode())
                    else:
                        self.send_error(400, "Invalid state parameter")
                else:
                    self.send_error(400, "Missing authorization code")
            
            def log_message(self, format, *args):
                # Suppress server logs
                pass
        
        self.server = HTTPServer(('localhost', 8080), CallbackHandler)
        server_thread = Thread(target=self.server.serve_forever, daemon=True)
        server_thread.start()
        
        print("🌐 Started local callback server on http://localhost:8080")
    
    def stop_callback_server(self):
        """Stop the callback server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def exchange_code_for_tokens(self, authorization_code):
        """Exchange authorization code for access tokens"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")
    
    def refresh_token(self, refresh_token):
        """Refresh an expired access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token refresh failed: {response.status_code} - {response.text}")
    
    def save_tokens(self, token_data):
        """Save tokens to local file with secure permissions"""
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        # Set secure file permissions (read/write for owner only)
        os.chmod(self.token_file, 0o600)
        print(f"💾 Tokens saved to {self.token_file} (secure permissions)")
    
    def load_tokens(self):
        """Load tokens from local file"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None
    
    def get_valid_access_token(self):
        """Get a valid access token, refreshing if necessary"""
        tokens = self.load_tokens()
        
        if not tokens:
            print("🔐 No saved tokens found. Starting OAuth2 authorization...")
            return self.authorize()
        
        # Check if token is expired (with 5 minute buffer)
        expires_at = tokens.get('expires_at', 0)
        current_time = datetime.now().timestamp()
        
        if current_time >= (expires_at - 300):  # 5 minutes buffer
            print("🔄 Access token expired, refreshing...")
            try:
                new_tokens = self.refresh_token(tokens['refresh_token'])
                self.save_tokens(new_tokens)
                return new_tokens['access_token']
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                print("🔐 Starting new authorization...")
                return self.authorize()
        
        print("✅ Using existing valid access token")
        return tokens['access_token']
    
    def authorize(self):
        """Complete OAuth2 authorization flow"""
        print("🚀 Starting Strava OAuth2 authorization...")
        
        # Start callback server
        self.start_callback_server()
        
        try:
            # Open authorization URL in browser
            auth_url = self.get_authorization_url()
            print(f"🌐 Opening authorization URL: {auth_url}")
            webbrowser.open(auth_url)
            
            print("⏳ Waiting for authorization (please approve in your browser)...")
            
            # Wait for authorization code
            import time
            timeout = 300  # 5 minutes timeout
            start_time = time.time()
            
            while not self.authorization_code and (time.time() - start_time) < timeout:
                time.sleep(1)
            
            if not self.authorization_code:
                raise Exception("Authorization timeout - no code received")
            
            # Exchange code for tokens
            print("🔄 Exchanging authorization code for tokens...")
            token_data = self.exchange_code_for_tokens(self.authorization_code)
            
            # Save tokens
            self.save_tokens(token_data)
            
            print("✅ OAuth2 authorization completed successfully!")
            return token_data['access_token']
            
        finally:
            self.stop_callback_server()


def main():
    """Test the OAuth2 flow"""
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ CLIENT_ID and CLIENT_SECRET must be set in .env file")
        return
    
    oauth = OAuth2Manager(client_id, client_secret)
    
    try:
        access_token = oauth.get_valid_access_token()
        print(f"🎉 Got access token: {access_token[:20]}...")
        
        # Test API call
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)
        
        if response.status_code == 200:
            athlete = response.json()
            print(f"👋 Hello {athlete['firstname']} {athlete['lastname']}!")
        else:
            print(f"❌ API test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ OAuth2 failed: {e}")


if __name__ == "__main__":
    main()
