from fastapi import APIRouter, Query, HTTPException
from core.services.external_api_service import fetch_external_stock_data, get_ticker_mapping
from models.schemas import UploadResponse

router = APIRouter()

@router.get("/tickers")
async def fetch_tickers():
    """
    Returns the grouped ticker mapping for all API providers.
    """
    return get_ticker_mapping()

@router.get("/fetch", response_model=UploadResponse)
async def fetch_market_data(
    api_choice: str = Query(..., description="API to use: 'Alpha Vantage' or 'Financial Prep'"),
    ticker: str = Query(..., description="Stock ticker symbol (e.g., AAPL)"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
):
    """
    Fetch market data from an external API (Alpha Vantage or Financial Modeling Prep).
    Returns the same format as file upload.
    """
    try:
        return fetch_external_stock_data(
            api_choice=api_choice,
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

