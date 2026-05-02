from fastapi import Header, HTTPException
from app.models.user_model import get_user_from_token

def get_current_user(x_authorization: str | None = Header(default=None, alias="X-Authorization")):
    user = get_user_from_token(x_authorization)
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return user
