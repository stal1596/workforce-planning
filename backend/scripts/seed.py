from app.db import SessionLocal
from app.models import Product

db = SessionLocal()
db.add_all([
    Product(name="Milk 1L", price=1.20, stock_qty=40, low_stock_at=10),
    Product(name="Yoghurt 500g", price=2.10, stock_qty=15, low_stock_at=5),
    Product(name="Bread Loaf", price=1.80, stock_qty=25, low_stock_at=8),
])
db.commit()
db.close()
print("Seeded 3 products.")