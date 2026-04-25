from geopy.distance import geodesic
import os

def analyze_severity(symptoms: str):
    """
    NLP keyword-based severity analyzer.
    Categorizes into High (Critical), Medium, Low.
    """
    symptoms_lower = symptoms.lower()
    
    high_keywords = [
        "pregnancy", "pregnant", "accident", "heart attack", "unconscious", 
        "breath", "breathing issue", "stroke", "severe", "bleeding", 
        "seizure", "chest pain"
    ]
    medium_keywords = [
        "vomiting", "dizzy", "fracture", "cut", "burn", "infection", "severe pain"
    ]
    low_keywords = [
        "fever", "headache", "cold", "leg pain", "hand pain", "normal", 
        "cough", "mild", "pain"
    ]
    
    is_high = any(kw in symptoms_lower for kw in high_keywords)
    is_medium = any(kw in symptoms_lower for kw in medium_keywords)
    
    # Priority checks
    if is_high:
        return "High", True
    elif is_medium:
        return "Medium", False
    else:
        # Default to Low for normal/minor symptoms
        return "Low", False

def generate_report(symptoms, severity, hospital):
    """
    Automatically generate a patient report.
    """
    icu_status = "Yes" if hospital.get("available_icu_beds", 0) > 0 else "No"
    
    report = f"""Patient Report

Symptoms: {symptoms}
Severity: {severity}

Recommended Hospital: {hospital.get('name')}

Reason:
- ICU Available: {icu_status}
- Beds Available: {hospital.get('available_beds', 0)}
- Distance: {hospital.get('distance_km', 0)}

Conclusion:
Hospital selected based on best resource availability and proximity."""
    
    return report

def find_best_hospitals(user_lat, user_lng, symptoms, hospitals_data):
    """
    Filters and ranks hospitals using a scoring-based algorithm.
    """
    severity_raw, is_critical = analyze_severity(symptoms)
    
    # Map frontend severity to scoring logic severity
    if severity_raw == "High":
        severity = "critical"
    elif severity_raw == "Medium":
        severity = "moderate"
    else:
        severity = "low"
        
    ranked_hospitals = []
    
    for h in hospitals_data:
        distance = float(h.get('distance', 0))
        icu_available = int(h.get('icu_available', 0))
        beds_available = int(h.get('beds_available', 0))
        h_type = h.get('type', 'general')
        name = h.get('name', 'Unknown Hospital')
        
        # Implementing scoring logic based on requirements
        score = 0
        
        # 1. Severity-based matching
        if severity == "critical":
            if icu_available == 1:
                score += 50
            else:
                score -= 50
                
            # Critical patients need emergency or multispecialty
            if h_type in ["emergency", "multispecialty"]:
                score += 40
            elif h_type == "clinic":
                score -= 100 # Clinics cannot handle critical emergencies
                
            score += beds_available * 2
            
        elif severity == "moderate":
            if h_type in ["general", "government", "multispecialty"]:
                score += 30
            elif h_type == "clinic":
                score -= 10
                
            score += beds_available * 3
            
        else: # low severity
            # Minor issues should go to clinics or general hospitals to save emergency resources
            if h_type in ["clinic", "general", "government"]:
                score += 40
            elif h_type == "emergency":
                score -= 40 # Heavily penalize going to ER for a cold
                
            score += beds_available * 1
            
        # 2. Distance scoring (closer is always better)
        score += max(0, 30 - distance * 3)
        
        # 3. Symptom-specific routing
        symptoms_lower = symptoms.lower()
        if "heart" in symptoms_lower or "stroke" in symptoms_lower or "chest pain" in symptoms_lower:
            if h_type == "multispecialty":
                score += 35
                
        if "fracture" in symptoms_lower or "accident" in symptoms_lower or "bleeding" in symptoms_lower or "burn" in symptoms_lower:
            if h_type == "emergency":
                score += 35
                
        if "pregnancy" in symptoms_lower or "pregnant" in symptoms_lower:
            if h_type in ["multispecialty", "general"]:
                score += 25
        
        # Provide fallback coordinates for UI Google Maps linking
        mock_lat = user_lat + (distance * 0.005)
        mock_lng = user_lng + (distance * 0.005)
        
        ranked_hospitals.append({
            "id": h.get("id"),
            "name": name,
            "latitude": mock_lat,
            "longitude": mock_lng,
            "distance_km": distance,
            "estimated_time_mins": int(distance * 2),
            "available_beds": beds_available,
            "available_icu_beds": icu_available,
            "traffic_level": "Medium",
            "has_icu": icu_available == 1,
            "specialties": str(h_type).capitalize(),
            "score": score
        })
    
    # Select the hospital with the highest score
    ranked_hospitals.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "severity": severity_raw,
        "is_critical": is_critical,
        "recommendations": ranked_hospitals
    }
