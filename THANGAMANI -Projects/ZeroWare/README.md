# 🛡️ ZeroWare — AI Malware Intelligence Platform

## Quick Start (3 steps)

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Run
```bash
python app.py
```
> First run will automatically train the AI model (~10 seconds). No manual steps needed.

### Step 3 — Open browser
```
http://localhost:5000
```

---

## Features
- AI-based malware detection (Random Forest)
- ZeroDNA fingerprinting
- ZeroReason explainable AI
- Trust Score & Risk Score
- Behavior prediction (no file execution)
- Malware Genome
- PDF report generation
- Scan history with search
- Dashboard with statistics

## Supported File Types
`.exe` `.dll` `.sys` `.scr` `.com` `.bin`

## Project Structure
```
ZeroWare/
├── app.py                  ← Main Flask app (run this)
├── train_model.py          ← AI model trainer (auto-runs on first start)
├── feature_extractor.py    ← PE feature extraction
├── predictor.py            ← AI prediction
├── zerodna.py              ← DNA fingerprinting
├── zeroreason.py           ← Explainable AI
├── trust_engine.py         ← Trust/Risk/ZeroDay scores
├── behavior_predictor.py   ← Static behavior prediction
├── report_generator.py     ← PDF report generation
├── advisor.py              ← Security recommendations
├── database.py             ← SQLite history
├── model/                  ← Trained model files (auto-created)
├── templates/              ← HTML templates
├── uploads/                ← Temp upload folder
├── quarantine/             ← Quarantine folder
├── reports/                ← Generated PDF reports
├── history.db              ← SQLite database (auto-created)
└── requirements.txt
```

## Notes
- The AI model is trained on synthetic data for demonstration.
- For production accuracy, replace with EMBER or Kaggle PE malware datasets.
- No file is executed during analysis — fully static analysis.
