# ShadowTwin Sentinel AI

A step-by-step implementation guide and reference code scaffold for an advanced network threat detection project.

## Files
- `sniffer.py` — PyShark packet capture + feature extraction (windowed aggregation)
- `train_model.py` — Isolation Forest training + scaling + explainable feature importance
- `app.py` — Flask server (loads model, runs background evaluation, SQLite logging, API routes)
- `templates/index.html` — Dark SOC dashboard with Chart.js + Attack Simulator button

## Run
```bash
python train_model.py
python app.py
```
Open: http://127.0.0.1:5000

