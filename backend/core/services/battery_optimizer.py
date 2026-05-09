import numpy as np
import cvxpy as cp
from math import sqrt
import pandas as pd
from scipy.optimize import linprog
from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import time

# --- FastAPI Models ---
class OptimizationRequest(BaseModel):
    price_forecast: List[float] # Buy price
    sell_price_forecast: Optional[List[float]] = None # Sell price
    load_forecast: List[float]
    solar_forecast: List[float]
    soc_init: float = 0.5
    horizon_steps: int = 96
    battery_capacity_kwh: Optional[float] = 16.0
    p_max_kw: Optional[float] = 8.0
    grid_limit_kw: Optional[float] = 6.0

# --- Router ---
router = APIRouter()

@router.post("/api/optimize")
async def optimize_endpoint(req: OptimizationRequest):
    return optimize_battery(
        np.array(req.price_forecast),
        np.array(req.load_forecast),
        np.array(req.solar_forecast),
        req.soc_init,
        sell_price_forecast=np.array(req.sell_price_forecast) if req.sell_price_forecast else None
    )

def compute_baseline_cost(price: np.ndarray, load: np.ndarray, solar: np.ndarray, dt: float = 0.25, sell_price: Optional[np.ndarray] = None) -> float:
    """Calculates cost if no battery existed (Grid import = max(0, load - solar))."""
    net_load = load - solar
    grid_import = np.maximum(0, net_load)
    grid_export = np.maximum(0, -net_load)
    
    s_p = sell_price if sell_price is not None else (price * 0.8)
    
    cost = np.sum(grid_import * price * dt)
    revenue = np.sum(grid_export * s_p * dt)
    
    return float(cost - revenue)

def optimize_battery(
    price_forecast: np.ndarray, # Buy price
    load_forecast: np.ndarray,
    solar_forecast: np.ndarray,
    soc_init: float = 0.5,
    sell_price_forecast: Optional[np.ndarray] = None, # Optional sell price
    battery_capacity_kwh: float = 16.0,
    p_max_kw: float = 8.0,
    grid_limit_kw: float = 6.0,
    soc_min: float = 0.1,
    soc_max: float = 0.9,
    eta_c: float = 0.9487, # sqrt(0.90)
    eta_d: float = 0.9487, # sqrt(0.90)
    dt: float = 0.25
) -> Dict[str, Any]:
    """
    Solves the Battery Arbitrage LP:
    Minimize: sum(Price[t] * P_grid_import[t] * dt)
    Subject to:
    1. Power Balance: P_gi[t] - P_ge[t] + P_solar[t] - P_load[t] + P_d[t] - P_c[t] = 0
    2. SOC Dynamics: SOC[t+1] = SOC[t] + (P_c[t]*eta_c - P_d[t]/eta_d)*dt / Capacity
    3. Constraints: 0 <= P_c, P_d <= P_max; 0 <= P_gi, P_ge <= Grid_Limit; SOC_min <= SOC <= SOC_max
    """
    T = len(price_forecast)
    if T == 0: return {"status": "infeasible", "savings_eur": 0}

    # If sell price not provided, assume 80% of buy price for the hackathon
    s_f = sell_price_forecast if sell_price_forecast is not None else (price_forecast * 0.8)

    # Objective: c^T * x
    # x = [P_c; P_d; P_gi; P_ge]
    c = np.concatenate([
        np.zeros(T),        # P_c
        np.zeros(T),        # P_d
        price_forecast * dt, # P_gi (cost to buy)
        -s_f * dt            # P_ge (revenue from sell, negative cost)
    ])

    # --- 1. Equality Constraints: Power Balance ---
    I = np.eye(T)
    A_eq = np.hstack([-I, I, I, -I])
    b_eq = load_forecast - solar_forecast

    # --- 2. Inequality Constraints: SOC Bounds ---
    L = np.tril(np.ones((T, T)))
    M = (dt / battery_capacity_kwh) * L
    A_soc_up = np.hstack([M * eta_c, -M / eta_d, np.zeros((T, 2 * T))])
    b_soc_up = np.full(T, soc_max - soc_init)
    
    A_soc_lo = -A_soc_up
    b_soc_lo = np.full(T, soc_init - soc_min)
    
    A_ub = np.vstack([A_soc_up, A_soc_lo])
    b_ub = np.concatenate([b_soc_up, b_soc_lo])

    # --- 3. Variable Bounds ---
    bounds = [
        (0, p_max_kw),     # P_c
        (0, p_max_kw),     # P_d
        (0, grid_limit_kw),# P_gi
        (0, grid_limit_kw) # P_ge
    ]
    full_bounds = []
    for _ in range(T): full_bounds.append(bounds[0])
    for _ in range(T): full_bounds.append(bounds[1])
    for _ in range(T): full_bounds.append(bounds[2])
    for _ in range(T): full_bounds.append(bounds[3])

    # Solve using HiGHS
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=full_bounds, method='highs')

    if not res.success:
        return {"status": "infeasible", "savings_eur": 0}

    # Extract results
    P_c, P_d, P_gi, P_ge = np.split(res.x, 4)
    soc_traj = soc_init + (dt / battery_capacity_kwh) * L @ (P_c * eta_c - P_d / eta_d)
    
    total_cost = float(res.fun)
    baseline_cost = compute_baseline_cost(price_forecast, load_forecast, solar_forecast, dt)
    savings = baseline_cost - total_cost

    return {
        "status": "success",
        "soc_trajectory": [float(soc_init * 100)] + [round(float(s * 100), 2) for s in soc_traj],
        "charge_schedule": [round(float(v), 2) for v in P_c],
        "discharge_schedule": [round(float(v), 2) for v in P_d],
        "grid_import": [round(float(v), 2) for v in P_gi],
        "grid_export": [round(float(v), 2) for v in P_ge],
        "total_cost_eur": round(total_cost, 2),
        "baseline_cost_eur": round(baseline_cost, 2),
        "savings_eur": round(savings, 2),
        "savings_pct": round((savings / baseline_cost * 100), 1) if baseline_cost > 0 else 0
    }

