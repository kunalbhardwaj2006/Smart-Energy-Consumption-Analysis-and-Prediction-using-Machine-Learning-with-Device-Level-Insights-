# =========================================================
# SMART ENERGY BACKEND API
# =========================================================

import os
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------------------------------------------------------
# PATH SETUP (ABSOLUTE - NO RELATIVE CONFUSION)
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "household_power_consumption.txt")
SCALER_PATH = os.path.join(PROJECT_ROOT, "feature_scaler.pkl")
TARGET_SCALER_PATH = os.path.join(PROJECT_ROOT, "target_scaler.pkl")

# ---------------------------------------------------------
# LOAD DATA FOR SIMPLE BASELINE PREDICTION
# ---------------------------------------------------------

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset not found at: {DATA_PATH}")

df = pd.read_csv(
    DATA_PATH,
    sep=";",
    na_values="?",
    low_memory=False
)

df["Datetime"] = pd.to_datetime(
    df["Date"] + " " + df["Time"],
    dayfirst=True,
    errors="coerce"
)

df["Global_active_power"] = pd.to_numeric(
    df["Global_active_power"],
    errors="coerce"
)

df = df.dropna(subset=["Datetime", "Global_active_power"])
df = df.set_index("Datetime")

# ---------------------------------------------------------
# SIMPLE BASELINE FORECAST (Last value repeat)
# ---------------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    hours_ahead = int(data.get("hours_ahead", 24))

    last_value = df["Global_active_power"].iloc[-1]

    predictions = [float(last_value)] * hours_ahead

    return jsonify({
        "hours_ahead": hours_ahead,
        "predictions": predictions,
        "unit": "kW",
        "model": "Naive Baseline (Last Value)"
    })


if __name__ == "__main__":
    app.run(debug=True)
