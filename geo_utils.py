import requests

def get_location(ip):
    try:
        # Localhost fallback
        if ip == "127.0.0.1":
            return {"lat": 20.5937, "lon": 78.9629}

        url = f"http://ip-api.com/json/{ip}"
        res = requests.get(url, timeout=2)
        data = res.json()

        return {
            "lat": data.get("lat", 20.5937),
            "lon": data.get("lon", 78.9629)
        }

    except:
        return {"lat": 20.5937, "lon": 78.9629}