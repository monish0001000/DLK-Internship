import os
import sys

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == 'admin').first()
    if admin_user:
        print("Admin user already exists.")
    else:
        new_admin = User(
            username='admin',
            email='admin@sentinelx.com',
            hashed_password=get_password_hash('admin123'),
            role='Administrator',
            is_active=True
        )
        db.add(new_admin)
        db.commit()
        print("Admin user created! Username: admin, Password: admin123")
    db.close()

if __name__ == '__main__':
    create_admin()
