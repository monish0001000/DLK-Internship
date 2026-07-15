import numpy as np
import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'malware_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'model', 'scaler.pkl')
FEATURES_PATH = os.path.join(os.path.dirname(__file__), 'model', 'feature_columns.pkl')

_model = None
_scaler = None
_feature_columns = None


def load_model():
    global _model, _scaler, _feature_columns
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        _feature_columns = joblib.load(FEATURES_PATH)


def predict(features: dict) -> dict:
    load_model()

    vector = []
    for col in _feature_columns:
        vector.append(float(features.get(col, 0)))

    X = np.array(vector).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    proba = _model.predict_proba(X_scaled)[0]
    prediction = _model.predict(X_scaled)[0]

    malware_prob = proba[1]
    safe_prob = proba[0]

    # Determine label
    if malware_prob >= 0.75:
        label = 'Malware'
    elif malware_prob >= 0.45:
        label = 'Suspicious'
    else:
        label = 'Safe'

    confidence = max(malware_prob, safe_prob) * 100

    return {
        'label': label,
        'confidence': round(confidence, 2),
        'malware_probability': round(malware_prob * 100, 2),
        'safe_probability': round(safe_prob * 100, 2),
    }
