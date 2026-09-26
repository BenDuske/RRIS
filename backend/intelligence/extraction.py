from typing import List, Optional
from backend.models import Event, ParsedFields
from backend.intelligence.llm_client import llm


# ---------------------------------------------------------------------------
# 1. Rule-Based Extraction Helpers
# ---------------------------------------------------------------------------

HAZARD_KEYWORDS = {
    "flood": ["flash flood", "standing water", "low water crossing", "flooding"],
    "fire": ["structure fire", "smoke visible", "active fire", "heavy smoke"],
    "hazmat": ["fuel leak", "hazmat", "chemical", "spill"],
    "medical": ["chest pain", "collapsed", "dizziness", "injury", "patient"],
    "traffic": ["lanes blocked", "traffic backing up", "significant delays", "vehicle incident"],
}

AGENCY_KEYWORDS = {
    "fire": ["fire department", "engine", "ladder", "defensive operations"],
    "ems": ["ems", "patient", "transporting", "medical emergency"],
    "police": ["pd", "police", "law enforcement"],
    "hazmat": ["hazmat", "fuel leak", "chemical spill"],
    "public_works": ["power company", "txdot", "road closure"],
}


def detect_hazards(text: str) -> List[str]:
    text_lower = text.lower()
    hazards = []

    for label, keywords in HAZARD_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            hazards.append(label)

    return hazards


def detect_agencies(text: str) -> List[str]:
    text_lower = text.lower()
    agencies = []

    for label, keywords in AGENCY_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            agencies.append(label)

    return agencies


def estimate_injuries(text: str) -> Optional[int]:
    text_lower = text.lower()

    if "no injuries" in text_lower:
        return 0
    if "injuries" in text_lower or "patient" in text_lower:
        # Very simple heuristic; LLM can refine this
        if "1" in text_lower:
            return 1
        if "2" in text_lower:
            return 2
        if "3" in text_lower:
            return 3
        return 1

    return None


def estimate_severity(text: str) -> Optional[int]:
    text_lower = text.lower()

    if "extreme" in text_lower or "mass casualty" in text_lower or "explosion" in text_lower:
        return 10
    if "severe" in text_lower or "critical" in text_lower or "life-threatening" in text_lower:
        return 8
    if any(w in text_lower for w in ["fire hazard", "entrap", "second alarm", "hazmat", "fuel leak"]):
        return 7
    if any(w in text_lower for w in ["collision", "crash", "rollover", "injuries", "active fire"]):
        return 6
    if "moderate" in text_lower or any(w in text_lower for w in ["lanes blocked", "dispatched"]):
        return 5
    if "minor" in text_lower or "stable" in text_lower or "conscious" in text_lower:
        return 3

    return None


def classify_incident_type(text: str) -> Optional[str]:
    text_lower = text.lower()

    if any(k in text_lower for k in HAZARD_KEYWORDS["fire"]):
        return "Structure Fire"
    if any(k in text_lower for k in HAZARD_KEYWORDS["flood"]):
        return "Flooding / Road Hazard"
    if any(k in text_lower for k in HAZARD_KEYWORDS["hazmat"]):
        return "HazMat Incident"
    if any(k in text_lower for k in HAZARD_KEYWORDS["medical"]):
        return "Medical Emergency"
    if any(k in text_lower for k in HAZARD_KEYWORDS["traffic"]):
        return "Traffic Incident"

    return None


# ---------------------------------------------------------------------------
# 2. Hybrid Extraction (Rule-Based + LLM)
# ---------------------------------------------------------------------------

def extract_parsed_fields(event: Event, use_llm: bool = True) -> ParsedFields:
    """
    Main entry point for extraction.
    - Starts with rule-based extraction
    - Optionally refines with LLM
    """

    text = event.raw_text

    # Start from existing parsed_fields (e.g., NWS already set incident_type/severity)
    pf = event.parsed_fields

    # Rule-based enrichment
    if pf.incident_type is None:
        pf.incident_type = classify_incident_type(text)

    if pf.hazards is None or len(pf.hazards) == 0:
        pf.hazards = detect_hazards(text)

    if pf.agencies_needed is None or len(pf.agencies_needed) == 0:
        pf.agencies_needed = detect_agencies(text)

    if pf.injuries is None:
        pf.injuries = estimate_injuries(text)

    if pf.severity_estimate is None:
        pf.severity_estimate = estimate_severity(text)

    if pf.key_details is None:
        pf.key_details = text[:500]  # simple default

    # Optional LLM refinement
    if use_llm and llm.available:
        try:
            llm_fields = llm.extract_fields(text)
            pf.incident_type = llm_fields.incident_type or pf.incident_type
            pf.injuries = llm_fields.injuries if llm_fields.injuries is not None else pf.injuries
            pf.hazards = llm_fields.hazards or pf.hazards
            pf.agencies_needed = llm_fields.agencies_needed or pf.agencies_needed
            pf.severity_estimate = llm_fields.severity_estimate or pf.severity_estimate
            pf.key_details = llm_fields.key_details or pf.key_details
        except Exception:
            pass

    return pf

