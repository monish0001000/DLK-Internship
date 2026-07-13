"""
SentinelX EDR - Report Generator Service
==========================================
Generates formatted Markdown reports from investigations and cases.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.report import Report
from app.models.investigation import Investigation
from app.models.case import Case

def generate_incident_report(db: Session, investigation_id: str) -> Report:
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise ValueError("Investigation not found")
        
    title = f"Incident Report: Alert {inv.alert_id}"
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # We use f-strings for templating instead of Jinja2 to minimize dependencies
    markdown = f"""# SentinelX EDR - Incident Report

**Generated:** {date_str}
**Investigation ID:** {inv.id}
**Risk Score:** {inv.risk_score}/100 ({inv.risk_level})

## Executive Summary
{inv.summary or 'No summary available.'}

## Root Cause Analysis
{inv.root_cause or 'No root cause identified.'}

## MITRE ATT&CK Mapping
| Tactic | Technique |
|---|---|
"""
    
    if inv.mitre_mapping:
        import json
        try:
            mapping = json.loads(inv.mitre_mapping) if isinstance(inv.mitre_mapping, str) else inv.mitre_mapping
            for m in mapping:
                markdown += f"| {m.get('tactic', 'Unknown')} | {m.get('technique_id', '')} - {m.get('name', '')} |\n"
        except Exception:
            markdown += "| Error | Could not parse MITRE mapping |\n"
    else:
        markdown += "| None | No techniques mapped |\n"
        
    markdown += f"""
## Timeline of Events
"""
    if inv.timeline:
        import json
        try:
            timeline = json.loads(inv.timeline) if isinstance(inv.timeline, str) else inv.timeline
            for t in timeline:
                markdown += f"- **{t.get('timestamp', '')}**: {t.get('event_type', '')} - {t.get('description', '')}\n"
        except Exception:
            markdown += "- Error parsing timeline data.\n"
    else:
        markdown += "- No timeline available.\n"
        
    markdown += f"""
## Recommendations
{inv.recommendations or 'No recommendations provided.'}

## Response Plan
"""
    if inv.response_plan:
        import json
        try:
            plan = json.loads(inv.response_plan) if isinstance(inv.response_plan, str) else inv.response_plan
            markdown += f"**Priority:** {plan.get('priority', 'medium')}\n\n**Actions:**\n"
            for a in plan.get('actions', []):
                markdown += f"- {a}\n"
            markdown += f"\n**Rationale:** {plan.get('rationale', '')}\n"
        except Exception:
            markdown += "Error parsing response plan.\n"
    else:
        markdown += "No response plan available.\n"

    report = Report(
        investigation_id=inv.id,
        title=title,
        report_type="incident",
        content_markdown=markdown,
        generated_by="ai"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def generate_executive_summary(db: Session, investigation_id: str) -> Report:
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise ValueError("Investigation not found")
        
    title = f"Executive Summary: Alert {inv.alert_id}"
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    markdown = f"""# Executive Incident Summary

**Date:** {date_str}
**Risk Level:** {inv.risk_level} ({inv.risk_score}/100)

## Overview
{inv.summary or 'No summary available.'}

## Business Impact
The identified incident indicates a potential risk to operations. Immediate review of the recommended actions is advised.

## Key Findings
{inv.root_cause or 'See full technical report for details.'}

## Recommended Actions
{inv.recommendations or 'No immediate actions recommended.'}
"""

    report = Report(
        investigation_id=inv.id,
        title=title,
        report_type="executive",
        content_markdown=markdown,
        generated_by="ai"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def generate_hunt_report(db: Session, case_id: str) -> Report:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError("Case not found")
        
    title = f"Hunt Report: {case.title}"
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    markdown = f"""# Threat Hunting Report

**Generated:** {date_str}
**Case:** {case.title}
**Status:** {case.status}

## Hunt Hypothesis
Investigation into suspicious activity related to this case.

## Methodology
Analyzed endpoint telemetry, process trees, and network connections associated with the case artifacts.

## Findings
{case.description or 'No detailed description provided.'}

## IOCs Discovered
See attached case evidence for specific indicators.

## Detection Gaps
Review current rules against findings to identify coverage improvements.
"""

    report = Report(
        case_id=case.id,
        title=title,
        report_type="hunt",
        content_markdown=markdown,
        generated_by="system"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
