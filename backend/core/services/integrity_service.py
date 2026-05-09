"""
Integrity Service — Validates and reconstructs energy data for engineering rigor.
Calculates SoC based on battery power and detects balance anomalies.
"""

from typing import List, Optional
from models.schemas import OHLCVPoint
import math

# Constants from user requirements
ETA_INV_SQRT = 0.9487  # sqrt(0.90)
DELTA_T = 0.25         # 15 minutes (0.25 hours)
C_BAT = 16.0           # Default capacity in kWh (can be adjusted if needed)

def validate_energy_integrity(points: List[OHLCVPoint]) -> List[OHLCVPoint]:
    """
    Step-by-step reconstruction of SoC and balance verification.
    Mutates points in-place to add soc_reconstructed and integrity_flags.
    """
    if not points:
        return points

    # Assume starting SoC is 0.5 if not known, or 0.0 if first point
    current_soc = 0.5 
    
    for i, p in enumerate(points):
        # 1. Check Energy Balance: load = PV + P_battery + P_grid
        # Note: In our system, battery_p < 0 is charging, > 0 is discharging
        # User Equation: load = PV + P_battery + P_grid
        # This implies P_battery > 0 means discharging (contributing to load)
        # and P_battery < 0 means charging (consuming PV/grid)
        
        if p.load_p is not None and p.pv_p is not None and p.battery_p is not None and p.grid_p is not None:
            # Re-verify the balance equation: balance = PV + Grid + Battery - Load
            balance = p.pv_p + p.grid_p + p.battery_p - p.load_p
            if abs(balance) > 0.5: # 0.5 kW tolerance
                p.integrity_flags.append(f"ENERGY_BALANCE_ANOMALY: {balance:.2f}kW")

        # 2. Reconstruct SoC
        if p.battery_p is not None:
            # charging adds |P_battery| × 0.9487 × 0.25 to SoC
            # discharging removes P_battery × (1/0.9487) × 0.25 from SoC
            
            p_bat = p.battery_p
            if p_bat < 0: # Charging
                delta_kwh = abs(p_bat) * ETA_INV_SQRT * DELTA_T
            else: # Discharging
                delta_kwh = - (p_bat * (1.0 / ETA_INV_SQRT) * DELTA_T)
            
            # Update SoC
            delta_soc = delta_kwh / C_BAT
            current_soc += delta_soc
            
            # Clamp and flag anomalies
            if current_soc > 1.001:
                p.integrity_flags.append(f"SOC_OVERFLOW: {current_soc:.2f}")
                # current_soc = 1.0 # Optional: clamp it
            elif current_soc < -0.001:
                p.integrity_flags.append(f"SOC_UNDERFLOW: {current_soc:.2f}")
                # current_soc = 0.0 # Optional: clamp it
            
            p.soc_reconstructed = round(max(0.0, min(1.0, current_soc)), 4)
            
            # Anomaly Detection: Conserve logic
            # If P_battery is suspiciously high or SoC is broken, flag it
            if abs(p_bat) > 20: # Unusual spike
                p.integrity_flags.append("SUSPICIOUS_POWER_SPIKE")

    return points
