import pickle
import shap
import numpy as np

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

explainer = shap.Explainer(model)

def get_shap_values(req, fail):
    try:
        data = np.array([[req, fail]])
        shap_values = explainer(data)

        return {
            "requests": float(shap_values.values[0][0]),
            "failed_logins": float(shap_values.values[0][1])
        }
    except:
        return {
            "requests": 0,
            "failed_logins": 0
        }