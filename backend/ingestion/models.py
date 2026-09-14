from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Location(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    radius: int = 50  # Default radius in meters

class ParsedFields(BaseModel):
    incident_type: Optional[str] = None
    location: Optional[Location] = None
    injuries: Optional[int] = None
    hazards: List[str] = Field(default_factory=list)
    agencies_needed: List[str] = Field(default_factory=list)
    severity_estimate: Optional[int] = Field(None, ge=1, le=10) # Bounded 1-10
    key_details: Optional[str] = None

class Provenance(BaseModel):
    origin: str
    received_at: datetime
    last_confirmed: Optional[datetime] = None
    supporting_sources: List[str] = Field(default_factory=list)
    contradicting_sources: List[str] = Field(default_factory=list)

class Event(BaseModel):
    """
    An Event is a single piece of incoming data (e.g., one NWS alert, one 911 transcript).
    """
    source_id: str
    source_type: str  # e.g., 'nws', 'cad', 'manual'
    timestamp: datetime
    location: Location
    raw_text: str
    parsed_fields: ParsedFields
    confidence: float = Field(..., ge=0.0, le=1.0) # Bounded 0.0 to 1.0
    provenance: Provenance

class Incident(BaseModel):
    """
    An Incident is the ground-truth object built by fusing multiple Events together.
    """
    id: Optional[int] = None
    status: str = "active"
    incident_type: str
    location: Location
    priority_score: int = Field(0, ge=0, le=100)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    events: List[Event] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
