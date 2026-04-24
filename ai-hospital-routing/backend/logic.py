from geopy.distance import geodesic

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

def find_best_hospitals(user_lat, user_lng, symptoms, hospitals_data):
    """
    Filters and ranks hospitals based on distance, traffic, ICU beds, and severity.
    """
    severity, is_critical = analyze_severity(symptoms)
    ranked_hospitals = []
    
    for h in hospitals_data:
        h_lat = float(h['latitude'])
        h_lng = float(h['longitude'])
        
        # Calculate distance
        distance_km = geodesic((user_lat, user_lng), (h_lat, h_lng)).kilometers
        
        available_beds = int(h.get('available_beds', 0))
        available_icu_beds = int(h.get('available_icu_beds', 0))
        has_icu = str(h.get('has_icu')).lower() == 'true'
        has_trauma = str(h.get('has_trauma')).lower() == 'true'
        traffic_level = str(h.get('traffic_level', 'Medium')).title()
        
        # CRITICAL CONDITION FILTERING
        if severity == "High":
            # Must have ICU beds OR Trauma
            # If a hospital is nearby but has 0 ICU beds/Normal beds, SKIP IT!
            if available_icu_beds <= 0 or available_beds <= 0:
                continue
            if not (has_icu or has_trauma or "maternity" in str(h.get("specialties", "")).lower()):
                continue

        # LOW/MEDIUM CONDITION FILTERING
        # Skip if no normal beds
        if available_beds <= 0:
            continue
            
        # Traffic time multiplier estimation
        # Low traffic: 2 mins/km, Medium: 4 mins/km, High: 7 mins/km
        traffic_multiplier = 4
        if traffic_level == "Low":
            traffic_multiplier = 2
        elif traffic_level == "High":
            traffic_multiplier = 7
            
        estimated_time_mins = int(distance_km * traffic_multiplier)
        
        # Scoring Algorithm (Lower is better)
        # Primary factor is TIME (not just distance). 
        # Secondary factor: subtract a tiny bit for more beds so it acts as a tie-breaker.
        score = estimated_time_mins - (available_icu_beds * 0.5 if severity == "High" else available_beds * 0.1)
        
        ranked_hospitals.append({
            "id": h["id"],
            "name": h["name"],
            "latitude": h["latitude"],
            "longitude": h["longitude"],
            "distance_km": round(distance_km, 2),
            "estimated_time_mins": estimated_time_mins,
            "available_beds": available_beds,
            "available_icu_beds": available_icu_beds,
            "traffic_level": traffic_level,
            "has_icu": has_icu,
            "specialties": str(h.get("specialties")),
            "score": score
        })
    
    # Sort by lowest score (fastest arrival + best capability)
    ranked_hospitals.sort(key=lambda x: x["score"])
    
    return {
        "severity": severity,
        "is_critical": is_critical,
        "recommendations": ranked_hospitals[:4] # Return top 4
    }
