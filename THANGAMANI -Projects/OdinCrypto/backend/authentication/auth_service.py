"""
OdinCrypto - Authentication using hashlib (no bcrypt dependency)
"""
import hashlib, secrets, os
from datetime import datetime
from backend.database.db import get_db

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000)
    return f"pbkdf2$sha256$260000${salt}${dk.hex()}"

def check_password(stored: str, password: str) -> bool:
    try:
        _, algo, iters, salt, dk_stored = stored.split('$')
        dk = hashlib.pbkdf2_hmac(algo, password.encode(), salt.encode(), int(iters))
        return secrets.compare_digest(dk.hex(), dk_stored)
    except Exception:
        return False

def log_action(user_id, action, details='', ip_address='', status='success'):
    db = get_db()
    db.execute(
        "INSERT INTO audit_logs (user_id, action, details, ip_address, status) VALUES (?,?,?,?,?)",
        (user_id, action, details, ip_address, status)
    )
    db.commit()
    db.close()

def register_user(username, email, password):
    db = get_db()
    if db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
        db.close()
        return {'success': False, 'message': 'Username already taken'}
    if db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
        db.close()
        return {'success': False, 'message': 'Email already registered'}
    pw_hash = hash_password(password)
    db.execute(
        "INSERT INTO users (username, email, password_hash, security_score) VALUES (?,?,?,?)",
        (username, email, pw_hash, 30)
    )
    db.commit()
    user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    db.close()
    log_action(user['id'], 'REGISTER', 'User registered')
    return {'success': True, 'user': dict(user)}

def verify_user(email, password):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user:
        db.close()
        return {'success': False, 'message': 'Invalid email or password'}
    if not check_password(user['password_hash'], password):
        db.close()
        return {'success': False, 'message': 'Invalid email or password'}
    if not user['is_active']:
        db.close()
        return {'success': False, 'message': 'Account disabled. Contact admin.'}
    db.execute("UPDATE users SET last_login=? WHERE id=?", (datetime.utcnow().isoformat(), user['id']))
    db.commit()
    u = dict(user)
    db.close()
    log_action(u['id'], 'LOGIN', 'User logged in')
    return {'success': True, 'user': u}

def change_password(user_id, old_password, new_password):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        db.close()
        return {'success': False, 'message': 'User not found'}
    if not check_password(user['password_hash'], old_password):
        db.close()
        return {'success': False, 'message': 'Current password is incorrect'}
    db.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_password), user_id))
    db.commit()
    db.close()
    log_action(user_id, 'PASSWORD_CHANGE', 'Password changed')
    return {'success': True, 'message': 'Password changed successfully'}

def calculate_security_score(user_id):
    db = get_db()
    keys = db.execute("SELECT COUNT(*) as c FROM key_pairs WHERE user_id=? AND is_revoked=0", (user_id,)).fetchone()['c']
    vault = db.execute("SELECT COUNT(*) as c FROM password_vault WHERE user_id=?", (user_id,)).fetchone()['c']
    db.close()
    score = 35
    if keys > 0: score += 25
    if vault > 0: score += 15
    if keys > 2: score += 10
    return min(score, 100)
