from app.core.security import verify_password
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()

if user:
    print(f"Hash in DB: {user.hashed_password}")
    is_valid = verify_password("admin123", user.hashed_password)
    print(f"Password 'admin123' is valid: {is_valid}")
else:
    print("User 'admin' not found.")
