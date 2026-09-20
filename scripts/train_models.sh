#!/usr/bin/env bash
# BharatVerse - Train ML Models
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================================="
echo " 🇮🇳 BharatVerse - Training ML Models (Phase 4)"
echo "=========================================================="

cd "$PROJECT_ROOT"

if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtualenv not found, using system python3..."
fi

# 1. Ensure synthetic data exists
if [ ! -f "data/synthetic/historical_occupancy.csv" ]; then
    echo "Generating synthetic dataset..."
    python data/synthetic/generate_synthetic_data.py
fi

# 2. Train XGBoost Demand Model & Isolation Forest Anomaly Detector
python ml/training/train_models.py

echo ""
echo "Model training completed. Artifacts saved in ml/models/:"
ls -lh ml/models/
