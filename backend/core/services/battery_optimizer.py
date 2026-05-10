import numpy as np
import pandas as pd
from scipy.optimize import linprog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- FastAPI Router ---
router = APIRouter()

class OptimizationRequest(BaseModel):
    buy_price: List[float]       # €/kWh
    sell_price: List[float]      # €/kWh
    load_forecast: List[float]   # kW
    solar_forecast: List[float]  # kW
    soc_init: float = 0.5        # 0.0 - 1.0
    battery_capacity_kwh: float = 16.0
    p_max_kw: float = 8.0
    grid_limit_kw: float = 6.0
    eta: float = 0.94868         # sqrt(0.90) for 90% round-trip efficiency
    dt: float = 0.25             # 15-min = 0.25 hours
    horizon_steps: int = 96

def compute_baseline_cost(
    buy_price: np.ndarray,
    sell_price: np.ndarray,
    load_kw: np.ndarray,
    solar_kw: np.ndarray,
    dt: float = 0.25
) -> float:
    """
    Calculates the cost if P_battery = 0 for all t (all load met by solar then grid).
    """
    net_load = load_kw - solar_kw
    grid_import = np.maximum(0, net_load)
    grid_export = np.maximum(0, -net_load)
    # Sign convention: negative = paid, positive = revenue
    cost = (grid_export * sell_price - grid_import * buy_price) * dt
    return float(np.sum(cost))

from scipy import sparse

def optimize_battery(
    buy_price: np.ndarray,
    sell_price: np.ndarray,
    load_forecast: np.ndarray,
    solar_forecast: np.ndarray,
    soc_init: float,
    battery_capacity_kwh: float = 16.0,
    p_max_kw: float = 8.0,
    grid_limit_kw: float = 6.0,
    eta: float = 0.94868,
    dt: float = 0.25
) -> dict:
    """
    Sparse Linear Programming formulation for Battery Optimization.
    Decision Variables: [P_charge, P_discharge, P_grid_import, P_grid_export, SoC, P_slack] (interleaved)
    """
    H = len(load_forecast)
    if H == 0:
        return {"success": False, "message": "Empty forecast"}

    # Total variables = 7 per step
    # x = [P_ch, P_dis, P_imp, P_exp, SOC, P_slack, P_curtail] (interleaved)
    num_vars = 7 * H
    
    # 1. Objective: Minimize costs
    c = np.zeros(num_vars)
    t_idx = np.arange(H)
    c[7 * t_idx + 2] = buy_price * dt
    c[7 * t_idx + 3] = -sell_price * dt
    c[7 * t_idx + 5] = 1000.0 * dt  # Slack penalty (Import violation)
    c[7 * t_idx + 6] = 1.0 * dt     # Curtailment penalty (Low cost to allow shedding excess solar)

    # 2. Equality Constraints (A_eq * x = b_eq)
    A_eq = sparse.lil_matrix((2 * H, num_vars))
    b_eq = np.zeros(2 * H)

    idx_ch = 7 * t_idx
    idx_dis = 7 * t_idx + 1
    idx_gi = 7 * t_idx + 2
    idx_ge = 7 * t_idx + 3
    idx_soc = 7 * t_idx + 4
    idx_slack = 7 * t_idx + 5
    idx_curtail = 7 * t_idx + 6
    
    row_pb = 2 * t_idx
    row_soc = 2 * t_idx + 1

    # Constraint 1: Power Balance (-P_ch + P_dis + P_imp - P_exp + P_slack - P_curtail = P_load - P_solar)
    A_eq[row_pb, idx_ch] = -1.0
    A_eq[row_pb, idx_dis] = 1.0
    A_eq[row_pb, idx_gi] = 1.0
    A_eq[row_pb, idx_ge] = -1.0
    A_eq[row_pb, idx_slack] = 1.0
    A_eq[row_pb, idx_curtail] = -1.0
    b_eq[row_pb] = load_forecast - solar_forecast

    # Constraint 2: SoC Dynamics
    factor_ch = -eta * dt / battery_capacity_kwh
    factor_dis = (1.0 / eta) * dt / battery_capacity_kwh
    
    A_eq[row_soc, idx_soc] = 1.0
    A_eq[row_soc, idx_ch] = factor_ch
    A_eq[row_soc, idx_dis] = factor_dis
    
    if H > 1:
        for t in range(1, H):
            A_eq[2 * t + 1, 7 * (t-1) + 4] = -1.0
            
    b_eq[row_soc[0]] = soc_init
    A_eq = A_eq.tocsr()

    # 3. Bounds
    bounds = []
    for _ in range(H):
        bounds.append((0, p_max_kw))      # P_charge
        bounds.append((0, p_max_kw))      # P_discharge
        bounds.append((0, grid_limit_kw)) # P_grid_import (HARD LIMIT)
        bounds.append((0, grid_limit_kw)) # P_grid_export
        bounds.append((0, 1.0))           # SoC
        bounds.append((0, 100.0))         # P_slack (Import violation)
        bounds.append((0, 100.0))         # P_curtail (Export violation / Solar shedding)

    # Solve using HiGHS
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if not res.success:
        return {"success": False, "message": res.message}
        
    x = res.x
    return {
        "success": True,
        "p_charge_kw": x[idx_ch],
        "p_discharge_kw": x[idx_dis],
        "p_grid_import_kw": x[idx_gi] + x[idx_slack],
        "p_grid_export_kw": x[idx_ge] + x[idx_curtail], # Total export including curtailed solar
        "soc": x[idx_soc],
        "cost_eur": (x[idx_ge] * sell_price - x[idx_gi] * buy_price - x[idx_slack] * 1000.0) * dt
    }

