"""
reports/pdf_generator.py
─────────────────────────
Generates a professional PDF incident report using ReportLab.
"""

import os
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# Color palette
NAVY   = colors.HexColor('#0a0e1a')
BLUE   = colors.HexColor('#00d4ff')
PURPLE = colors.HexColor('#7c3aed')
RED    = colors.HexColor('#ef4444')
AMBER  = colors.HexColor('#f59e0b')
GREEN  = colors.HexColor('#10b981')
GRAY   = colors.HexColor('#94a3b8')
WHITE  = colors.white
DARK   = colors.HexColor('#1e293b')


def _sev_color(sev):
    return {
        'critical': RED,
        'high':     AMBER,
        'medium':   colors.HexColor('#f97316'),
        'low':      GREEN,
        'info':     GRAY,
    }.get(sev, GRAY)


def generate_pdf() -> str:
    """Generate PDF report and return file path."""
    from flask import current_app
    from database.models import RawEvent, Alert, MitreEvent, RiskScore, Endpoint

    reports_dir = current_app.config.get('REPORTS_DIR', 'reports_output')
    os.makedirs(reports_dir, exist_ok=True)

    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(reports_dir, f'EDRLite_Report_{ts}.pdf')

    doc    = SimpleDocTemplate(filepath, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    # ── Title ────────────────────────────────────────────────
    title_style = ParagraphStyle('title',
        fontSize=24, fontName='Helvetica-Bold',
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=6)
    sub_style = ParagraphStyle('sub',
        fontSize=11, fontName='Helvetica',
        textColor=GRAY, alignment=TA_CENTER, spaceAfter=20)

    story.append(Paragraph("🛡 EDRLite Incident Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        sub_style))
    story.append(HRFlowable(width='100%', thickness=2, color=BLUE))
    story.append(Spacer(1, 0.5*cm))

    h2 = ParagraphStyle('h2', fontSize=14, fontName='Helvetica-Bold',
                         textColor=NAVY, spaceAfter=8, spaceBefore=12)
    body = ParagraphStyle('body', fontSize=10, fontName='Helvetica',
                           textColor=colors.black, spaceAfter=4)

    # ── Executive Summary ────────────────────────────────────
    story.append(Paragraph("Executive Summary", h2))

    total_events    = RawEvent.query.count()
    total_alerts    = Alert.query.count()
    open_alerts     = Alert.query.filter_by(status='open').count()
    critical_alerts = Alert.query.filter(Alert.severity=='critical').count()
    mitre_count     = MitreEvent.query.with_entities(MitreEvent.technique_id).distinct().count()
    endpoints       = Endpoint.query.count()

    summary_data = [
        ['Metric', 'Value'],
        ['Total Events Collected',   str(total_events)],
        ['Total Alerts Generated',   str(total_alerts)],
        ['Open Alerts',              str(open_alerts)],
        ['Critical Severity Alerts', str(critical_alerts)],
        ['MITRE Techniques Observed',str(mitre_count)],
        ['Endpoints Monitored',      str(endpoints)],
    ]
    tbl = Table(summary_data, colWidths=[10*cm, 6*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), WHITE]),
        ('GRID',        (0,0), (-1,-1), 0.5, GRAY),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── Recent Alerts ────────────────────────────────────────
    story.append(Paragraph("Recent Alerts (Last 20)", h2))
    recent_alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(20).all()

    if recent_alerts:
        alert_data = [['Timestamp', 'Alert Name', 'Severity', 'Status', 'Host']]
        for a in recent_alerts:
            alert_data.append([
                a.timestamp.strftime('%Y-%m-%d %H:%M') if a.timestamp else '-',
                a.alert_name[:40],
                a.severity.upper(),
                a.status,
                a.hostname or '-',
            ])
        atbl = Table(alert_data, colWidths=[3.5*cm, 6*cm, 2.5*cm, 3*cm, 3*cm])
        row_colors = []
        for i, a in enumerate(recent_alerts, start=1):
            row_colors.append(('TEXTCOLOR', (2, i), (2, i), _sev_color(a.severity)))
        atbl.setStyle(TableStyle([
            ('BACKGROUND',  (0,0), (-1,0), DARK),
            ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
            ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), WHITE]),
            ('GRID',        (0,0), (-1,-1), 0.3, GRAY),
            ('TOPPADDING',  (0,0), (-1,-1), 4),
            ('BOTTOMPADDING',(0,0),(-1,-1), 4),
            *row_colors,
        ]))
        story.append(atbl)
    else:
        story.append(Paragraph("No alerts recorded.", body))

    story.append(Spacer(1, 0.5*cm))

    # ── MITRE Techniques ─────────────────────────────────────
    story.append(Paragraph("MITRE ATT&CK Techniques Observed", h2))
    from sqlalchemy import func
    techniques = (
        MitreEvent.query
        .with_entities(MitreEvent.technique_id, MitreEvent.technique_name,
                       MitreEvent.tactic, func.count(MitreEvent.id).label('cnt'))
        .group_by(MitreEvent.technique_id, MitreEvent.technique_name, MitreEvent.tactic)
        .order_by(func.count(MitreEvent.id).desc())
        .all()
    )
    if techniques:
        tdata = [['Technique ID', 'Name', 'Tactic', 'Detections']]
        for t in techniques:
            tdata.append([t.technique_id, t.technique_name[:35], t.tactic, str(t.cnt)])
        ttbl = Table(tdata, colWidths=[3*cm, 7*cm, 5*cm, 3*cm])
        ttbl.setStyle(TableStyle([
            ('BACKGROUND',  (0,0), (-1,0), PURPLE),
            ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
            ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0,0), (-1,-1), 9),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f3f0ff'), WHITE]),
            ('GRID',        (0,0), (-1,-1), 0.3, GRAY),
            ('TOPPADDING',  (0,0), (-1,-1), 5),
            ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ]))
        story.append(ttbl)
    else:
        story.append(Paragraph("No MITRE techniques mapped.", body))

    # ── Footer ───────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width='100%', thickness=1, color=GRAY))
    story.append(Paragraph(
        "EDRLite — Endpoint Detection, Threat Hunting & MITRE ATT&CK Correlation Platform",
        ParagraphStyle('footer', fontSize=8, textColor=GRAY, alignment=TA_CENTER)
    ))

    doc.build(story)
    return filepath
