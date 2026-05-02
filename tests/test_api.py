import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)



def register_and_login(team_name, car_type="MECH"):
    client.post("/users", json={
        "team_name": team_name,
        "team_leader_name": "Test Leader",
        "car_type": car_type,
        "email": f"{team_name.replace(' ', '')}@test.com",
        "password": "password123"
    })
    res = client.post("/login", json={
        "team_name": team_name,
        "password": "password123"
    })
    return res.json().get("session_token")



def test_register_success():
    res = client.post("/users", json={
        "team_name": "Team Alpha",
        "team_leader_name": "Alice",
        "car_type": "MECH",
        "email": "alpha@test.com",
        "password": "pass123"
    })
    assert res.status_code == 201

def test_register_duplicate_team_name():
    client.post("/users", json={
        "team_name": "Team Duplicate",
        "team_leader_name": "Bob",
        "car_type": "MECH",
        "email": "dup1@test.com",
        "password": "pass123"
    })
    res = client.post("/users", json={
        "team_name": "Team Duplicate",
        "team_leader_name": "Bob",
        "car_type": "MECH",
        "email": "dup2@test.com",
        "password": "pass123"
    })
    assert res.status_code == 400

def test_register_invalid_email():
    res = client.post("/users", json={
        "team_name": "Team BadEmail",
        "team_leader_name": "Carol",
        "car_type": "EV",
        "email": "notanemail",
        "password": "pass123"
    })
    assert res.status_code == 422

def test_register_whitespace_only_team_name():
    res = client.post("/users", json={
        "team_name": "   ",
        "team_leader_name": "Dave",
        "car_type": "MECH",
        "email": "ws@test.com",
        "password": "pass123"
    })
    assert res.status_code == 422



def test_login_success():
    client.post("/users", json={
        "team_name": "Team Login",
        "team_leader_name": "Eve",
        "car_type": "MECH",
        "email": "login@test.com",
        "password": "pass123"
    })
    res = client.post("/login", json={
        "team_name": "Team Login",
        "password": "pass123"
    })
    assert res.status_code == 200
    assert "session_token" in res.json()

def test_login_wrong_password():
    res = client.post("/login", json={
        "team_name": "Team Login",
        "password": "wrongpassword"
    })
    assert res.status_code == 400

def test_dashboard_without_token_returns_401():
    res = client.get("/dashboard")
    assert res.status_code == 401

def test_dashboard_with_fake_token_returns_401():
    res = client.get("/dashboard", headers={"X-Authorization": "faketoken"})
    assert res.status_code == 401


# ── Schema validation on prediction input 
def test_predict_engine_temp_too_high_returns_422():
    token = register_and_login("Team SchemaTest", "MECH")
    res = client.post("/predict", json={
        "engine": {
            "engine_temp_c": 999,
            "oil_pressure_psi": 50,
            "engine_rpm": 7000,
            "vibration_g": 1.2,
            "coolant_temp_c": 82
        }
    }, headers={"X-Authorization": token})
    assert res.status_code == 422

def test_predict_no_components_returns_400():
    token = register_and_login("Team NoComp", "MECH")
    res = client.post("/predict", json={},
                      headers={"X-Authorization": token})
    assert res.status_code == 400


#  Car type restriction 

def test_ev_team_cannot_predict_engine():
    token = register_and_login("Team EV", "EV")
    res = client.post("/predict", json={
        "engine": {
            "engine_temp_c": 90,
            "oil_pressure_psi": 50,
            "engine_rpm": 7000,
            "vibration_g": 1.2,
            "coolant_temp_c": 82
        }
    }, headers={"X-Authorization": token})
    assert res.status_code == 403

def test_mech_team_cannot_predict_battery():
    token = register_and_login("Team MECH", "MECH")
    res = client.post("/predict", json={
        "battery": {
            "battery_voltage_v": 12.8,
            "battery_temp_c": 28,
            "battery_current_a": 20,
            "battery_health_pct": 90
        }
    }, headers={"X-Authorization": token})
    assert res.status_code == 403


#  Valid prediction 
def test_valid_brake_prediction_returns_score():
    token = register_and_login("Team BrakeTest", "MECH")
    res = client.post("/predict", json={
        "brake": {
            "brake_temp_c": 180,
            "brake_pad_wear_mm": 1.5,
            "brake_fluid_psi": 1000,
            "brake_fade_idx": 0.15
        }
    }, headers={"X-Authorization": token})
    assert res.status_code == 200
    results = res.json()["results"]
    assert len(results) == 1
    assert results[0]["component"] == "brake"
    assert 0 <= results[0]["risk_score"] <= 100
    assert results[0]["risk_level"] in ["low", "medium", "high", "critical"]