import numpy as np
from typing import List, Dict, Any

def simulate_soc_timeline(
    prices: List[float],
    capacity_kwh: float = 100.0,
    max_power_kw: float = 50.0,
    efficiency: float = 0.9,
    initial_soc_pct: float = 0.5
) -> Dict[str, Any]:
    """
    Simulates State-of-Charge (SOC) based on a simple arbitrage strategy.
    
    Strategy: 
    - Charge when price is in the lower 30th percentile.
    - Discharge when price is in the upper 30th percentile.
    - Idle otherwise.
    """
    if not prices:
        return {"soc_points": [], "actions": [], "revenue": 0.0}

    soc = initial_soc_pct # 0.0 to 1.0
    soc_points = [float(soc * 100)]
    actions = []
    total_revenue = 0.0
    
    # Baseline comparison: Assume a constant 50kW facility load
    base_load_kw = 50.0
    baseline_grid_cost = 0.0
    optimized_grid_cost = 0.0
    
    p_low = np.percentile(prices, 30)
    p_high = np.percentile(prices, 70)
    
    # Assume 1-hour intervals for simplicity in this simulation
    for price in prices:
        action = "IDLE"
        power_used = 0.0
        
        # 1. Calculate Baseline (Do-nothing: buy all from grid)
        baseline_grid_cost += (base_load_kw * price)
        
        # 2. Strategy Logic
        if price <= p_low and soc < 1.0:
            energy_to_full = (1.0 - soc) * capacity_kwh / efficiency
            charge_energy = min(max_power_kw, energy_to_full)
            soc += (charge_energy * efficiency) / capacity_kwh
            total_revenue -= (charge_energy * price)
            action = "CHARGE"
            power_used = charge_energy
        elif price >= p_high and soc > 0.0:
            energy_to_empty = soc * capacity_kwh
            discharge_energy = min(max_power_kw, energy_to_empty)
            soc -= (discharge_energy / capacity_kwh)
            total_revenue += (discharge_energy * price * efficiency)
            action = "DISCHARGE"
            power_used = discharge_energy
            
        # 3. Calculate Optimized Grid Cost (Base Load + Battery Actions)
        net_grid_draw = base_load_kw + (power_used if action == "CHARGE" else -power_used if action == "DISCHARGE" else 0)
        optimized_grid_cost += (max(0, net_grid_draw) * price)
        
        soc_points.append(round(float(soc * 100), 2))
        actions.append({
            "type": action,
            "power_kw": round(float(power_used), 2),
            "price": round(float(price), 2)
        })
        
    savings = baseline_grid_cost - optimized_grid_cost
    savings_pct = (savings / baseline_grid_cost * 100) if baseline_grid_cost > 0 else 0
        
    return {
        "soc_points": soc_points,
        "actions": actions,
        "total_revenue": round(float(total_revenue), 2),
        "final_soc": round(float(soc * 100), 2),
        "baseline_cost": round(float(baseline_grid_cost), 2),
        "optimized_cost": round(float(optimized_grid_cost), 2),
        "savings": round(float(savings), 2),
        "savings_pct": round(float(savings_pct), 1)
    }
