from datetime import datetime
from backend.database.db import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    mfa_enabled = db.Column(db.Boolean, default=False)
    security_score = db.Column(db.Integer, default=0)

    keys = db.relationship('KeyPair', backref='user', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True, cascade='all, delete-orphan')
    shared_files = db.relationship('SharedFile', backref='user', lazy=True, cascade='all, delete-orphan')
    passwords = db.relationship('PasswordVault', backref='user', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('SecureNote', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'mfa_enabled': self.mfa_enabled,
            'security_score': self.security_score
        }


class KeyPair(db.Model):
    __tablename__ = 'key_pairs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key_name = db.Column(db.String(100), nullable=False)
    algorithm = db.Column(db.String(20), nullable=False)  # RSA-2048, RSA-4096
    public_key = db.Column(db.Text, nullable=False)
    private_key_encrypted = db.Column(db.Text, nullable=False)
    is_revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rotated_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'key_name': self.key_name,
            'algorithm': self.algorithm,
            'public_key': self.public_key,
            'is_revoked': self.is_revoked,
            'created_at': self.created_at.isoformat()
        }


class SharedFile(db.Model):
    __tablename__ = 'shared_files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    share_token = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    expiry_date = db.Column(db.DateTime)
    download_limit = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='success')

    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status
        }


class PasswordVault(db.Model):
    __tablename__ = 'password_vault'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    site_name = db.Column(db.String(100), nullable=False)
    username_enc = db.Column(db.Text, nullable=False)
    password_enc = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255))
    notes_enc = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class SecureNote(db.Model):
    __tablename__ = 'secure_notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title_enc = db.Column(db.Text, nullable=False)
    content_enc = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
