from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .database import load_hospitals
from .logic import find_best_hospitals, generate_report

router = APIRouter()

# Load data into memory (Mock Database initialization)
HOSPITALS_DB = load_hospitals()

class PatientRequest(BaseModel):
    age: int
    gender: str
    symptoms: str
    latitude: float
    longitude: float

class ReportRequest(BaseModel):
    symptoms: str
    severity: str
    hospital_name: str
    icu_available: int
    beds_available: int
    distance_km: float

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

@router.post("/generate_report")
async def api_generate_report(request: ReportRequest):
    """
    Endpoint to generate a patient report for a specific hospital.
    """
    try:
        hospital = {
            "name": request.hospital_name,
            "available_icu_beds": request.icu_available,
            "available_beds": request.beds_available,
            "distance_km": request.distance_km
        }
        report_text = generate_report(request.symptoms, request.severity, hospital)
        return {"status": "success", "message": "Report generated successfully.", "report": report_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

