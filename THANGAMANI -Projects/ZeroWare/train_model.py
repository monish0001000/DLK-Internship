"""
ZeroWare Model Trainer
Generates a synthetic training model since real datasets require downloads.
Replace with real EMBER/Kaggle dataset for production use.
"""

import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS = [
    'file_size', 'overall_entropy', 'machine_type', 'num_sections',
    'timestamp', 'characteristics', 'image_base', 'entry_point',
    'subsystem', 'dll_characteristics', 'size_of_image', 'size_of_headers',
    'checksum', 'size_of_stack_reserve', 'size_of_heap_reserve',
    'max_section_entropy', 'avg_section_entropy', 'min_section_entropy',
    'exec_sections', 'write_sections', 'total_section_size',
    'num_imported_dlls', 'num_imported_apis', 'suspicious_api_count',
    'has_network_dll', 'has_crypto_dll', 'has_registry_dll',
    'num_exports', 'num_resources', 'has_signature',
    'overlay_size', 'num_strings', 'has_url_strings', 'has_ip_pattern', 'is_packed'
]

N_FEATURES = len(FEATURE_COLUMNS)


def generate_synthetic_data(n_samples=2000):
    np.random.seed(42)
    X = []
    y = []

    # Safe files (label=0)
    for _ in range(n_samples // 2):
        sample = [
            np.random.randint(50000, 5000000),    # file_size
            np.random.uniform(4.0, 6.5),           # overall_entropy
            0x14c,                                  # machine_type x86
            np.random.randint(3, 8),               # num_sections
            np.random.randint(1000000000, 1700000000),  # timestamp
            np.random.randint(0, 512),             # characteristics
            0x400000,                               # image_base
            np.random.randint(4096, 65536),        # entry_point
            np.random.choice([2, 3]),               # subsystem
            np.random.randint(0, 256),             # dll_characteristics
            np.random.randint(100000, 10000000),   # size_of_image
            np.random.randint(1024, 4096),         # size_of_headers
            np.random.randint(0, 100000),          # checksum
            np.random.randint(65536, 1048576),     # size_of_stack_reserve
            np.random.randint(4096, 65536),        # size_of_heap_reserve
            np.random.uniform(3.5, 6.5),           # max_section_entropy
            np.random.uniform(3.0, 5.5),           # avg_section_entropy
            np.random.uniform(1.0, 4.0),           # min_section_entropy
            np.random.randint(1, 3),               # exec_sections
            np.random.randint(0, 2),               # write_sections
            np.random.randint(50000, 2000000),     # total_section_size
            np.random.randint(3, 20),              # num_imported_dlls
            np.random.randint(30, 200),            # num_imported_apis
            np.random.randint(0, 3),               # suspicious_api_count
            np.random.randint(0, 2),               # has_network_dll
            np.random.randint(0, 2),               # has_crypto_dll
            np.random.randint(0, 2),               # has_registry_dll
            np.random.randint(0, 50),              # num_exports
            np.random.randint(0, 20),              # num_resources
            np.random.randint(0, 2),               # has_signature
            0,                                      # overlay_size
            np.random.randint(100, 500),           # num_strings
            np.random.randint(0, 2),               # has_url_strings
            0,                                      # has_ip_pattern
            0,                                      # is_packed
        ]
        X.append(sample)
        y.append(0)

    # Malware files (label=1)
    for _ in range(n_samples // 2):
        sample = [
            np.random.randint(10000, 500000),      # file_size (often smaller)
            np.random.uniform(6.5, 8.0),           # overall_entropy (high = packed)
            np.random.choice([0x14c, 0x8664]),     # machine_type
            np.random.randint(1, 6),               # num_sections (few or many)
            np.random.randint(0, 500000000),       # timestamp (old or 0)
            np.random.randint(0, 512),             # characteristics
            np.random.choice([0x400000, 0x10000000]),  # image_base
            np.random.randint(0, 100000),          # entry_point
            np.random.choice([2, 3, 0]),            # subsystem
            np.random.randint(0, 256),             # dll_characteristics
            np.random.randint(50000, 5000000),     # size_of_image
            np.random.randint(512, 2048),          # size_of_headers
            0,                                      # checksum (0 = suspicious)
            np.random.randint(65536, 1048576),     # size_of_stack_reserve
            np.random.randint(4096, 65536),        # size_of_heap_reserve
            np.random.uniform(7.0, 8.0),           # max_section_entropy HIGH
            np.random.uniform(6.0, 7.8),           # avg_section_entropy HIGH
            np.random.uniform(4.0, 7.0),           # min_section_entropy
            np.random.randint(1, 4),               # exec_sections
            np.random.randint(1, 3),               # write_sections
            np.random.randint(10000, 1000000),     # total_section_size
            np.random.randint(1, 10),              # num_imported_dlls (few = packed)
            np.random.randint(5, 80),              # num_imported_apis (few = packed)
            np.random.randint(3, 15),              # suspicious_api_count HIGH
            np.random.randint(0, 2),               # has_network_dll
            np.random.randint(0, 2),               # has_crypto_dll
            np.random.randint(0, 2),               # has_registry_dll
            0,                                      # num_exports
            np.random.randint(0, 5),               # num_resources
            0,                                      # has_signature (unsigned)
            np.random.randint(0, 50000),           # overlay_size
            np.random.randint(10, 200),            # num_strings
            np.random.randint(0, 2),               # has_url_strings
            np.random.randint(0, 2),               # has_ip_pattern
            1,                                      # is_packed
        ]
        X.append(sample)
        y.append(1)

    return np.array(X), np.array(y)


def train_and_save():
    print("[*] Generating synthetic training data...")
    X, y = generate_synthetic_data(3000)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("[*] Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)

    accuracy = model.score(X_test_scaled, y_test)
    print(f"[+] Model Accuracy: {accuracy*100:.2f}%")

    os.makedirs('model', exist_ok=True)
    joblib.dump(model, 'model/malware_model.pkl')
    joblib.dump(scaler, 'model/scaler.pkl')
    joblib.dump(FEATURE_COLUMNS, 'model/feature_columns.pkl')
    print("[+] Model saved to model/malware_model.pkl")
    return accuracy


if __name__ == '__main__':
    train_and_save()
