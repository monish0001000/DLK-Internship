"""
OdinCrypto - Application Entry Point
"""
import os
from datetime import timedelta
from flask import Flask
from backend.database.db import init_db
from backend.api.routes import main

def create_app():
    app = Flask(__name__,
                template_folder='frontend/templates',
                static_folder='frontend/static')

    app.secret_key = os.environ.get('SECRET_KEY', 'odincrypto-secret-key-change-in-production-2024!')
    app.permanent_session_lifetime = timedelta(hours=2)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

    base = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER']    = os.path.join(base, 'uploads')
    app.config['ENCRYPTED_FOLDER'] = os.path.join(base, 'encrypted')
    app.config['DECRYPTED_FOLDER'] = os.path.join(base, 'decrypted')
    app.config['KEYS_FOLDER']      = os.path.join(base, 'keys')

    for d in ['uploads','encrypted','decrypted','keys','logs','database']:
        os.makedirs(os.path.join(base, d), exist_ok=True)

    init_db()
    app.register_blueprint(main)
    return app


if __name__ == '__main__':
    app = create_app()

    # Create default admin
    from backend.database.db import get_db
    from backend.authentication.auth_service import hash_password
    db = get_db()
    if not db.execute("SELECT id FROM users WHERE username='admin'").fetchone():
        db.execute("INSERT INTO users (username,email,password_hash,is_admin,security_score) VALUES (?,?,?,?,?)",
                   ('admin','admin@odincrypto.local', hash_password('Admin@1234'), 1, 100))
        db.commit()
        print("✅ Admin created: admin@odincrypto.local / Admin@1234")
    db.close()

    print("🔐 OdinCrypto → http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
