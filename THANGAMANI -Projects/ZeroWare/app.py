import os
import time
import json
import shutil
import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash

from database import init_db, save_scan, get_all_scans, get_scan_by_id, get_stats, delete_scan
from feature_extractor import extract_features
from predictor import predict
from zerodna import get_zerodna
from zeroreason import get_reasons
from trust_engine import calculate_trust_score, calculate_risk_score, calculate_zeroday_probability
from behavior_predictor import predict_behavior, get_genome
from report_generator import generate_report
from advisor import get_recommendations, generate_analyst_summary

app = Flask(__name__)
app.secret_key = 'zeroware-secret-2024'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
QUARANTINE_FOLDER = os.path.join(os.path.dirname(__file__), 'quarantine')
REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), 'reports')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QUARANTINE_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

init_db()

# Train model if not present
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'malware_model.pkl')
if not os.path.exists(MODEL_PATH):
    print("[ZeroWare] Training AI model for first run...")
    import train_model
    train_model.train_and_save()
    print("[ZeroWare] Model ready.")


@app.route('/')
def index():
    stats = get_stats()
    return render_template('index.html', stats=stats)


@app.route('/scan', methods=['POST'])
def scan():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = f.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    f.save(save_path)

    start = time.time()
    try:
        features = extract_features(save_path)

        if 'error' in features and len(features) <= 2:
            return jsonify({'error': f"Feature extraction failed: {features['error']}"}), 500

        pred = predict(features)
        sha256 = features.get('sha256', '')
        zerodna = get_zerodna(features, sha256)
        reasons = get_reasons(features, pred['label'])
        trust = calculate_trust_score(features, pred['label'])
        risk_score = calculate_risk_score(features, pred['malware_probability'])
        top_sim = zerodna.get('top_match', {}).get('similarity', 0) if zerodna.get('top_match') else 0
        zeroday_prob = calculate_zeroday_probability(features, top_sim)
        behaviors = predict_behavior(features)
        genome = get_genome(features)
        recommendations = get_recommendations(pred['label'], features, behaviors)
        summary = generate_analyst_summary(pred['label'], features, reasons, zerodna)

        duration = round(time.time() - start, 3)

        result = {
            'file_name': filename,
            'features': features,
            'prediction': pred,
            'zerodna': zerodna,
            'reasons': reasons,
            'trust': trust,
            'risk_score': risk_score,
            'zeroday_prob': zeroday_prob,
            'behaviors': behaviors,
            'genome': genome,
            'recommendations': recommendations,
            'analyst_summary': summary,
            'scan_duration': duration
        }

        scan_id = save_scan(result, duration)
        result['scan_id'] = scan_id

        # Remove imported_dlls and imported_apis from JSON response (too large)
        result['features'] = {k: v for k, v in features.items()
                              if k not in ('imported_dlls', 'imported_apis')}

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(save_path):
            os.remove(save_path)


@app.route('/history')
def history():
    scans = get_all_scans(200)
    for s in scans:
        try:
            s['reasons'] = json.loads(s['reasons']) if s['reasons'] else []
        except:
            s['reasons'] = []
        try:
            s['behaviors'] = json.loads(s['behaviors']) if s['behaviors'] else {}
        except:
            s['behaviors'] = {}
        try:
            s['recommendations'] = json.loads(s['recommendations']) if s['recommendations'] else []
        except:
            s['recommendations'] = []
    return render_template('history.html', scans=scans)


@app.route('/scan/<int:scan_id>')
def view_scan(scan_id):
    scan = get_scan_by_id(scan_id)
    if not scan:
        flash('Scan not found', 'danger')
        return redirect(url_for('history'))
    try:
        scan['reasons'] = json.loads(scan['reasons']) if scan['reasons'] else []
        scan['behaviors'] = json.loads(scan['behaviors']) if scan['behaviors'] else {}
        scan['recommendations'] = json.loads(scan['recommendations']) if scan['recommendations'] else []
    except:
        pass
    return render_template('scan_detail.html', scan=scan)


@app.route('/report/<int:scan_id>')
def download_report(scan_id):
    scan = get_scan_by_id(scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404
    try:
        scan['reasons'] = json.loads(scan['reasons']) if scan['reasons'] else []
        scan['behaviors'] = json.loads(scan['behaviors']) if scan['behaviors'] else {}
        scan['recommendations'] = json.loads(scan['recommendations']) if scan['recommendations'] else []
    except:
        pass

    result = {
        'file_name': scan['file_name'],
        'features': {'md5': scan['md5'], 'sha256': scan['sha256'], 'file_size': scan['file_size']},
        'prediction': {'label': scan['prediction'], 'confidence': scan['confidence']},
        'trust': {'score': scan['trust_score'], 'level': 'Low' if scan['trust_score'] < 45 else ('Medium' if scan['trust_score'] < 75 else 'High')},
        'risk_score': scan['risk_score'],
        'zeroday_prob': scan['zeroday_prob'],
        'zerodna': {'dna_id': scan['zerodna_id']},
        'reasons': scan['reasons'],
        'behaviors': scan['behaviors'],
        'recommendations': scan['recommendations'],
    }
    report_path = os.path.join(REPORTS_FOLDER, f'report_{scan_id}.pdf')
    generate_report(result, report_path)
    return send_file(report_path, as_attachment=True,
                     download_name=f'ZeroWare_Report_{scan["file_name"]}_{scan_id}.pdf',
                     mimetype='application/pdf')


@app.route('/delete/<int:scan_id>', methods=['POST'])
def delete_scan_route(scan_id):
    delete_scan(scan_id)
    return jsonify({'success': True})


@app.route('/dashboard')
def dashboard():
    stats = get_stats()
    scans = get_all_scans(50)
    return render_template('dashboard.html', stats=stats, scans=scans)


@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())


@app.route('/api/history')
def api_history():
    scans = get_all_scans(50)
    for s in scans:
        s.pop('reasons', None)
        s.pop('behaviors', None)
        s.pop('recommendations', None)
    return jsonify(scans)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
