import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models.user import User
from app.core.security import get_password_hash

DATABASE_URL = "sqlite:///./sentinelx.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reset_admin():
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == 'admin').first()
    if admin_user:
        admin_user.hashed_password = get_password_hash('admin123')
        db.commit()
        print("Password reset to admin123")
    else:
        print("Admin user not found!")
    db.close()

if __name__ == "__main__":
    reset_admin()
