from flask import Flask, request, jsonify, send_from_directory
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='www', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('www', 'index.html')

# Serve any static file from www/
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('www', filename)

# Mock eel.js so the browser doesn't 404
@app.route('/eel.js')
def eel_js():
    return 'console.log("eel.js mock loaded");', 200, {'Content-Type': 'application/javascript'}

@app.route('/api/allCommands', methods=['POST'])
def all_commands():
    data = request.json
    query = data.get('query', '')

    groq_key = os.getenv('GROQ_API_KEY', '')
    
    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant. Keep responses concise and helpful."},
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
    return jsonify({
        "cpu": 12.5,
        "battery": 100,
        "plugged": True
    })

@app.route('/api/password_login', methods=['POST'])
def password_login():
    data = request.json
    entered = data.get('password', '')
    # Default web password is 'jarvis' — set WEB_PASSWORD env var on Render to change it
    correct = os.getenv('WEB_PASSWORD', 'jarvis')
    if entered == correct:
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Incorrect password. Try 'jarvis'"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
