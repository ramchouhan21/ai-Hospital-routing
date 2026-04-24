from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .database import load_hospitals
from .logic import find_best_hospitals

router = APIRouter()

# Load data into memory (Mock Database initialization)
HOSPITALS_DB = load_hospitals()

class PatientRequest(BaseModel):
    age: int
    gender: str
    symptoms: str
    latitude: float
    longitude: float

@router.post("/predict")
async def predict_hospital(request: PatientRequest):
    """
    Endpoint to predict the best hospital based on patient symptoms and location.
    """
    if not HOSPITALS_DB:
        raise HTTPException(status_code=500, detail="Database not loaded properly.")
        
    try:
        results = find_best_hospitals(
            user_lat=request.latitude,
            user_lng=request.longitude,
            symptoms=request.symptoms,
            hospitals_data=HOSPITALS_DB
        )
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
