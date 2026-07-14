import pandas as pd
from sklearn.ensemble import IsolationForest

# Load processed data
data = pd.read_csv("/home/kali/Network-Anomaly-Detection/dataset/processed_network.csv")

# Train Isolation Forest model
model = IsolationForest(contamination=0.05, random_state=42)

# Fit the model
model.fit(data)

# Predict anomalies
data["Anomaly"] = model.predict(data)

# Convert predictions
data["Anomaly"] = data["Anomaly"].replace({1: "Normal", -1: "Anomaly"})

print(data.head())

# Save results
data.to_csv("/home/kali/Network-Anomaly-Detection/dataset/anomaly_results.csv", index=False)

print("\nModel trained successfully!")
print("Results saved as anomaly_results.csv")
