import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier




df = pd.read_csv("fs_telemetry_data.csv")



# Feature sets

component_configs = {
    "Engine": {
        "features": [
            "engine_temp_c",
            "oil_pressure_psi",
            "engine_rpm",
            "vibration_g",
            "coolant_temp_c"
        ],
        "target": "engine_failure"
    },

    "Brakes": {
        "features": [
            "brake_temp_c",
            "brake_pad_wear_mm",
            "brake_fluid_psi",
            "brake_fade_idx"
        ],
        "target": "brake_failure"
    },

    "Battery": {
        "features": [
            "battery_voltage_v",
            "battery_temp_c",
            "battery_current_a",
            "battery_health_pct"
        ],
        "target": "battery_failure"
    }
}



# Models to compare


models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Decision Tree": DecisionTreeClassifier(
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=80,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
}



# Run comparison

results = []

for component_name, config in component_configs.items():

    X = df[config["features"]]
    y = df[config["target"]]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    for model_name, model in models.items():

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        # Probability for ROC-AUC
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test)[:, 1]
        else:
            y_prob = y_pred

        results.append({
            "Component": component_name,
            "Model": model_name,
            "Accuracy": accuracy_score(y_test, y_pred),
            "Precision": precision_score(y_test, y_pred),
            "Recall": recall_score(y_test, y_pred),
            "F1 Score": f1_score(y_test, y_pred),
            "ROC-AUC": roc_auc_score(y_test, y_prob)
        })



# Display and save results

results_df = pd.DataFrame(results)

print("\nMODEL COMPARISON RESULTS")
print(results_df.to_string(index=False))

results_df.to_csv("model_comparison_results.csv", index=False)

print("\nResults saved to: model_comparison_results.csv")