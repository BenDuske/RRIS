import json
import logging
import os
from backend.models import ParsedFields

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extract structured fields from this emergency report.
Return ONLY valid JSON with these fields:
- incident_type: one of Fire, Medical, Transportation, Weather, HazMat, Infrastructure, Public Safety, Rescue
- injuries: integer or null
- hazards: list of short hazard descriptions
- agencies_needed: list of agencies (Fire, EMS, Police, HazMat, etc.)
- severity_estimate: integer 1-10
- key_details: one sentence summary

Report:
{text}"""

SUMMARY_PROMPT = """Summarize this emergency incident in one concise sentence for a first responder dashboard.
Include: what happened, where, and current severity.

Reports:
{text}"""


class LLMClient:
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not self.api_key:
                raise RuntimeError("OPENAI_API_KEY not set. Set it in environment or pass to LLMClient().")
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def extract_fields(self, text: str) -> ParsedFields:
        if not self.available:
            logger.warning("LLM unavailable, returning empty ParsedFields")
            return ParsedFields()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract structured data from emergency reports. Return only valid JSON."},
                    {"role": "user", "content": EXTRACTION_PROMPT.format(text=text)},
                ],
                temperature=0.1,
                max_tokens=500,
            )
            raw = response.choices[0].message.content.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            data = json.loads(raw)
            return ParsedFields(**data)
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return ParsedFields()

    def summarize(self, text: str) -> str:
        if not self.available:
            return text[:200]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You summarize emergency incidents for first responder dashboards. Be concise."},
                    {"role": "user", "content": SUMMARY_PROMPT.format(text=text)},
                ],
                temperature=0.2,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM summarization failed: {e}")
            return text[:200]


# Rule-based fallback for structured sources (no LLM needed)
def extract_fields_rulebased(raw_text: str, source_type: str) -> ParsedFields:
    text_lower = raw_text.lower()

    incident_type = None
    type_keywords = {
        "Fire": ["fire", "smoke", "burn", "flame", "arson"],
        "Medical": ["medical", "injury", "injured", "cardiac", "unconscious", "breathing", "collapsed"],
        "Transportation": ["collision", "crash", "accident", "rollover", "traffic", "vehicle", "pileup"],
        "Weather": ["flood", "tornado", "storm", "hail", "wind", "lightning", "warning", "watch"],
        "HazMat": ["hazmat", "chemical", "spill", "leak", "fuel", "gas", "toxic", "radiation"],
        "Infrastructure": ["power", "outage", "water main", "bridge", "building collapse", "utility"],
        "Public Safety": ["shooting", "suspicious", "threat", "crowd", "protest", "evacuat"],
        "Rescue": ["rescue", "trapped", "entrap", "swift water", "confined space"],
    }
    for itype, keywords in type_keywords.items():
        if any(kw in text_lower for kw in keywords):
            incident_type = itype
            break

    hazards = []
    hazard_keywords = {
        "fuel_leak": ["fuel leak", "fuel spill", "gasoline"],
        "fire_hazard": ["fire hazard", "fire risk", "flammable"],
        "flooding": ["flood", "standing water", "water level"],
        "entrapment": ["trapped", "entrap", "pinned"],
        "structure_fire": ["structure fire", "building fire"],
        "active_fire": ["active fire", "fully involved"],
        "chemical": ["chemical", "hazmat", "toxic"],
        "downed_lines": ["power line", "downed line", "electrical"],
    }
    for hazard, keywords in hazard_keywords.items():
        if any(kw in text_lower for kw in keywords):
            hazards.append(hazard)

    agencies = []
    if any(w in text_lower for w in ["fire", "smoke", "burn", "flame"]):
        agencies.append("Fire")
    if any(w in text_lower for w in ["injur", "medical", "ems", "ambulance", "collapsed"]):
        agencies.append("EMS")
    if any(w in text_lower for w in ["police", "suspect", "crime", "shooting"]):
        agencies.append("Police")
    if any(w in text_lower for w in ["hazmat", "chemical", "spill", "toxic"]):
        agencies.append("HazMat")

    severity = 5
    high_severity = ["critical", "fatal", "mass casualty", "explosion", "active fire", "entrap", "second alarm"]
    low_severity = ["minor", "non-injury", "stable", "resolved", "cleared"]
    if any(w in text_lower for w in high_severity):
        severity = 8
    elif any(w in text_lower for w in low_severity):
        severity = 3

    key_details = raw_text[:150].strip()

    return ParsedFields(
        incident_type=incident_type,
        injuries=None,
        hazards=hazards,
        agencies_needed=agencies,
        severity_estimate=severity,
        key_details=key_details,
    )


llm = LLMClient()
