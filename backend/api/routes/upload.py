"""
Upload route — accepts a raw market data file (CSV/TSV/JSON/XLSX/XLS),
parses it server-side, and returns normalised OHLCV data + KPIs.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from core.services.upload_service import parse_uploaded_file
from models.schemas import UploadResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {"csv", "tsv", "json", "xlsx", "xls"}
MAX_FILE_SIZE_MB   = 50


@router.post("/", response_model=UploadResponse, summary="Upload and parse a market data file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV / TSV / JSON / XLSX / XLS file containing market OHLCV data.

    The backend will:
    - Auto-detect the file format and delimiter.
    - Map common column name variants to open / high / low / close / volume.
    - Compute KPIs (current price, period change, volatility, row count).
    - Return a fully normalised series ready for the chart.

    Required columns (case-insensitive): **date/timestamp** and **close/price**.
    Optional columns: open, high, low, volume.
    """
    # ── Validate extension ──────────────────────────────────────────────────
    filename = file.filename or "upload"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # ── Read raw bytes ──────────────────────────────────────────────────────
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Maximum allowed: {MAX_FILE_SIZE_MB} MB.",
        )

    # ── Parse & normalise ───────────────────────────────────────────────────
    try:
        result = parse_uploaded_file(filename, content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return result
