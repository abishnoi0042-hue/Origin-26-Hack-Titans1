from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class RiskAssessment(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    level: str = Field(..., description="Low, Moderate, High, Severe")
    color: str = Field(..., description="Hex code for risk level")
    primary_factors: List[str] = Field(default_factory=list)
    environmental_score: int = Field(..., ge=0, le=100)
    vulnerability_multiplier: float = Field(...)

class AdvisoryResponse(BaseModel):
    risk_level: str = Field(..., description="Low, Moderate, High, or Severe")
    risk_score: int = Field(..., ge=0, le=100, description="Calculated 0-100 risk score")
    summary: str = Field(..., description="Personalized explanation in plain English")
    outdoor_activity: str = Field(..., description="Outdoor activity recommendation")
    health_precautions: List[str] = Field(default_factory=list, description="Health specific precautions")
    weather_precautions: List[str] = Field(default_factory=list, description="Weather specific precautions")
    best_time_outside: str = Field(..., description="Best time to go outside today")
    things_to_avoid: List[str] = Field(default_factory=list, description="Activities or exposures to avoid")
    risk_breakdown: Optional[Dict[str, Any]] = None
    ai_provider: str = Field("rule_based_fallback", description="gemini, groq, or rule_based_fallback")
    disclaimer: str = Field(
        "This advisory is for informational purposes only and is not a substitute for professional medical advice.",
        description="Mandatory medical disclaimer"
    )
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class AdvisoryRequest(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str] = "Current Location"
    profile: Optional[Dict[str, Any]] = None
