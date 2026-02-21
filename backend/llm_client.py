# backend/llm_client.py
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

try:
    from google import genai
except Exception as e:
    genai = None
    print("IMPORT ERROR:", repr(e))

_client = None
if API_KEY and genai:
    try:
        _client = genai.Client(api_key=API_KEY)
    except Exception as e:
        print("CLIENT INIT ERROR:", repr(e))

def ask_gemini(system_prompt: str, user_prompt: str) -> Optional[str]:
    if not _client:
        print("LLM not initialized")
        return None

    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",  # ✅ working current model
            contents=f"{system_prompt}\n\nUser: {user_prompt}"
        )

        if response.text:
            return response.text.strip()

        print("No text returned:", response)
        return None

    except Exception as e:
        print("GEMINI CALL FAILED:", repr(e))
        return None