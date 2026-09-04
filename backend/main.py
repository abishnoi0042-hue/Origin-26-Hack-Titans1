import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes.weather_routes import router as weather_router
from routes.advisory_routes import router as advisory_router
from routes.demo_routes import router as demo_router

app = FastAPI(
    title="AeroHealth AI Backend",
    description="Personalized Weather & AQI Health Advisory System API",
    version="1.0.0"
)

# CORS configuration to allow local frontend and demo deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(weather_router)
app.include_router(advisory_router)
app.include_router(demo_router)

@app.get("/")
def root():
    return {
        "service": "AeroHealth AI Backend",
        "tagline": "Because environmental risk is personal.",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health_check():
    gemini_configured = bool(os.getenv("GEMINI_API_KEY", "").strip())
    groq_configured = bool(os.getenv("GROQ_API_KEY", "").strip())
    openweather_configured = bool(os.getenv("OPENWEATHER_API_KEY", "").strip())

    return {
        "status": "healthy",
        "ai_engine": {
            "gemini": gemini_configured,
            "groq": groq_configured,
            "rule_based_fallback": True
        },
        "apis": {
            "open_meteo": "active",
            "open_meteo_aqi": "active",
            "openweather_custom_key": openweather_configured
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
