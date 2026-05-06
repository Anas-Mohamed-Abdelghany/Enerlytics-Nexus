from fastapi import APIRouter
from core.services.simulator_service import run_backtest
from models.schemas import BacktestResults, SimulationRequest

router = APIRouter()

@router.post("/", response_model=BacktestResults)
async def post_simulation(req: SimulationRequest):
    """
    Run a synthetic back‑test over the requested time window.
    """
    return run_backtest(
        market=req.market,
        start_days_ago=req.start_days_ago,
        end_days_ago=req.end_days_ago,
        initial_capital=req.initial_capital,
        risk_profile=req.risk_profile,
        series=req.series
    )
