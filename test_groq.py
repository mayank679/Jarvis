import os
import base64
from groq import Groq

from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    print("Testing text...")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Hello, world!"
            }
        ],
        model="llama3-8b-8192",
    )
    print("Text:", chat_completion.choices[0].message.content)
except Exception as e:
    print("Text Error:", e)

try:
    print("Testing vision...")
    # 1px transparent gif base64
    b64 = "R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/gif;base64,{b64}"}}
                ]
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )
    print("Vision:", chat_completion.choices[0].message.content)
except Exception as e:
    print("Vision Error:", e)
