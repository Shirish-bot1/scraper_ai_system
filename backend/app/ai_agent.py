from groq import Groq
import os
from dotenv import load_dotenv
from app.services.data_fetcher import (
    get_complete_municipality_data
)
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY)


def chat_with_agent(user_query, municipality_name):

    data = get_complete_municipality_data(
        municipality_name
    )

    if not data:
        return "Municipality information not available."

    prompt = f"""
You are a professional assistant for Nepali Local Government data.

Municipality Data:
{data}

User Question:
{user_query}

Rules:
1. Use only the municipality data provided.
2. Do not invent information.
3. If data is missing, say it is not available.
4. Answer clearly and professionally.
5. if asked in english name give info by understanding it.
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant for Nepal Municipalities."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception as e:
        print("Groq Error:", e)
        return "AI service is currently unavailable."