from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()

if user:
    user.email = "admin@sentinelx.com"
    db.commit()
    print("Updated admin email to admin@sentinelx.com")
else:
    print("User 'admin' not found.")
