import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

try:
    from google import genai
except Exception as e:
    genai = None
    print("Could not import google.genai:", e)

_client = None
if API_KEY and genai:
    _client = genai.Client(api_key=API_KEY)

def ask_gemini(system_prompt: str, user_prompt: str) -> str | None:
    if _client is None:
        return None
    
    candidates = [
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro",
        "models/gemini-2.0-flash",
        "models/gemini-pro-latest",
    ]

    for model_name in candidates:
        try:
            resp = _client.models.generate_content(
                model=model_name,
                contents=f"{system_prompt}\n\nUser: {user_prompt}"
            )
            text = getattr(resp, "text", None)
            if text:
                return text
        except Exception as e:
            # Try next model
            continue

    return None