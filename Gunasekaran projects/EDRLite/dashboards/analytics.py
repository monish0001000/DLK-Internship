"""
dashboards/analytics.py
────────────────────────
Main Flask blueprint — all dashboard routes.
"""

import json
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func, desc

analytics_bp = Blueprint('analytics', __name__)


# ─────────────────────────────────────────────────────────────
#  HOME / DASHBOARD
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/')
@login_required
def dashboard():
    from database.models import RawEvent, Alert, MitreEvent, RiskScore, Endpoint

    total_events   = RawEvent.query.count()
    total_alerts   = Alert.query.count()
    active_alerts  = Alert.query.filter_by(status='open').count()
    critical_alerts= Alert.query.filter(Alert.severity=='critical', Alert.status=='open').count()
    mitre_count    = MitreEvent.query.with_entities(
                         MitreEvent.technique_id).distinct().count()
    endpoints      = Endpoint.query.count()

    # Recent 10 events
    recent_events  = RawEvent.query.order_by(desc(RawEvent.timestamp)).limit(10).all()

    # Risk distribution
    risk_dist = {}
    for level in ['critical','high','medium','low','info']:
        risk_dist[level] = RiskScore.query.filter_by(risk_level=level).count()

    # Alerts by severity
    sev_dist = {}
    for sev in ['critical','high','medium','low']:
        sev_dist[sev] = Alert.query.filter_by(severity=sev).count()

    # Events per day (last 7 days)
    daily_counts = []
    daily_labels = []
    for i in range(6, -1, -1):
        day = datetime.now(timezone.utc) - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = start + timedelta(days=1)
        cnt   = RawEvent.query.filter(
            RawEvent.timestamp >= start,
            RawEvent.timestamp <  end
        ).count()
        daily_labels.append(day.strftime('%b %d'))
        daily_counts.append(cnt)

    # Top techniques
    top_techniques = (
        MitreEvent.query
        .with_entities(MitreEvent.technique_id, MitreEvent.technique_name,
                       func.count(MitreEvent.id).label('cnt'))
        .group_by(MitreEvent.technique_id, MitreEvent.technique_name)
        .order_by(desc('cnt'))
        .limit(5)
        .all()
    )

    return render_template('dashboard.html',
        total_events=total_events,
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        critical_alerts=critical_alerts,
        mitre_count=mitre_count,
        endpoints=endpoints,
        recent_events=recent_events,
        risk_dist=risk_dist,
        sev_dist=sev_dist,
        daily_labels=json.dumps(daily_labels),
        daily_counts=json.dumps(daily_counts),
        top_techniques=top_techniques,
    )


# ─────────────────────────────────────────────────────────────
#  TIMELINE
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/timeline')
@login_required
def timeline():
    from database.models import RawEvent

    page       = request.args.get('page', 1, type=int)
    event_type = request.args.get('type', '')
    hostname   = request.args.get('hostname', '')
    hours      = request.args.get('hours', 24, type=int)

    query = RawEvent.query
    if event_type:
        query = query.filter_by(event_type=event_type)
    if hostname:
        query = query.filter_by(hostname=hostname)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    query  = query.filter(RawEvent.timestamp >= cutoff)

    events = query.order_by(desc(RawEvent.timestamp)).paginate(
        page=page, per_page=30, error_out=False)

    return render_template('timeline.html',
        events=events,
        event_type=event_type,
        hostname=hostname,
        hours=hours,
    )


# ─────────────────────────────────────────────────────────────
#  ALERTS
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/alerts')
@login_required
def alerts():
    from database.models import Alert

    page     = request.args.get('page', 1, type=int)
    severity = request.args.get('severity', '')
    status   = request.args.get('status', '')

    query = Alert.query
    if severity:
        query = query.filter_by(severity=severity)
    if status:
        query = query.filter_by(status=status)

    alerts_page = query.order_by(desc(Alert.timestamp)).paginate(
        page=page, per_page=25, error_out=False)

    return render_template('alerts.html', alerts=alerts_page,
                           severity=severity, status=status)


@analytics_bp.route('/alerts/<int:alert_id>/update', methods=['POST'])
@login_required
def update_alert(alert_id):
    from database.db import db
    from database.models import Alert

    alert  = Alert.query.get_or_404(alert_id)
    action = request.form.get('action')

    status_map = {
        'acknowledge':    'acknowledged',
        'escalate':       'escalated',
        'false_positive': 'false_positive',
        'reopen':         'open',
    }
    if action in status_map:
        alert.status = status_map[action]
        db.session.commit()
        flash(f"Alert #{alert_id} marked as {status_map[action]}.", 'success')
    return redirect(url_for('analytics.alerts'))


# ─────────────────────────────────────────────────────────────
#  MITRE ATT&CK VIEW
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/mitre')
@login_required
def mitre():
    from database.models import MitreEvent
    from sqlalchemy import func

    # Aggregate technique counts
    results = (
        MitreEvent.query
        .with_entities(
            MitreEvent.technique_id,
            MitreEvent.technique_name,
            MitreEvent.tactic,
            func.count(MitreEvent.id).label('count')
        )
        .group_by(MitreEvent.technique_id, MitreEvent.technique_name, MitreEvent.tactic)
        .all()
    )

    # Build technique map: { tactic: [{id, name, count}] }
    tactic_map = {}
    for r in results:
        if r.tactic not in tactic_map:
            tactic_map[r.tactic] = []
        tactic_map[r.tactic].append({
            'id':    r.technique_id,
            'name':  r.technique_name,
            'count': r.count,
        })

    total_techniques = len(set(r.technique_id for r in results))
    total_detections = sum(r.count for r in results)

    TACTIC_ORDER = [
        'Initial Access','Execution','Persistence','Privilege Escalation',
        'Defense Evasion','Credential Access','Discovery','Lateral Movement',
        'Collection','Command and Control','Exfiltration','Impact'
    ]

    return render_template('mitre.html',
        tactic_map=tactic_map,
        tactic_order=TACTIC_ORDER,
        total_techniques=total_techniques,
        total_detections=total_detections,
        tactic_map_json=json.dumps(tactic_map),
    )


