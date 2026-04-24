# AI-Powered Hospital Routing System

A premium, full-stack smart healthcare routing application that instantly analyzes patient symptoms and live hospital capacities to guide them to the most appropriate medical facility in critical moments.

## Project Structure

```
ai-hospital-routing/
│
├── backend/                 # FastAPI Backend Engine
│   ├── main.py              # Application entry point
│   ├── routes.py            # API endpoints (/predict)
│   ├── logic.py             # Severity NLP analysis + distance scoring
│   ├── database.py          # Hospital dataset loader
│   └── hospitals.csv        # Mock dataset with beds and ICU data
│
├── frontend/                # Premium HTML/CSS/JS Frontend
│   ├── index.html           # Landing page with dynamic hero & trusted features
│   ├── input.html           # Input form, voice recognition, GPS & results view
│   ├── style.css            # Custom CSS properties and modern styling
│   ├── script.js            # Global scripts (Smooth scroll, SOS logic)
│   └── input.js             # Voice API, GPS, and mock frontend-backend logic
│
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Features

### Frontend (User Experience)
* **Real-World Medical Grade UI**: Custom-built using `HTML`, `CSS`, and `JavaScript` (no generic templates). Features soft shadows, premium typography (`Inter`), and modern spacing.
* **Smart Input Methods**: Supports standard text input and native **Voice Recognition** (Microphone) for fast symptom entry.
* **Live GPS Detection**: One-click precise geolocation.
* **SOS Button**: Immediate, floating emergency dialer (`tel:108`).
* **Visual Triage**: Color-coded severity badges (Critical, Moderate, Mild).

### Backend (AI Routing Engine)
* **FastAPI Powered**: Highly performant, async Python web framework.
* **NLP Keyword Triage**: Automatically parses symptoms (e.g. "chest pain", "fever") into clinical severity tiers.
* **Geospatial Distance Scoring**: Uses `geopy` to calculate the exact distance to hospitals.
* **Smart Filtering**: Automatically filters out hospitals without available beds, and enforces ICU/Trauma center requirements for Critical patients.

## How to Run

### 1. Start the Backend
1. Ensure Python 3.9+ is installed.
2. Navigate to the root folder: `cd ai-hospital-routing`
3. Install dependencies: 
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn backend.main:app --reload
   ```
5. The API will be live at `http://localhost:8000`.

### 2. Launch the Frontend
Simply open `frontend/index.html` in any modern web browser. No local web server is strictly required for the UI, but using an extension like *Live Server* in VSCode is recommended for the best experience.

## Why this is different
This is not just a form. It’s an interactive, simulated environment built exactly how a modern health-tech startup would deploy a life-saving tool, perfectly bridging the gap between immediate accessibility and powerful backend routing intelligence.
