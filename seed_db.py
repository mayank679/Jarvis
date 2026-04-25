import sqlite3

def seed_db():
    try:
        con = sqlite3.connect("jarvis.db")
        cursor = con.cursor()

        # Create tables if they don't exist
        cursor.execute("CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))")
        cursor.execute("CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))")

        # Define 10 system commands
        sys_commands = [
            ('one note', 'C:\\Program Files\\Microsoft Office\\root\\Office16\\ONENOTE.exe'),
            ('notepad', 'notepad.exe'),
            ('calculator', 'calc.exe'),
            ('paint', 'mspaint.exe'),
            ('command prompt', 'cmd.exe'),
            ('file explorer', 'explorer.exe'),
            ('task manager', 'taskmgr.exe'),
            ('control panel', 'control.exe'),
            ('word', 'winword.exe'),
            ('excel', 'excel.exe'),
            ('powerpoint', 'powerpnt.exe'),
            ('chrome', 'chrome.exe'),
            ('edge', 'msedge.exe')
        ]

        # Define 10 web commands
        web_commands = [
            ('youtube', 'https://www.youtube.com/'),
            ('canva', 'https://www.canva.com/'),
            ('google', 'https://www.google.com/'),
            ('github', 'https://github.com/'),
            ('chatgpt', 'https://chatgpt.com/'),
            ('netflix', 'https://www.netflix.com/'),
            ('amazon', 'https://www.amazon.in/'),
            ('whatsapp', 'https://web.whatsapp.com/'),
            ('linkedin', 'https://www.linkedin.com/'),
            ('spotify', 'https://open.spotify.com/'),
            ('twitter', 'https://twitter.com/'),
            ('instagram', 'https://www.instagram.com/'),
        ]

        # Insert sys commands if they don't already exist
        for name, path in sys_commands:
            cursor.execute('SELECT * FROM sys_command WHERE name=?', (name,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO sys_command (name, path) VALUES (?, ?)", (name, path))

        # Insert web commands if they don't already exist
        for name, url in web_commands:
            cursor.execute('SELECT * FROM web_command WHERE name=?', (name,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO web_command (name, url) VALUES (?, ?)", (name, url))

        con.commit()
        print("Successfully added sys_command and web_command entries.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if con:
            con.close()

if __name__ == "__main__":
    seed_db()
