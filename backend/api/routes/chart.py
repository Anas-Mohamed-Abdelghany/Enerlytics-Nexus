from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict, Any
from core.services.chart_service import generate_plotly_chart
from models.schemas import OHLCVPoint

router = APIRouter()

@router.post("/render")
async def render_chart(
    series: List[OHLCVPoint] = Body(..., embed=True),
    ticker: str = Body("Market", embed=True),
    theme: str = Body("dark", embed=True),
    chart_type: str = Body("candlestick", embed=True),
    indicators: List[str] = Body(None, embed=True),
    vlines: List[Any] = Body(None, embed=True)
) -> Dict[str, Any]:

    """
    Returns a Plotly HTML string for the provided OHLCV series.
    """
    try:
        charts = generate_plotly_chart(series, ticker, theme, chart_type, indicators, vlines)
        return {"charts": charts}
    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Chart generation failed: {str(e)}")

