from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class Location(BaseModel):
    lat: Optional[float]
    lng: Optional[float]
    address: Optional[str] = None
    radius: Optional[int] = None

class ParsedFields(BaseModel):
    incident_type: Optional[str]
    location: Optional[Location]
    injuries: Optional[int]
    hazards: Optional[List[str]]
    agencies_needed: Optional[List[str]]
    severity_estimate: Optional[int]
    key_details: Optional[str]

class Provenance(BaseModel):
    origin: str
    received_at: datetime
    last_confirmed: Optional[datetime]
    supporting_sources: List[str] = []
    contradicting_sources: List[str] = []

class Event(BaseModel):
    source_id: str
    source_type: str
    timestamp: datetime
    location: Location
    raw_text: str
    parsed_fields: ParsedFields
    confidence: float
    provenance: Provenance

class PriorityScore(BaseModel):
    value: int
    confidence: float
    breakdown: Dict[str, float]

class Incident(BaseModel):
    id: Optional[int]
    incident_type: Optional[str]
    location: Location
    priority: Optional[int]
    confidence: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    events: List[Event] = []
