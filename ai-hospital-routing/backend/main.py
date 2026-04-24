from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="MedRoute AI - Smart Hospital Routing API",
    description="API for routing patients to the best hospitals based on severity and live availability.",
    version="1.0.0"
)

# Configure CORS to allow the frontend to interact with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with the specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to MedRoute AI API. Use POST /api/v1/predict to get hospital recommendations."
    }

if __name__ == "__main__":
    import uvicorn
    # Start the server locally
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8050, reload=True)