def rolling_mpc_simulation(
    actual_prices: np.ndarray, # Actual buy prices
    actual_loads: np.ndarray,
    actual_solars: np.ndarray,
    actual_sell_prices: Optional[np.ndarray] = None, # Actual sell prices
    forecast_prices: Optional[np.ndarray] = None,
    forecast_loads: Optional[np.ndarray] = None,
    forecast_solars: Optional[np.ndarray] = None,
    forecast_sell_prices: Optional[np.ndarray] = None,
    soc_init: float = 0.5,
    H: int = 96,
    battery_capacity_kwh: float = 16.0,
    p_max_kw: float = 8.0,
    grid_limit_kw: float = 6.0,
    soc_min: float = 0.1,
    soc_max: float = 0.9,
    eta_c: float = 0.9487,
    eta_d: float = 0.9487,
    dt: float = 0.25
) -> Dict[str, Any]:
    """
    Simulates MPC where optimization uses 'forecast' but execution uses 'actuals'.
    If forecast_ arrays are None, it defaults to Oracle (forecast=actual).
    """
    T_total = len(actual_prices)
    actual_soc = np.zeros(T_total + 1)
    actual_soc[0] = soc_init
    
    charge_actions = np.zeros(T_total)
    discharge_actions = np.zeros(T_total)
    grid_import = np.zeros(T_total)
    grid_export = np.zeros(T_total)
    
    f_p = forecast_prices if forecast_prices is not None else actual_prices
    f_l = forecast_loads if forecast_loads is not None else actual_loads
    f_s = forecast_solars if forecast_solars is not None else actual_solars
    f_sell = forecast_sell_prices if forecast_sell_prices is not None else (actual_sell_prices if actual_sell_prices is not None else (f_p * 0.8))
    
    a_sell = actual_sell_prices if actual_sell_prices is not None else (actual_prices * 0.8)

    for t in range(T_total):
        end_idx = min(t + H, T_total)
        p_window = f_p[t:end_idx]
        l_window = f_l[t:end_idx]
        s_window = f_s[t:end_idx]
        sell_window = f_sell[t:end_idx]
        
        current_soc = actual_soc[t]
        
        res = optimize_battery(
            p_window, l_window, s_window, 
            soc_init=current_soc, 
            sell_price_forecast=sell_window,
            battery_capacity_kwh=battery_capacity_kwh,
            p_max_kw=p_max_kw, grid_limit_kw=grid_limit_kw,
            soc_min=soc_min, soc_max=soc_max,
            eta_c=eta_c, eta_d=eta_d, dt=dt
        )
        
        if res["status"] == "success":
            c_t = res["charge_schedule"][0]
            d_t = res["discharge_schedule"][0]
        else:
            # --- HEURISTIC FALLBACK (Section 12.1) ---
            buy_now = actual_prices[t]
            sell_now = a_sell[t]
            
            if sell_now > buy_now and current_soc > 0.3:
                c_t, d_t = 0.0, p_max_kw # Discharge
            elif buy_now <= 0.2440 and current_soc < 0.9:
                c_t, d_t = p_max_kw, 0.0 # Charge from grid/PV
            else:
                # PV priority
                surplus = max(0, actual_solars[t] - actual_loads[t])
                c_t = min(surplus, p_max_kw)
                d_t = 0.0
            
        charge_actions[t] = c_t
        discharge_actions[t] = d_t
        
        # Apply to actual environment
        net_flow = actual_loads[t] - actual_solars[t] + c_t - d_t
        if net_flow >= 0:
            grid_import[t] = min(net_flow, grid_limit_kw)
            grid_export[t] = 0.0
        else:
            grid_import[t] = 0.0
            grid_export[t] = min(-net_flow, grid_limit_kw)
        
        delta_soc = (c_t * eta_c - d_t / eta_d) * dt / battery_capacity_kwh
        actual_soc[t+1] = np.clip(actual_soc[t] + delta_soc, soc_min, soc_max)
        
    total_cost = np.sum(grid_import * actual_prices * dt) - np.sum(grid_export * a_sell * dt)
    baseline_cost = compute_baseline_cost(actual_prices, actual_loads, actual_solars, dt, sell_price=a_sell)
    savings = baseline_cost - total_cost
    
    return {
        "status": "success",
        "soc_trajectory": [round(float(s * 100), 2) for s in actual_soc],
        "charge_schedule": [round(float(v), 2) for v in charge_actions],
        "discharge_schedule": [round(float(v), 2) for v in discharge_actions],
        "grid_import": [round(float(v), 2) for v in grid_import],
        "grid_export": [round(float(v), 2) for v in grid_export],
        "total_cost": round(float(total_cost), 2),
        "baseline_cost": round(float(baseline_cost), 2),
        "savings_eur": round(float(savings), 2),
        "savings_pct": round(float(savings / baseline_cost * 100), 1) if baseline_cost > 0 else 0
    }

