from flask import Flask, request, jsonify
import pickle
import sqlite3
import subprocess
import threading
import datetime
from flask_cors import CORS   # ✅ ADD THIS

from security_utils import (
    check_ip_reputation,
    check_behavior,
    is_honeypot_triggered,
    learn_new_rule,
    check_auto_rules
)

# ✅ NEW SAFE IMPORTS
try:
    from geo_utils import get_location
except:
    def get_location(ip):
        return {"lat": 20.5937, "lon": 78.9629}

try:
    from shap_explainer import get_shap_values
except:
    def get_shap_values(r, f):
        return {"requests": 0, "failed_logins": 0}

print("🚀 Starting AI Firewall Server...")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# 🔥 Database
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# ✅ UPDATED TABLE (adds lat/lon safely)
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    requests INTEGER,
    failed_logins INTEGER,
    attack TEXT,
    reason TEXT,
    timestamp TEXT,
    lat REAL,
    lon REAL
)
""")
conn.commit()

# 🔥 Load model
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully!")
except:
    model = None

# 🔥 Globals
request_count = 0
blocked_ips = set()
ip_attack_count = {}
retrain_count = 0

# 🏠 Home
@app.route("/")
def home():
    return "AI Firewall Running ✅"

# 🧪 Test API
@app.route("/test")
def test():
    if model is None:
        return "Model not loaded"
    pred = model.predict([[200, 10]])
    return "Attack" if pred[0] == 1 else "Normal"

# 🔓 UNBLOCK
@app.route("/unblock", methods=["GET"])
def unblock():
    blocked_ips.clear()
    ip_attack_count.clear()
    return jsonify({"status": "✅ All IPs unblocked"})

# 🔁 RETRAIN COUNT
@app.route("/retrain_count")
def retrain_count_api():
    return jsonify({"retrain_count": retrain_count})

@app.route("/logs", methods=["GET"])
def get_logs():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ip, requests, failed_logins, attack, reason, timestamp, lat, lon
            FROM logs
            ORDER BY timestamp DESC
            LIMIT 100
        """)

        rows = cursor.fetchall()

        conn.close()

        # ✅ Convert to JSON format
        data = []
        for row in rows:
            data.append({
                "ip": row[0],
                "requests": row[1],
                "failed_logins": row[2],
                "attack": row[3],
                "reason": row[4],
                "timestamp": row[5],
                "lat": row[6],
                "lon": row[7]
            })

        return jsonify(data)

    except Exception as e:
        print("❌ Logs API Error:", e)
        return jsonify([])

# 🍯 Honeypot
@app.route("/admin-login")
def honeypot():
    ip = request.remote_addr
    blocked_ips.add(ip)
    return "🚨 Honeypot triggered! You are blocked."

# 🔁 Retrain
def retrain_model():
    global model, retrain_count

    subprocess.run(["python", "retrain.py"])

    try:
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)

        retrain_count += 1

        with open("retrain_log.txt", "a") as f:
            f.write(f"{datetime.datetime.now()} - Retrain #{retrain_count}\n")

    except Exception as e:
        print("❌ Error:", e)

# 🚨 MAIN API
@app.route("/predict", methods=["POST"])
def predict():
    global request_count

    try:
        ip = request.remote_addr

        if ip in blocked_ips:
            return jsonify({"status": "🚫 IP Blocked"}), 403

        data = request.get_json()
        url = data.get("url", "")

        requests_count = int(data["requests"])
        failed_logins = int(data["failed_logins"])

        reason = []

        if check_ip_reputation(ip):
            attack_type = "Malicious IP"
            reason.append("IP flagged globally")

        elif is_honeypot_triggered(url):
            attack_type = "Honeypot Access"
            blocked_ips.add(ip)
            reason.append("Accessed fake endpoint")

        elif check_behavior(ip, requests_count):
            attack_type = "Behavioral Anomaly"
            reason.append("Abnormal traffic spike")

        else:
            prediction = model.predict([[requests_count, failed_logins]])
            attack_type = "Normal"

            url_lower = url.lower()

            if "select" in url_lower or "drop" in url_lower:
                attack_type = "SQL Injection"
                learn_new_rule(url_lower)
                reason.append("SQL keywords detected")

            elif "<script>" in url_lower:
                attack_type = "XSS Attack"
                reason.append("Script tag detected")

            elif prediction[0] == 1:
                attack_type = "ML Anomaly"
                reason.append("ML anomaly")

            if check_auto_rules(url_lower):
                attack_type = "Learned Attack Pattern"
                reason.append("Matched learned rule")

        # 🚫 Block logic
        if attack_type != "Normal":
            ip_attack_count[ip] = ip_attack_count.get(ip, 0) + 1
            if ip_attack_count[ip] >= 5:
                blocked_ips.add(ip)
                attack_type = "IP Blocked"

        # 🌍 SAFE GEO
        geo = get_location(ip)

        # 🧠 SAFE SHAP
        try:
            shap_data = get_shap_values(requests_count, failed_logins)
        except:
            shap_data = {"requests": 0, "failed_logins": 0}

        # 💾 Save logs (UPDATED)
        cursor.execute("""
            INSERT INTO logs (ip, requests, failed_logins, attack, reason, timestamp, lat, lon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ip,
            requests_count,
            failed_logins,
            attack_type,
            ", ".join(reason),
            str(datetime.datetime.now()),
            geo["lat"],
            geo["lon"]
        ))
        conn.commit()

        # 🔁 Retrain
        request_count += 1
        if request_count >= 5:
            threading.Thread(target=retrain_model).start()
            request_count = 0

        return jsonify({
            "status": attack_type,
            "reason": reason,
            "ip": ip,
            "shap": shap_data   # 🔥 NEW
        })

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": "Error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    
