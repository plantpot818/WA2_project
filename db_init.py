import sqlite3

conn = sqlite3.connect("exam.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS exams (
    test_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT,
    classes TEXT, 
    subject TEXT, 
    location TEXT, 
    date TEXT, 
    start_time TEXT, 
    end_time TEXT,
    description TEXT,
);
''')

conn.commit()
conn.close()