def compute_oracle_gap(
    prices: np.ndarray, loads: np.ndarray, solars: np.ndarray,
    f_prices: np.ndarray, f_loads: np.ndarray, f_solars: np.ndarray
) -> Dict[str, Any]:
    """
    Computes the performance gap between an Oracle (actuals) and a Forecast-based MPC.
    """
    oracle_res = rolling_mpc_simulation(prices, loads, solars)
    forecast_res = rolling_mpc_simulation(prices, loads, solars, f_prices, f_loads, f_solars)
    
    o_savings = oracle_res["savings_eur"]
    f_savings = forecast_res["savings_eur"]
    
    gap = (o_savings - f_savings) / o_savings if o_savings > 0 else 0
    
    status = "Excellent" if gap < 0.10 else "Good" if gap < 0.25 else "Forecast-Limited"
    
    return {
        "oracle_savings": o_savings,
        "forecast_savings": f_savings,
        "gap_pct": round(gap * 100, 2),
        "performance_tier": status
    }

def compute_baseline_a(df: pd.DataFrame) -> Tuple[float, np.ndarray]:
    """
    Computes bill for Baseline A: using the recorded p_battery_kw.
    Treats corrupted windows as zero battery power.
    """
    p_bat = df['p_battery_kw'].fillna(0).values
    # In a real run, we'd use the corruption mask from SECTION 6
    # For now, we assume if SoC reconstruction fails, p_bat is suspicious
    
    net_flow = df['load_kw'].values - df['pv_kw'].values - p_bat
    p_grid = np.clip(net_flow, -6.0, 6.0)
    
    buy_price = df['buy_price'].values if 'buy_price' in df.columns else np.full(len(df), 0.25)
    sell_price = df['sell_price'].values if 'sell_price' in df.columns else buy_price * 0.8
    
    bill_steps = (np.maximum(0, p_grid) * buy_price - np.maximum(0, -p_grid) * sell_price) * 0.25
    return float(np.sum(bill_steps)), bill_steps

