"""
auth/auth.py
─────────────
Flask-Login authentication blueprint.
Default credentials: admin / EDRLite@2024
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import login_manager

auth_bp = Blueprint('auth', __name__)

# ── Simple in-memory user (single admin user) ────────────────
class AdminUser(UserMixin):
    id       = 1
    username = None

    def __init__(self, username):
        self.username = username

    def get_id(self):
        return str(self.id)


# Will be populated by app.py with hashed password from config
_admin_hash: str = ''
_admin_username: str = 'admin'


def init_auth(username: str, password: str):
    global _admin_hash, _admin_username
    _admin_username = username
    _admin_hash     = generate_password_hash(password)


@login_manager.user_loader
def load_user(user_id):
    if str(user_id) == '1':
        return AdminUser(_admin_username)
    return None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('analytics.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if username == _admin_username and check_password_hash(_admin_hash, password):
            user = AdminUser(username)
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Welcome back, Commander! 🛡️', 'success')
            return redirect(next_page or url_for('analytics.dashboard'))
        else:
            flash('Invalid credentials. Access denied.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
