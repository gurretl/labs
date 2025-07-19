import os
from openai import AzureOpenAI
import requests

# Configure Azure OpenAI client using environment variables
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

def get_strava_activities():
    """
    Fetch all Strava activities from the local MCP server API.
    Returns a tuple: (list of activities, total count).
    Handles both the new and legacy response formats.
    """
    try:
        print("🔄 Fetching Strava activities...")
        response = requests.get("http://localhost:8000/activities", timeout=60)  # Longer timeout for large data
        print(f"📡 Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"📊 Raw response type: {type(data)}")

            # Handle new response format (dict with 'activities' key)
            if isinstance(data, dict) and "activities" in data:
                activities = data["activities"]
                total_count = data.get("total_activities", 0)
                period = data.get("period", "unknown")
                print(f"✅ Found {total_count} activities for period {period}")
                return activities, total_count
            elif isinstance(data, list):
                # Legacy format: direct list of activities
                print(f"✅ Found {len(data)} activities (legacy format)")
                return data, len(data)
            else:
                print(f"❌ Unexpected data format: {data}")
                return None, 0
        else:
            print(f"❌ MCP Server Error: {response.status_code} - {response.text}")
            return None, 0
    except Exception as e:
        print(f"❌ MCP Server Error: {str(e)}")
        return None, 0

def generate_response(user_input):
    """
    Generate a chatbot response to the user's question, using Strava activity data if relevant.
    If the question is about Strava, fetches activities and provides all data to the LLM for analysis.
    """
    context = ""

    # Detect if the user's question is about Strava or activities
    if "strava" in user_input.lower() or "activity" in user_input.lower() or "sport" in user_input.lower():
        print("🔍 Strava-related question detected, fetching data...")
        activities, total_count = get_strava_activities()

        print(f"📈 Retrieved: {total_count} activities")

        if activities and isinstance(activities, list) and len(activities) > 0:
            print(f"✅ Processing {len(activities)} activities...")

            # Compute general statistics (no sorting or advanced analysis here)
            total_distance = sum(a.get('distance', 0) for a in activities) / 1000  # in km
            total_time = sum(a.get('moving_time', 0) for a in activities) / 3600  # in hours

            print(f"📊 Stats: {total_distance:.1f}km, {total_time:.1f}h")

            # Count activity types
            activity_types = {}
            for a in activities:
                activity_type = a.get('type', 'Unknown')
                activity_types[activity_type] = activity_types.get(activity_type, 0) + 1

            print(f"🏃 Activity types: {activity_types}")

            # Prepare raw activity data for the LLM (all activities, unsorted)
            activities_data = []
            for i, a in enumerate(activities):
                try:
                    distance_km = a.get('distance', 0) / 1000
                    time_hours = a.get('moving_time', 0) / 3600
                    elevation = a.get('total_elevation_gain', 0)
                    activity_data = {
                        "name": a.get('name', 'Unknown name'),
                        "type": a.get('type', 'Unknown'),
                        "distance_km": round(distance_km, 1),
                        "time_hours": round(time_hours, 1),
                        "elevation_gain_m": elevation,
                        "start_date": a.get('start_date', '')
                    }
                    activities_data.append(activity_data)

                    if i < 5:  # Log only the first 5 for debug
                        print(f"  Activity {i+1}: {activity_data['name']} - {distance_km:.1f}km")

                except Exception as e:
                    print(f"❌ Error parsing activity {i+1}: {str(e)}")

            # Build context for the LLM with all raw data and clear instructions
            context = f"""Here is the user's Strava data (2024-2025):

SUMMARY STATISTICS:
- Total activities: {total_count}
- Total distance: {total_distance:.1f} km
- Total time: {total_time:.1f} hours
- Activity types: {', '.join([f"{k}: {v}" for k, v in activity_types.items()])}

ALL ACTIVITIES DATA (sorted by date, MOST RECENT FIRST):
{activities_data}

IMPORTANT NOTES:
- Activities are sorted by date with the MOST RECENT activity FIRST (index 0)
- When user asks for "last activity" or "most recent", it's the FIRST item in the list
- All dates are in ISO format (YYYY-MM-DDTHH:MM:SSZ)
- Please analyze this data carefully to answer the user's question
"""
        else:
            print("❌ No activities found or error in data")
            context = "Unable to retrieve Strava activities or no activities found.\n"

    # Build the prompt for the LLM
    messages = [
        {
            "role": "system",
            "content": (
                "You are a motivational Strava sports assistant. 🏃‍♂️ "
                "When the user asks about their Strava activities, you need to analyze the provided data "
                "to answer their questions accurately. Look through ALL the activities data to find "
                "the correct information (longest, shortest, fastest, etc.). "
                "Provide analysis, encouragement, and improvement suggestions. "
                "Use emojis to make your responses more engaging! 💪"
            )
        },
        {
            "role": "user",
            "content": f"{context}Question: {user_input}"
        }
    ]

    try:
        # Call the Azure OpenAI chat completion API
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error calling Azure OpenAI: {str(e)}"

if __name__ == "__main__":
    """
    Main interactive loop for the Strava chatbot.
    Continuously prompts the user for questions and prints the AI's response.
    Type 'quit', 'exit', or 'bye' to stop the chatbot.
    """
    print("🚀 Strava Chatbot started! Ask me about your activities...")
    print("-" * 50)
    while True:
        user_input = input("💬 Ask your question: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye! Keep training! 💪")
            break
        response = generate_response(user_input)
        print("\n🤖 Bot response:")
        print(response)
        print("-" * 50)
