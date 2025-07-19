# Strava MCP Server 🏃‍♂️

A FastAPI-based server that provides a REST API interface to Strava activity data, featuring OAuth2 authentication and AI-powered chatbot integration.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Chatbot Integration](#chatbot-integration)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)

## 🎯 Overview

This project consists of two main components:
1. **FastAPI Backend Server** (`server.py`) - Handles Strava OAuth and provides REST API endpoints
2. **AI Chatbot** (`strava_chatbot.py`) - Provides natural language interface to analyze your Strava activities

The system allows you to authenticate with Strava, retrieve your activity data (filtered for 2024-2025), and interact with an AI assistant to analyze your training patterns, performance trends, and statistics.

## ✨ Features

### Backend Server

- 🔐 **OAuth2 Authentication** with Strava
- 🔄 **Automatic Token Refresh** handling
- 📊 **Activity Data Retrieval** with pagination support
- 📅 **Date Filtering** (2024-2025 period for performance optimization)
- ️ **Error Handling** and validation

### AI Chatbot

- 🤖 **Natural Language Processing** using Azure OpenAI GPT-4o
- 📊 **Activity Analysis** and insights with real-time calculations
- 📈 **Performance Tracking** and trend analysis
- 🗣️ **Conversational Interface** for data exploration
- 🧮 **Smart Statistics** - AI calculates metrics on demand

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐    OAuth2    ┌─────────────────┐
│   AI Chatbot    │ ──────────────> │  FastAPI Server │ ──────────> │   Strava API    │
│ (strava_chatbot)│                 │   (server.py)   │             │                 │
└─────────────────┘                 └─────────────────┘             └─────────────────┘
         │                                   │
         │                                   │
         v                                   v
┌─────────────────┐                 ┌─────────────────┐
│  Azure OpenAI   │                 │ In-Memory Store │
│     API         │                 │    (tokens)     │
└─────────────────┘                 └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Strava Developer Account
- Azure OpenAI Account
- Git

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd strava-mcp
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Strava Application Setup

1. Go to [Strava Developers](https://developers.strava.com/)
2. Create a new application
3. Set Authorization Callback Domain to `localhost`
4. Note your `Client ID` and `Client Secret`

### 2. Azure OpenAI Setup

1. Create an Azure OpenAI resource
2. Deploy a GPT-4o model
3. Get your API endpoint and key

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Strava Configuration
CLIENT_ID=your_strava_client_id
CLIENT_SECRET=your_strava_client_secret

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## 🎮 Usage

### Starting the Server

1. **Start the FastAPI server**
```bash
uvicorn server:app --reload --port 8000
```

2. **Authorize with Strava**
   - Visit `http://localhost:8000/authorize`
   - Complete the OAuth flow
   - You'll be redirected back with authorization success

3. **Test the API**
```bash
# Get activities
curl http://localhost:8000/activities

# Get statistics
curl http://localhost:8000/stats
```

### Using the Chatbot

```bash
python strava_chatbot.py
```

Example interactions:
- "How many activities did I do this year?"
- "What's my average running pace?"
- "Show me my longest bike ride"
- "Compare my performance between 2024 and 2025"

## 🔗 API Endpoints

### Authentication
- `GET /` - Health check and welcome message
- `GET /authorize` - Initiate Strava OAuth flow
- `GET /callback` - Handle OAuth callback

### Data Retrieval
- `GET /activities` - Get all activities (2024-2025)

### Response Examples

**GET /activities**

```json
{
  "total_activities": 267,
  "activities": [
    {
      "name": "Morning Run",
      "distance": 5000,
      "moving_time": 1800,
      "type": "Run",
      "start_date": "2024-01-15T07:00:00Z",
      "total_elevation_gain": 50,
      "average_speed": 2.78
    }
  ],
  "period": "2024-2025"
}
```

## 🤖 Chatbot Integration

The chatbot uses Azure OpenAI's GPT-4o model with function calling to:

1. **Fetch Data** - Calls the FastAPI server to get activity data
2. **Analyze** - Processes data to answer user questions and calculate statistics in real-time
3. **Respond** - Provides insights in natural language

### Key Functions

- `get_strava_activities()` - Retrieves activity data from the server
- `generate_response()` - Processes user queries with AI and calculates metrics on demand

## 🎬 **Pour votre vidéo YouTube**

**Structure simplifiée et plus claire :**
- `GET /` → Health check
- `GET /authorize` → OAuth flow  
- `GET /callback` → Token exchange
- `GET /activities` → **Seule source de données** (2024-2025)

**Avantages pour la vidéo :**
- ✅ **Moins de code à expliquer** (API ultra-simple)
- ✅ **Demo plus fluide** et directe
- ✅ **Focus sur l'architecture principale**
- ✅ **Le chatbot paraît plus intelligent** (il fait tous les calculs)

**Exemple de questions pour la démo :**
- *"Combien d'activités j'ai fait cette année ?"* → L'IA compte et répond
- *"Quelle est ma distance totale ?"* → L'IA calcule en temps réel
- *"Compare mes performances 2024 vs 2025"* → L'IA analyse et compare

Le chatbot devient le **vrai cerveau** du système ! 🧠

## 📁 Project Structure

```text
strava-mcp/
├── server.py              # FastAPI backend server (4 endpoints only!)
├── strava_chatbot.py      # AI chatbot interface
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── README.md             # This file
├── start_server.sh       # Server startup script
├── backup/               # Backup files
│   ├── main.py
│   └── strava_chatbot.py
└── tests/                # Experimental MCP files
    ├── mcp_server.py
    └── chatbot_mcp.py
```

## 🛠️ Development

### Key Dependencies

- **FastAPI 0.104.1** - Modern web framework for APIs
- **Uvicorn 0.24.0** - ASGI server for FastAPI
- **Requests 2.31.0** - HTTP library for API calls
- **OpenAI 1.3.7** - Azure OpenAI integration
- **Python-dotenv 1.0.0** - Environment variable management

### Running in Development Mode

```bash
# Start server with auto-reload
uvicorn server:app --reload --port 8000

# Run chatbot
python strava_chatbot.py
```

### Adding New Endpoints

1. Add the endpoint function in `server.py`
2. Add corresponding function in `strava_chatbot.py` if needed
3. Update the chatbot's function definitions for AI integration
4. Test the integration

**Note**: With the simplified architecture, most new features should be implemented in the chatbot's AI logic rather than new API endpoints.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Notes

- **Token Storage**: Currently uses in-memory storage. For production, implement database storage.
- **Date Filtering**: Limited to 2024-2025 for performance optimization.
- **Rate Limiting**: Strava API has rate limits (100 requests per 15 minutes, 1000 per day).
- **Security**: Ensure environment variables are properly secured in production.
- **AI-First Architecture**: Statistics and analysis are calculated by the AI chatbot for maximum flexibility.

## 🔧 Troubleshooting

### Common Issues

1. **Token Expired**: The server automatically handles token refresh
2. **OAuth Failed**: Check your Strava app configuration and callback URL
3. **No Activities**: Ensure you have activities in the 2024-2025 period
4. **Chatbot Not Responding**: Verify Azure OpenAI configuration

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

---

## Built with ❤️ for the Strava community