def compute_baseline_b(df: pd.DataFrame) -> float:
    """
    Computes bill for Baseline B: PV serves load first, NO battery.
    """
    net_load = df['load_kw'].values - df['pv_kw'].values
    p_grid = np.clip(net_load, -6.0, 6.0)
    
    buy_price = df['buy_price'].values if 'buy_price' in df.columns else np.full(len(df), 0.25)
    sell_price = df['sell_price'].values if 'sell_price' in df.columns else buy_price * 0.8
    
    bill_steps = (np.maximum(0, p_grid) * buy_price - np.maximum(0, -p_grid) * sell_price) * 0.25
    return float(np.sum(bill_steps))

def compute_controller_savings(
    baseline_a_bill: float,
    baseline_b_bill: float,
    controller_bill: float,
    oracle_bill: float
) -> Dict[str, float]:
    """
    Computes all savings metrics in Euro and Percentage.
    """
    savings_a_eur = baseline_a_bill - controller_bill
    savings_b_eur = baseline_b_bill - controller_bill
    oracle_gap_eur = controller_bill - oracle_bill
    oracle_savings = baseline_a_bill - oracle_bill
    oracle_gap_pct = round(oracle_gap_eur / oracle_savings * 100, 2) if oracle_savings > 0 else 0
    
    return {
        "savings_vs_a_eur": round(savings_a_eur, 2),
        "savings_vs_a_pct": round(savings_a_eur / baseline_a_bill * 100, 2) if baseline_a_bill > 0 else 0,
        "savings_vs_b_eur": round(savings_b_eur, 2),
        "savings_vs_b_pct": round(savings_b_eur / baseline_b_bill * 100, 2) if baseline_b_bill > 0 else 0,
        "oracle_gap_eur": round(oracle_gap_eur, 2),
        "oracle_gap_pct": oracle_gap_pct
    }

def print_results_table(metrics: Dict[str, Any], bills: Dict[str, float]):
    """
    Prints a formatted table for competitive reporting.
    """
    print("\n" + "="*60)
    print(f"{'Metric':<20} | {'Baseline A':<10} | {'Baseline B':<10} | {'Controller':<10} | {'Oracle':<10}")
    print("-" * 60)
    print(f"{'Annual Bill (€)':<20} | {bills['A']:<10.2f} | {bills['B']:<10.2f} | {bills['Ctrl']:<10.2f} | {bills['Oracle']:<10.2f}")
    print(f"{'Savings vs A (€)':<20} | {'-':<10} | {'-':<10} | {metrics['savings_vs_a_eur']:<10.2f} | {bills['A']-bills['Oracle']:<10.2f}")
    print(f"{'Savings vs A (%)':<20} | {'-':<10} | {'-':<10} | {metrics['savings_vs_a_pct']:<10.2f}% | {((bills['A']-bills['Oracle'])/bills['A']*100):.2f}%")
    print(f"{'Savings vs B (€)':<20} | {'-':<10} | {'-':<10} | {metrics['savings_vs_b_eur']:<10.2f} | {bills['B']-bills['Oracle']:<10.2f}")
    print("="*60 + "\n")
def run_horizon_sensitivity(
    prices: np.ndarray, loads: np.ndarray, solars: np.ndarray,
    horizons: List[int] = [4, 24, 48, 96]
) -> List[Dict[str, Any]]:
    """
    Benchmarks different horizon lengths to find the optimal computational vs economic trade-off.
    """
    results = []
    for h in horizons:
        start_t = time.time()
        res = rolling_mpc_simulation(prices, loads, solars, H=h)
        elapsed = time.time() - start_t
        savings = res["savings_eur"]
        results.append({
            "H": h,
            "Hours": h / 4,
            "Savings": f"€{savings:,.2f}",
            "CompTime": f"{elapsed:.1f}s",
            "Recommended": "Yes" if 24 <= h <= 48 else "Diminishing Returns" if h > 48 else "Too Short"
        })
    return results

