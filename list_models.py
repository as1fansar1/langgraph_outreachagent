import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key or "your_groq_api_key_here" in api_key:
    # Try to see if we can find it in the user's environment if they promoted it? 
    # Or just warn.
    pass

url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    models = response.json()
    print(json.dumps(models, indent=2))
except Exception as e:
    print(f"Error fetching models: {e}")
