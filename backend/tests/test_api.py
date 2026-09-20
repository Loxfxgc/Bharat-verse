"""
BharatVerse - Automated Test Suite
Tests all core APIs and the complete Sense -> Predict -> Simulate -> Optimize -> Act -> Learn loop.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["components"]["ortools_solver"] == "ready"

def test_digital_twin_overview():
    res = client.get("/api/resources/digital-twin/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_resources"] >= 20
    assert data["system_status"] == "ONLINE"

def test_resources_list():
    res = client.get("/api/resources")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    # verify Universal Resource Model fields
    room = items[0]
    assert "resource_id" in room
    assert "capacity" in room
    assert "status" in room
    assert "capabilities" in room

def test_prediction_model():
    payload = {
        "room_id": "ROOM_R102",
        "day_of_week": 1,
        "hour": 10,
        "is_weekend": 0,
        "exam_period": 0
    }
    res = client.post("/api/predictions/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "predicted_occupancy" in data
    assert data["predicted_occupancy"] > 0
    assert data["confidence"] > 0.70

def test_anomaly_detection():
    # Test an extreme overcrowding event (98 occupants in room capacity 60)
    payload = {
        "resource_id": "ROOM_R101",
        "actual_occupancy": 98,
        "hour": 14,
        "is_weekend": 0
    }
    res = client.post("/api/anomalies/detect", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["active", "normal"]
    assert "severity" in data

def test_simulation_what_if():
    # Ensure R102 is available for clean simulation test
    client.put("/api/resources/ROOM_R102", json={"status": "available", "current_occupancy": 0})
    client.put("/api/resources/ROOM_R101", json={"status": "occupied", "current_occupancy": 60})

    payload = {
        "scenario_name": "Test DS301 Relocation",
        "course_id": "CRS_DS301",
        "target_room_id": "ROOM_R102"
    }
    res = client.post("/api/simulation/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["feasible"] is True
    assert data["capacity_check"] == "PASS"
    assert data["equipment_check"] == "PASS"

def test_constraint_optimization_solver():
    # Ensure R102 is available so it's a top candidate
    client.put("/api/resources/ROOM_R102", json={"status": "available", "current_occupancy": 0})

    payload = {"course_id": "CRS_DS301"}
    res = client.post("/api/optimization/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["solver_status"] in ["OPTIMAL", "FEASIBLE"]
    assert data["best_allocation"] in ["ROOM_R102", "ROOM_AUD1", "ROOM_R104"]
    assert len(data["candidates"]) > 0
    assert "explanation" in data

def test_recommendation_and_approval_flow():
    # 1. Fetch pending recommendations
    res = client.get("/api/recommendations")
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) > 0
    flagship = recs[0]
    rec_id = flagship["rec_id"]

    # 2. Approve the recommendation
    approval_payload = {
        "decision": "approved",
        "reviewer": "Director of Campus Infrastructure",
        "comments": "Capacity compliance verified with OR-Tools."
    }
    app_res = client.post(f"/api/approvals/{rec_id}/approve", json=approval_payload)
    assert app_res.status_code == 200
    app_data = app_res.json()
    assert app_data["success"] is True
    assert app_data["status"] == "executed"

    # 3. Check that feedback record was generated
    fb_res = client.get("/api/feedback/metrics")
    assert fb_res.status_code == 200
    fb_data = fb_res.json()
    assert fb_data["total_feedback_events"] >= 1
    assert fb_data["system_prediction_accuracy"] > 80.0

def test_graph_topology():
    res = client.get("/api/graph/topology")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0

def test_ml_metrics():
    res = client.get("/api/ml/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
