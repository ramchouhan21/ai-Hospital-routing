from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import random
import uvicorn

app = FastAPI(title="Advanced Hospital Recommendation System")

# Global state to simulate dynamic behavior (database substitute)
hospitals_db = []

def load_data():
    global hospitals_db
    try:
        df = pd.read_csv('structured_hospitals.csv')
        hospitals_db = df.to_dict('records')
        
        # Ensure numerical types
        for h in hospitals_db:
            h['beds_available'] = int(h['beds_available'])
            h['wait_time_minutes'] = int(h['wait_time_minutes'])
    except Exception as e:
        print(f"Error loading dataset: {e}")
        hospitals_db = []

load_data()

class RecommendRequest(BaseModel):
    symptoms: List[str]

# STEP 2: SYMPTOM -> SEVERITY MAPPING
CRITICAL_SYMPTOMS = ['chest pain', 'heart attack', 'breathing issue', 'stroke', 'difficulty breathing']
MODERATE_SYMPTOMS = ['fever', 'infection', 'injury', 'nausea', 'vomiting']
LOW_SYMPTOMS = ['cold', 'headache', 'fatigue', 'common cold', 'cough']

def get_severity(symptoms: List[str]):
    severity_level = 'Low'
    severity_priority = 0.3
    
    for sym in symptoms:
        sym_lower = sym.lower()
        if sym_lower in CRITICAL_SYMPTOMS:
            return 'Critical', 1.0  # Immediately return if critical is found
        elif sym_lower in MODERATE_SYMPTOMS:
            severity_level = 'Moderate'
            severity_priority = 0.6
            
    return severity_level, severity_priority

