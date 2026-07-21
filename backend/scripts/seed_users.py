from app.auth import hash_password
from app.db import SessionLocal
from app.models import User

db = SessionLocal()
db.add_all([
    User(email="rosa@greenbasket.shop", password_hash=hash_password("changeme123"), role="admin"),
    User(email="priya@greenbasket.shop", password_hash=hash_password("changeme123"), role="employee"),
])
db.commit()
db.close()
print("Seeded 2 users.")