import sqlite3
con = sqlite3.connect("jarvis.db")
cur = con.cursor()
cur.execute("SELECT name, mobile_no FROM contacts WHERE LOWER(name) LIKE '%aakash%'")
for row in cur.fetchall()[:5]:
    print(row[0], "|", row[1])
