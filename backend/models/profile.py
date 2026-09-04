from pydantic import BaseModel, Field
from typing import List, Optional

class UserProfile(BaseModel):
    age_group: str = Field("Adult", description="Child, Teen, Adult, Elderly")
    health_conditions: List[str] = Field(default_factory=lambda: ["None"], description="List of conditions: None, Asthma, Heart Disease, Respiratory Problems, Allergies")
    occupation: str = Field("Indoor Worker", description="Indoor Worker, Outdoor Worker, Student, Athlete, Other")
    activity_level: str = Field("Moderate", description="Low, Moderate, High")
    name: Optional[str] = Field(None, description="Optional user name or alias")

    # Helper properties
    def has_condition(self, condition: str) -> bool:
        return any(c.lower() == condition.lower() for c in self.health_conditions)

    @property
    def is_vulnerable_age(self) -> bool:
        return self.age_group in ["Child", "Elderly"]

    @property
    def is_outdoor_exposed(self) -> bool:
        return self.occupation in ["Outdoor Worker", "Athlete"]
