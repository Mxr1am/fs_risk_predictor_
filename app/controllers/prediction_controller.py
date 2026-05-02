from fastapi import HTTPException
from app.models.history_model import save_test, get_history, delete_test, delete_all_history
from app.schemas import PredictionRequest
from app.services.prediction_service import allowed_components_for_car_type, predict_component

def get_dashboard(current_user: dict):
    return {"team_name": current_user["team_name"], "team_leader_name": current_user["team_leader_name"], "car_type": current_user["car_type"], "available_components": allowed_components_for_car_type(current_user["car_type"]), "email": current_user["email"]}

def run_prediction(payload: PredictionRequest, current_user: dict):
    allowed_components = allowed_components_for_car_type(current_user["car_type"])
    submitted = {"engine": payload.engine, "brake": payload.brake, "battery": payload.battery}
    submitted = {component: data for component, data in submitted.items() if data is not None}
    if not submitted:
        raise HTTPException(status_code=400, detail="no component data supplied")
    disallowed = [component for component in submitted if component not in allowed_components]
    if disallowed:
        raise HTTPException(status_code=403, detail=f"{current_user['car_type']} teams cannot run predictions for: {', '.join(disallowed)}")
    results = []
    for component, model_input in submitted.items():
        values = model_input.model_dump()
        result = predict_component(component, values)
        if payload.save_result:
            result["test_id"] = save_test(current_user["user_id"], component, values, result["risk_score"], result["risk_level"])
        results.append(result)
    return {"results": results}

def history(current_user: dict):
    return {"history": get_history(current_user["user_id"])}
    

def delete_history_item(test_id: int, current_user: dict):
    deleted = delete_test(current_user["user_id"], test_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="test history item not found"
        )

    return {
        "message": "test history item deleted",
        "test_id": test_id
    }


def clear_history(current_user: dict):
    deleted_count = delete_all_history(current_user["user_id"])

    return {
        "message": "test history cleared",
        "deleted_count": deleted_count
    }
