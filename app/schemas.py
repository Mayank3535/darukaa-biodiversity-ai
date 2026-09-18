from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SoilState(BaseModel):
    organic_carbon: Optional[float] = None
    unit: Optional[str] = None
    texture: Optional[str] = None
    ph: Optional[float] = None


class LandUseState(BaseModel):
    crop: Optional[str] = None
    system: Optional[str] = None
    area: Optional[float] = None
    area_unit: Optional[str] = None


class EnvironmentalState(BaseModel):
    region: Optional[str] = None
    rainfall: Optional[str] = None
    soil: SoilState = Field(default_factory=SoilState)
    land_use: LandUseState = Field(default_factory=LandUseState)
    biodiversity: Dict[str, Any] = Field(default_factory=dict)
    climate: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeRequest(BaseModel):
    query: Optional[str] = None
    region: Optional[str] = None
    rainfall: Optional[str] = None
    soil: Optional[SoilState] = None
    land_use: Optional[LandUseState] = None


class ChatRequest(BaseModel):
    session_id: str = "demo-user"
    message: str


class Evidence(BaseModel):
    title: str
    source_url: str
    organization: Optional[str] = None
    topic: Optional[str] = None
    supporting_point: str


class Recommendation(BaseModel):
    intervention: str
    rationale: str
    expected_effects: List[str]
    implementation: List[str]
    metrics: List[str]
    time_horizon: str
    tradeoffs: List[str]


class EnvironmentalAssessment(BaseModel):
    summary: str
    diagnosis: List[str]
    key_interactions: List[str]
    recommendation: Recommendation
    evidence: List[Evidence]
    assumptions: List[str]
    missing_information: List[str]
    confidence: str