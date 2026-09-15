import httpx
import logging
import json
from datetime import datetime, timezone

# Import your normalizer and models
from ingestion.normalizer import normalize_report
from models import Event

logger = logging.getLogger(__name__)

# The NWS API requires a descriptive User-Agent
USER_AGENT = "(RRIS_Capstone, your.email@ttu.edu)" 
NWS_ALERTS_URL = "https://api.weather.gov/alerts/active?zone=TXZ035" # TXZ035 is Lubbock County

async def fetch_nws_alerts() -> list:
    """Polls the NWS API for active weather alerts in Lubbock County."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(NWS_ALERTS_URL, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data.get("features", [])
        except Exception as e:
            logger.error(f"Error polling NWS API: {e}")
            return []

def map_nws_severity(nws_severity: str) -> int:
    """Maps NWS textual severity to our 1-10 integer scale."""
    mapping = {
        "Extreme": 10,
        "Severe": 8,
        "Moderate": 5,
        "Minor": 3,
        "Unknown": 1
    }
    return mapping.get(nws_severity, 5)

def process_nws_alert(feature: dict) -> Event:
    """
    Takes a raw NWS GeoJSON feature, normalizes it, and extracts fields via rules.
    """
    props = feature.get("properties", {})
    geometry = feature.get("geometry")
    
    # 1. Parse Coordinates
    lat, lng = 33.5779, -101.8552 # Default Lubbock coordinates
    if geometry and geometry.get("type") == "Polygon":
        first_coord = geometry["coordinates"][0][0]
        lng, lat = first_coord[0], first_coord[1]

    # 2. Build the raw_input dict for your normalizer
    raw_input = {
        "raw_text": json.dumps(feature),
        "lat": lat,
        "lng": lng,
        "address": props.get("areaDesc", "Lubbock Area"),
        "radius": 5000,  # 5km default for wide weather events
        "source_id": props.get("id", "nws_unknown"),
        "source_type": "nws",
        "timestamp": datetime.now(timezone.utc),
        "confidence": 1.0  # Absolute confidence in NWS API
    }

    # 3. Normalize the report into an Event object (parsed_fields will be empty)
    event = normalize_report(raw_input)

    # 4. Rule-Based Entity Extraction (Modifying the object in place)
    event.parsed_fields.incident_type = props.get("event", "Weather Event")
    event.parsed_fields.severity_estimate = map_nws_severity(props.get("severity"))
    
    # Use key_details to store the headline and instructional text
    headline = props.get("headline", "")
    instruction = props.get("instruction", "")
    event.parsed_fields.key_details = f"{headline}\n\n{instruction}".strip()
    
    # NWS provides exact sent times, so we update the provenance confirmation
    sent_time_str = props.get("sent")
    if sent_time_str:
        try:
            # Handle standard ISO 8601 formatting from NWS
            event.provenance.last_confirmed = datetime.fromisoformat(sent_time_str)
        except ValueError:
            pass 

    return event

async def poll_and_ingest():
    """Triggered by APScheduler. Fetches, processes, and passes data to Fusion."""
    logger.info("Polling NWS API for active alerts...")
    raw_alerts = await fetch_nws_alerts()
    
    if not raw_alerts:
        logger.info("No active NWS alerts found.")
        return

    events = [process_nws_alert(alert) for alert in raw_alerts]
    
    for event in events:
        logger.info(f"Ingested NWS Event: {event.parsed_fields.incident_type}")
        # TODO: Pass the fully populated Event object to the Fusion Engine
        # fusion_engine.process_event(event)
