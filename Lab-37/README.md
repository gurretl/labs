# Strava MCP (Model Context Protocol) Integration

A simplified implementation of the Model Context Protocol (MCP) for Strava activity data, providing a chatbot interface to analyze your Strava activities using Azure OpenAI.

## Features

- **MCP Protocol**: Simplified JSON-RPC implementation compatible with Python 3.8+
- **Strava OAuth2**: Complete authentication flow with automatic token refresh
- **Real-time Data**: Fetches actual Strava activities from 2022-2025 (including all 2024 data)
- **AI Chat Interface**: Azure OpenAI GPT-4o integration for conversational analysis
- **Historical Analysis**: Retrieves up to 400+ activities for comprehensive statistics

## Architecture

The project consists of 4 core files implementing a clean MCP architecture:

```bash
📁 strava-mcp/
├── server.py           # MCP server - provides Strava tools via JSON-RPC
├── strava_chatbot.py   # MCP client + chatbot interface with Azure OpenAI
├── oauth2_manager.py   # OAuth2 authentication manager
├── start_server.sh     # System launcher
├── .env               # Environment variables (Strava & Azure credentials)
└── requirements.txt   # Python dependencies
```

## Quick Start

### 1. Environment Setup

Create a `.env` file with your credentials:

```env
# Strava OAuth2 Configuration  
CLIENT_ID=your_strava_client_id
CLIENT_SECRET=your_strava_client_secret

# Azure OpenAI Configuration
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_VERSION=2024-10-21
```

### 2. OAuth2 Setup (Required)

