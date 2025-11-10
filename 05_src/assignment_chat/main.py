import gradio as gr
import openai
import requests
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import chromadb
from chromadb.config import Settings
import numpy as np
import pandas as pd
import datetime
import json
import os
from openai import OpenAI   
from dotenv import load_dotenv
from utils.logger import get_logger
from assignment_chat.prompts import return_instructions_root




_logs = get_logger(__name__)

load_dotenv(".env")
load_dotenv(".secrets")
client = OpenAI()

open_ai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


tools = [
    {
        "type": "function",
        "name": "get_wather_summary",
        "description": "This tool retrieves the weather of a city for today.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "weather of a city",
                }
            },
            "required": ["city"],
            "additionalProperties": False
        },
        
    },
]


CITY_COORDS = {
    "toronto": (43.7, -79.38),
    "vancouver": (49.28, -123.12),
    "montreal": (45.50, -73.56),
    "colima": (19.24, 103.72),
    "paris": (48.85, 2.35)
}


def get_weather_summary(city:str):
    city_lower = city.lower()
    if city_lower not in CITY_COORDS:
        return f"Sorry, I only know a few cities right now: {', '.join(CITY_COORDS.keys())}."

    lat, lon = CITY_COORDS[city_lower]
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true"
    )
    r = requests.get(url)
    if r.status_code != 200:
        return f"Couldn't fetch weather data for {city}."

    data = r.json().get("current_weather", {})
    temp = data.get("temperature")
    wind = data.get("windspeed")
    weather_info = f"Temperature {temp}°C and wind speed {wind} km/h in {city.title()}."

    # Prepare messages for chat in a specific tone llike in past assignment
    messages = [
        {"role": "system", "content": "You are a friendly rapper assistant giving short weather updates."},
        {"role": "user", "content": f"Summarize the following weather info for a friendly chat response:\n{weather_info}\nMake it African-American Vernacular English tone."}
    ]

    completion = client.chat.completions.create(
        model=open_ai_model,
        messages=messages,
        temperature=0.7
    )

    summary = completion.choices[0].message.content.strip()
    return summary



def weather_chat(city: str) -> str:
    _logs.info(f'User message: {city}')
    
    instructions = return_instructions_root()
    
    user_msg = {
        "role": "user",
        "content": city
    }
    
    conversation_input = user_msg
    
    response = get_weather_summary(conversation_input)
        
    
    conversation_input += response.output



    return response.output_text