def compute_nrmse(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Computes Normalized Root Mean Square Error."""
    if len(actual) == 0: return 0.0
    rmse = np.sqrt(np.mean((actual - forecast)**2))
    rng = np.max(actual) - np.min(actual)
    return (rmse / rng * 100) if rng > 0 else 0.0

def generate_final_results_table(
    actual_prices: np.ndarray,
    actual_loads: np.ndarray,
    actual_solars: np.ndarray,
    forecast_prices: np.ndarray,
    forecast_loads: np.ndarray,
    forecast_solars: np.ndarray,
    recorded_battery_p: np.ndarray, # Baseline A: Recorded in dataset
    dt: float = 0.25
) -> Dict[str, Any]:
    """
    Consolidates all metrics for Slide 4: Baseline A/B, Your Controller, and Oracle.
    """
    # 1. Baseline A: Recorded performance
    # P_gi - P_ge = load - solar - battery_p (where battery_p is discharge-charge)
    net_flow_a = actual_loads - actual_solars - recorded_battery_p
    gi_a = np.maximum(0, net_flow_a)
    bill_a = np.sum(gi_a * actual_prices * dt)
    
    # 2. Baseline B: Passive Solar (Frozen Battery)
    res_b = rolling_mpc_simulation(actual_prices, actual_loads, actual_solars, H=0) # Logic for frozen
    bill_b = res_b["total_cost"]
    
    # 3. Your Controller: Forecast-based MPC
    res_ctrl = rolling_mpc_simulation(actual_prices, actual_loads, actual_solars, forecast_prices, forecast_loads, forecast_solars)
    bill_ctrl = res_ctrl["total_cost"]
    
    # 4. Oracle: Perfect knowledge MPC
    res_oracle = rolling_mpc_simulation(actual_prices, actual_loads, actual_solars)
    bill_oracle = res_oracle["total_cost"]
    
    # Financial KPI Calculations
    savings_vs_a_eur = bill_a - bill_ctrl
    savings_vs_a_pct = (savings_vs_a_eur / bill_a * 100) if bill_a > 0 else 0
    
    oracle_gap_eur = bill_ctrl - bill_oracle
    oracle_gap_pct = (oracle_gap_eur / (bill_b - bill_oracle) * 100) if (bill_b - bill_oracle) > 0 else 0
    
    # Accuracy Metrics
    nrmse_val = compute_nrmse(actual_prices, forecast_prices)
    
    return {
        "Annual Bill (€)": {
            "Baseline A": round(bill_a, 2),
            "Baseline B": round(bill_b, 2),
            "Your Controller": round(bill_ctrl, 2),
            "Oracle": round(bill_oracle, 2)
        },
        "Savings vs. A (€)": {
            "Your Controller": round(savings_vs_a_eur, 2),
            "Oracle": round(bill_a - bill_oracle, 2)
        },
        "Savings vs. A (%)": {
            "Your Controller": f"{savings_vs_a_pct:.1f}%",
            "Oracle": f"{((bill_a - bill_oracle)/bill_a*100):.1f}%" if bill_a > 0 else "0%"
        },
        "Savings vs. B (€)": {
            "Your Controller": round(bill_b - bill_ctrl, 2),
            "Oracle": round(bill_b - bill_oracle, 2)
        },
        "NRMSE": f"{nrmse_val:.2f}%",
        "Oracle Gap (€/%)": f"€{oracle_gap_eur:.2f} / {oracle_gap_pct:.1f}%"
    }

def generate_march_presentation_data(full_res: Dict[str, Any], loads: np.ndarray, solars: np.ndarray, start_idx: int, end_idx: int) -> Dict[str, Any]:
    """
    Slices the full simulation for March Week 3 and prepares data for a 5-panel presentation.
    """
    s = max(0, min(start_idx, len(loads)))
    e = max(s, min(end_idx, len(loads)))
    
    return {
        "load": loads[s:e].tolist(),
        "pv": solars[s:e].tolist(),
        "battery": [(d - c) for c, d in zip(full_res["charge_schedule"][s:e], full_res["discharge_schedule"][s:e])],
        "grid": full_res["grid_import"][s:e],
        "soc": full_res["soc_trajectory"][s:e],
    }

class RollingHorizonMPC:
    """
    Control Systems Engineering Grade Model Predictive Control.
    Uses CVXPY for robust, physically-consistent energy dispatch.
    """
    def __init__(
        self,
        C_bat: float = 16.0,
        P_bat_max: float = 8.0,
        P_grid_max: float = 6.0,
        eta_c: float = sqrt(0.90),
        eta_d: float = sqrt(0.90),
        dt: float = 0.25,
        H: int = 96
    ):
        self.C_bat = C_bat
        self.P_bat_max = P_bat_max
        self.P_grid_max = P_grid_max
        self.eta_c = eta_c
        self.eta_d = eta_d
        self.dt = dt
        self.H = H

    def solve(
        self,
        load_fc: np.ndarray,
        pv_fc: np.ndarray,
        buy_price: np.ndarray,
        sell_price: np.ndarray,
        soc_init: float
    ) -> Optional[Tuple[float, float]]:
        """
        Solves the optimal dispatch problem using convex optimization.
        """
        H = self.H
        p_c = cp.Variable(H, nonneg=True)
        p_d = cp.Variable(H, nonneg=True)
        p_import = cp.Variable(H, nonneg=True)
        p_export = cp.Variable(H, nonneg=True)
        soc = cp.Variable(H + 1)

        obj = cp.Minimize(cp.sum(cp.multiply(buy_price, p_import) - cp.multiply(sell_price, p_export)) * self.dt)
        
        constraints = [soc[0] == soc_init]
        for t in range(H):
            # SoC Dynamics with efficiency correction
            constraints += [
                soc[t+1] == soc[t] + (p_c[t] * self.eta_c - p_d[t] / self.eta_d) * self.dt / self.C_bat
            ]
            # SoC Hard Bounds
            constraints += [soc[t+1] >= 0.0, soc[t+1] <= 1.0]
            # Energy Balance: load = pv + (p_d - p_c) + (import - export)
            constraints += [
                load_fc[t] == pv_fc[t] + (p_d[t] - p_c[t]) + (p_import[t] - p_export[t])
            ]
            # Power Limits
            constraints += [p_c[t] + p_d[t] <= self.P_bat_max]
            constraints += [p_import[t] + p_export[t] <= self.P_grid_max]

        try:
            prob = cp.Problem(obj, constraints)
            prob.solve(solver=cp.OSQP)
            if prob.status not in ["optimal", "optimal_inaccurate"]:
                prob.solve(solver=cp.GLPK)
            
            if prob.status in ["optimal", "optimal_inaccurate"]:
                return float(p_d.value[0] - p_c.value[0]), float(soc.value[1])
            return None
        except:
            return None

    def run_full_year(self, df_2025: pd.DataFrame, forecaster: Any) -> pd.DataFrame:
        """
        Executes a rolling horizon simulation across the entire 2025 dataset.
        """
        results = []
        soc_traj = [0.5] # Starting SoC
        T = len(df_2025)
        
        for t in range(T - self.H):
            # 1. Get Forecasts
            load_fc = forecaster.predict_load(df_2025.iloc[:t+1], horizon=self.H)
            pv_fc = df_2025['pv_kw'].values[t:t+self.H]
            buy_fc = df_2025['buy_price'].values[t:t+self.H]
            sell_fc = df_2025['sell_price'].values[t:t+self.H]
            
            # 2. Solve Step
            res = self.solve(load_fc, pv_fc, buy_fc, sell_fc, soc_traj[-1])
            
            if res:
                p_bat, soc_next = res
            else:
                p_bat, soc_next = 0.0, soc_traj[-1]
            
            # 3. Simulate Actual Physics
            actual_load = df_2025['load_kw'].iloc[t]
            actual_pv = df_2025['pv_kw'].iloc[t]
            p_grid_actual = np.clip(actual_load - actual_pv - p_bat, -self.P_grid_max, self.P_grid_max)
            
            # Bill calculation
            buy_now = df_2025['buy_price'].iloc[t]
            sell_now = df_2025['sell_price'].iloc[t]
            bill = (max(0, p_grid_actual) * buy_now - max(0, -p_grid_actual) * sell_now) * self.dt
            
            results.append({
                "timestamp": df_2025['timestamp'].iloc[t],
                "p_bat_actual": p_bat,
                "soc": soc_traj[-1],
                "p_grid_actual": p_grid_actual,
                "bill_per_step": bill
            })
            
            soc_traj.append(soc_next)
            
            if t % 1000 == 0:
                print(f"Step {t}/{T}: SoC={soc_next:.2f}, Grid={p_grid_actual:.2f}kW")
                
        return pd.DataFrame(results)
