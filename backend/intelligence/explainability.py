from typing import Dict, List
from backend.models import Event, Incident, PriorityScore
from backend.config import config


# ---------------------------------------------------------------------------
# 1. Event Confidence Explanation
# ---------------------------------------------------------------------------

def explain_event_confidence(event: Event, related_events: List[Event]) -> Dict:
    """
    Produces a human-readable explanation of how the confidence score was computed.
    """

    explanation = {
        "source_type": event.source_type,
        "source_reliability": f"Source '{event.source_type}' has reliability score based on predefined trust levels.",
        "recency": f"Event timestamp {event.timestamp} compared against current time.",
        "consistency": "Compared incident_type and key details against other related events.",
        "provenance": {
            "supporting_sources": event.provenance.supporting_sources,
            "contradicting_sources": event.provenance.contradicting_sources,
        },
        "final_confidence": event.confidence,
    }

    return explanation


# ---------------------------------------------------------------------------
# 2. Priority Score Explanation
# ---------------------------------------------------------------------------

def explain_priority_score(score: PriorityScore) -> Dict:
    """
    Converts the priority score breakdown into a readable explanation.
    """

    readable = {
        "priority_value": score.value,
        "confidence": score.confidence,
        "breakdown": {},
    }

    for factor, weight in score.breakdown.items():
        readable["breakdown"][factor] = f"Factor '{factor}' contributed {weight:.2f} to the final score."

    return readable


# ---------------------------------------------------------------------------
# 3. Fusion Decision Explanation
# ---------------------------------------------------------------------------

def explain_fusion_decision(event: Event, incident: Incident, reason: str) -> Dict:
    """
    Explains why an event was merged into an incident.
    """

    return {
        "event_id": event.source_id,
        "incident_id": incident.id,
        "reason": reason,
        "event_location": {
            "lat": event.location.lat,
            "lng": event.location.lng,
            "radius": event.location.radius,
        },
        "incident_location": {
            "lat": incident.location.lat,
            "lng": incident.location.lng,
            "radius": incident.location.radius,
        },
        "event_timestamp": event.timestamp,
        "incident_last_update": incident.updated_at,
    }


# ---------------------------------------------------------------------------
# 4. Incident Update Explanation
# ---------------------------------------------------------------------------

def explain_incident_update(incident: Incident, new_event: Event) -> Dict:
    """
    Explains how the incident changed after adding a new event.
    """

    return {
        "incident_id": incident.id,
        "new_event_id": new_event.source_id,
        "changes": {
            "incident_type": incident.incident_type,
            "severity": incident.priority,
            "confidence": incident.confidence,
            "event_count": len(incident.events),
        },
        "provenance": {
            "supporting_sources": new_event.provenance.supporting_sources,
            "contradicting_sources": new_event.provenance.contradicting_sources,
        },
    }


# ---------------------------------------------------------------------------
# 5. Full Incident Explainability Bundle
# ---------------------------------------------------------------------------

def build_incident_explainability(incident: Incident, priority: PriorityScore) -> Dict:
    """
    Builds a full explainability package for the frontend.
    """

    return {
        "incident_id": incident.id,
        "incident_type": incident.incident_type,
        "priority_explanation": explain_priority_score(priority),
        "events": [
            {
                "source_id": e.source_id,
                "confidence_explanation": explain_event_confidence(e, incident.events),
            }
            for e in incident.events
        ],
    }

