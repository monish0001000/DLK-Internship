"""
train_model.py - ML Model Training
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

CSV_PATH = os.path.join("data", "flow_features.csv")
MODEL_PATH = os.path.join("models", "model.pkl")

SYN_THRESHOLD = 1
PACKET_RATE_THRESHOLD = 5
MANY_PORTS_PACKET_COUNT = 1


def auto_label(row):
    if row["syn_count"] >= SYN_THRESHOLD and row["packet_count"] <= MANY_PORTS_PACKET_COUNT:
        return 1
    if row["packet_rate"] >= PACKET_RATE_THRESHOLD:
        return 1
    return 0


def load_and_label():
    df = pd.read_csv(CSV_PATH)
    print(f"[train] Loaded {len(df)} rows from {CSV_PATH}")
    df["label"] = df.apply(auto_label, axis=1)
    print("[train] Label distribution:")
    print(df["label"].value_counts())
    return df


FEATURE_COLS = [
    "packet_count", "byte_count", "packet_rate",
    "byte_rate", "syn_count", "avg_packet_size",
]


def train(df):
    X = df[FEATURE_COLS]
    y = df["label"]

    if y.nunique() < 2:
        print("[train] WARNING: only one class present in data. "
              "Collect more varied traffic (normal + scan) before training.")
        return None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("\n[train] Classification report:")
    print(classification_report(y_test, y_pred, target_names=["normal", "anomaly"]))
    print("[train] Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\n[train] Feature importances:")
    for col, imp in sorted(zip(FEATURE_COLS, clf.feature_importances_), key=lambda x: -x[1]):
        print(f"  {col}: {imp:.3f}")

    return clf


def save_model(clf):
    os.makedirs("models", exist_ok=True)
    joblib.dump({"model": clf, "features": FEATURE_COLS}, MODEL_PATH)
    print(f"\n[train] Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    if not os.path.exists(CSV_PATH):
        print(f"[train] ERROR: {CSV_PATH} not found. Run extractor.py first to collect data.")
        exit(1)

    df = load_and_label()
    clf = train(df)
    if clf is not None:
        save_model(clf)
