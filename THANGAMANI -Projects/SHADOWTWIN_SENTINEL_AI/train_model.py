import os
import joblib
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "packet_count",
    "avg_packet_size",
    "tcp_pct",
    "udp_pct",
    "icmp_pct",
    "syn_rate",
    "ack_rate",
    "rst_rate",
    "dst_ip_diversity",
    "unique_ports_targeted",
    "flow_duration",
    "inter_arrival_time",
]


def compute_feature_importance_from_isoforest(model: IsolationForest, feature_names):
    """Pragmatic explainability for IsolationForest.

    IsolationForest doesn't provide feature_importances_ directly.
    We approximate importance by looking at how splits reduce anomaly score.
    For simplicity and stability, we return normalized absolute values from
    a subsampled decision-function sensitivity via finite differences.
    """

    import numpy as np

    # Use small perturbation sensitivity around zero (after scaling).
    base = 0.0
    # Create a synthetic baseline row at mean=0, std=1 (scaled space)
    x0 = np.array([base for _ in feature_names], dtype=float).reshape(1, -1)

    base_score = -model.decision_function(x0)[0]  # higher means more anomalous

    importances = []
    for i in range(len(feature_names)):
        x1 = x0.copy()
        x1[0, i] += 0.25  # perturb in scaled space
        s1 = -model.decision_function(x1)[0]
        importances.append(abs(s1 - base_score))

    imp = np.array(importances, dtype=float)
    if imp.sum() <= 0:
        return {k: 0.0 for k in feature_names}
    imp = imp / imp.sum()
    return {k: float(v) for k, v in zip(feature_names, imp)}


def load_baseline_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Baseline CSV not found: {path}. Create it with columns: {', '.join(FEATURES)}"
        )

    df = pd.read_csv(path)
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Baseline CSV missing required feature columns: {missing}")

    return df


# Absolute-path config (so train_model.py works from any working directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_CSV = os.path.join(BASE_DIR, "baseline_normal_network_activity.csv")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "isolation_forest.joblib")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler.joblib")
FEATURE_IMPORTANCE_PATH = os.path.join(ARTIFACTS_DIR, "feature_importance.joblib")


def train(baseline_csv_path: str = BASELINE_CSV):
    print(f"[train_model] Absolute CSV path: {baseline_csv_path}")
    if not os.path.exists(baseline_csv_path):
        raise FileNotFoundError(
            f"Baseline CSV not found: {baseline_csv_path}. Create it with columns: {', '.join(FEATURES)}"
        )

    df = load_baseline_csv(baseline_csv_path)


    X = df[FEATURES].astype(float)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_scaled)

    feature_importance = compute_feature_importance_from_isoforest(model, FEATURES)

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(feature_importance, FEATURE_IMPORTANCE_PATH)


    print("Training complete.")
    print(f"Saved model to artifacts/isolation_forest.joblib")
    print(f"Saved scaler to artifacts/scaler.joblib")
    print(f"Saved feature importance to artifacts/feature_importance.joblib")


if __name__ == "__main__":
    # Default baseline file name (edit if needed)
    # CSV must contain the 12 feature columns listed in FEATURES.
    train()

