import sqlite3
import datetime
import eel
import os

DB_PATH = "chat_history.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    # Legacy table (keep for backwards compatibility if needed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # New tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            user_message TEXT,
            bot_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    ''')
    
    con.commit()
    con.close()

# Initialize database on import
init_db()

@eel.expose
def create_conversation(title):
    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO conversations (title, created_at)
            VALUES (?, ?)
        ''', (title, timestamp))
        conv_id = cursor.lastrowid
        con.commit()
        con.close()
        return {"success": True, "conversation_id": conv_id}
    except Exception as e:
        print(f"Error creating conversation: {e}")
        return {"success": False, "error": str(e)}

@eel.expose
def get_conversations():
    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        cursor.execute('SELECT id, title, created_at FROM conversations ORDER BY id DESC')
        rows = cursor.fetchall()
        con.close()
        
        conversations = []
        for row in rows:
            conversations.append({
                "id": row[0],
                "title": row[1],
                "created_at": row[2]
            })
        return {"success": True, "data": conversations}
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return {"success": False, "error": str(e), "data": []}

@eel.expose
def get_messages(conversation_id):
    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        cursor.execute('SELECT user_message, bot_response, timestamp FROM messages WHERE conversation_id = ? ORDER BY id ASC', (conversation_id,))
        rows = cursor.fetchall()
        con.close()
        
        history = []
        for row in rows:
            history.append({
                "user_message": row[0],
                "bot_response": row[1],
                "timestamp": row[2]
            })
        return {"success": True, "data": history}
    except Exception as e:
        print(f"Error getting messages: {e}")
        return {"success": False, "error": str(e), "data": []}

@eel.expose
def save_message(conversation_id, user_message, bot_response):
    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO messages (conversation_id, user_message, bot_response, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (conversation_id, user_message, bot_response, timestamp))
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        print(f"Error saving message: {e}")
        return {"success": False, "error": str(e)}

@eel.expose
def delete_conversation(conversation_id):
    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        # Due to ON DELETE CASCADE (if enabled in PRAGMA) or just manual delete
        cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
        cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        print(f"Error deleting conversation: {e}")
        return {"success": False, "error": str(e)}

# Legacy save_chat for fallback compatibility
@eel.expose
def save_chat(user_message, bot_response):
    try:
        con = sqlite3.connect(DB_PATH)
        cursor = con.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO chat_history (user_message, bot_response, timestamp)
            VALUES (?, ?, ?)
        ''', (user_message, bot_response, timestamp))
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def get_history():
    pass

@eel.expose
def clear_history():
    pass
