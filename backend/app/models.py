from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.sql import func
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="employee")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock_qty = Column(Integer, nullable=False, default=0)
    low_stock_at = Column(Integer, nullable=False, default=5)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    sold_at = Column(Date, server_default=func.current_date())

class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(Date, nullable=False)
    predicted_qty = Column(Integer, nullable=False)
    model_version = Column(String, nullable=False)