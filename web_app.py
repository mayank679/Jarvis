from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from dotenv import load_dotenv
import sqlite3
from engine.features import geminai, analyze_image
from engine.command import speak

load_dotenv()

app = Flask(__name__, static_folder='www', static_url_path='')

# Mock eel.expose for web
@app.route('/')
def index():
    return send_from_directory('www', 'index.html')

@app.route('/api/allCommands', methods=['POST'])
def all_commands():
    data = request.json
    query = data.get('query')
    # In web mode, we just return the LLM response text
    # We need to modify geminai to return text instead of just speaking
    from engine.config import ASSISTANT_NAME, LLM_KEY
    from groq import Groq
    from engine.helper import markdown_to_text
    
    try:
        query = query.replace(ASSISTANT_NAME, "")
        client = Groq(api_key=LLM_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant. Keep responses concise."},
                {"role": "user", "content": query}
            ],
            model="llama-3.3-70b-versatile",
        )
        response_text = chat_completion.choices[0].message.content
        return jsonify({"success": True, "response": response_text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/get_system_stats')
def system_stats():
    # Mock stats for web demo
    return jsonify({
        "cpu": 15.5,
        "battery": 85,
        "plugged": True
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
