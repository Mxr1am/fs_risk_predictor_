from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class CarType(str, Enum):
    EV = "EV"
    MECH = "MECH"

class RegisterRequest(BaseModel):
    team_name: str = Field(..., min_length=1)
    team_leader_name: str = Field(..., min_length=1)
    car_type: CarType
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("team_name", "team_leader_name")
    @classmethod
    def strip_required_strings(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("field cannot be empty")
        return value

class LoginRequest(BaseModel):
    team_name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class UpdateProfileRequest(BaseModel):
    team_leader_name: Optional[str] = Field(default=None, min_length=1)
    email: Optional[EmailStr] = None

    @field_validator("team_leader_name")
    @classmethod
    def strip_team_leader_name(cls, value: Optional[str]):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("team leader name cannot be empty")
        return value

class EngineInput(BaseModel):
    engine_temp_c: float = Field(..., ge=40, le=150)
    oil_pressure_psi: float = Field(..., ge=8, le=80)
    engine_rpm: float = Field(..., ge=800, le=14500)
    vibration_g: float = Field(..., ge=0.1, le=6.5)
    coolant_temp_c: float = Field(..., ge=35, le=125)

class BrakeInput(BaseModel):
    brake_temp_c: float = Field(..., ge=15, le=560)
    brake_pad_wear_mm: float = Field(..., ge=0, le=8)
    brake_fluid_psi: float = Field(..., ge=400, le=1400)
    brake_fade_idx: float = Field(..., ge=0, le=1)

class BatteryInput(BaseModel):
    battery_voltage_v: float = Field(..., ge=9, le=15.5)
    battery_temp_c: float = Field(..., ge=5, le=75)
    battery_current_a: float = Field(..., ge=0, le=90)
    battery_health_pct: float = Field(..., ge=25, le=100)

class PredictionRequest(BaseModel):
    engine: Optional[EngineInput] = None
    brake: Optional[BrakeInput] = None
    battery: Optional[BatteryInput] = None
    save_result: bool = False