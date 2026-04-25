import pandas as pd
import random

# Load datasets
try:
    hospitals_df = pd.read_csv('hospital_data_bangalore.csv')
    diseases_df = pd.read_csv('Disease_symptom_and_patient_profile_dataset.csv')
except FileNotFoundError:
    print("Ensure hospital_data_bangalore.csv and Disease_symptom_and_patient_profile_dataset.csv are in the current directory.")
    exit()

# Get unique diseases/symptoms
unique_diseases = diseases_df['Disease'].unique()

# Define a mapping from specializations to possible symptoms/diseases
specialization_map = {
    'Cardiac': ['Stroke', 'Chest Pain', 'Hypertension', 'Heart Attack'],
    'Respiratory': ['Asthma', 'Influenza', 'Common Cold', 'Allergic Rhinitis', 'Difficulty Breathing', 'Cough'],
    'General': ['Dengue Fever', 'Fever', 'Diabetes', 'Common Cold', 'Fatigue', 'Typhoid', 'Malaria'],
    'Oncology': ['Liver Cancer', 'Breast Cancer', 'Lung Cancer'],
    'Orthopedics': ['Rheumatoid Arthritis', 'Osteoarthritis', 'Bone Fracture', 'Joint Pain'],
    'Psychiatry': ['Anxiety Disorders', 'Depression', 'Bipolar Disorder'],
    'Dermatology': ['Eczema', 'Acne', 'Psoriasis', 'Skin Rash'],
    'Endocrinology': ['Hyperthyroidism', 'Hypothyroidism', 'Diabetes'],
    'Urology': ['Urinary Tract Infection', 'Kidney Stones', 'Prostate Issues'],
    'Gastroenterology': ['Pancreatitis', 'Gastroenteritis', 'Ulcer', 'Nausea', 'Stomach Ache'],
    'Neurology': ['Stroke', 'Migraine', 'Seizures', 'Headache'],
    'Pediatrics': ['Fever', 'Cough', 'Chickenpox', 'Measles'],
    'Maternity/Gynecology': ['Pregnancy Complications', 'PCOS', 'Pelvic Pain'],
    'Multi-specialty': ['Influenza', 'Asthma', 'Diabetes', 'Stroke', 'Liver Cancer', 'Pancreatitis', 'Fever', 'Fatigue'] 
}

symptom_pool = list(unique_diseases) + ['Fever', 'Cough', 'Fatigue', 'Difficulty Breathing', 'Headache', 'Chest Pain', 'Nausea', 'Vomiting']

def assign_specialization(hospital_name, hospital_type):
    name_lower = str(hospital_name).lower()
    type_lower = str(hospital_type).lower()
    
    # Keyword based matching for specialization
    if 'heart' in name_lower or 'cardiac' in name_lower: return 'Cardiac'
    if 'cancer' in name_lower or 'oncology' in name_lower: return 'Oncology'
    if 'eye' in name_lower or 'nethralaya' in name_lower: return 'Ophthalmology'
    if 'children' in name_lower or 'pediatric' in name_lower: return 'Pediatrics'
    if 'maternity' in name_lower or 'women' in name_lower or 'fertility' in name_lower or 'maternity' in type_lower: return 'Maternity/Gynecology'
    if 'ortho' in name_lower or 'bone' in name_lower: return 'Orthopedics'
    if 'gastro' in name_lower or 'gastroenterologist' in type_lower: return 'Gastroenterology'
    if 'neuro' in name_lower or 'brain' in name_lower: return 'Neurology'
    if 'kidney' in name_lower or 'urology' in name_lower or 'nephro' in name_lower: return 'Urology'
    if 'skin' in name_lower or 'derma' in name_lower: return 'Dermatology'
    
    # Based on hospital type
    if 'specialized' in type_lower:
        return random.choice(['Cardiac', 'Oncology', 'Neurology', 'Orthopedics', 'Multi-specialty', 'Gastroenterology'])
    if 'general' in type_lower:
        return 'General'
        
    # Default fallback
    return random.choice(['Multi-specialty', 'General', 'Multi-specialty'])

def get_supported_symptoms(spec):
    pool = specialization_map.get(spec, symptom_pool)
    # Ensure the pool is large enough
    if len(pool) < 3:
        pool = pool + random.sample(symptom_pool, 3)
    
    # Select 3 to 5 unique symptoms
    count = random.randint(3, 5)
    selected = random.sample(list(set(pool)), min(count, len(set(pool))))
    return ', '.join(selected)

new_hospitals = []

# Ensure reproducibility for realistic data
random.seed(42)

for idx, row in hospitals_df.iterrows():
    h_name = row['Hospital_name']
    if pd.isna(h_name):
        continue
    
    spec = assign_specialization(h_name, row['Type'])
    symp = get_supported_symptoms(spec)
    
    # Assign realistic ICU availability
    if spec in ['Cardiac', 'Neurology', 'Oncology', 'Multi-specialty', 'Gastroenterology', 'Respiratory', 'General']:
        icu = 'Yes' if random.random() > 0.2 else 'No' # 80% chance
    else:
        icu = 'Yes' if random.random() > 0.7 else 'No' # 30% chance
        
    # Assign realistic bed capacity
    beds = random.randint(5, 50)
    if spec == 'Multi-specialty':
        beds = random.randint(20, 50) # Multi-specialty hospitals are generally larger
        
    # Assign realistic wait times
    wait_time = random.randint(5, 60)
    
    new_hospitals.append({
        'hospital_name': h_name,
        'location': 'Bengaluru',
        'specialization': spec,
        'icu_available': icu,
        'beds_available': beds,
        'wait_time_minutes': wait_time,
        'supported_symptoms': symp
    })

new_df = pd.DataFrame(new_hospitals)
new_df.to_csv('structured_hospitals.csv', index=False)
print("Dataset generated successfully: structured_hospitals.csv")
