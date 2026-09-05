from google import genai
import os

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("No existe GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Responde únicamente: GEMINI_OK"
)

print(response.text)
