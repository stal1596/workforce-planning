from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: Decimal
    stock_qty: int
    low_stock_at: int


class ProductCreate(BaseModel):
    name: str
    price: Decimal = Field(gt=0)
    stock_qty: int = Field(ge=0, default=0)
    low_stock_at: int = Field(ge=0, default=5)


class StockUpdate(BaseModel):
    stock_qty: int = Field(ge=0)


class SaleCreate(BaseModel):
    product_id: int
    qty: int = Field(gt=0)


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    qty: int
    sold_at: date