import csv
import sqlite3

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

# Clear existing contacts to avoid duplicates
cursor.execute('DELETE FROM contacts')
con.commit()

# indices based on the CSV structure: 0 for Name, 20 for Phone 1 - Value
desired_columns_indices = [0, 20]

with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    # Skip header row
    next(csvreader, None)
    
    count = 0
    for row in csvreader:
        if len(row) > 20:
            name = row[0].strip()
            mobile_no = row[20].strip()
            if name and mobile_no:
                cursor.execute(''' INSERT INTO contacts (id, name, mobile_no) VALUES (null, ?, ?);''', (name, mobile_no))
                count += 1

con.commit()
print(f"Successfully imported {count} contacts into jarvis.db")
con.close()
