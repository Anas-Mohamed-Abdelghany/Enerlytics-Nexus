"""
Upload Service — parses uploaded market data files server-side.

Supported formats:
  CSV  · TSV  · JSON  · XLSX  · XLS

Column auto-detection is case-insensitive and handles common aliases.
Supported columns:
  - timestamp (required)
  - close/price (required)
  - open, high, low, volume (optional)
  - battery_p, grid_p, load_p, pv_p (optional energy metrics)
  - selling_price_eur_kwh (optional price alias)
KPI calculations (volatility, period change) are done here so the
frontend only receives ready-to-use numbers.
"""

from __future__ import annotations

import io
import json
import math
from typing import List, Dict, Any, Optional

import pandas as pd

from models.schemas import OHLCVPoint, KPIResponse, UploadResponse
from core.services.integrity_service import validate_energy_integrity


# ─── Column alias map ────────────────────────────────────────────────────────
_COL_ALIASES: Dict[str, List[str]] = {
    "timestamp": ["timestamp", "time", "date", "datetime", "date_time",
                  "open_time", "period", "t"],
    "open":      ["open", "open_price", "o"],
    "high":      ["high", "high_price", "h"],
    "low":       ["low",  "low_price",  "l"],
    "close":     ["close", "close_price", "price", "last", "c", "p", "selling_price_eur_kwh", "selling_price", "price_eur_kwh", "price_kwh"],
    "volume":    ["volume", "vol", "v"],
    # Energy Aliases
    "battery_p": ["battery_p", "battery_power", "battery"],
    "grid_p":    ["grid_p", "grid_power", "grid"],
    "load_p":    ["load_p", "load_power", "load"],
    "pv_p":      ["pv_p", "pv_power", "pv", "solar"],
    "selling_price": ["selling_price_eur_kwh", "selling_price", "price_eur_kwh", "price_kwh"],
}


def _find_col(columns: List[str], field: str) -> Optional[str]:
    """Return the first matching column name for the given OHLCV field."""
    lc = [c.lower() for c in columns]
    for alias in _COL_ALIASES[field]:
        if alias in lc:
            return columns[lc.index(alias)]
    return None


def _normalise_df(df: pd.DataFrame) -> List[OHLCVPoint]:
    """
    Map a raw DataFrame (any column naming) to a list of OHLCVPoint objects.
    Raises ValueError with a clear message if required columns are missing.
    """
    cols = df.columns.tolist()

    ts_col    = _find_col(cols, "timestamp")
    close_col = _find_col(cols, "close")

    if ts_col is None:
        raise ValueError(
            "No date/timestamp column found. "
            "Expected one of: timestamp, time, date, datetime."
        )
    if close_col is None:
        raise ValueError(
            "No close/price column found. "
            "Expected one of: close, price, selling_price_eur_kwh, last."
        )

    open_col   = _find_col(cols, "open")
    high_col   = _find_col(cols, "high")
    low_col    = _find_col(cols, "low")
    volume_col = _find_col(cols, "volume")
    
    # Energy columns
    battery_col = _find_col(cols, "battery_p")
    grid_col    = _find_col(cols, "grid_p")
    load_col    = _find_col(cols, "load_p")
    pv_col      = _find_col(cols, "pv_p")
    sell_col    = _find_col(cols, "selling_price")

    # Parse timestamps
    df["_ts"] = pd.to_datetime(df[ts_col], infer_datetime_format=True, errors="coerce")
    df["_close"] = pd.to_numeric(df[close_col], errors="coerce")
    df = df.dropna(subset=["_ts", "_close"])
    df = df[df["_close"] > 0]
    df = df.sort_values("_ts").reset_index(drop=True)

    if df.empty:
        raise ValueError("No valid rows found after parsing. Check that the date and close columns contain valid data.")

    points: List[OHLCVPoint] = []
    for _, row in df.iterrows():
        close = float(row["_close"])
        open_  = float(pd.to_numeric(row[open_col],   errors="coerce")) if open_col   else close
        high   = float(pd.to_numeric(row[high_col],   errors="coerce")) if high_col   else close
        low    = float(pd.to_numeric(row[low_col],    errors="coerce")) if low_col    else close
        vol    = float(pd.to_numeric(row[volume_col], errors="coerce")) if volume_col else 0.0

        # Guard NaN → fallback to close
        if math.isnan(open_): open_ = close
        if math.isnan(high):  high  = close
        if math.isnan(low):   low   = close
        if math.isnan(vol):   vol   = 0.0

        ts_ms = int(row["_ts"].timestamp() * 1000)

        points.append(OHLCVPoint(
            timestamp=ts_ms,
            open=open_,
            high=high,
            low=low,
            close=close,
            volume=vol,
            battery_p=float(pd.to_numeric(row[battery_col], errors="coerce")) if battery_col else None,
            grid_p=float(pd.to_numeric(row[grid_col],       errors="coerce")) if grid_col    else None,
            load_p=float(pd.to_numeric(row[load_col],       errors="coerce")) if load_col    else None,
            pv_p=float(pd.to_numeric(row[pv_col],           errors="coerce")) if pv_col      else None,
            selling_price=float(pd.to_numeric(row[sell_col], errors="coerce")) if sell_col   else None,
        ))

    return points


