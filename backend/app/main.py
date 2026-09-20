"""
BharatVerse - Core Backend Application (FastAPI)
Autonomous Resource Intelligence & Orchestration Platform
Phase 4 Implementation
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure PROJECT_ROOT in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.database.seed_data import seed_database
from backend.app.api.resources import router as resources_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.anomalies import router as anomalies_router
from backend.app.api.simulation import router as simulation_router
from backend.app.api.optimization import router as optimization_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.approvals import router as approvals_router
from backend.app.api.feedback import router as feedback_router
from backend.app.api.graph_and_ml import graph_router, ml_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database is seeded on startup
    seed_database()
    yield

app = FastAPI(
    title="BharatVerse - Resource Intelligence Platform",
    description="Autonomous Resource Intelligence & Orchestration for Smart Campus Operations. Implements Sense, Understand, Predict, Simulate, Optimize, Explain, Act, and Learn loop.",
    version="4.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(resources_router)
app.include_router(predictions_router)
app.include_router(anomalies_router)
app.include_router(simulation_router)
app.include_router(optimization_router)
app.include_router(recommendations_router)
app.include_router(approvals_router)
app.include_router(feedback_router)
app.include_router(graph_router)
app.include_router(ml_router)

# Mount frontend static directory
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend", "public")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "platform": "BharatVerse Autonomous Resource Intelligence",
        "version": "4.0.0",
        "status": "ONLINE",
        "docs": "/docs",
        "loop": ["Sense", "Understand", "Predict", "Simulate", "Optimize", "Explain", "Act", "Learn"]
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "components": {
            "database": "sqlite_connected",
            "xgboost_demand_model": "loaded",
            "isolation_forest_anomaly": "loaded",
            "ortools_solver": "ready",
            "graph_engine": "active"
        }
    }
