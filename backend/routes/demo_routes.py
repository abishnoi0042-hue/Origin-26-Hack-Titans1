from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/api/demo", tags=["demo"])

DEMO_SCENARIOS = [
    {
        "id": "healthy_adult",
        "title": "Healthy Adult",
        "badge": "Low Sensitivity",
        "badge_color": "emerald",
        "icon": "user-check",
        "description": "Standard physiological baseline. Tolerates normal ambient variations with standard hydration.",
        "profile": {
            "name": "Alex",
            "age_group": "Adult",
            "health_conditions": ["None"],
            "occupation": "Indoor Worker",
            "activity_level": "Moderate"
        }
    },
    {
        "id": "asthma_patient",
        "title": "Asthma Patient",
        "badge": "High Respiratory Risk",
        "badge_color": "amber",
        "icon": "wind",
        "description": "Hyper-reactive airways. Highly susceptible to PM2.5, ozone spikes, and abrupt weather transitions.",
        "profile": {
            "name": "Maya",
            "age_group": "Teen",
            "health_conditions": ["Asthma"],
            "occupation": "Student",
            "activity_level": "High"
        }
    },
    {
        "id": "outdoor_worker",
        "title": "Outdoor Worker",
        "badge": "Extreme Ambient Exposure",
        "badge_color": "orange",
        "icon": "hard-hat",
        "description": "Prolonged occupational exposure. Prone to heat stress, solar UV radiation, and continuous air pollution inhalation.",
        "profile": {
            "name": "Carlos",
            "age_group": "Adult",
            "health_conditions": ["Allergies"],
            "occupation": "Outdoor Worker",
            "activity_level": "High"
        }
    },
    {
        "id": "elderly_person",
        "title": "Elderly Person",
        "badge": "Severe Vulnerability",
        "badge_color": "red",
        "icon": "shield-alert",
        "description": "Reduced thermoregulation and cardiac reserves. Highly vulnerable to temperature extremes and poor air quality.",
        "profile": {
            "name": "Eleanor",
            "age_group": "Elderly",
            "health_conditions": ["Heart Disease", "Respiratory Problems"],
            "occupation": "Other",
            "activity_level": "Low"
        }
    }
]

@router.get("/scenarios", response_model=List[Dict[str, Any]])
def get_demo_scenarios():
    """Return pre-configured demonstration scenarios for testing personalization."""
    return DEMO_SCENARIOS
