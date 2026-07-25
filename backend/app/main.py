from fastapi import FastAPI
from app.routers import products, sales
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, products, sales, forecasts



app = FastAPI(title= "GreenBasket API")
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(forecasts.router, prefix="/api/forecast", tags=["forecast"])


@app.get("/health")
def health():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)