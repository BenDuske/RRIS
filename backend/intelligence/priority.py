from typing import Dict
from backend.models import Incident, PriorityScore
from backend.config import config


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
    Aggregates across all events — takes the worst case for each factor.
    """

    w = config.priority_weights

    max_severity = None
    max_injuries = None
    all_hazards = []
    all_agencies = []

    for event in incident.events:
        pf = event.parsed_fields
        if pf.severity_estimate is not None:
            max_severity = max(max_severity or 0, pf.severity_estimate)
        if pf.injuries is not None:
            max_injuries = max(max_injuries or 0, pf.injuries)
        all_hazards.extend(pf.hazards or [])
        all_agencies.extend(pf.agencies_needed or [])

    unique_hazards = list(set(all_hazards))
    unique_agencies = list(set(all_agencies))

    severity_score = normalize_severity(max_severity)
    injuries_score = normalize_injuries(max_injuries)
    hazards_score = normalize_hazards(unique_hazards)
    agencies_score = normalize_agencies(unique_agencies)
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

