#!/usr/bin/env python3
"""
Strava MCP Client - A client that uses a simplified MCP protocol to communicate with the Strava server.
This client provides a chatbot interface that can call MCP tools to retrieve Strava data.
Compatible with Python 3.8.
"""

import asyncio
import json
import os
import subprocess
import sys
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Configure Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

class SimpleMCPClient:
    """Simple MCP client that communicates with the Strava server via subprocess"""
    
    def __init__(self):
        self.server_process = None
        self.available_tools = []
    
    async def start_server(self):
        """Start the MCP server as a subprocess"""
        try:
            print("🚀 Starting MCP Strava Server...")
            # Start the server with Python from venv
            python_path = ".venv/bin/python" if os.path.exists(".venv/bin/python") else "python3"
            self.server_process = await asyncio.create_subprocess_exec(
                python_path, "server.py",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print("✅ MCP Server started")
            
            # Initialize and get available tools
            await self.initialize()
            return True
            
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
    
    async def initialize(self):
        """Initialize the session and discover available tools"""
        try:
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "simple-mcp-1.0",
                    "capabilities": {"tools": True},
                    "clientInfo": {"name": "strava-chatbot", "version": "1.0.0"}
                }
            }
            
            response = await self._send_request(init_request)
            if response and "result" in response:
                print("🔧 MCP session initialized")
            
            # List available tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = await self._send_request(tools_request)
            if response and "result" in response and "tools" in response["result"]:
                self.available_tools = response["result"]["tools"]
                print(f"🛠️ Available tools: {[tool['name'] for tool in self.available_tools]}")
            
        except Exception as e:
            print(f"❌ MCP initialization failed: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Call a tool via simplified MCP protocol"""
        try:
            if arguments is None:
                arguments = {}
            
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            print(f"🛠️ Calling MCP tool: {tool_name}")
            response = await self._send_request(request)
            
            if response and "result" in response:
                content = response["result"].get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", "")
            elif response and "error" in response:
                error_msg = response["error"].get("message", "Unknown error")
                print(f"❌ Tool error: {error_msg}")
                return f"Error: {error_msg}"
            
            return None
            
        except Exception as e:
            print(f"❌ Tool call failed: {e}")
            return f"Error calling tool {tool_name}: {str(e)}"
    
    async def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC request to the MCP server"""
        try:
            if not self.server_process:
                raise Exception("MCP server not started")
            
            # Send request
            request_str = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_str.encode())
            await self.server_process.stdin.drain()
            
            # Read response with buffer for large messages
            response_lines = []
            while True:
                try:
                    # Read with a timeout to avoid hanging
                    response_line = await asyncio.wait_for(
                        self.server_process.stdout.readline(), 
                        timeout=30.0
                    )
                    
                    if not response_line:
                        break
                        
                    line_str = response_line.decode().strip()
                    if line_str:
                        # Try to parse as complete JSON
                        try:
                            return json.loads(line_str)
                        except json.JSONDecodeError:
                            # If it's not complete JSON, accumulate lines
                            response_lines.append(line_str)
                            # Try to parse accumulated lines
                            combined = ''.join(response_lines)
                            try:
                                return json.loads(combined)
                            except json.JSONDecodeError:
                                continue
                                
                except asyncio.TimeoutError:
                    print("⚠️ Timeout waiting for server response", file=sys.stderr)
                    break
            
            # If we accumulated lines but couldn't parse, try once more
            if response_lines:
                try:
                    combined = ''.join(response_lines)
                    return json.loads(combined)
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON response: {e}", file=sys.stderr)
                    print(f"Response preview: {combined[:200]}...", file=sys.stderr)
            
            return None
            
        except Exception as e:
            print(f"❌ MCP communication error: {e}")
            return None
    
    async def stop_server(self):
        """Stop the MCP server"""
        if self.server_process:
            try:
                self.server_process.terminate()
                await self.server_process.wait()
                print("🛑 MCP Server stopped")
            except Exception as e:
                print(f"❌ Error stopping server: {e}")

# Global MCP client instance
mcp_client = SimpleMCPClient()

async def get_strava_activities_via_mcp(limit: int = 50, sport_type: Optional[str] = None):
    """Get Strava activities using MCP tools"""
    try:
        arguments = {"limit": limit}  # Reduced limit to avoid communication issues
        if sport_type:
            arguments["sport_type"] = sport_type
        
        result = await mcp_client.call_tool("get_activities", arguments)
        if result:
            return json.loads(result)
        return None
        
    except Exception as e:
        print(f"❌ Error getting activities via MCP: {e}")
        return None

async def get_strava_stats_via_mcp():
    """Get Strava statistics using MCP tools"""
    try:
        result = await mcp_client.call_tool("get_activity_stats")
        if result:
            return json.loads(result)
        return None
        
    except Exception as e:
        print(f"❌ Error getting stats via MCP: {e}")
        return None

async def generate_response(user_input: str) -> str:
    """Generate a chatbot response using MCP tools"""
    
    # Build the system message with available tools
    available_tools_str = ", ".join([tool["name"] for tool in mcp_client.available_tools])
    
    messages = [
        {
            "role": "system",
            "content": (
                f"You are a factual Strava data assistant with access to MCP tools. 📊\n"
                f"Available tools: {available_tools_str}\n"
                f"When users ask about their Strava activities, analyze the data and provide direct, factual answers.\n"
                f"Be concise and focus only on answering what was asked.\n"
                f"Do not add motivational suggestions unless specifically requested.\n"
                f"Present data clearly with relevant statistics.\n\n"
                f"If the user asks about activities, the data will be provided automatically."
            )
        }
    ]
    
    # Check if this is a Strava-related question
    if any(keyword in user_input.lower() for keyword in ["strava", "activity", "activities", "sport", "run", "ride", "bike", "workout"]):
        print("🔍 Strava-related question detected, fetching MCP data...")
        
        # Get activities data via MCP protocol
        activities_data = await get_strava_activities_via_mcp()
        stats_data = await get_strava_stats_via_mcp()
        
        if activities_data and stats_data:
            context = f"""Here is the user's Strava data retrieved via MCP protocol:

SUMMARY STATISTICS:
{json.dumps(stats_data, indent=2)}

RECENT ACTIVITIES DATA:
{json.dumps(activities_data, indent=2)}

The data is sorted by date with the MOST RECENT activity FIRST.
Please analyze this data to answer the user's question accurately.
"""
            messages.append({
                "role": "user",
                "content": f"{context}\n\nUser Question: {user_input}"
            })
        else:
            messages.append({
                "role": "user", 
                "content": f"Unable to retrieve Strava data via MCP protocol. User Question: {user_input}"
            })
    else:
        # Non-Strava question
        messages.append({
            "role": "user",
            "content": user_input
        })
    
    try:
        # Call Azure OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"Error calling Azure OpenAI: {str(e)}"

async def main():
    """Main chatbot loop using simplified MCP protocol"""
    print("🚀 Strava MCP Chatbot starting...")
    
    # Start MCP server
    if not await mcp_client.start_server():
        print("❌ Failed to start MCP server. Exiting.")
        return
    
    try:
        print("🤖 Strava MCP Chatbot ready! Ask me about your activities...")
        print("💡 Available via MCP: get_activities, get_activity_stats")
        print("-" * 60)
        
        while True:
            user_input = input("💬 Ask your question: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Keep training! 💪")
                break
            
            response = await generate_response(user_input)
            print("\n🤖 Bot response:")
            print(response)
            print("-" * 60)
    
    finally:
        # Always stop the MCP server
        await mcp_client.stop_server()

if __name__ == "__main__":
    asyncio.run(main())


