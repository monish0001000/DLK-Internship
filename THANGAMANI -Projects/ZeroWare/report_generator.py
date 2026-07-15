import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_report(result: dict, output_path: str) -> str:
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle('ZeroTitle', fontSize=22, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#00d4ff'), alignment=TA_CENTER, spaceAfter=6)
    sub_style = ParagraphStyle('ZeroSub', fontSize=11, fontName='Helvetica',
                                textColor=colors.grey, alignment=TA_CENTER, spaceAfter=20)
    story.append(Paragraph("🛡️ ZeroWare Security Report", title_style))
    story.append(Paragraph("AI-Powered Malware Intelligence Platform", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#00d4ff')))
    story.append(Spacer(1, 12))

    # Scan info
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pred = result.get('prediction', {})
    label = pred.get('label', 'Unknown')
    label_color = {'Malware': colors.red, 'Suspicious': colors.orange, 'Safe': colors.green}.get(label, colors.grey)

    info_data = [
        ['File Name', result.get('file_name', 'N/A')],
        ['Scan Date', now],
        ['Prediction', label],
        ['Confidence', f"{pred.get('confidence', 0):.1f}%"],
    ]

    info_table = Table(info_data, colWidths=[5*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#00d4ff')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # Hashes
    features = result.get('features', {})
    story.append(Paragraph("File Hashes", ParagraphStyle('Sec', fontSize=13, fontName='Helvetica-Bold',
                                                          textColor=colors.HexColor('#1a1a2e'), spaceAfter=6)))
    hash_data = [
        ['MD5', features.get('md5', 'N/A')],
        ['SHA256', features.get('sha256', 'N/A')],
    ]
    hash_table = Table(hash_data, colWidths=[3*cm, 14*cm])
    hash_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('WORDWRAP', (1, 0), (1, -1), True),
    ]))
    story.append(hash_table)
    story.append(Spacer(1, 16))

    # Scores
    trust = result.get('trust', {})
    story.append(Paragraph("Intelligence Scores", ParagraphStyle('Sec2', fontSize=13, fontName='Helvetica-Bold',
                                                                   textColor=colors.HexColor('#1a1a2e'), spaceAfter=6)))
    score_data = [
        ['Trust Score', f"{trust.get('score', 0)}/100 ({trust.get('level', 'N/A')})"],
        ['Risk Score', f"{result.get('risk_score', 0)}/100"],
        ['Zero-Day Probability', f"{result.get('zeroday_prob', 0)}%"],
        ['ZeroDNA ID', result.get('zerodna', {}).get('dna_id', 'N/A')],
    ]
    score_table = Table(score_data, colWidths=[5*cm, 12*cm])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#00d4ff')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 16))

    # AI Reasons
    reasons = result.get('reasons', [])
    if reasons:
        story.append(Paragraph("AI Explanation (ZeroReason)", ParagraphStyle('Sec3', fontSize=13, fontName='Helvetica-Bold',
                                                                               textColor=colors.HexColor('#1a1a2e'), spaceAfter=6)))
        for r in reasons:
            story.append(Paragraph(f"• {r.get('text', '')}", ParagraphStyle('Reason', fontSize=9, leftIndent=12, spaceAfter=4)))
        story.append(Spacer(1, 12))

    # Behavior predictions
    behaviors = result.get('behaviors', {})
    if behaviors:
        story.append(Paragraph("Behavior Predictions", ParagraphStyle('Sec4', fontSize=13, fontName='Helvetica-Bold',
                                                                        textColor=colors.HexColor('#1a1a2e'), spaceAfter=6)))
        beh_data = [[b, f"{p}%"] for b, p in behaviors.items()]
        beh_table = Table(beh_data, colWidths=[10*cm, 7*cm])
        beh_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        story.append(beh_table)
        story.append(Spacer(1, 12))

    # Recommendations
    recs = result.get('recommendations', [])
    if recs:
        story.append(Paragraph("Security Recommendations", ParagraphStyle('Sec5', fontSize=13, fontName='Helvetica-Bold',
                                                                            textColor=colors.HexColor('#1a1a2e'), spaceAfter=6)))
        for rec in recs:
            story.append(Paragraph(f"➤ {rec}", ParagraphStyle('Rec', fontSize=9, leftIndent=12, spaceAfter=4,
                                                                textColor=colors.HexColor('#c0392b'))))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Paragraph("Generated by ZeroWare AI Malware Intelligence Platform",
                            ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER, spaceBefore=8)))

    doc.build(story)
    return output_path
