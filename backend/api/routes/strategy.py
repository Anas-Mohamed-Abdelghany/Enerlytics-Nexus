from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict, Any
import pandas as pd

from core.services.strategy_service import analyze_stock_data, find_best_strategy
from models.schemas import OHLCVPoint

router = APIRouter()

@router.post("/analyze")
async def analyze_strategy(
    strategy: str = Body(..., description="Strategy name to apply"),
    series: List[OHLCVPoint] = Body(..., description="Historical OHLCV data")
) -> Dict[str, Any]:
    """
    Applies a specified technical analysis strategy to the dataset.
    """
    try:
        df = pd.DataFrame([p.model_dump() for p in series])
        result_df = analyze_stock_data(df, strategy)
        
        # Replace NaN with None for JSON serialization
        result_df = result_df.replace({pd.NA: None, float('nan'): None})
        
        return {
            "strategy": strategy,
            "data": result_df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/best")
async def get_best_strategy(
    series: List[OHLCVPoint] = Body(..., embed=True, description="Historical OHLCV data")
) -> Dict[str, Any]:
    """
    Evaluates all strategies and returns the one with the highest performance score.
    """
    try:
        df = pd.DataFrame([p.model_dump() for p in series])
        best_strategy, best_score = find_best_strategy(df)
        
        return {
            "best_strategy": best_strategy,
            "score": best_score
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
