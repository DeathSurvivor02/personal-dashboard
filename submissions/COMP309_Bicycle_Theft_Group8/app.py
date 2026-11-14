"""
COMP309 - Data Warehousing & Predictive Analytics (Group 8)
Flask REST API & Interactive Prediction UI for Toronto Bicycle Theft Recovery
"""

import json
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "artifacts" / "model.pkl"
METRICS_PATH = BASE_DIR / "artifacts" / "metrics.json"

app = Flask(__name__)

_model = None
_metrics = None


def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found at {MODEL_PATH}. Run train_model.py first."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def get_metrics():
    global _metrics
    if _metrics is None and METRICS_PATH.exists():
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            _metrics = json.load(f)
    return _metrics or {}


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", metrics=get_metrics())


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": MODEL_PATH.exists()})


@app.route("/metrics", methods=["GET"])
def metrics():
    return jsonify(get_metrics())


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True)
    if payload is None:
        payload = request.form.to_dict()

    required = [
        "OCC_MONTH",
        "OCC_DOW",
        "OCC_HOUR",
        "DIVISION",
        "PREMISES_TYPE",
        "BIKE_TYPE",
        "BIKE_COST",
        "BIKE_COLOUR",
    ]
    missing = [field for field in required if field not in payload or str(payload[field]).strip() == ""]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        row = {
            "OCC_MONTH": str(payload["OCC_MONTH"]).strip(),
            "OCC_DOW": str(payload["OCC_DOW"]).strip(),
            "OCC_HOUR": int(payload["OCC_HOUR"]),
            "DIVISION": str(payload["DIVISION"]).strip(),
            "PREMISES_TYPE": str(payload["PREMISES_TYPE"]).strip(),
            "BIKE_TYPE": str(payload["BIKE_TYPE"]).strip(),
            "BIKE_COST": float(payload["BIKE_COST"]),
            "BIKE_COLOUR": str(payload["BIKE_COLOUR"]).strip(),
        }
    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"Invalid numeric value: {exc}"}), 400

    df = pd.DataFrame([row])
    model = get_model()
    pred_class = int(model.predict(df)[0])
    prob_recovered = float(model.predict_proba(df)[0][1])

    return jsonify(
        {
            "prediction": "RECOVERED" if pred_class == 1 else "STOLEN",
            "predicted_label": pred_class,
            "recovery_probability": round(prob_recovered, 4),
            "input": row,
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
