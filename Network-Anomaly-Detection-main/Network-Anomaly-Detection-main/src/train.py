import pandas as pd
from sklearn.ensemble import IsolationForest

# Load processed data
data = pd.read_csv("/home/kali/Network-Anomaly-Detection/dataset/processed_network.csv")

# Create Isolation Forest model
model = IsolationForest(contamination=0.05, random_state=42)

# Train model
model.fit(data)

# Predict anomalies
predictions = model.predict(data)

# Add prediction column
data["Anomaly"] = predictions

# Convert labels
data["Anomaly"] = data["Anomaly"].replace({1: "Normal", -1: "Anomaly"})

# Display first rows
print(data.head())

# Count results
print("\nSummary:")
print(data["Anomaly"].value_counts())

# Save results
data.to_csv("/home/kali/Network-Anomaly-Detection/dataset/anomaly_results.csv", index=False)

print("\nResults saved to anomaly_results.csv")
