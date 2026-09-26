from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from backend.ingestion.normalizer import normalize_report
from backend.intelligence.fusion import process_event, INCIDENTS, INCIDENT_META
from backend.intelligence.explainability import build_incident_explainability
from backend.intelligence.priority import (
    compute_priority_score,
    normalize_severity,
    normalize_injuries,
    normalize_hazards,
    normalize_agencies,
    normalize_confidence,
)

app = FastAPI(title="RRIS Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: List[WebSocket] = []

ESCALATION_HAZARDS = {"fuel_leak", "fire_hazard", "hazmat", "entrapment", "active_fire", "chemical"}


def enrich_incident(incident) -> dict:
    data = incident.model_dump(mode="json")
    meta = INCIDENT_META.get(incident.id, {})

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

    data["priority_breakdown"] = {
        "severity": round(normalize_severity(max_severity) * 10, 1),
        "injuries": round(normalize_injuries(max_injuries) * 10, 1),
        "hazards": round(normalize_hazards(list(set(all_hazards))) * 10, 1),
        "agencies": round(normalize_agencies(list(set(all_agencies))) * 10, 1),
        "confidence": round(normalize_confidence(incident.confidence) * 10, 1),
    }

    prev = meta.get("previous_priority")
    data["priority_delta"] = (incident.priority or 0) - prev if prev is not None else 0

    data["confirmed"] = meta.get("confirmed", False)
    data["human_priority"] = meta.get("human_priority")

    timeline = []
    seen_hazards = set()
    for i, event in enumerate(incident.events):
        event_hazards = set(event.parsed_fields.hazards or [])
        new_escalation = event_hazards & ESCALATION_HAZARDS - seen_hazards

        if i == 0:
            entry_type = "created"
        elif new_escalation:
            entry_type = "escalation"
        else:
            entry_type = "evidence"

        seen_hazards |= event_hazards

        timeline.append({
            "type": entry_type,
            "summary": event.parsed_fields.key_details or event.raw_text[:120],
            "created_at": event.timestamp.isoformat()
            if hasattr(event.timestamp, "isoformat")
            else str(event.timestamp),
            "source_type": event.source_type,
            "source_id": event.source_id,
        })
    data["timeline"] = timeline

    lims = []
    if len(incident.events) == 1:
        lims.append("Single source report")
    unconfirmed = sum(1 for e in incident.events if not e.provenance.last_confirmed)
    if unconfirmed:
        lims.append(f"{unconfirmed} source(s) unconfirmed")
    has_injury_gap = any(e.parsed_fields.injuries is None for e in incident.events)
    if has_injury_gap and len(incident.events) > 1:
        lims.append("Injury count not confirmed by all sources")
    data["limitations"] = lims

    return data


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.remove(ws)


async def broadcast_incident(incident):
    data = {"type": "incident_update", "incident": enrich_incident(incident)}
    for ws in list(clients):
        try:
            await ws.send_json(data)
        except Exception:
            clients.remove(ws)


@app.post("/ingest")
async def ingest_event(raw_input: dict):
    event = normalize_report(raw_input)
    incident = process_event(event)
    await broadcast_incident(incident)
    return {
        "status": "ok",
        "incident_id": incident.id,
        "incident_priority": incident.priority,
        "incident_confidence": incident.confidence,
        "event_count": len(incident.events),
    }


@app.get("/incidents")
def list_incidents():
    return [enrich_incident(i) for i in INCIDENTS]


@app.get("/incidents/{incident_id}")
def get_incident_details(incident_id: int):
    incident = next((i for i in INCIDENTS if i.id == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    priority_score = compute_priority_score(incident)
    return {
        "incident": enrich_incident(incident),
        "explainability": build_incident_explainability(incident, priority_score),
    }


@app.post("/incidents/{incident_id}/confirm")
async def confirm_incident(incident_id: int):
    incident = next((i for i in INCIDENTS if i.id == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    meta = INCIDENT_META.setdefault(incident_id, {})
    meta["confirmed"] = True
    await broadcast_incident(incident)
    return {"status": "confirmed", "incident_id": incident_id, "priority": incident.priority}


class AdjustRequest(BaseModel):
    priority: int


@app.post("/incidents/{incident_id}/adjust")
async def adjust_incident(incident_id: int, body: AdjustRequest):
    incident = next((i for i in INCIDENTS if i.id == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    meta = INCIDENT_META.setdefault(incident_id, {})
    meta["previous_priority"] = incident.priority
    meta["human_priority"] = body.priority
    meta["confirmed"] = True
    incident.priority = max(0, min(100, body.priority))
    await broadcast_incident(incident)
    return {"status": "adjusted", "incident_id": incident_id, "priority": incident.priority}
