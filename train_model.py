
import os
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "fs_telemetry_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

ENGINE_FEATURES = [
    "engine_temp_c", "oil_pressure_psi", "engine_rpm",
    "vibration_g", "coolant_temp_c"
]
BRAKE_FEATURES = [
    "brake_temp_c", "brake_pad_wear_mm",
    "brake_fluid_psi", "brake_fade_idx"
]
BATTERY_FEATURES = [
    "battery_voltage_v", "battery_temp_c",
    "battery_current_a", "battery_health_pct"
]
components = {
    "engine":  (ENGINE_FEATURES,  "engine_failure"),
    "brake":   (BRAKE_FEATURES,   "brake_failure"),
    "battery": (BATTERY_FEATURES, "battery_failure"),
}

metadata = {}

for name, (features, target) in components.items():
    print(f"\n{'='*50}")
    print(f" Training {name.upper()} model")
    print(f"{'='*50}")

    X = df[features].values
    y = df[target].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=80,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)
    cv_auc = cross_val_score(model, X, y, cv=3, scoring="roc_auc").mean()

    print(f"\nTest ROC-AUC : {auc:.4f}")
    print(f"3-fold CV AUC: {cv_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["No Failure", "Failure"]))

    importances = dict(zip(features, model.feature_importances_.round(4).tolist()))
    sorted_imp = sorted(importances.items(), key=lambda x: -x[1])

    print("Feature importances:")
    for feat, imp in sorted_imp:
        bar = "█" * int(imp * 40)
        print(f"  {feat:<25} {imp:.4f}  {bar}")

    model_path = os.path.join(MODEL_DIR, f"{name}_model.pkl")
    joblib.dump(model, model_path)
    print(f"\nSaved: {model_path}")

    metadata[name] = {
        "features": features,
        "target": target,
        "auc_test": round(float(auc), 4),
        "auc_cv": round(float(cv_auc), 4),
        "failure_rate": round(float(y.mean()), 3),
        "n_samples": len(df),
        "feature_importance": {k: v for k, v in sorted_imp}
    }

metadata_path = os.path.join(MODEL_DIR, "metadata.json")
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)

print("\n All models trained and saved.")
print("Metadata saved to:", metadata_path)
