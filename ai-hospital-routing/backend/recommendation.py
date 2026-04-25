import pandas as pd

def recommend_hospitals(user_symptoms, severity_score, required_icu=False):
    """
    Recommend top 3 hospitals based on user symptoms, severity, and ICU requirement.
    
    Inputs:
    - user_symptoms: list of strings (e.g., ['Fever', 'Cough'])
    - severity_score: integer from 1 to 10
    - required_icu: boolean, whether ICU is strictly needed
    
    Process:
    - Match user symptoms with hospital supported_symptoms
    - Calculate score based on symptom matches, wait time, and available beds
    - Sort and return top 3
    """
    try:
        df = pd.read_csv('structured_hospitals.csv')
    except FileNotFoundError:
        print("Dataset structured_hospitals.csv not found. Please run generate_dataset.py first.")
        return []
    
    # Filter by ICU if strictly required
    if required_icu:
        df = df[df['icu_available'] == 'Yes']
        
    recommendations = []
    
    for idx, row in df.iterrows():
        # Parse supported symptoms into a clean list
        supported = [s.strip().lower() for s in str(row['supported_symptoms']).split(',')]
        
        # Count how many of the user's symptoms the hospital supports
        matches = sum(1 for sym in user_symptoms if sym.lower() in supported)
        
        # Only consider hospitals that match at least one symptom
        if matches > 0:
            # Score formula:
            # + 15 points per matched symptom
            # + 0.1 points per available bed (more beds = higher capacity)
            # - Penalty for wait time: penalty is harsher if severity is high
            wait_penalty_multiplier = 0.5 if severity_score > 7 else 0.2
            wait_penalty = row['wait_time_minutes'] * wait_penalty_multiplier
            
            score = (matches * 15) + (row['beds_available'] * 0.1) - wait_penalty
            
            recommendations.append({
                'hospital_name': row['hospital_name'],
                'location': row['location'],
                'specialization': row['specialization'],
                'wait_time_minutes': row['wait_time_minutes'],
                'beds_available': row['beds_available'],
                'icu_available': row['icu_available'],
                'match_score': round(score, 2),
                'matched_symptoms': matches
            })
            
    # Sort by match score descending
    recommendations = sorted(recommendations, key=lambda x: x['match_score'], reverse=True)
    
    # Return top 3
    return recommendations[:3]

# --- Example Usage ---
if __name__ == "__main__":
    test_symptoms = ['Fever', 'Common Cold', 'Difficulty Breathing']
    severity = 8 # High severity (1-10)
    needs_icu = True
    
    print("="*50)
    print(f"SEARCHING HOSPITALS...")
    print(f"Symptoms: {', '.join(test_symptoms)}")
    print(f"Severity: {severity}/10")
    print(f"ICU Required: {'Yes' if needs_icu else 'No'}")
    print("="*50)
    
    top_hospitals = recommend_hospitals(test_symptoms, severity, needs_icu)
    
    if not top_hospitals:
        print("\nNo matching hospitals found based on the criteria.")
    else:
        for i, h in enumerate(top_hospitals, 1):
            print(f"\n{i}. {h['hospital_name']} ({h['specialization']})")
            print(f"   Location: {h['location']}")
            print(f"   Match Score: {h['match_score']}")
            print(f"   Wait time: {h['wait_time_minutes']} mins")
            print(f"   Beds Available: {h['beds_available']}")
            print(f"   ICU: {h['icu_available']}")
            print(f"   Matched Symptoms: {h['matched_symptoms']}")
    print("\n" + "="*50)
