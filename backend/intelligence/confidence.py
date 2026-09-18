from datetime import datetime, timezone
from typing import List
from backend.models import Event
from backend.intelligence.config import config


# ---------------------------------------------------------------------------
# 1. Source Reliability Table
# ---------------------------------------------------------------------------

SOURCE_RELIABILITY = {
    "nws": 1.0,        # Official government alerts
    "cad": 0.9,        # Dispatch center
    "traffic": 0.85,   # TxDOT, traffic sensors
    "manual": 0.75,    # Field reports, human-entered
    "pdf": 0.7,        # Uploaded documents
    "unknown": 0.5,
}


# ---------------------------------------------------------------------------
# 2. Recency Score
# ---------------------------------------------------------------------------

def compute_recency_score(event: Event) -> float:
    """
    Newer events should have higher confidence.
    0.0 = very old
    1.0 = just now
    """

    now = datetime.now(timezone.utc)
    age_seconds = (now - event.timestamp).total_seconds()

    # 0–30 minutes window
    if age_seconds <= 0:
        return 1.0
    if age_seconds >= 1800:
        return 0.0

    return max(0.0, 1.0 - (age_seconds / 1800))


# ---------------------------------------------------------------------------
# 3. Consistency Score
# ---------------------------------------------------------------------------

def compute_consistency_score(event: Event, related_events: List[Event]) -> float:
    """
    Measures how consistent this event is with other events in the same incident.
    If many events support it → high score.
    If many contradict it → low score.
    """

    if not related_events:
        return 0.5  # Neutral baseline

    support = 0
    contradict = 0

    for e in related_events:
        if e.parsed_fields.incident_type == event.parsed_fields.incident_type:
            support += 1
        else:
            contradict += 1

    total = support + contradict
    if total == 0:
        return 0.5

    return support / total


# ---------------------------------------------------------------------------
# 4. Provenance Score
# ---------------------------------------------------------------------------

def compute_provenance_score(event: Event) -> float:
    """
    Uses provenance tracking:
    - supporting_sources increase confidence
    - contradicting_sources decrease confidence
    """

    s = len(event.provenance.supporting_sources)
    c = len(event.provenance.contradicting_sources)

    if s == 0 and c == 0:
        return 0.5

    return max(0.0, min(1.0, (s - c + 1) / (s + c + 2)))


# ---------------------------------------------------------------------------
# 5. Final Confidence Score
# ---------------------------------------------------------------------------

def compute_event_confidence(event: Event, related_events: List[Event]) -> float:
    """
    Weighted confidence model:
    - source reliability
    - recency
    - consistency with other events
    - provenance support
    """

    w = config.confidence_weights

    source_score = SOURCE_RELIABILITY.get(event.source_type, SOURCE_RELIABILITY["unknown"])
    recency_score = compute_recency_score(event)
    consistency_score = compute_consistency_score(event, related_events)
    provenance_score = compute_provenance_score(event)

    final = (
        w["source_reliability"] * source_score +
        w["recency"] * recency_score +
        w["consistency"] * consistency_score
    )

    # Blend provenance into final score
    final = (final + provenance_score) / 2

    return max(0.0, min(1.0, final))

