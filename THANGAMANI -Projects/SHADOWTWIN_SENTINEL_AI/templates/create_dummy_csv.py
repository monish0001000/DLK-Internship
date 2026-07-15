import pandas as pd
import numpy as np
import os

# Create dummy baseline data with 200 normal network flow records
np.random.seed(42)
n_samples = 200

data = {
    'packet_count': np.random.randint(5, 50, n_samples),
    'avg_packet_size': np.random.randint(64, 500, n_samples),
    'tcp_pct': np.random.uniform(70, 95, n_samples),
    'udp_pct': np.random.uniform(5, 25, n_samples),
    'icmp_pct': np.random.uniform(0, 5, n_samples),
    'syn_rate': np.random.uniform(0.1, 2.0, n_samples),
    'ack_rate': np.random.uniform(5.0, 20.0, n_samples),
    'rst_rate': np.random.uniform(0.0, 0.5, n_samples),
    'dst_ip_diversity': np.random.randint(1, 5, n_samples),
    'unique_ports_targeted': np.random.randint(1, 4, n_samples),
    'flow_duration': np.random.uniform(1.0, 10.0, n_samples),
    'inter_arrival_time': np.random.uniform(0.01, 0.2, n_samples)
}

df = pd.DataFrame(data)
csv_name = "baseline_normal_network_activity.csv"
df.to_csv(csv_name, index=False)
print(f"🔥 Successfully created: {csv_name} with {n_samples} samples!")