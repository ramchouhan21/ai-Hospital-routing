from advanced_recommendation_api import recommend_hospital, RecommendRequest
import json

def test_api():
    print("\n--- TEST 1: CRITICAL SYMPTOMS ---")
    req = RecommendRequest(symptoms=["chest pain", "breathing issue"])
    response = recommend_hospital(req)
    print(json.dumps(response, indent=2))
    
    print("\n--- TEST 2: LOW SYMPTOMS ---")
    req = RecommendRequest(symptoms=["headache"])
    response = recommend_hospital(req)
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    test_api()