@app.post("/recommend-hospital")
def recommend_hospital(req: RecommendRequest):
    global hospitals_db
    
    if not hospitals_db:
        raise HTTPException(status_code=500, detail="Database not loaded.")
        
    symptoms = req.symptoms
    if not symptoms:
        raise HTTPException(status_code=400, detail="No symptoms provided.")
        
    severity_level, severity_priority = get_severity(symptoms)
    
    # STEP 7: EDGE CASE - All Full
    if all(h['beds_available'] <= 0 for h in hospitals_db):
        return {"message": "ALERT: ALL HOSPITALS ARE FULL. PLEASE CALL EMERGENCY SERVICES IMMEDIATELY."}
        
    # STEP 7: EDGE CASE - No ICU when Critical
    if severity_level == 'Critical':
        has_icu_available = any((h['icu_available'].lower() == 'yes' and h['beds_available'] > 0) for h in hospitals_db)
        if not has_icu_available:
            # Fallback: return hospital with max beds
            max_beds_h = max((h for h in hospitals_db if h['beds_available'] > 0), key=lambda x: x['beds_available'])
            
            # Dynamic Behavior
            max_beds_h['beds_available'] -= 1
            max_beds_h['wait_time_minutes'] += 10
            
            return {
                "severity": severity_level,
                "recommended": [{
                    "hospital": max_beds_h['hospital_name'],
                    "score": 0.0,
                    "reason": "CRITICAL EMERGENCY: No ICUs available in city. Routed to hospital with maximum beds.",
                    "why_others_lower": "N/A - Emergency Fallback"
                }]
            }

    candidates = []
    
    # STEP 3 & 4: FILTER AND SCORE
    for h in hospitals_db:
        if h['beds_available'] <= 0:
            continue  # Skip full hospitals
            
        supported = [s.strip().lower() for s in str(h['supported_symptoms']).split(',')]
        spec = str(h['specialization']).lower()
        
        # Filtering logic: Match symptoms OR is a general/multi-specialty hospital
        matches_symptom = any(sym.lower() in supported for sym in symptoms)
        is_general = (spec == 'general' or spec == 'multi-specialty')
        
        if not (matches_symptom or is_general):
            continue  # Remove irrelevant hospitals
            
        # Scoring components
        icu_score = 1.0 if h['icu_available'].lower() == 'yes' else 0.0
        
        # Distance (simulate random realistic value 1km - 25km)
        distance_km = random.uniform(1.0, 25.0)
        dist_score = max(0, 1 - (distance_km / 25.0)) # Closer = higher score
        
        # Wait time (lower is better, max assumed 120 mins for normalization)
        wait_time = h['wait_time_minutes']
        wait_score = max(0, 1 - (wait_time / 120.0))
        
        # Final Score Calculation
        score = (0.4 * severity_priority) + (0.25 * icu_score) + (0.2 * dist_score) + (0.15 * wait_score)
        
        candidates.append({
            'hospital_ref': h,
            'score': round(score, 3),
            'distance_km': round(distance_km, 1),
            'icu_score': icu_score,
            'wait_score': wait_score,
            'matches_symptom': matches_symptom
        })
        
    # STEP 7: EDGE CASE - No Match
    if not candidates:
        # Fallback to a general hospital
        fallback_candidates = [h for h in hospitals_db if h['beds_available'] > 0 and str(h['specialization']).lower() == 'general']
        if fallback_candidates:
            selected = max(fallback_candidates, key=lambda x: x['beds_available'])
            
            selected['beds_available'] -= 1
            selected['wait_time_minutes'] += 10
            
            return {
                "severity": severity_level,
                "recommended": [{
                    "hospital": selected['hospital_name'],
                    "score": 0.0,
                    "reason": "No exact symptom match found. Routed to General hospital with available beds.",
                    "why_others_lower": "N/A - Fallback"
                }]
            }
        else:
            return {"message": "No suitable hospitals found."}

    # Sort by highest score
    candidates.sort(key=lambda x: x['score'], reverse=True)
    top_3 = candidates[:3]
    
    # STEP 6: DYNAMIC BEHAVIOR
    # We assume the user goes to the #1 recommended hospital, so we update its stats
    top_choice = top_3[0]['hospital_ref']
    top_choice['beds_available'] -= 1
    top_choice['wait_time_minutes'] += random.randint(5, 15)
    
    # STEP 5: FORMAT OUTPUT
    response_data = []
    
    for i, c in enumerate(top_3):
        h = c['hospital_ref']
        
        # Determine "Why selected"
        reasons = []
        if c['icu_score'] == 1: reasons.append("ICU available")
        if c['wait_score'] > 0.7: reasons.append("low wait time")
        if c['matches_symptom']: reasons.append("matches symptoms")
        else: reasons.append("multi-specialty fallback")
        if c['distance_km'] < 5.0: reasons.append("very close distance")
        
        # Determine "Why others ranked lower"
        why_others_lower = "N/A (Top Choice)"
        if i > 0:
            top_c = top_3[0]
            negatives = []
            if c['distance_km'] > top_c['distance_km']: negatives.append("Further away")
            if h['wait_time_minutes'] > top_c['hospital_ref']['wait_time_minutes']: negatives.append("Longer wait time")
            if c['icu_score'] < top_c['icu_score']: negatives.append("Lacks ICU")
            
            why_others_lower = " + ".join(negatives) if negatives else "Slightly lower overall weighted score"
            
        response_data.append({
            "hospital": h['hospital_name'],
            "score": c['score'],
            "distance_km": c['distance_km'],
            "wait_time": h['wait_time_minutes'],
            "beds_left": h['beds_available'], # This will show the updated value for the top choice
            "reason": " + ".join(reasons),
            "why_others_lower": why_others_lower
        })

    return {
        "severity": severity_level,
        "recommended": response_data
    }

# Provide an example of how to test it locally
if __name__ == "__main__":
    print("="*50)
    print("🚀 Starting Advanced Recommendation API...")
    print("Test with: curl -X POST http://127.0.0.1:8000/recommend-hospital -H 'Content-Type: application/json' -d '{\"symptoms\": [\"chest pain\", \"breathing issue\"]}'")
    print("="*50)
    uvicorn.run(app, host="127.0.0.1", port=8000)
