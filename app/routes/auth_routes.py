from fastapi import APIRouter, Depends, Header
from app.controllers import user_controller
from app.middleware.authentication import get_current_user
from app.schemas import RegisterRequest, LoginRequest, UpdateProfileRequest

router = APIRouter(tags=["Authentication"])

@router.post("/users", status_code=201)
def register(payload: RegisterRequest):
    return user_controller.create_account(payload)

@router.post("/login")
def login(payload: LoginRequest):
    return user_controller.login(payload)

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user), x_authorization: str | None = Header(default=None, alias="X-Authorization")):
    return user_controller.logout(x_authorization)

@router.patch("/profile")
def update_profile(
    payload: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    return user_controller.update_profile(payload, current_user)