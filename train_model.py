import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

print("Starting training...")

df = pd.read_csv("../dataset/data.csv")
print("Dataset loaded:")
print(df)

X = df[["requests", "failed_logins"]]
y = df["label"]

model = RandomForestClassifier()
model.fit(X, y)

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained successfully!")