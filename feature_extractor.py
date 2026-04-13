def extract_features(data):
    return [
        data.get("requests", 1),
        data.get("failed_logins", 0)
    ]