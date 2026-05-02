import joblib
import numpy as np




engine_model = joblib.load("models/engine_model.pkl")
brake_model = joblib.load("models/brake_model.pkl")
battery_model = joblib.load("models/battery_model.pkl")


# Helper function


def predict_case(name, engine_vals, brake_vals, battery_vals):
    
    engine_risk = engine_model.predict_proba(
        np.array([engine_vals])
    )[0][1] * 100

    brake_risk = brake_model.predict_proba(
        np.array([brake_vals])
    )[0][1] * 100

    battery_risk = battery_model.predict_proba(
        np.array([battery_vals])
    )[0][1] * 100

   
    print(f"{name}")
    print(f"Engine Risk:  {engine_risk:.1f}%")
    print(f"Brake Risk:   {brake_risk:.1f}%")
    print(f"Battery Risk: {battery_risk:.1f}%")







# 1 Healthy baseline


predict_case(
    "Healthy Baseline",
    [90, 50, 7000, 1.2, 82],
    [180, 1.5, 1000, 0.15],
    [12.8, 28, 20, 90]
)



# ENGINE EDGE CASES


predict_case(
    "High Engine Temperature",
    [145, 50, 7000, 1.2, 82],
    [180, 1.5, 1000, 0.15],
    [12.8, 28, 20, 90]
)

predict_case(
    "Low Oil Pressure",
    [90, 10, 7000, 1.2, 82],
    [180, 1.5, 1000, 0.15],
    [12.8, 28, 20, 90]
)

predict_case(
    "Extreme RPM",
    [90, 50, 14000, 1.2, 82],
    [180, 1.5, 1000, 0.15],
    [12.8, 28, 20, 90]
)

predict_case(
    "High Vibration",
    [90, 50, 7000, 6.0, 82],
    [180, 1.5, 1000, 0.15],
    [12.8, 28, 20, 90]
)

predict_case(
    "High Coolant Temperature",
    [90, 50, 7000, 1.2, 120],
    [180, 1.5, 1000, 0.15],
    [12.8, 28, 20, 90]
)



# BRAKE EDGE CASES

predict_case(
    "High Brake Temperature",
    [90,50,7000,1.2,82],
    [520,1.5,1000,0.15],
    [12.8,28,20,90]
)

predict_case(
    "High Pad Wear",
    [90,50,7000,1.2,82],
    [180,7.5,1000,0.15],
    [12.8,28,20,90]
)

predict_case(
    "Low Brake Pressure",
    [90,50,7000,1.2,82],
    [180,1.5,450,0.15],
    [12.8,28,20,90]
)

predict_case(
    "Severe Brake Fade",
    [90,50,7000,1.2,82],
    [180,1.5,1000,0.95],
    [12.8,28,20,90]
)



# BATTERY EDGE CASES


predict_case(
    "Low Battery Voltage",
    [90,50,7000,1.2,82],
    [180,1.5,1000,0.15],
    [9.5,28,20,90]
)

predict_case(
    "Moderate Battery Stress",
    [90,50,7000,1.2,82],
    [180,1.5,1000,0.15],
    [12.2,35,35,75]
)

predict_case(
    "High Battery Temperature",
    [90,50,7000,1.2,82],
    [180,1.5,1000,0.15],
    [12.8,70,20,90]
)

predict_case(
    "High Battery Current",
    [90,50,7000,1.2,82],
    [180,1.5,1000,0.15],
    [12.8,28,85,90]
)

predict_case(
    "Low Battery Health",
    [90,50,7000,1.2,82],
    [180,1.5,1000,0.15],
    [12.8,28,20,30]
)


# COMBINED FAILURE CASE


predict_case(
    "Combined Severe Failure Case",
    [145,10,14000,6.0,120],
    [520,7.5,450,0.95],
    [9.5,70,85,30]
)



# ALL IDEAL CASE


predict_case(
    "Ideal Best Case",
    [80,60,5000,0.5,75],
    [140,0.5,1200,0.05],
    [13.5,20,10,98]
)