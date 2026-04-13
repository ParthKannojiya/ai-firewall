import requests

# 🌐 Threat Intelligence (AbuseIPDB-like simulation)
def check_ip_reputation(ip):
    # Simulated (free version without API key)
    suspicious_ips = ["192.168.1.100", "10.0.0.5"]
    return ip in suspicious_ips


# 🤖 Behavioral profiling
ip_behavior = {}

def check_behavior(ip, requests_count):
    if ip not in ip_behavior:
        ip_behavior[ip] = []

    ip_behavior[ip].append(requests_count)

    # Keep last 5 records
    if len(ip_behavior[ip]) > 5:
        ip_behavior[ip].pop(0)

    avg = sum(ip_behavior[ip]) / len(ip_behavior[ip])

    if requests_count > avg * 3:
        return True  # anomaly
    return False


# 🍯 Honeypot detection
def is_honeypot_triggered(url):
    fake_paths = ["admin-login", "root-access", "config.php"]
    return any(path in url for path in fake_paths)


# ⚙️ Adaptive rule learning
auto_rules = set()

def learn_new_rule(url):
    if "select" in url or "drop" in url:
        auto_rules.add("SQL_PATTERN")

def check_auto_rules(url):
    if "SQL_PATTERN" in auto_rules:
        if "select" in url or "drop" in url:
            return True
    return False