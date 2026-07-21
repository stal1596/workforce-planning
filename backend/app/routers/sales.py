from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Product, Sale
from app.schemas import SaleCreate, SaleOut

router = APIRouter()


@router.get("", response_model=list[SaleOut])
def list_sales(product_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Sale)
    if product_id is not None:
        query = query.filter(Sale.product_id == product_id)
    return query.all()


@router.post("", response_model=SaleOut, status_code=201)
def record_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    product = db.get(Product, sale.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if sale.qty > product.stock_qty:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot sell {sale.qty} — only {product.stock_qty} in stock",
        )
    product.stock_qty -= sale.qty
    db_sale = Sale(product_id=sale.product_id, qty=sale.qty)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale