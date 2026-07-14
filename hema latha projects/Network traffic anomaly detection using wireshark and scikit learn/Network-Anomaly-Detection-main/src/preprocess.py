import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Load dataset
df = pd.read_csv("/home/kali/Network-Anomaly-Detection/dataset/network.csv")

# Remove rows with missing values
df = df.dropna()

# Select useful columns
data = df[['Protocol', 'Length']].copy()

# Convert protocol names (TCP, UDP, TLS, etc.) into numbers
encoder = LabelEncoder()
data['Protocol'] = encoder.fit_transform(data['Protocol'])

print("Processed Data:")
print(data.head())

# Save processed dataset
data.to_csv("/home/kali/Network-Anomaly-Detection/dataset/processed_network.csv", index=False)

print("\nProcessed dataset saved successfully!")