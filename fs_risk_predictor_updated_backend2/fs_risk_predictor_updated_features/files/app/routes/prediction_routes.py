from fastapi import APIRouter, Depends
from app.controllers import prediction_controller
from app.middleware.authentication import get_current_user
from app.schemas import PredictionRequest

router = APIRouter(tags=["Predictions"])

@router.get("/dashboard")
def dashboard(current_user: dict = Depends(get_current_user)):
    return prediction_controller.get_dashboard(current_user)

@router.post("/predict")
def predict(payload: PredictionRequest, current_user: dict = Depends(get_current_user)):
    return prediction_controller.run_prediction(payload, current_user)

@router.get("/history")
def history(current_user: dict = Depends(get_current_user)):
    return prediction_controller.history(current_user)

@router.delete("/history/{test_id}")
def delete_history_item(
    test_id: int,
    current_user: dict = Depends(get_current_user)
):
    return prediction_controller.delete_history_item(test_id, current_user)


@router.delete("/history")
def clear_history(current_user: dict = Depends(get_current_user)):
    return prediction_controller.clear_history(current_user)
