from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from backend.ingestion.normalizer import normalize_report
from backend.intelligence.fusion import process_event, INCIDENTS
from backend.intelligence.explainability import get_incident_with_explainability

app = FastAPI(title="RRIS Backend", version="1.0")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected WebSocket clients
clients: List[WebSocket] = []


# ---------------------------------------------------------------------------
# WebSocket for live incident streaming
# ---------------------------------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)

    try:
        while True:
            await ws.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        clients.remove(ws)


async def broadcast_incident(incident):
    """Send updated incident to all connected clients."""
    for ws in clients:
        try:
            await ws.send_json({
                "type": "incident_update",
                "incident": incident,
            })
        except Exception:
            pass


# ---------------------------------------------------------------------------
# REST Endpoint: Inject Event (used by simulator, NWS poller, PDF ingestion)
# ---------------------------------------------------------------------------

@app.post("/ingest")
async def ingest_event(raw_input: dict):
    """
    Accepts raw_input from any ingestion source:
    - Simulator
    - NWS poller
    - PDF ingestion
    - CAD feed
    """

    event = normalize_report(raw_input)
    incident = process_event(event)

    # Broadcast to frontend
    await broadcast_incident(incident)

    return {
        "status": "ok",
        "incident_id": incident.id,
        "incident_priority": incident.priority,
        "incident_confidence": incident.confidence,
    }


# ---------------------------------------------------------------------------
# REST Endpoint: Get all incidents
# ---------------------------------------------------------------------------

@app.get("/incidents")
def list_incidents():
    return INCIDENTS


# ---------------------------------------------------------------------------
# REST Endpoint: Get incident with explainability
# ---------------------------------------------------------------------------

@app.get("/incidents/{incident_id}")
def get_incident_details(incident_id: int):
    return get_incident_with_explainability(incident_id)


# ---------------------------------------------------------------------------
# Startup banner
# ---------------------------------------------------------------------------

print("RRIS backend initialized — FastAPI running")

