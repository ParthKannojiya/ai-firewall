import streamlit as st
import pandas as pd
import requests

# ✅ Session state (for SHAP persistence)
if "last_response" not in st.session_state:
    st.session_state.last_response = None

st.set_page_config(page_title="AI Firewall", layout="wide")

st.title("🔥 AI Firewall Control Panel")

# 🔥 USE YOUR LIVE RENDER URL HERE
API_BASE = "https://your-render-app.onrender.com"

API_URL = f"{API_BASE}/predict"
UNBLOCK_URL = f"{API_BASE}/unblock?all=true"
RETRAIN_URL = f"{API_BASE}/retrain_count"
LOGS_URL = f"{API_BASE}/logs"

# 🧪 Test panel
st.sidebar.header("🧪 Test Firewall")

req = st.sidebar.slider("Requests", 0, 1000, 100)
fail = st.sidebar.slider("Failed Logins", 0, 100, 5)
url = st.sidebar.text_input("URL (for attack testing)", "home")

if st.sidebar.button("🚀 Send Request"):
    res = requests.post(API_URL, json={
        "requests": req,
        "failed_logins": fail,
        "url": url
    })
    response = res.json()

    # ✅ Save response (for SHAP)
    st.session_state.last_response = response

    st.sidebar.success(response)

    if "reason" in response:
        st.sidebar.info(f"🧠 Reason: {', '.join(response['reason'])}")

# 🔓 Unblock
if st.sidebar.button("🔓 Unblock All IPs"):
    res = requests.get(UNBLOCK_URL)
    st.sidebar.success(res.json())

# 🔁 Retrain Count
try:
    res = requests.get(RETRAIN_URL)
    retrain_count = res.json()["retrain_count"]
except:
    retrain_count = 0

st.metric("🔁 Retrain Count", retrain_count)

# 🔥 📊 LOAD DATA FROM BACKEND API (FIXED)
try:
    res = requests.get(LOGS_URL)
    data = res.json()
    df = pd.DataFrame(data)
except:
    df = pd.DataFrame()

# Handle empty DB
if df.empty:
    st.warning("No data available yet...")
    st.stop()

# Metrics
col1, col2 = st.columns(2)

attack_count = df[df["attack"] != "Normal"].shape[0]
normal_count = df[df["attack"] == "Normal"].shape[0]

col1.metric("🚨 Total Attacks", attack_count)
col2.metric("✅ Normal Traffic", normal_count)

# 📈 Attack Types
st.subheader("📈 Attack Types")
st.bar_chart(df["attack"].value_counts())

# 📊 Request Trend
st.subheader("📊 Requests Trend")
st.line_chart(df["requests"])

# 🌍 Attacks by IP
st.subheader("🌍 Attacks by IP")
st.bar_chart(df["ip"].value_counts())

# 🧠 Attack Reasons
st.subheader("🧠 Attack Reasons Analysis")

if "reason" in df.columns:
    reason_series = df["reason"].astype(str).str.split(", ").explode()
    st.bar_chart(reason_series.value_counts())

# 📋 Logs
st.subheader("📋 Logs (Latest 20)")
st.dataframe(df.tail(20))

# 📁 Retrain History (REMOVED FILE ACCESS → OPTIONAL API LATER)
st.subheader("📁 Retrain History")
st.info("Retrain history not available in cloud yet")

# 🌍 Attack Map
st.subheader("🌍 Attack Map")

if "lat" in df.columns and "lon" in df.columns:
    map_df = df[["lat", "lon"]].dropna()
    if not map_df.empty:
        st.map(map_df)
    else:
        st.info("No location data yet")
else:
    st.info("Geo data not available yet")

# 🧠 SHAP Feature Impact
st.subheader("🧠 SHAP Feature Impact")

if st.session_state.last_response:
    response = st.session_state.last_response

    if "shap" in response:
        shap_data = response["shap"]

        shap_df = pd.DataFrame({
            "Feature": list(shap_data.keys()),
            "Impact": list(shap_data.values())
        })

        st.bar_chart(shap_df.set_index("Feature"))
    else:
        st.info("No SHAP data available")
else:
    st.info("Run a test request to see SHAP values")
