# 🇮🇳 BharatVerse — Autonomous Resource Intelligence & Orchestration

> **A configurable, closed-loop resource intelligence and orchestration platform that converts heterogeneous operational data into predicted, simulated, constraint-aware and explainable resource decisions, and safely executes approved actions with feedback.**

---

## 🚀 Quick Start

### 1. Environment Setup
The system uses Python 3.11 with FastAPI, XGBoost, Scikit-Learn, Google OR-Tools, and NetworkX.
```bash
# Activate virtual environment
source .venv/bin/activate
```

### 2. How to Train the Models
BharatVerse features two machine learning models:
1. **XGBoost Regressor**: Predicts hourly resource demand and room occupancy.
2. **Isolation Forest**: Detects unusual spikes, off-hours drain, and ghost bookings.

Run the training pipeline:
```bash
./scripts/train_models.sh
# or directly:
python ml/training/train_models.py
```

#### Training Pipeline Details:
- **Dataset**: Ingests 25,920 hourly sensor records across campus spaces over 90 days.
- **Engineered Features**:
  - `is_weekend` (41.3% importance)
  - `hist_avg_occupancy` (34.5% importance)
  - `day_of_week` (10.5% importance)
  - `room_capacity` (7.1% importance)
  - `hour` (4.5% importance)
  - `equipment_count` (1.1% importance)
  - `exam_period` (0.9% importance)
  - `cost_per_hour` (0.2% importance)
- **Validation Metrics**:
  - $R^2$ Score: **0.8745 (87.45% Accuracy)**
  - Mean Absolute Error (MAE): **6.57 occupants**
  - Root Mean Squared Error (RMSE): **16.04 occupants**
- **Model Artifacts Saved In `ml/models/`**:
  - `xgboost_demand_model.json`
  - `isolation_forest_anomaly.joblib`
  - `metadata.json`

---

### 2.1 Analyzing & Ingesting New Resources for Training
When new resources (rooms, research labs, auditoriums) are commissioned:

#### Method A: Using the Python Ingestion Pipeline
```bash
source .venv/bin/activate
python ml/training/ingest_and_analyze_resource.py
```
Or import in Python:
```python
from ml.training.ingest_and_analyze_resource import analyze_and_ingest_resource

report = analyze_and_ingest_resource({
    "resource_id": "ROOM_ROBOTICS_LAB",
    "name": "Autonomous Drone & Robotics Arena",
    "type": "laboratory",
    "capacity": 50,
    "capabilities": ["robotics_kit", "sensors", "high_speed_net"],
    "cost_per_hour": 125.0
}, days_of_history=30, retrain_now=True)
```

#### Method B: Via the Web Dashboard
1. Open the **Model Training Center** in the UI.
2. Scroll to **➕ Enter New Resource & Retrain Model**.
3. Fill in Resource ID, Name, Type, Capacity, Capabilities, and Hourly Cost.
4. Click **⚡ Ingest, Analyze & Retrain**.
The platform will automatically:
- Profile the resource and compute safe capacity boundaries.
- Calculate overcrowding anomaly limits (`capacity * 1.15`).
- Ingest baseline telemetry into `historical_occupancy.csv`.
- Register the resource in the Digital Twin and database.
- Retrain the XGBoost and Isolation Forest models.
- Provide an instant 24-hour forecast curve specifically for the new resource!

---

### 3. Launching the Platform
Start the FastAPI server:
```bash
./scripts/start_server.sh
# or:
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- **Web Application Dashboard**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔄 The Closed-Loop Engine

```text
┌─────────┐    ┌────────────┐    ┌───────────┐    ┌────────────┐
│  SENSE  │ ──►│ UNDERSTAND │ ──►│  PREDICT  │ ──►│  SIMULATE  │
└─────────┘    └────────────┘    └───────────┘    └────────────┘
                                                         │
                                                         ▼
┌─────────┐    ┌────────────┐    ┌───────────┐    ┌────────────┐
│  LEARN  │◄── │    ACT     │◄── │  EXPLAIN  │◄── │  OPTIMIZE  │
└────┬────┘    └────────────┘    └───────────┘    └────────────┘
     │
     └───────────────────────► Back to SENSE
```

| Phase | Technology | Function |
|---|---|---|
| **Sense & Understand** | SQLite / PostgreSQL + Universal Resource Model | Maintains operational state of 25 campus spaces |
| **Represent Relationships** | NetworkX / Neo4j Graph | Models multi-hop dependencies (Courses, Faculty, Rooms, Equipment) |
| **Predict Demand** | XGBoost Regressor | Forecasts 24-hour occupancy curves and flags capacity shortages |
| **Detect Anomalies** | Isolation Forest | Flags spikes, off-hours resource drain, and ghost reservations |
| **What-If Simulation** | Simulation Engine | Pre-tests candidate moves and calculates utilization & cost impact |
| **Optimize Decisions** | Google OR-Tools CP-SAT | Finds feasible allocations under hard constraints (capacity, equipment, status) |
| **Explain Decisions** | Explainability Engine | Generates structured decision cards (WHAT, WHY, IMPACT, CONFIDENCE) |
| **Risk-Aware Automation** | Automation Engine | Medium/high risk requires human approval; low risk executes automatically |
| **Closed Feedback Loop** | Feedback System | Compares predicted vs actual utilization post-execution to calibrate models |

---

## 🎯 Flagship Demonstration Scenario
- **Problem**: Course `DS301` has **85 enrolled students**, currently scheduled in `Room R101` (Max capacity: **60**). A critical capacity violation is detected.
- **What-If Simulation**: Simulates relocating to `Room R102` (Capacity 100, Projector + Computer + Audio).
- **Constraint Optimization**: Google OR-Tools CP-SAT solver evaluates all candidate rooms:
  - `Room R101`: Infeasible (Capacity 60 < 85)
  - `Room R103`: Infeasible (Missing computer equipment)
  - `Room R104`: Infeasible (Occupied at that time slot)
  - `Room R102`: **Optimal Feasible Solution**
- **Decision Recommendation**:
  - **WHY**: Ample 100-seat capacity, all instructional capabilities verified, faculty schedule free.
  - **IMPACT**: +18% room utilization, -5% operational cost per student.
  - **CONFIDENCE**: 91%.
- **Action**: One-click approval updates the Digital Twin in real-time.
- **Learn**: Actual utilization (82%) recorded against predicted utilization (85%) with 97% accuracy.

---

## 🧪 Running Automated Tests
```bash
PYTHONPATH=. pytest backend/tests/test_api.py -v
```
All 10 tests verify end-to-end integration across the API, prediction models, OR-Tools optimizer, approvals, and the feedback loop.
