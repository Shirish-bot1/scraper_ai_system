from groq import Groq
import os
import re
from dotenv import load_dotenv

from app.services.data_fetcher import (
    get_complete_municipality_data,
    get_multiple_municipalities
)

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)


def chat_with_agent(user_query, municipality_name):

    query_lower = user_query.lower()

    # ==========================
    # SMART REQUEST DETECTION
    # ==========================

    limit = None

    # detect number request (e.g. 5 municipalities)
    match = re.search(r"\b(\d+)\b", query_lower)
    if match:
        limit = int(match.group(1))

    # all municipalities shortcut
    if "all municipalities" in query_lower:
        limit = 753

    # ==========================
    # FETCH DATA
    # ==========================
    try:
        if limit:
            data = get_multiple_municipalities(limit)
        else:
            data = get_complete_municipality_data(municipality_name)

        if not data:
            return "Municipality information not found."

    except Exception as e:
        print("Data Fetch Error:", e)
        return "Error fetching municipality data."

    # ==========================
    # CLEAN + STRICT PROMPT
    # ==========================
    prompt = f"""
You are "Municipality AI Assistant" for Nepal government data.

==========================
STRICT OUTPUT RULES
==========================

1. NEVER output CSV format.
2. NEVER output markdown tables.
3. NEVER output raw JSON or database format.
4. ALWAYS respond in clean, structured natural language.
5. If user asks for CSV:
   → ONLY respond: "CSV file is ready for download"
   → DO NOT print data.
6. If user asks for table:
   → Convert into bullet points.
7. NEVER invent data not present in DATA.
8. NEVER repeat same information in multiple formats.
9. Keep response professional like ChatGPT.

==========================
DATA (SOURCE OF TRUTH)
==========================
{data}

==========================
USER QUESTION
==========================
{user_query}

==========================
RESPONSE STYLE (IMPORTANT)
==========================

- Respond like a helpful chat assistant, NOT a report generator.
- Do NOT force fixed bullet structure every time.
- Use bullets ONLY when helpful.
- Prefer natural sentences + short explanations.
- Ask follow-up questions when needed.
- If user is unclear → ask clarification instead of guessing.
- Keep tone conversational and interactive like ChatGPT.

IF MULTIPLE MUNICIPALITIES:
- Start with short summary line
- Then list municipalities as clean bullets:
  • Name – District – Province – Mayor

IF CSV REQUESTED:
- DO NOT generate data
- Only say CSV is available for download
"""

    # ==========================
    # GROQ CALL
    # ==========================
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a professional government data assistant.

CORE RULES:
- Be precise and factual
- Never hallucinate
- Never output CSV or tables
- Always format responses cleanly like ChatGPT
- Prefer bullet points and structured text
- Summarize large datasets instead of dumping them
- You are an interactive assistant, not a static database viewer.
- If user asks something simple → answer briefly.
- If user asks comparison → explain differences conversationally.
- If user asks vague question → ask follow-up question.
- You can suggest insights (like population trends, governance info if available).
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=1200
        )

        return response.choices[0].message.content

    except Exception as e:
        print("Groq Error:", e)
        return "AI service is currently unavailable."