def rolling_mpc_optimize(
    buy_price: np.ndarray,
    sell_price: np.ndarray,
    load_forecast: np.ndarray,
    solar_forecast: np.ndarray,
    soc_init: float,
    horizon_steps: int = 96,
    battery_capacity_kwh: float = 16.0,
    p_max_kw: float = 8.0,
    grid_limit_kw: float = 6.0,
    eta: float = 0.94868,
    dt: float = 0.25
) -> Dict[str, Any]:
    """
    Vectorized Rolling Horizon MPC to prevent look-ahead bias.
    Returns the full dispatch schedule and trajectories.
    """
    T = len(load_forecast)
    current_soc = soc_init
    
    full_charge = []
    full_discharge = []
    full_soc = []
    full_costs = []
    
    for k in range(T):
        end_idx = min(k + horizon_steps, T)
        
        # Record current state BEFORE updating
        full_soc.append(float(current_soc))

        # Optimize for the future window
        res = optimize_battery(
            buy_price=buy_price[k:end_idx],
            sell_price=sell_price[k:end_idx],
            load_forecast=load_forecast[k:end_idx],
            solar_forecast=solar_forecast[k:end_idx],
            soc_init=current_soc,
            battery_capacity_kwh=battery_capacity_kwh,
            p_max_kw=p_max_kw,
            grid_limit_kw=grid_limit_kw,
            eta=eta,
            dt=dt
        )
        
        if res["success"]:
            # Apply only the FIRST step
            p_ch = res["p_charge_kw"][0]
            p_dis = res["p_discharge_kw"][0]
            cost = res["cost_eur"][0]
            # Update SoC for the NEXT step
            current_soc = res["soc"][0]
        else:
            # Emergency Fallback
            p_ch, p_dis = 0.0, 0.0
            net = load_forecast[k] - solar_forecast[k]
            cost = max(0, net) * buy_price[k] * dt - max(0, -net) * sell_price[k] * dt
            # SoC remains constant if optimization fails
            
        full_charge.append(float(p_ch))
        full_discharge.append(float(p_dis))
        full_costs.append(float(cost))
        
    return {
        "charge_schedule": full_charge,
        "discharge_schedule": full_discharge,
        "soc_trajectory": full_soc,
        "costs": full_costs,
        "total_cost": sum(full_costs)
    }

@router.post("/optimize")
async def run_optimization(request: OptimizationRequest):
    try:
        result = rolling_mpc_optimize(
            buy_price=np.array(request.buy_price),
            sell_price=np.array(request.sell_price),
            load_forecast=np.array(request.load_forecast),
            solar_forecast=np.array(request.solar_forecast),
            soc_init=request.soc_init,
            horizon_steps=request.horizon_steps,
            battery_capacity_kwh=request.battery_capacity_kwh,
            p_max_kw=request.p_max_kw,
            grid_limit_kw=request.grid_limit_kw,
            eta=request.eta,
            dt=request.dt
        )
        
        baseline = compute_baseline_cost(
            np.array(request.buy_price),
            np.array(request.sell_price),
            np.array(request.load_forecast),
            np.array(request.solar_forecast),
            request.dt
        )
        
        savings = baseline - result["total_cost"]
        result["baseline_cost"] = baseline
        result["savings_eur"] = savings
        result["savings_pct"] = (savings / baseline * 100) if baseline > 0 else 0
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
