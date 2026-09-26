from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from backend.ingestion.normalizer import normalize_report
from backend.intelligence.fusion import process_event, INCIDENTS
from backend.intelligence.explainability import build_incident_explainability
from backend.intelligence.priority import compute_priority_score

app = FastAPI(title="RRIS Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: List[WebSocket] = []


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
    data = {
        "type": "incident_update",
        "incident": incident.model_dump(mode="json"),
    }
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
    return [i.model_dump(mode="json") for i in INCIDENTS]


@app.get("/incidents/{incident_id}")
def get_incident_details(incident_id: int):
    incident = next((i for i in INCIDENTS if i.id == incident_id), None)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    priority_score = compute_priority_score(incident)
    return {
        "incident": incident.model_dump(mode="json"),
        "explainability": build_incident_explainability(incident, priority_score),
    }
