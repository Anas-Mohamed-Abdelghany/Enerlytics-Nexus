import random
from datetime import datetime, timedelta
from typing import List
from models.schemas import BacktestResults, TradeLogEntry, PriceData, OHLCVPoint

def _apply_strategy(price_series: List[float], risk_profile: str) -> List[TradeLogEntry]:
    trades: List[TradeLogEntry] = []
    position = None
    entry_price = 0.0
    
    # Adjust thresholds based on risk profile (Lowered for demo visibility)
    thresholds = {
        "Conservative": 0.005, # 0.5% 
        "Balanced": 0.01,      # 1.0%
        "Aggressive": 0.02     # 2.0%
    }
    t = thresholds.get(risk_profile, 0.02)

    for i in range(1, len(price_series)):
        prev = price_series[i - 1]
        cur = price_series[i]
        change_pct = (cur - prev) / prev

        if position is None and change_pct <= -t:
            position = "LONG"
            entry_price = cur
            trades.append(
                TradeLogEntry(timestamp=datetime.utcnow() - timedelta(days=len(price_series)-i), action="BUY", price=cur, quantity=1.0, pnl=0.0)
            )
        elif position == "LONG" and change_pct >= t:
            pnl = cur - entry_price
            trades.append(
                TradeLogEntry(timestamp=datetime.utcnow() - timedelta(days=len(price_series)-i), action="SELL", price=cur, quantity=1.0, pnl=round(pnl, 2))
            )
            position = None

    if position == "LONG":
        pnl = price_series[-1] - entry_price
        trades.append(
            TradeLogEntry(timestamp=datetime.utcnow(), action="SELL", price=price_series[-1], quantity=1.0, pnl=round(pnl, 2))
        )
    return trades

def run_backtest(market: str = "US-TEXAS", start_days_ago: int = 30, end_days_ago: int = 0, initial_capital: float = 10_000.0, risk_profile: str = "Balanced", series: List[OHLCVPoint] = None) -> BacktestResults:
    """
    Simulate a back‑test over a synthetic price series.
    # TODO: Engineers will inject real PyTorch/GARCH/Pandas logic here.
    """
    if series and len(series) > 0:
        price_series = [p.close for p in series]
    else:
        from core.services.market_service import get_historical_prices
        
        price_data: PriceData = get_historical_prices(market=market, timeframe="1Y", interval="1D")
        
        # We only need the close prices for the strategy
        price_series = [p.close for p in price_data.series]

    trade_log = _apply_strategy(price_series, risk_profile)

    final_capital = initial_capital + sum(t.pnl for t in trade_log)
    total_return_pct = ((final_capital - initial_capital) / initial_capital) * 100
    roi_pct = total_return_pct

    now = datetime.utcnow()
    start_date = now - timedelta(days=start_days_ago)
    end_date = now - timedelta(days=end_days_ago)

    return BacktestResults(
        market=market,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        final_capital=round(final_capital, 2),
        total_return_pct=round(total_return_pct, 2),
        roi_pct=round(roi_pct, 2),
        trade_log=trade_log,
    )
