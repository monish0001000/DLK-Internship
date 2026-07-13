import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
def upsert_user():
    db = SessionLocal()
    user = db.query(User).filter(User.username == 'MONISH').first()
    if user:
        user.hashed_password = get_password_hash('admin123')
        print('User MONISH updated with password admin123.')
    else:
        new_user = User(
            username='MONISH',
            email='monish@sentinelx.com',
            hashed_password=get_password_hash('admin123'),
            role='Administrator',
            is_active=True
        )
        db.add(new_user)
        print('User MONISH created with password admin123.')
    db.commit()
    db.close()
if __name__ == '__main__':
    upsert_user()
