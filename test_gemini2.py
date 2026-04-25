import google.generativeai as genai
import os

from dotenv import load_dotenv
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content("Hello")
    print("Gemini 2.5 Flash Response:", response.text)
except Exception as e:
    print("Gemini 2.5 Flash Error:", e)

try:
    model2 = genai.GenerativeModel("gemini-1.5-flash")
    response2 = model2.generate_content("Hello")
    print("Gemini 1.5 Flash Response:", response2.text)
except Exception as e:
    print("Gemini 1.5 Flash Error:", e)