1. **Create a Strava App:**
   - Go to [Strava Developers](https://www.strava.com/settings/api)
   - Create a new application with:
     - **Authorization Callback Domain**: `localhost`
     - **Authorization Callback URL**: `http://localhost:8080/callback`

2. **OAuth2 Flow:**
   - The system uses proper OAuth2 authorization code flow
   - On first run, it will automatically open your browser for authorization
   - Tokens are stored securely in `.strava_tokens.json` (excluded from git)
   - Automatic refresh handling with 5-minute buffer

### 3. Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Launch

```bash
# Make launcher executable
chmod +x start_server.sh

# Start the MCP system
./start_server.sh
```

**🔐 OAuth2 Flow (Automatic):**

- **First run:** The system will automatically detect no tokens and start OAuth2 authorization
- **Browser opens:** Approve the authorization request
- **Tokens saved:** System stores tokens securely in `.strava_tokens.json`
- **Future runs:** Automatic token refresh, no manual intervention needed

**Note:** You do NOT need to run `oauth2_manager.py` manually - it's handled automatically by the system!

## Testing & Validation

### 🧪 **System Tests**

**1. OAuth2 Authorization Test (Optional - for troubleshooting only):**

```bash
# Test OAuth2 flow independently (only if issues occur)
python oauth2_manager.py
```

**Note:** This is NOT required for normal usage - OAuth2 is handled automatically by `./start_server.sh`

Expected output:

```text
🚀 Starting Strava OAuth2 authorization...
🌐 Opening authorization URL: https://www.strava.com/oauth/authorize?...
⏳ Waiting for authorization (please approve in your browser)...
✅ OAuth2 authorization completed successfully!
👋 Hello [Your Name]!
```

**2. MCP Server Test:**

```bash
# Test MCP server directly (advanced)
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python server.py
```

**3. Full Integration Test:**

```bash
# Complete system test
./start_server.sh
```

### 🔍 **Validation Checklist**

**✅ Environment Setup:**

- [ ] `.env` file exists with valid credentials
- [ ] Virtual environment activated
- [ ] All dependencies installed

**✅ OAuth2 Configuration:**

- [ ] Strava app created with correct callback URL
- [ ] CLIENT_ID and CLIENT_SECRET configured
- [ ] OAuth2 flow completes successfully
- [ ] `.strava_tokens.json` created with secure permissions (600)

**✅ System Functionality:**

- [ ] MCP server starts without errors
- [ ] Chatbot connects to MCP server
- [ ] Azure OpenAI integration working
- [ ] Real Strava data retrieved (test with "How many activities do I have?")

### 🐛 **Troubleshooting**

**OAuth2 Issues:**

```bash
# If authorization fails, delete tokens and retry
rm .strava_tokens.json
python oauth2_manager.py
```

**Python Environment Issues:**

```bash
# Check Python version (requires 3.8+)
python --version

# Recreate virtual environment if needed
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Port Conflicts:**

```bash
# If port 8080 is busy, kill conflicting processes
lsof -ti:8080 | xargs kill -9
```

### ✅ **Expected Test Results**

When everything works correctly:

1. **OAuth2 Test:** Browser opens → You authorize → Success message → API test passes
2. **System Test:** MCP server starts → Chatbot connects → Ask "What's my longest activity?" → Real data returned
3. **File Security:** `.strava_tokens.json` has 600 permissions → File excluded from git

### 🚀 **Sample Test Session**

```bash
$ ./start_server.sh
🚀 Starting Strava MCP System...
📦 Using configured Python environment...
🤖 Strava MCP Chatbot ready! Ask me about your activities...
💡 Available via MCP: get_activities, get_activity_stats
------------------------------------------------------------

💬 Ask your question: What is my longest activity?
🔍 Strava-related question detected, fetching MCP data...
🛠️ Calling MCP tool: get_activities
📈 Retrieved 250 activities...
🛠️ Tool called: get_activity_stats

🤖 Bot response:
Your longest activity is "Swisspeaks 360" - a hike covering 413.18 km on 2024-09-07. 
This was an impressive 68.8-hour adventure with 21,733m of elevation gain.

Your other notable long activities include:
- "Niesen" (31.8 km hike)  
- "Jungfraujoch" (28.4 km hike)
- "Matterhorn" (26.7 km hike)
------------------------------------------------------------
```

## MCP Tools Available

The server provides two main tools accessible via the MCP protocol:

- **`get_activities`**: Retrieve Strava activities with filtering options
- **`get_activity_stats`**: Get comprehensive activity statistics including longest activities

## Usage Examples

Once the chatbot is running, you can ask questions like:

```bash
💬 Ask your question: What is my longest activity on Strava?
💬 Ask your question: How many activities did I do in 2024?
💬 Ask your question: Show me my running statistics
💬 Ask your question: What's my total distance this year?
```

The system will automatically:

1. Detect Strava-related questions
2. Call appropriate MCP tools to fetch real data
3. Provide factual, data-driven responses without unnecessary motivational content

## Technical Details

### MCP Implementation

- **Protocol**: Simplified JSON-RPC over subprocess stdin/stdout
- **Compatibility**: Python 3.8+ (no modern syntax dependencies)
- **Communication**: Asynchronous message handling with timeout protection

### Strava Integration

- **OAuth2**: Complete authentication flow with token refresh
- **Data Range**: 2022-2025 to capture all historical activities
- **Rate Limiting**: Intelligent pagination and request management
- **Real Data**: Connects to actual Strava API, no demo/mock data

### AI Integration

- **Model**: Azure OpenAI GPT-4o
- **Approach**: Factual analysis without unnecessary motivational suggestions
- **Context**: Full activity data provided for accurate responses

## Development

### File Structure

- `server.py`: Core MCP server handling Strava API integration
- `strava_chatbot.py`: MCP client with subprocess management and AI integration
- `oauth2_manager.py`: Complete OAuth2 flow with token management
- `start_server.sh`: Simple launcher that activates venv and starts the chatbot

### Key Classes

- `StravaAPI`: Handles OAuth2 and API interactions
- `OAuth2Manager`: Complete OAuth2 authorization code flow
- `SimpleMCPClient`: MCP protocol client implementation
- `SimpleMCPServer`: JSON-RPC server for tool execution

## Requirements

- Python 3.8+
- Strava Developer Account (for OAuth2 credentials)
- Azure OpenAI Account (for GPT-4o access)
- Active internet connection for API calls

## License

This project demonstrates MCP protocol implementation for educational purposes.
