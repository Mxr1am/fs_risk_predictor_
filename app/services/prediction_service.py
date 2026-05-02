from pathlib import Path
import joblib

PROJECT_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_DIR / "models"

ENGINE_FEATURES = ["engine_temp_c", "oil_pressure_psi", "engine_rpm", "vibration_g", "coolant_temp_c"]
BRAKE_FEATURES = ["brake_temp_c", "brake_pad_wear_mm", "brake_fluid_psi", "brake_fade_idx"]
BATTERY_FEATURES = ["battery_voltage_v", "battery_temp_c", "battery_current_a", "battery_health_pct"]

MODEL_CONFIG = {
    "engine": {
        "features": ENGINE_FEATURES,
        "model": joblib.load(MODEL_DIR / "engine_model.pkl"),
        "allowed_car_types": ["MECH"]
    },
    "brake": {
        "features": BRAKE_FEATURES,
        "model": joblib.load(MODEL_DIR / "brake_model.pkl"),
        "allowed_car_types": ["EV", "MECH"]
    },
    "battery": {
        "features": BATTERY_FEATURES,
        "model": joblib.load(MODEL_DIR / "battery_model.pkl"),
        "allowed_car_types": ["EV"]
    },
}

def risk_level(score: float) -> str:
    if score >= 75:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"

def allowed_components_for_car_type(car_type: str) -> list[str]:
    if car_type == "EV":
        return ["brake", "battery"]
    if car_type == "MECH":
        return ["engine", "brake"]
    return []

def predict_component(component: str, values: dict) -> dict:
    config = MODEL_CONFIG[component]
    feature_order = config["features"]
    input_vector = [[float(values[feature]) for feature in feature_order]]
    probability = config["model"].predict_proba(input_vector)[0][1]
    score = round(float(probability) * 100, 2)
    return {"component": component, "risk_score": score, "risk_level": risk_level(score), "features_used": feature_order}
