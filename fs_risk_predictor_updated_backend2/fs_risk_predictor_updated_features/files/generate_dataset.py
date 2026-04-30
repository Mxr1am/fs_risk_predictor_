import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

np.random.seed(42)
N = 8000


def normal(loc, scale, low, high, n=N):
    return np.clip(np.random.normal(loc, scale, n), low, high)


# -----------------------------------------------------------------------------
# Synthetic Formula Student telemetry dataset
# -----------------------------------------------------------------------------
# The feature list has deliberately been reduced to the direct engineering
# indicators that are easiest to justify for each component.
#
# Engine risk uses: high engine temperature, low oil pressure, high RPM,
# high vibration, and high coolant temperature.
# Brake risk uses: high brake temperature, high pad wear, low hydraulic fluid
# pressure, and high brake fade.
# Battery risk uses: low voltage, high temperature, high current draw, and low
# battery state of health.
# -----------------------------------------------------------------------------

# ENGINE FEATURES (slightly tightened extremes)
engine_temp_c = normal(90, 18, 50, 140, N)
oil_pressure_psi = normal(55, 12, 12, 80, N)
engine_rpm = normal(7000, 2500, 1000, 14000, N)
vibration_g = normal(1.2, 0.9, 0.1, 6.0, N)
coolant_temp_c = normal(85, 12, 50, 120, N)

# BRAKE FEATURES (reduce unrealistic extremes)
brake_temp_c = normal(220, 110, 50, 520, N)
brake_pad_wear_mm = normal(2.5, 1.8, 0.0, 8.0, N)
brake_fluid_psi = normal(1000, 150, 500, 1400, N)
brake_fade_idx = normal(0.2, 0.12, 0.0, 1.0, N)

# BATTERY FEATURES (more realistic EV ranges)
battery_voltage_v = normal(13.0, 1.0, 10.5, 14.5, N)
battery_temp_c = normal(30, 8, 10, 65, N)
battery_current_a = normal(25, 15, 0, 80, N)
battery_health_pct = normal(85, 10, 40, 100, N)


def risk_score(pos_feats, neg_feats):
    """
    Build a synthetic risk score from standardised feature values.

    pos_feats: higher value means higher risk.
    neg_feats: lower value means higher risk.
    """
    score = np.zeros(N)
    for arr, w in pos_feats:
        score += w * (arr - arr.mean()) / (arr.std() + 1e-8)
    for arr, w in neg_feats:
        score += w * -(arr - arr.mean()) / (arr.std() + 1e-8)
    return score


engine_raw = risk_score(
    [
        (engine_temp_c, 0.26),
        (engine_rpm, 0.16),
        (vibration_g, 0.20),
        (coolant_temp_c, 0.14),
    ],
    [(oil_pressure_psi, 0.14)]
)

brake_raw = risk_score(
    [
        (brake_temp_c, 0.30),
        (brake_pad_wear_mm, 0.22),
        (brake_fade_idx, 0.20),
    ],
    [(brake_fluid_psi, 0.12)]
)

battery_raw = risk_score(
    [
        (battery_temp_c, 0.20),
        (battery_current_a, 0.18),
    ],
    [
        (battery_voltage_v, 0.22),
        (battery_health_pct, 0.15),
    ]
)

# Mark the highest-risk 12% of rows as failures for each component.
engine_failure = (engine_raw >= np.percentile(engine_raw, 88)).astype(int)
brake_failure = (brake_raw >= np.percentile(brake_raw, 88)).astype(int)
battery_failure = (battery_raw >= np.percentile(battery_raw, 88)).astype(int)

df = pd.DataFrame({
    "engine_temp_c": np.round(engine_temp_c, 2),
    "oil_pressure_psi": np.round(oil_pressure_psi, 2),
    "engine_rpm": np.round(engine_rpm, 0),
    "vibration_g": np.round(vibration_g, 3),
    "coolant_temp_c": np.round(coolant_temp_c, 2),
    "brake_temp_c": np.round(brake_temp_c, 2),
    "brake_pad_wear_mm": np.round(brake_pad_wear_mm, 3),
    "brake_fluid_psi": np.round(brake_fluid_psi, 2),
    "brake_fade_idx": np.round(brake_fade_idx, 3),
    "battery_voltage_v": np.round(battery_voltage_v, 3),
    "battery_temp_c": np.round(battery_temp_c, 2),
    "battery_current_a": np.round(battery_current_a, 2),
    "battery_health_pct": np.round(battery_health_pct, 2),
    "engine_failure": engine_failure,
    "brake_failure": brake_failure,
    "battery_failure": battery_failure,
})

print("Dataset shape:", df.shape)
print("Failure rates:")
print(f"  Engine:  {df['engine_failure'].mean():.1%}")
print(f"  Brake:   {df['brake_failure'].mean():.1%}")
print(f"  Battery: {df['battery_failure'].mean():.1%}")

csv_path = os.path.join(BASE_DIR, "fs_telemetry_data.csv")
df.to_csv(csv_path, index=False)
print("Saved to:", csv_path)