def _compute_kpis(points: List[OHLCVPoint]) -> KPIResponse:
    closes = [p.close for p in points]
    current  = closes[-1]
    previous = closes[-2] if len(closes) > 1 else current
    change   = current - previous
    change_pct = 0.0 if previous == 0 else (change / previous) * 100

    max_c = max(closes)
    min_c = min(closes)
    volatility = 0.0 if min_c == 0 else ((max_c - min_c) / min_c) * 100

    return KPIResponse(
        current=round(current, 4),
        change_pct=round(change_pct, 4),
        is_positive=change >= 0,
        volatility=round(volatility, 4),
        points=len(points),
    )


# ─── Public entry point ──────────────────────────────────────────────────────

def parse_uploaded_file(filename: str, content: bytes) -> UploadResponse:
    """
    Parse raw file bytes and return a normalised UploadResponse.

    Args:
        filename: Original filename (used to detect format by extension).
        content:  Raw file bytes from the multipart upload.

    Returns:
        UploadResponse with series + KPIs.

    Raises:
        ValueError: If the file cannot be parsed or required columns are absent.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "csv"
    buf = io.BytesIO(content)

    try:
        if ext in ("xlsx", "xls"):
            df = pd.read_excel(buf, engine="openpyxl" if ext == "xlsx" else None)

        elif ext == "json":
            data = json.loads(content.decode("utf-8", errors="replace"))
            # Support root array OR { series/data/candles/ohlcv: [...] }
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                for key in ("series", "data", "candles", "ohlcv", "result", "bars"):
                    if key in data and isinstance(data[key], list):
                        df = pd.DataFrame(data[key])
                        break
                else:
                    raise ValueError(
                        "JSON root must be an array or an object with a "
                        "'series', 'data', 'candles', or 'ohlcv' key."
                    )
            else:
                raise ValueError("Unsupported JSON structure.")

        else:
            # CSV / TSV — auto-detect delimiter
            text = content.decode("utf-8", errors="replace")
            first_line = text.split("\n")[0]
            if "\t" in first_line:
                sep = "\t"
            elif ";" in first_line:
                sep = ";"
            else:
                sep = ","
            df = pd.read_csv(io.StringIO(text), sep=sep, low_memory=False)

    except (ValueError, KeyError):
        raise  # re-raise our own errors unchanged
    except Exception as e:
        raise ValueError(f"Could not read file: {e}") from e

    if df.empty:
        raise ValueError("The uploaded file appears to be empty.")

    # Strip leading/trailing whitespace from column names
    df.columns = [str(c).strip() for c in df.columns]

    series = _normalise_df(df)
    
    # Apply Data Integrity Layer (SoC Reconstruction & Anomaly Detection)
    series = validate_energy_integrity(series)
    
    kpis   = _compute_kpis(series)

    return UploadResponse(
        filename=filename,
        rows=len(series),
        series=series,
        kpis=kpis,
    )
