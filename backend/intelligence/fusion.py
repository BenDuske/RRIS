from datetime import datetime, timezone
from typing import List, Optional

from backend.models import Event, Incident, Location
from backend.config import config
from backend.intelligence.extraction import extract_parsed_fields
from backend.intelligence.confidence import compute_event_confidence
from backend.intelligence.priority import compute_priority_score


INCIDENTS: List[Incident] = []
_next_id = 1


def haversine_distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    from math import radians, sin, cos, sqrt, atan2

    R = 6371000
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


def find_matching_incident(event: Event) -> Optional[Incident]:
    for incident in INCIDENTS:
        if not is_spatially_close(event.location, incident.location):
            continue

        ref_time = incident.updated_at or incident.created_at
        if ref_time and not is_temporally_close(event.timestamp, ref_time):
            continue

        return incident

    return None


def process_event(event: Event) -> Incident:
    global _next_id

    event.parsed_fields = extract_parsed_fields(event, use_llm=False)
    event.confidence = compute_event_confidence(event, [])

    matching = find_matching_incident(event)
    now = datetime.now(timezone.utc)

    if matching:
        matching.events.append(event)
        event.confidence = compute_event_confidence(event, matching.events)
        matching.confidence = sum(e.confidence for e in matching.events) / len(matching.events)

        if event.parsed_fields.incident_type and not matching.incident_type:
            matching.incident_type = event.parsed_fields.incident_type

        priority_score = compute_priority_score(matching)
        matching.priority = priority_score.value
        matching.updated_at = now
        return matching

    incident = Incident(
        id=_next_id,
        incident_type=event.parsed_fields.incident_type,
        location=event.location,
        priority=0,
        confidence=event.confidence,
        created_at=now,
        updated_at=now,
        events=[event],
    )
    _next_id += 1

    priority_score = compute_priority_score(incident)
    incident.priority = priority_score.value

    INCIDENTS.append(incident)
    return incident
