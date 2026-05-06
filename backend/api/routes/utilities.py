from fastapi import APIRouter, HTTPException, Query
from core.services.external_api_service import get_twelve_data_exchange_rate, get_twelve_data_currency_conversion
from typing import Optional

router = APIRouter()

@router.get("/exchange-rate")
async def exchange_rate(symbol: str):
    try:
        return get_twelve_data_exchange_rate(symbol)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/convert")
async def convert_currency(symbol: str, amount: float):
    try:
        return get_twelve_data_currency_conversion(symbol, amount)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
