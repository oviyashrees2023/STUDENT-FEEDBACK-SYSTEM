import sqlite3

con = sqlite3.connect("database.db")

con.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password BLOB,
    role TEXT
)
""")

con.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id TEXT,
    course TEXT,
    rating INTEGER,
    comment TEXT,
    sentiment_score REAL,
    topics TEXT,
    date TEXT
)
""")

con.commit()
con.close()
print("Database created")
