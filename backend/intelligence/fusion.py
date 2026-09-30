from datetime import datetime, timezone
from typing import List, Optional

from backend.models import Event, Incident, Location
from backend.config import config
from backend.intelligence.extraction import extract_parsed_fields
from backend.intelligence.confidence import compute_event_confidence
from backend.intelligence.priority import compute_priority_score


INCIDENTS: List[Incident] = []
INCIDENT_META: dict = {}  # id -> {previous_priority, confirmed, human_priority}
_next_id = 1

TYPE_SEVERITY_RANK = {
    "Structure Fire": 90,
    "HazMat Incident": 85,
    "Medical Emergency": 80,
    "Traffic Incident": 60,
    "Flooding / Road Hazard": 50,
    "Weather": 20,
}


def reset_state():
    global _next_id
    INCIDENTS.clear()
    INCIDENT_META.clear()
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


# Scene classes: incidents of different classes at the same spot are
# separate events (e.g. a house fire next to a highway crash).
_ROAD = {"Traffic Incident", "Flooding / Road Hazard", "HazMat Incident"}
_FIRE = {"Structure Fire"}


def types_compatible(incident_type: Optional[str], event_type: Optional[str]) -> bool:
    if not incident_type or not event_type or incident_type == event_type:
        return True
    if incident_type in _ROAD and event_type in _ROAD:
        return True
    # A medical call is usually a consequence of the scene it is reported at
    if "Medical Emergency" in (incident_type, event_type):
        return True
    return False


def find_matching_incident(event: Event) -> Optional[Incident]:
    """Nearest incident that is close in space and time and of a compatible type."""
    best, best_dist = None, None
    for incident in INCIDENTS:
        if not is_spatially_close(event.location, incident.location):
            continue

        ref_time = incident.updated_at or incident.created_at
        if ref_time and not is_temporally_close(event.timestamp, ref_time):
            continue

        if not types_compatible(incident.incident_type, event.parsed_fields.incident_type):
            continue

        dist = haversine_distance_m(
            event.location.lat, event.location.lng,
            incident.location.lat, incident.location.lng,
        )
        if best is None or dist < best_dist:
            best, best_dist = incident, dist

    return best


def process_event(event: Event) -> Incident:
    global _next_id

    event.parsed_fields = extract_parsed_fields(event, use_llm=False)
    # Blend the source's self-reported confidence with our computed score
    reported = event.confidence
    event.confidence = (reported + compute_event_confidence(event, [])) / 2

    matching = find_matching_incident(event)
    now = datetime.now(timezone.utc)

    if matching:
        existing_ids = {e.source_id for e in matching.events}
        if event.source_id in existing_ids:
            return matching

        INCIDENT_META.setdefault(matching.id, {})["previous_priority"] = matching.priority

        matching.events.append(event)
        event.confidence = (reported + compute_event_confidence(event, matching.events)) / 2
        matching.confidence = sum(e.confidence for e in matching.events) / len(matching.events)

        new_type = event.parsed_fields.incident_type
        if new_type:
            cur_rank = TYPE_SEVERITY_RANK.get(matching.incident_type, 0)
            new_rank = TYPE_SEVERITY_RANK.get(new_type, 0)
            if new_rank > cur_rank:
                matching.incident_type = new_type

        meta = INCIDENT_META[matching.id]
        priority_score = compute_priority_score(matching)
        meta["ai_priority"] = priority_score.value
        if not meta.get("confirmed"):
            matching.priority = priority_score.value
        elif priority_score.value != meta.get("confirmed_ai_priority"):
            # Human confirmed/adjusted earlier; keep their number but flag
            # that new evidence has arrived since.
            meta["stale_confirmation"] = True

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
