from typing import Dict
from backend.models import Incident, PriorityScore
from backend.intelligence.config import config


# ---------------------------------------------------------------------------
# 1. Factor Normalization Helpers
# ---------------------------------------------------------------------------

def normalize_severity(severity: int | None) -> float:
    """
    Severity is already on a 1–10 scale.
    Normalize to 0.0–1.0.
    """
    if severity is None:
        return 0.0
    return min(1.0, max(0.0, severity / 10))


def normalize_injuries(injuries: int | None) -> float:
    """
    Injuries: 0–3+ mapped to 0.0–1.0.
    """
    if injuries is None:
        return 0.0
    if injuries <= 0:
        return 0.0
    if injuries == 1:
        return 0.33
    if injuries == 2:
        return 0.66
    return 1.0  # 3+ injuries


def normalize_hazards(hazards: list[str]) -> float:
    """
    Hazards: more hazards = higher score.
    """
    if not hazards:
        return 0.0
    return min(1.0, len(hazards) / 3)  # cap at 3 hazards


def normalize_agencies(agencies: list[str]) -> float:
    """
    Agencies needed: more agencies = more complex incident.
    """
    if not agencies:
        return 0.0
    return min(1.0, len(agencies) / 4)  # cap at 4 agencies


def normalize_confidence(confidence: float | None) -> float:
    """
    Confidence is already 0.0–1.0.
    """
    if confidence is None:
        return 0.0
    return min(1.0, max(0.0, confidence))
    

# ---------------------------------------------------------------------------
# 2. Compute Priority Score
# ---------------------------------------------------------------------------

def compute_priority_score(incident: Incident) -> PriorityScore:
    """
    Computes a weighted priority score (0–100) for an incident.
    Uses severity, injuries, hazards, agencies, and confidence.
    """

    # Pull weights from config
    w = config.priority_weights

    # Aggregate incident-level fields
    # We use the most recent event for severity/injuries if available
    latest_event = incident.events[-1] if incident.events else None
    pf = latest_event.parsed_fields if latest_event else None

    severity_score = normalize_severity(pf.severity_estimate if pf else None)
    injuries_score = normalize_injuries(pf.injuries if pf else None)
    hazards_score = normalize_hazards(pf.hazards if pf else [])
    agencies_score = normalize_agencies(pf.agencies_needed if pf else [])
    confidence_score = normalize_confidence(incident.confidence)

    # Weighted sum
    final_score = (
        w["severity"] * severity_score +
        w["injuries"] * injuries_score +
        w["hazards"] * hazards_score +
        w["agencies_needed"] * agencies_score +
        w["confidence"] * confidence_score
    )

    # Convert to 0–100 scale
    final_value = int(final_score * 100)

    # Breakdown for explainability
    breakdown: Dict[str, float] = {
        "severity": w["severity"] * severity_score,
        "injuries": w["injuries"] * injuries_score,
        "hazards": w["hazards"] * hazards_score,
        "agencies_needed": w["agencies_needed"] * agencies_score,
        "confidence": w["confidence"] * confidence_score,
    }

    return PriorityScore(
        value=final_value,
        confidence=confidence_score,
        breakdown=breakdown,
    )

