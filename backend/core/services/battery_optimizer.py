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
    cost = (grid_import * buy_price - grid_export * sell_price) * dt
    return float(np.sum(cost))

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
    Vectorized Linear Programming formulation for Battery Optimization.
    Decision Variables: [P_charge, P_discharge, P_grid_import, P_grid_export, SoC] (interleaved)
    """
    H = len(load_forecast)
    if H == 0:
        return {"success": False, "message": "Empty forecast"}

    # Total variables = 5 per step
    # x = [P_ch[0], P_dis[0], P_imp[0], P_exp[0], SOC[0], ... P_ch[H-1], ...]
    num_vars = 5 * H
    
    # 1. Objective: Minimize (P_imp * buy_price - P_exp * sell_price) * dt
    c = np.zeros(num_vars)
    t_idx = np.arange(H)
    c[5 * t_idx + 2] = buy_price * dt    # Import index
    c[5 * t_idx + 3] = -sell_price * dt   # Export index (revenue is negative cost)

    # 2. Equality Constraints (A_eq * x = b_eq)
    # 2 rows per step: Power Balance and SoC Dynamics
    A_eq = np.zeros((2 * H, num_vars))
    b_eq = np.zeros(2 * H)

    idx_ch = 5 * t_idx
    idx_dis = 5 * t_idx + 1
    idx_gi = 5 * t_idx + 2
    idx_ge = 5 * t_idx + 3
    idx_soc = 5 * t_idx + 4
    
    row_pb = 2 * t_idx
    row_soc = 2 * t_idx + 1

    # Constraint 1: Power Balance
    # -P_ch + P_dis + P_imp - P_exp = P_load - P_solar
    A_eq[row_pb, idx_ch] = -1.0
    A_eq[row_pb, idx_dis] = 1.0
    A_eq[row_pb, idx_gi] = 1.0
    A_eq[row_pb, idx_ge] = -1.0
    b_eq[row_pb] = load_forecast - solar_forecast

    # Constraint 2: SoC Dynamics
    # SoC[t] - SoC[t-1] - P_ch[t]*eta*(dt/Cap) + P_dis[t]*(1/eta)*(dt/Cap) = 0
    factor_ch = -eta * dt / battery_capacity_kwh
    factor_dis = (1.0 / eta) * dt / battery_capacity_kwh
    
    A_eq[row_soc, idx_soc] = 1.0
    A_eq[row_soc, idx_ch] = factor_ch
    A_eq[row_soc, idx_dis] = factor_dis
    
    # Link SoC[t] with SoC[t-1]
    if H > 1:
        A_eq[row_soc[1:], idx_soc[:-1]] = -1.0
        
    # Boundary: SoC at t=0 depends on initial SoC
    b_eq[row_soc[0]] = soc_init

    # 3. Bounds
    bounds = []
    for _ in range(H):
        bounds.append((0, p_max_kw))      # P_charge
        bounds.append((0, p_max_kw))      # P_discharge
        bounds.append((0, grid_limit_kw)) # P_grid_import
        bounds.append((0, grid_limit_kw)) # P_grid_export
        bounds.append((0, 1.0))           # SoC

    # Solve using HiGHS
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if not res.success:
        return {"success": False, "message": res.message}
        
    x = res.x
    return {
        "success": True,
        "p_charge_kw": x[idx_ch],
        "p_discharge_kw": x[idx_dis],
        "p_grid_import_kw": x[idx_gi],
        "p_grid_export_kw": x[idx_ge],
        "soc": x[idx_soc],
        "cost_eur": (x[idx_gi] * buy_price - x[idx_ge] * sell_price) * dt
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
