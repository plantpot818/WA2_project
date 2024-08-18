import sqlite3

conn = sqlite3.connect("exam.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    stu_index TEXT,
    stu_name TEXT,
    class TEXT,
    subject TEXT,
    PRIMARY KEY (stu_index, subject)
);
''')

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
    FOREIGN KEY (subject) REFERENCES students(subject),
    FOREIGN KEY (classes) REFERENCES students(class)
);
''')

conn.commit()
conn.close()
