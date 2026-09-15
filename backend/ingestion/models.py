from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class Location(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    radius: Optional[int] = 50  # Defaulted to 50 meters

class ParsedFields(BaseModel):
    incident_type: Optional[str] = None
    location: Optional[Location] = None
    injuries: Optional[int] = None
    hazards: List[str] = Field(default_factory=list)  # Prevents shared list bug
    agencies_needed: List[str] = Field(default_factory=list)
    severity_estimate: Optional[int] = Field(None, ge=1, le=10) # 1-10 scale
    key_details: Optional[str] = None

class Provenance(BaseModel):
    origin: str
    received_at: datetime
    last_confirmed: Optional[datetime] = None
    supporting_sources: List[str] = Field(default_factory=list)
    contradicting_sources: List[str] = Field(default_factory=list)

class Event(BaseModel):
    source_id: str
    source_type: str
    timestamp: datetime
    location: Location
    raw_text: str
    parsed_fields: ParsedFields
    confidence: float = Field(..., ge=0.0, le=1.0) # 0.0 to 1.0 scale
    provenance: Provenance

class PriorityScore(BaseModel):
    value: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    breakdown: Dict[str, float] = Field(default_factory=dict)

class Incident(BaseModel):
    id: Optional[int] = None
    incident_type: Optional[str] = None
    location: Location
    priority: Optional[int] = Field(None, ge=0, le=100)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    events: List[Event] = Field(default_factory=list)
