"""
FastAPI entry point for the Enerlytics AI backend.

- CORS is fully enabled for local React development (http://localhost:5173).
- Routers for market data, forecasting, and simulator are registered.
- The OpenAPI documentation is automatically available at /docs and /redoc.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers (will be defined in backend/app/api/routes/)
from api.routes import market, forecast, simulator, upload, resample, strategy, chart, utilities

app = FastAPI(
    title="Enerlytics AI Backend",
    version="0.1.0",
    description="FastAPI service exposing market data, price forecasts, and trading‑strategy simulation endpoints."
)

# CORS configuration – allow the React dev server to call the API.
origins = [
    "http://localhost:5173",          # Vite dev server
    "http://localhost:5174",          # Vite fallback port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],              # Permit GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],              # Permit custom headers (Auth, etc.)
)

# Include routers
app.include_router(market.router,   prefix="/api/market",    tags=["Market"])
app.include_router(forecast.router, prefix="/api/forecast",  tags=["Forecast"])
app.include_router(simulator.router,prefix="/api/simulate",  tags=["Simulator"])
app.include_router(upload.router,   prefix="/api/upload",    tags=["Upload"])
app.include_router(resample.router, prefix="/api/resample",  tags=["Resample"])
app.include_router(strategy.router, prefix="/api/strategy",  tags=["Strategy"])
app.include_router(chart.router,    prefix="/api/chart",     tags=["Chart"])
app.include_router(utilities.router,prefix="/api/utils",     tags=["Utilities"])

@app.get("/", tags=["Health"])
async def health_check() -> dict:
    """
    Basic health check endpoint.
    Returns a static JSON confirming the service is running.
    """
    return {"status": "ok", "message": "Enerlytics AI backend is alive"}
