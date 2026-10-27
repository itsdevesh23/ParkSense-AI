"""
backend/main.py
FastAPI Application Entry Point for ParkSense AI.
Federated Multi-Lot Smart Parking Forecasting Platform on Birmingham IoT Streams.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes.auth_routes import router as auth_router
from backend.routes.facility_routes import router as facility_router
from backend.routes.owner_routes import router as owner_router
from backend.routes.admin_routes import router as admin_router
from backend.routes.report_routes import router as report_router

app = FastAPI(
    title="ParkSense AI - Smart Parking Forecasting Platform",
    description="Full-stack federated multi-lot parking forecasting API based on Attention-LSTM IoT streams",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for local development and production frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(auth_router)
app.include_router(facility_router)
app.include_router(owner_router)
app.include_router(admin_router)
app.include_router(report_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ParkSense AI Backend",
        "version": "2.0.0",
        "active_dataset": "Birmingham Municipal IoT Stream (30 Facilities)",
        "models_loaded": ["Personalized FedAvg", "Global FedAvg", "Centralized Attention-LSTM", "XGBoost", "ARIMA"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
