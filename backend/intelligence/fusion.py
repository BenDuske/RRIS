from datetime import datetime, timezone
from typing import List, Optional

from backend.models import Event, Incident, PriorityScore, Location
from backend.intelligence.config import config
from backend.intelligence.extraction import extract_parsed_fields
from backend.intelligence.confidence import compute_event_confidence
from backend.intelligence.priority import compute_priority_score
from backend.intelligence.explainability import build_incident_explainability


# In-memory incident store for now (can be replaced with DB later)
INCIDENTS: List[Incident] = []


# ---------------------------------------------------------------------------
# 1. Distance & Time Helpers
# ---------------------------------------------------------------------------

def haversine_distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Rough haversine distance in meters between two lat/lng points.
    Good enough for clustering in a single city.
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371000  # Earth radius in meters

    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def is_spatially_close(loc1: Location, loc2: Location) -> bool:
    if loc1.lat is None or loc1.lng is None or loc2.lat is None or loc2.lng is None:
        return False

    dist = haversine_distance_m(loc1.lat, loc1.lng, loc2.lat, loc2.lng)
    return dist <= config.fusion_distance_threshold_m


def is_temporally_close(t1: datetime, t2: datetime) -> bool:
    delta = abs((t2 - t1).total_seconds())
    return delta <= config.fusion_time_threshold_s


# ---------------------------------------------------------------------------
# 2. Find Matching Incident
# ---------------------------------------------------------------------------

def find_matching_incident(event: Event) -> Optional[Incident]:
    """
    Finds an existing incident that this event should be fused into,
    based on time, location, and incident_type.
    """

    for incident in INCIDENTS:
        if incident.incident_type and event.parsed_fields
