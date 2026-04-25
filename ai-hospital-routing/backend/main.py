from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import random
import os
import uvicorn

app = FastAPI(
    title="MedRoute AI - Smart Hospital Routing API",
    description="API for routing patients to the best hospitals based on severity and live availability.",
    version="1.0.0"
)

# Configure CORS to allow the frontend to interact with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset dynamically
hospitals_db = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "structured_hospitals.csv")

def load_data():
    global hospitals_db
    try:
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(f"{CSV_PATH} not found.")
        df = pd.read_csv(CSV_PATH)
        hospitals_db = df.to_dict('records')
        for h in hospitals_db:
            h['beds_available'] = int(h['beds_available'])
            h['wait_time_minutes'] = int(h['wait_time_minutes'])
    except Exception as e:
        print(f"Error loading dataset: {e}")
        hospitals_db = []

load_data()

class PatientRequest(BaseModel):
    age: int
    gender: str
    symptoms: str
    latitude: float
    longitude: float

CRITICAL_SYMPTOMS = ['chest pain', 'heart attack', 'breathing issue', 'stroke', 'difficulty breathing']
MODERATE_SYMPTOMS = ['fever', 'infection', 'injury', 'nausea', 'vomiting']

def get_severity(symptoms: str):
    severity_level = 'Low'
    severity_priority = 0.3
    syms = [s.strip().lower() for s in symptoms.split(',')]
    syms.extend(symptoms.lower().split())
    
    for sym in syms:
        if any(c in sym for c in CRITICAL_SYMPTOMS) or any(sym in c for c in CRITICAL_SYMPTOMS):
            return 'High', 1.0
        elif any(m in sym for m in MODERATE_SYMPTOMS) or any(sym in m for m in MODERATE_SYMPTOMS):
            severity_level = 'Medium'
            severity_priority = 0.6
    return severity_level, severity_priority

@app.get("/")
def read_root():
    return {"message": "Welcome to MedRoute AI API. Use POST /api/v1/predict to get hospital recommendations."}

@app.post("/api/v1/predict")
def predict_hospital(req: PatientRequest):
    if not hospitals_db:
        load_data() # Try loading again
        if not hospitals_db:
            raise HTTPException(status_code=500, detail="Database not loaded properly.")
        
    severity_level, severity_priority = get_severity(req.symptoms)
    
    candidates = []
    
    for h in hospitals_db:
        if h['beds_available'] <= 0:
            continue
            
        icu_score = 1.0 if str(h['icu_available']).lower() == 'yes' else 0.0
        distance_km = random.uniform(1.0, 25.0)
        dist_score = max(0, 1 - (distance_km / 25.0))
        wait_time = h['wait_time_minutes']
        wait_score = max(0, 1 - (wait_time / 120.0))
        
        score = (0.4 * severity_priority) + (0.25 * icu_score) + (0.2 * dist_score) + (0.15 * wait_score)
        
        candidates.append({
            'hospital_ref': h,
            'score': round(score, 3),
            'distance_km': round(distance_km, 1),
            'icu_score': icu_score,
            'wait_time': wait_time
        })
        
    candidates.sort(key=lambda x: x['score'], reverse=True)
    top_3 = candidates[:3]
    
    response_data = []
    for c in top_3:
        h = c['hospital_ref']
        icu_beds = random.randint(1, 10) if str(h['icu_available']).lower() == 'yes' else 0
        
        # Mock coordinates near user
        mock_lat = req.latitude + (c['distance_km'] * 0.005)
        mock_lng = req.longitude + (c['distance_km'] * 0.005)
        
        response_data.append({
            "name": h['hospital_name'],
            "estimated_time_mins": c['wait_time'],
            "distance_km": c['distance_km'],
            "available_beds": h['beds_available'],
            "available_icu_beds": icu_beds,
            "traffic_level": random.choice(["Low", "Medium", "High"]),
            "has_icu": str(h['icu_available']).lower() == 'yes',
            "specialties": str(h['specialization']).capitalize(),
            "score": c['score'],
            "latitude": mock_lat,
            "longitude": mock_lng
        })

    return {
        "status": "success",
        "data": {
            "severity": severity_level,
            "recommendations": response_data
        }
    }

class ReportRequest(BaseModel):
    symptoms: str
    severity: str
    hospital_name: str
    icu_available: int
    beds_available: int
    distance_km: float

@app.post("/api/v1/generate_report")
def api_generate_report(req: ReportRequest):
    icu_status = "Yes" if req.icu_available > 0 else "No"
    report = f"""Patient Report

Symptoms: {req.symptoms}
Severity: {req.severity}

Recommended Hospital: {req.hospital_name}

Reason:
- ICU Available: {icu_status}
- Beds Available: {req.beds_available}
- Distance: {req.distance_km} km

Conclusion:
Hospital selected based on best resource availability and proximity."""
    return {"status": "success", "message": "Report generated successfully.", "report": report}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8050, reload=True)
