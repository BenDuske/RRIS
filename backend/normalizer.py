from datetime import datetime
from models import Event, Location, ParsedFields, Provenance

def normalize_report(raw_input: dict) -> Event:
    """
    Convert any raw report (NWS, CAD, PDF, manual) into a standard Event envelope.
    """

    # 1. Extract raw text
    raw_text = raw_input.get("raw_text", "")

    # 2. Build location object
    location = Location(
        lat=raw_input.get("lat"),
        lng=raw_input.get("lng"),
        address=raw_input.get("address"),
        radius=raw_input.get("radius", 50)
    )

    # 3. Empty parsed fields (LLM or rule-based extraction fills this later)
    parsed_fields = ParsedFields(
        incident_type=None,
        location=location,
        injuries=None,
        hazards=[],
        agencies_needed=[],
        severity_estimate=None,
        key_details=None
    )

    # 4. Provenance tracking
    provenance = Provenance(
        origin=raw_input.get("source_type", "unknown"),
        received_at=datetime.utcnow(),
        last_confirmed=None,
        supporting_sources=[],
        contradicting_sources=[]
    )

    # 5. Build Event envelope
    event = Event(
        source_id=raw_input.get("source_id", "unknown"),
        source_type=raw_input.get("source_type", "manual"),
        timestamp=raw_input.get("timestamp", datetime.utcnow()),
        location=location,
        raw_text=raw_text,
        parsed_fields=parsed_fields,
        confidence=raw_input.get("confidence", 0.7),
        provenance=provenance
    )

    return event
  
def update_provenance(event: Event, new_source: str, confirmed: bool = False):
    if confirmed:
        event.provenance.supporting_sources.append(new_source)
        event.provenance.last_confirmed = datetime.utcnow()
    else:
        event.provenance.contradicting_sources.append(new_source)