# ─────────────────────────────────────────────────────────────
#  THREAT HUNTING
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/hunting')
@login_required
def hunting():
    PRESET_QUERIES = [
        {
            'title': 'All Running Processes',
            'query': 'SELECT pid, name, cmdline, path, uid FROM processes LIMIT 50;',
        },
        {
            'title': 'Listening Ports',
            'query': 'SELECT p.name, lp.pid, lp.port, lp.protocol, lp.address FROM listening_ports lp JOIN processes p ON lp.pid = p.pid WHERE lp.port != 0 LIMIT 50;',
        },
        {
            'title': 'Active Network Connections',
            'query': "SELECT p.name, s.pid, s.remote_address, s.remote_port, s.state FROM process_open_sockets s JOIN processes p ON s.pid = p.pid WHERE s.remote_address != '' LIMIT 50;",
        },
        {
            'title': 'Cron Jobs',
            'query': 'SELECT command, path, username FROM crontab;',
        },
        {
            'title': 'Startup Items',
            'query': 'SELECT name, path, args, type, status FROM startup_items;',
        },
        {
            'title': 'USB Devices',
            'query': 'SELECT vendor, model, serial, removable FROM usb_devices;',
        },
        {
            'title': 'Logged-in Users',
            'query': 'SELECT username, tty, host, time FROM logged_in_users;',
        },
        {
            'title': 'OS Info',
            'query': 'SELECT name, version, platform FROM os_version;',
        },
    ]
    return render_template('hunting.html', presets=PRESET_QUERIES)


@analytics_bp.route('/hunting/query', methods=['POST'])
@login_required
def run_hunt_query():
    from collectors.osquery_runner import run_raw_query

    query = request.json.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Empty query', 'results': []})

    results, error = run_raw_query(query)
    return jsonify({'results': results, 'error': error, 'count': len(results)})


# ─────────────────────────────────────────────────────────────
#  ASSET INVENTORY
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/assets')
@login_required
def assets():
    from database.models import Endpoint, Alert, RawEvent, RiskScore
    from sqlalchemy import func

    endpoints = Endpoint.query.order_by(desc(Endpoint.last_seen)).all()

    # Enrich with per-endpoint stats
    enriched = []
    for ep in endpoints:
        event_count = RawEvent.query.filter_by(hostname=ep.hostname).count()
        alert_count = Alert.query.filter_by(hostname=ep.hostname, status='open').count()
        latest_rs   = (
            RiskScore.query
            .join(RawEvent, RiskScore.event_id == RawEvent.id)
            .filter(RawEvent.hostname == ep.hostname)
            .order_by(desc(RiskScore.calculated_at))
            .first()
        )
        enriched.append({
            'endpoint':     ep,
            'event_count':  event_count,
            'alert_count':  alert_count,
            'risk_score':   latest_rs.score      if latest_rs else 0,
            'risk_level':   latest_rs.risk_level if latest_rs else 'info',
        })

    return render_template('assets.html', endpoints=enriched)


# ─────────────────────────────────────────────────────────────
#  REPORTS PAGE
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/reports')
@login_required
def reports():
    import os
    from flask import current_app
    reports_dir = current_app.config.get('REPORTS_DIR', 'reports_output')
    files = []
    if os.path.isdir(reports_dir):
        for f in sorted(os.listdir(reports_dir), reverse=True):
            fpath = os.path.join(reports_dir, f)
            files.append({
                'name': f,
                'size': os.path.getsize(fpath),
                'modified': datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d %H:%M'),
            })
    return render_template('reports.html', files=files)


@analytics_bp.route('/reports/generate/pdf')
@login_required
def generate_pdf_report():
    from reports.pdf_generator import generate_pdf
    from flask import send_file
    path = generate_pdf()
    return send_file(path, as_attachment=True,
                     download_name=f"EDRLite_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")


@analytics_bp.route('/reports/generate/csv')
@login_required
def generate_csv_report():
    from reports.csv_export import generate_csv_zip
    from flask import send_file
    path = generate_csv_zip()
    return send_file(path, as_attachment=True,
                     download_name=f"EDRLite_CSV_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")


# ─────────────────────────────────────────────────────────────
#  API ENDPOINTS (for dashboard live refresh & active response)
# ─────────────────────────────────────────────────────────────
@analytics_bp.route('/api/kill/<int:pid>', methods=['POST'])
@login_required
def kill_process(pid):
    import psutil
    try:
        p = psutil.Process(pid)
        p.terminate()
        return jsonify({'status': 'success', 'message': f'Process {pid} terminated.'})
    except psutil.NoSuchProcess:
        return jsonify({'status': 'error', 'message': 'Process not found or already dead.'})
    except psutil.AccessDenied:
        return jsonify({'status': 'error', 'message': 'Access denied.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



@analytics_bp.route('/api/stats')
@login_required
def api_stats():
    from database.models import RawEvent, Alert, MitreEvent, RiskScore
    return jsonify({
        'total_events':    RawEvent.query.count(),
        'active_alerts':   Alert.query.filter_by(status='open').count(),
        'critical_alerts': Alert.query.filter(Alert.severity=='critical', Alert.status=='open').count(),
        'mitre_techniques':MitreEvent.query.with_entities(MitreEvent.technique_id).distinct().count(),
        'timestamp':       datetime.now(timezone.utc).isoformat(),
    })
