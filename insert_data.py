import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Insert sample data
data = [
    (20, 1, "Normal"),
    (50, 2, "Normal"),
    (300, 80, "Attack"),
    (500, 120, "Attack")
]

cursor.executemany("INSERT INTO logs (requests, failed_logins, attack) VALUES (?, ?, ?)", data)

conn.commit()
conn.close()

print("✅ Sample data inserted!")