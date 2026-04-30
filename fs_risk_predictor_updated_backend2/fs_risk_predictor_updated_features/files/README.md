# FS Risk Predictor — Formula Student Component Failure Prediction

## What it does
Predicts the risk of **engine**, **brake**, and **battery** failure using a reduced set of direct telemetry indicators for each component.

This version uses fewer features than the original so the model is easier to explain and defend from an engineering point of view.

## Model: Random Forest Classifier
- **Algorithm:** Random Forest classifier
- **Trees:** 80 decision trees
- **Class balance:** `class_weight='balanced'`
- **Train/test split:** 80% training data, 20% testing data
- **3 separate models:** one for engine, one for brakes, one for battery

## Current performance after feature reduction
| Component | Test ROC-AUC | 3-fold CV AUC | F1 Failure |
|---|---:|---:|---:|
| Engine | 0.9894 | 0.9882 | 0.88 |
| Brake | 0.9935 | 0.9939 | 0.89 |
| Battery | 0.9960 | 0.9934 | 0.92 |

These scores are high because the dataset is synthetic and the failure labels are generated from the same engineering rules that the model learns from. This is suitable for a prototype/demo, but real car telemetry would be needed for real-world validation.

## Setup

```bash
# 1. Install dependencies
pip install flask scikit-learn numpy pandas joblib

or

pip install -r requirements.txt
# 2. Generate dataset
python generate_dataset.py

# 3. Train models
python train_model.py

# 4. Start the server
python app.py
# Running on http://localhost:5050

or python -m uvicorn app.main:app --reload --port 3333

# 5. Open the app
# Visit http://localhost:5050 in your browser
```

## Dataset description
`generate_dataset.py` creates 8,000 synthetic telemetry samples.

### Engine features kept
- `engine_temp_c`
- `oil_pressure_psi`
- `engine_rpm`
- `vibration_g`
- `coolant_temp_c`

**Engine failure rule:** risk increases with high engine temperature, high RPM, high vibration, high coolant temperature, and low oil pressure.

### Brake features kept
- `brake_temp_c`
- `brake_pad_wear_mm`
- `brake_fluid_psi`
- `brake_fade_idx`

**Brake failure rule:** risk increases with high brake temperature, high brake pad wear, high brake fade, and low brake fluid pressure.

Note: in this version, `brake_pad_wear_mm` means the **amount of pad material worn away**, so a higher value is worse.

### Battery features kept
- `battery_voltage_v`
- `battery_temp_c`
- `battery_current_a`
- `battery_health_pct`

**Battery failure rule:** risk increases with low voltage, high battery temperature, high current draw, and low battery health.

## Files
- `generate_dataset.py` — creates the synthetic CSV dataset
- `train_model.py` — trains the 3 Random Forest models
- `app.py` — Flask backend API
- `index.html` — frontend dashboard
- `models/` — saved model files and metadata
- `fs_telemetry_data.csv` — generated synthetic dataset

## API
`POST /predict`

JSON body should include only the selected telemetry fields above. The API returns risk percentages for engine, brake, and battery, plus sensor warnings.
