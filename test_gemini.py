import google.generativeai as genai
import os

from dotenv import load_dotenv
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content("Hello")
    print("Gemini Response:", response.text)
except Exception as e:
    print("Gemini Error:", e)
