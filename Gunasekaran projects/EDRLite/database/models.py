from datetime import datetime, timezone
import json
from database.db import db


# ─────────────────────────────────────────────────────────────
#  Endpoint
# ─────────────────────────────────────────────────────────────
class Endpoint(db.Model):
    __tablename__ = 'endpoints'

    id          = db.Column(db.Integer, primary_key=True)
    hostname    = db.Column(db.String(255), unique=True, nullable=False)
    ip_address  = db.Column(db.String(45))
    os_version  = db.Column(db.String(255))
    last_seen   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status      = db.Column(db.String(20), default='active')   # active | inactive

    events      = db.relationship('RawEvent', backref='endpoint_ref', lazy='dynamic')
    alerts      = db.relationship('Alert',    backref='endpoint_ref', lazy='dynamic')

    def to_dict(self):
        return {
            'id':         self.id,
            'hostname':   self.hostname,
            'ip_address': self.ip_address,
            'os_version': self.os_version,
            'last_seen':  self.last_seen.isoformat() if self.last_seen else None,
            'status':     self.status,
        }


# ─────────────────────────────────────────────────────────────
#  Raw Event
# ─────────────────────────────────────────────────────────────
class RawEvent(db.Model):
    __tablename__ = 'raw_events'

    id          = db.Column(db.Integer, primary_key=True)
    timestamp   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    event_type  = db.Column(db.String(50), index=True)    # process | network | usb | startup
    event_data  = db.Column(db.Text)                       # JSON string
    hostname    = db.Column(db.String(255), db.ForeignKey('endpoints.hostname'), index=True)

    alerts      = db.relationship('Alert',      backref='raw_event', lazy='dynamic')
    mitre_maps  = db.relationship('MitreEvent', backref='raw_event', lazy='dynamic')
    risk_scores = db.relationship('RiskScore',  backref='raw_event', lazy='dynamic')

    def get_data(self):
        try:
            return json.loads(self.event_data) if self.event_data else {}
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id':         self.id,
            'timestamp':  self.timestamp.isoformat() if self.timestamp else None,
            'event_type': self.event_type,
            'event_data': self.get_data(),
            'hostname':   self.hostname,
        }


# ─────────────────────────────────────────────────────────────
#  Alert
# ─────────────────────────────────────────────────────────────
class Alert(db.Model):
    __tablename__ = 'alerts'

    id          = db.Column(db.Integer, primary_key=True)
    timestamp   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    alert_name  = db.Column(db.String(255), nullable=False)
    severity    = db.Column(db.String(20), default='medium')   # critical|high|medium|low|info
    status      = db.Column(db.String(20), default='open')     # open|acknowledged|escalated|false_positive
    description = db.Column(db.Text)
    hostname    = db.Column(db.String(255), db.ForeignKey('endpoints.hostname'), index=True)
    event_id    = db.Column(db.Integer,    db.ForeignKey('raw_events.id'))
    source      = db.Column(db.String(50), default='sigma')    # sigma | ioc | manual

    def to_dict(self):
        return {
            'id':          self.id,
            'timestamp':   self.timestamp.isoformat() if self.timestamp else None,
            'alert_name':  self.alert_name,
            'severity':    self.severity,
            'status':      self.status,
            'description': self.description,
            'hostname':    self.hostname,
            'event_id':    self.event_id,
            'source':      self.source,
        }


# ─────────────────────────────────────────────────────────────
#  MITRE Event Mapping
# ─────────────────────────────────────────────────────────────
class MitreEvent(db.Model):
    __tablename__ = 'mitre_events'

    id             = db.Column(db.Integer, primary_key=True)
    event_id       = db.Column(db.Integer, db.ForeignKey('raw_events.id'), index=True)
    technique_id   = db.Column(db.String(20))    # e.g. T1059
    technique_name = db.Column(db.String(255))
    tactic         = db.Column(db.String(100))   # e.g. Execution
    timestamp      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id':             self.id,
            'event_id':       self.event_id,
            'technique_id':   self.technique_id,
            'technique_name': self.technique_name,
            'tactic':         self.tactic,
            'timestamp':      self.timestamp.isoformat() if self.timestamp else None,
        }


# ─────────────────────────────────────────────────────────────
#  Risk Score
# ─────────────────────────────────────────────────────────────
class RiskScore(db.Model):
    __tablename__ = 'risk_scores'

    id             = db.Column(db.Integer, primary_key=True)
    event_id       = db.Column(db.Integer, db.ForeignKey('raw_events.id'), index=True)
    score          = db.Column(db.Float, default=0.0)
    risk_level     = db.Column(db.String(20), default='low')   # critical|high|medium|low|info
    factors        = db.Column(db.Text)                         # JSON: breakdown of score
    calculated_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_factors(self):
        try:
            return json.loads(self.factors) if self.factors else {}
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id':            self.id,
            'event_id':      self.event_id,
            'score':         self.score,
            'risk_level':    self.risk_level,
            'factors':       self.get_factors(),
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
        }
