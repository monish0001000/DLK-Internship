"""
predictor.py - Upgraded ML Inference Engine
Uses attack_detector.py for multi-attack classification.

Run:  sudo python3 predictor.py eth0
"""

import sys
import time
import joblib
import os
import pandas as pd

from extractor import start_extractor
from attack_detector import classify_attack
from logger import log_alert, log_normal, print_dashboard

MODEL_PATH = os.path.join("models", "model.pkl")
DASHBOARD_INTERVAL = 10

_last_dashboard = 0.0


def load_model():
    if not os.path.exists(MODEL_PATH):
        print(f"[predictor] ERROR: {MODEL_PATH} not found. Run train_model.py first.")
        sys.exit(1)
    bundle = joblib.load(MODEL_PATH)
    print(f"[predictor] Model loaded. Features: {bundle['features']}")
    return bundle["model"], bundle["features"]


def make_on_features(model, feature_cols):
    def on_features(rows):
        global _last_dashboard

        for flow in rows:
            # Step 1: ML confidence score (pandas DataFrame - no warning)
            X = pd.DataFrame(
                [[flow[col] for col in feature_cols]],
                columns=feature_cols
            )
            proba = model.predict_proba(X)[0]
            ml_confidence = proba[1] if len(proba) > 1 else 0.0

            # Step 2: Attack classification (ML + rules combined)
            result = classify_attack(flow, ml_confidence)

            # Step 3: Log
            if result["is_anomaly"]:
                log_alert(flow, result)
            else:
                log_normal(flow)

        now = time.time()
        if now - _last_dashboard >= DASHBOARD_INTERVAL:
            print_dashboard()
            _last_dashboard = now

    return on_features


def run(interface="eth0"):
    model, feature_cols = load_model()
    on_features = make_on_features(model, feature_cols)

    print(f"[predictor] Starting Multi-Attack IDS on '{interface}'")
    print(f"[predictor] Detecting: PORT_SCAN | DDOS_FLOOD | BRUTE_FORCE | ANOMALY")
    stop_event, sniff_stop = start_extractor(interface=interface, on_features=on_features)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[predictor] Shutting down IDS...")
        stop_event.set()
        sniff_stop.set()
        time.sleep(1)


if __name__ == "__main__":
    iface = sys.argv[1] if len(sys.argv) > 1 else "eth0"
    run(interface=iface)
