from fastapi import HTTPException
from app.models import user_model
from app.schemas import RegisterRequest, LoginRequest

def create_account(payload: RegisterRequest):
    try:
        user_id = user_model.create_account(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"user_id": user_id}

def login(payload: LoginRequest):
    user_id = user_model.authenticate_user(payload.team_name, payload.password)
    if user_id is None:
        raise HTTPException(status_code=400, detail="invalid team name or password")
    token = user_model.get_token(user_id)
    if token is None:
        token = user_model.set_token(user_id)
    return {"user_id": user_id, "session_token": token}

def logout(token: str | None):
    if not token:
        raise HTTPException(status_code=400, detail="missing X-Authorization token")
    user_model.remove_token(token)
    return {"message": "logged out"}