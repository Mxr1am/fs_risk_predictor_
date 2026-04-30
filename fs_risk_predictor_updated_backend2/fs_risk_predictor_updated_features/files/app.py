"""
Formula Student Component Failure Predictor — Flask Backend
"""

from flask import Flask, request, jsonify, send_from_directory
import joblib
import json
import numpy as np
import os

app = Flask(__name__, static_folder=".")

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

# Load models and metadata 
models = {
    "engine":  joblib.load(os.path.join(MODEL_DIR, "engine_model.pkl")),
    "brake":   joblib.load(os.path.join(MODEL_DIR, "brake_model.pkl")),
    "battery": joblib.load(os.path.join(MODEL_DIR, "battery_model.pkl")),
}

with open(os.path.join(MODEL_DIR, "metadata.json")) as f:
    metadata = json.load(f)

ENGINE_FEATURES  = metadata["engine"]["features"]
BRAKE_FEATURES   = metadata["brake"]["features"]
BATTERY_FEATURES = metadata["battery"]["features"]

#  Sensor safe ranges (for frontend warnings)
SAFE_RANGES = {
    "engine_temp_c":        (40,  115,   "°C"),
    "oil_pressure_psi":     (25,  75,    "psi"),
    "engine_rpm":           (800, 12500, "RPM"),
    "vibration_g":          (0,   4.0,   "g"),
    "coolant_temp_c":       (35,  105,   "°C"),
    "brake_temp_c":         (15,  400,   "°C"),
    "brake_pad_wear_mm":    (0,   6.0,   "mm worn"),
    "brake_fluid_psi":      (700, 1400,  "psi"),
    "brake_fade_idx":       (0,   0.5,   "idx"),
    "battery_voltage_v":    (11.5,15.0,  "V"),
    "battery_temp_c":       (5,   50,    "°C"),
    "battery_current_a":    (0,   65,    "A"),
    "battery_health_pct":   (55,  100,   "%"),
}

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    def get_features(keys):
        vals = []
        for k in keys:
            v = data.get(k)
            if v is None:
                return None, f"Missing field: {k}"
            vals.append(float(v))
        return np.array(vals).reshape(1, -1), None

    results = {}
    warnings = []

    for component, features in [
        ("engine",  ENGINE_FEATURES),
        ("brake",   BRAKE_FEATURES),
        ("battery", BATTERY_FEATURES),
    ]:
        X, err = get_features(features)
        if err:
            return jsonify({"error": err}), 400

        prob      = float(models[component].predict_proba(X)[0, 1])
        risk_pct  = round(prob * 100, 1)
        risk_level = (
            "critical" if risk_pct >= 70 else
            "high"     if risk_pct >= 45 else
            "moderate" if risk_pct >= 25 else
            "low"
        )

        results[component] = {
            "risk_pct":   risk_pct,
            "risk_level": risk_level,
        }

    # Check individual sensor warnings
    for sensor, (lo, hi, unit) in SAFE_RANGES.items():
        val = data.get(sensor)
        if val is not None:
            val = float(val)
            if val < lo:
                warnings.append({"sensor": sensor, "value": val, "unit": unit,
                                  "msg": f"{sensor} is below safe minimum ({lo}{unit})"})
            elif val > hi:
                warnings.append({"sensor": sensor, "value": val, "unit": unit,
                                  "msg": f"{sensor} exceeds safe maximum ({hi}{unit})"})

    return jsonify({
        "predictions": results,
        "warnings":    warnings,
        "model_info": {
            "engine_auc":  metadata["engine"]["auc_cv"],
            "brake_auc":   metadata["brake"]["auc_cv"],
            "battery_auc": metadata["battery"]["auc_cv"],
        }
    })

@app.route("/metadata")
def get_metadata():
    return jsonify(metadata)

if __name__ == "__main__":
    print("Starting Formula Student Failure Predictor...")
    print(f"Models loaded: {list(models.keys())}")
    app.run(debug=True, port=5050)
