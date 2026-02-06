from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os

app = Flask(__name__)

# --------------------------------------------------
# Configuration
# --------------------------------------------------
DATA_PATH = "data/household_power_consumption.txt"
MODEL_PATH = "energy_model.pkl"

# --------------------------------------------------
# Load & Prepare Data
# --------------------------------------------------
def load_data():
    df = pd.read_csv(
        DATA_PATH,
        sep=";",
        na_values="?"
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

    hourly = df["Global_active_power"].resample("h").mean().dropna()

    return hourly


# --------------------------------------------------
# Train or Load Model
# --------------------------------------------------
def train_or_load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)

    data = load_data()

    X = np.arange(len(data)).reshape(-1, 1)
    y = data.values

    model = LinearRegression()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    return model


model = train_or_load_model()


# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Smart Energy Consumption API is running",
        "status": "OK"
    })


@app.route("/predict", methods=["POST"])
def predict():
    """
    Expected JSON:
    {
        "hours_ahead": 24
    }
    """

    input_data = request.get_json()
    hours = int(input_data.get("hours_ahead", 24))

    data = load_data()
    last_index = len(data)

    future_X = np.arange(last_index, last_index + hours).reshape(-1, 1)
    predictions = model.predict(future_X)

    return jsonify({
        "hours_ahead": hours,
        "predictions": predictions.tolist(),
        "unit": "kW",
        "model": "Linear Regression (Baseline)"
    })


# --------------------------------------------------
# Run Server
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
