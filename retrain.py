import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

print("🔄 Retraining model with real data...")

DB_FILE = "database.db"

# 1️⃣ Connect to the database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 2️⃣ Create the 'logs' table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requests INTEGER NOT NULL,
    failed_logins INTEGER NOT NULL,
    attack TEXT NOT NULL
)
""")
conn.commit()

# 3️⃣ Insert sample data only if table is empty
cursor.execute("SELECT COUNT(*) FROM logs")
count = cursor.fetchone()[0]

if count == 0:
    print("⚠️ No data found in 'logs'. Inserting sample data...")
    sample_data = [
        (10, 0, "Normal"),
        (50, 5, "Attack"),
        (20, 1, "Normal"),
        (100, 10, "Attack")
    ]
    cursor.executemany(
        "INSERT INTO logs (requests, failed_logins, attack) VALUES (?, ?, ?)",
        sample_data
    )
    conn.commit()

# 4️⃣ Now read the logs table safely
df = pd.read_sql_query("SELECT * FROM logs", conn)
conn.close()

# 5️⃣ Check if data exists
if df.empty:
    print("❌ No data found in database. Cannot retrain.")
    exit()

print("📊 Raw Data:")
print(df.head())

# 6️⃣ Convert labels to numeric
df["label"] = df["attack"].apply(lambda x: 0 if x == "Normal" else 1)

# 7️⃣ Select features
X = df[["requests", "failed_logins"]]
y = df["label"]

print("📊 Training on:")
print(X.head())

# 8️⃣ Train RandomForest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 9️⃣ Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model retrained successfully using real attack data!")