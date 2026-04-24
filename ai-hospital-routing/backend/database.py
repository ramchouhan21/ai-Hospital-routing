import pandas as pd
import os

# Get absolute path to the CSV file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "hospitals.csv")

def load_hospitals():
    """
    Load hospitals data from CSV.
    In a real app, this would connect to a real database system.
    """
    try:
        df = pd.read_csv(CSV_PATH)
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []
