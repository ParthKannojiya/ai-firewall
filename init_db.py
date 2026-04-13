import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create logs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requests INTEGER,
    failed_logins INTEGER,
    attack TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database and logs table created successfully!")