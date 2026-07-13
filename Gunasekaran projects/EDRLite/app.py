"""
app.py — EDRLite Application Entry Point
"""

import os
import logging
from flask import Flask
from config import Config
from flask_socketio import SocketIO
from database.db import db, login_manager, init_db

socketio = SocketIO()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Ensure report output directory exists
    os.makedirs(app.config['REPORTS_DIR'], exist_ok=True)

    # Init DB + Login Manager
    init_db(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')

    # Init Auth
    from auth.auth import auth_bp, init_auth
    init_auth(app.config['ADMIN_USERNAME'], app.config['ADMIN_PASSWORD'])
    app.register_blueprint(auth_bp)

    # Init Dashboard
    from dashboards.analytics import analytics_bp
    app.register_blueprint(analytics_bp)

    # Init Telemetry API for Remote Agents
    from api.telemetry import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app

app = create_app()




if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("  EDRLite — Endpoint Detection & Response Platform")
    logger.info("  http://127.0.0.1:5000")
    logger.info(f"  Login: admin / EDRLite@2024")
    logger.info("=" * 60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
