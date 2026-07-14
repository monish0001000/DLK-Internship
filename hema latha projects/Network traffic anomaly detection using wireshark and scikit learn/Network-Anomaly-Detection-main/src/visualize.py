import pandas as pd
import matplotlib.pyplot as plt

# Load results
data = pd.read_csv("/home/kali/Network-Anomaly-Detection/dataset/anomaly_results.csv")

# Count anomalies
counts = data["Anomaly"].value_counts()

print(counts)

# Draw bar chart
plt.figure(figsize=(6,4))
plt.bar(counts.index, counts.values)

plt.title("Network Traffic Anomaly Detection")
plt.xlabel("Traffic Type")
plt.ylabel("Number of Packets")

# Save graph
plt.savefig("/home/kali/Network-Anomaly-Detection/dataset/anomaly_graph.png")

# Show graph
plt.show()
