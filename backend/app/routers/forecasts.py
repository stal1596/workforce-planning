from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Forecast, User
from app.schemas import ForecastOut

router = APIRouter()


@router.get("/{product_id}", response_model=list[ForecastOut])
def get_forecast(product_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Forecast)
        .filter(Forecast.product_id == product_id)
        .order_by(Forecast.date)
        .all()
    )