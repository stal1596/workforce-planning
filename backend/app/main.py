from fastapi import FastAPI
from app.routers import products, sales

app = FastAPI(title= "GreenBasket API")
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])

@app.get("/health")
def health():
    return {"status": "ok"}

