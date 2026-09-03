# RRIS — Architecture & Tech Stack

Rapid Response Information System: a layered, human-centered emergency information system scoped for an 8-week capstone.

> **Locked decisions:**
> - Database: **SQLite** (zero-config, file-based, no deployment overhead)
> - Intelligence layer: **hybrid** — LLM API for entity extraction and summarization from free-text reports; rule-based logic for classification, priority scoring, and fusion (transparent, auditable decisions)
> - Simulated data: generated offline (by team members), uploaded as PDFs for ingestion — NOT LLM-generated at runtime

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                                                             │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐  │
│  │  Incident     │  │   Map View    │  │  Explainability  │  │
│  │  Dashboard    │  │  (Leaflet.js) │  │     Panel        │  │
│  │  + Timeline   │  │               │  │  • provenance    │  │
│  │  + Deltas     │  │  • Markers    │  │  • confidence    │  │
│  │  ("what       │  │  • Clusters   │  │  • data sources  │  │
│  │   changed")   │  │  • Overlays   │  │  • limitations   │  │
│  └──────┬────────┘  └──────┬────────┘  └────────┬─────────┘  │
│         │                  │                    │            │
│         └──────────┬───────┘                    │            │
│                    │       Role Filter           │            │
│                    ▼            ▼                ▼            │
│         ┌──────────────────────────────────────────┐         │
│         │         WebSocket Event Stream           │         │
│         │   (real-time push to all UI components)  │         │
│         └──────────────────┬───────────────────────┘         │
├────────────────────────────┼────────────────────────────────┤
│                    APPLICATION LAYER                          │
│                            │                                │
│  ┌─────────────────────────┴──────────────────────────┐     │
│  │               Incident Manager                      │     │
│  │                                                     │     │
│  │  • Maintains Incident Objects — one per real-world  │     │
│  │    event (the single source of truth)               │     │
│  │  • Attaches new evidence to existing incidents      │     │
│  │  • Tracks state transitions + builds timeline       │     │
│  │  • Computes priority score P(L,S,H,C,T,R,V)        │     │
│  │  • Generates deltas ("what changed since last view")│     │
│  │  • Emits events via WebSocket on any state change   │     │
│  └─────────────────────────┬──────────────────────────┘     │
│                            │                                │
│  ┌─────────────────────────┴──────────────────────────┐     │
│  │               REST API (FastAPI)                    │     │
│  │                                                     │     │
│  │  GET  /incidents          — list active incidents   │     │
│  │  GET  /incidents/{id}     — full incident + evidence│     │
│  │  GET  /incidents/{id}/timeline — event history      │     │
│  │  GET  /incidents/{id}/deltas   — changes since ts   │     │
│  │  POST /reports            — manual report entry     │     │
│  │  GET  /status             — system health + sources │     │
│  └────────────────────────────────────────────────────┘     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    INTELLIGENCE LAYER                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │   Entity      │  │  Incident Fusion │  │   Priority   │  │
│  │  Extraction   │──│     Engine       │──│    Scorer    │  │
│  │               │  │                  │  │              │  │
│  │  • NER/regex  │  │  • Geo+temporal  │  │  • Weighted  │  │
│  │    for known  │  │    clustering    │  │    formula   │  │
│  │    fields     │  │  • Dedup detect  │  │  • Conf and  │  │
│  │  • LLM API   │  │    (similarity   │  │    severity  │  │
│  │    for free-  │  │    threshold)    │  │    SEPARATE  │  │
│  │    text parse │  │  • Merge logic   │  │  • Decays    │  │
│  │  • Geocoding  │  │    (attach       │  │    over time │  │
│  │    (lat/lng)  │  │    evidence to   │  │    without   │  │
│  │  • Summarize  │  │    incident)     │  │    refresh   │  │
│  └──────────────┘  └──────────────────┘  └──────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                     INGESTION LAYER                          │
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌───────────┐ ┌─────────┐ │
│  │ NWS Weather│  │Traffic Feed│  │ Simulated │ │ Manual  │ │
│  │ API        │  │ (TxDOT /   │  │ CAD /     │ │ Report  │ │
│  │            │  │  simulated)│  │ Dispatch  │ │ Entry   │ │
│  │ • Alerts   │  │            │  │ Feed      │ │         │ │
│  │ • Forecasts│  │ • Incidents│  │           │ │ • Web   │ │
│  │ • Watches  │  │ • Closures │  │ • 911     │ │   form  │ │
│  │ • Warnings │  │            │  │ • Field   │ │ • API   │ │
│  └─────┬──────┘  └─────┬──────┘  └────┬──────┘ └───┬─────┘ │
│        │               │              │             │       │
│        ▼               ▼              ▼             ▼       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Normalizer / Schema Mapper                 │    │
│  │                                                      │    │
│  │  Every raw report → standard Event envelope:        │    │
│  │  {                                                   │    │
│  │    source_id,          // which feed                 │    │
│  │    source_type,        // "nws" | "traffic" | "cad"  │    │
│  │    timestamp,          // ISO-8601 UTC               │    │
│  │    location: {lat, lng, address, radius},            │    │
│  │    raw_text,           // original unmodified        │    │
│  │    parsed_fields: {},  // extracted structured data  │    │
│  │    confidence,         // source reliability 0–1     │    │
│  │    provenance: {       // full audit trail           │    │
│  │      origin, received_at, last_confirmed,            │    │
│  │      supporting_sources, contradicting_sources       │    │
│  │    }                                                 │    │
│  │  }                                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                      DATA LAYER                              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                      SQLite                           │    │
│  │                                                      │    │
│  │  incidents        — one row per real-world event     │    │
│  │  events           — raw normalized reports           │    │
│  │  incident_events  — links events to incidents        │    │
│  │  timeline_entries — state changes + deltas           │    │
│  │  sources          — registered feed metadata         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow (End to End)

```
Raw report arrives (API poll, webhook, or manual entry)
        │
        ▼
   Normalizer converts to standard Event envelope
   (attaches provenance: source, timestamp, confidence)
        │
        ▼
   Entity Extraction pulls structured fields
   (incident type, location, injuries, hazards, agencies)
        │
        ▼
   Incident Fusion Engine checks:
   "Does this match an existing incident?"
        │
   ┌────┴────┐
   │         │
  YES        NO
   │         │
   ▼         ▼
  Attach    Create new
  as new    Incident Object
  evidence
   │         │
   └────┬────┘
        │
        ▼
   Priority Scorer recalculates
   P = f(L, S, H, C, T, R, V)
   (confidence and severity scored independently)
        │
        ▼
   Incident Manager updates state
   Generates timeline entry + delta
        │
        ▼
   WebSocket pushes update to all connected clients
        │
        ▼
   Dashboard / Map / Explainability Panel update in real time
```

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| **Frontend** | React + Leaflet.js | Component-based UI, free OpenStreetMap tiles (no API key), markers/clusters/overlays |
| **Backend** | Python (FastAPI) | Async-native, auto-generated Swagger docs (demo asset), Pydantic schema enforcement |
| **Intelligence** | Hybrid: LLM API + rule-based | LLM extracts entities and summarizes free-text reports; rule-based logic handles classification, scoring, and fusion — transparent and auditable where it counts |
| **Database** | SQLite | Zero-config, file-based, no deployment overhead. One file = entire database |
| **Real-time** | WebSockets (FastAPI native) | Push incident updates to all dashboards instantly. No polling lag |
| **Maps** | Leaflet.js + OpenStreetMap | Free, no API key, supports markers, popups, circle overlays, clustering |
| **Simulated Data** | Team-authored PDFs + Python replay scripts | Team members create realistic reports offline, upload as PDFs for ingestion during demo |
| **Deployment** | Local dev server | `uvicorn` + `npm run dev` on localhost — production deployment not required |

### Frontend Dependencies

```
react                 — UI framework
react-leaflet         — React bindings for Leaflet.js
leaflet               — map rendering
leaflet.markercluster — cluster nearby incidents on zoom-out
recharts (optional)   — charts for the explainability panel
```

**Why React:** Component model makes Dashboard, Map, and Explainability Panel independent modules that all react to the same incident state. WebSocket events update shared state → all panels re-render.

**Why Leaflet over Mapbox/Google Maps:** No API key. Free forever. The capstone needs markers, popups, and overlays — not satellite imagery or turn-by-turn routing.

### Backend Dependencies

```
fastapi               — async web framework + auto-docs
uvicorn               — ASGI server
pydantic              — data validation (Event envelope, Incident schema)
httpx                 — async HTTP client for polling external APIs
apscheduler           — scheduled polling (NWS every 60s)
```

**Why FastAPI over Flask/Django:** Async-native (WebSocket + concurrent API polling). Swagger UI auto-generates API docs — walk the instructor through every endpoint during the demo. Pydantic models enforce the Event envelope schema at the code level.

---

## Intelligence Layer (Detail)

### Entity Extraction (Hybrid: Rule-Based + LLM)

```python
# Structured feeds: rule-based, direct field mapping (fast, transparent)
def extract_from_nws(alert: dict) -> ParsedFields:
    return ParsedFields(
        incident_type=map_nws_event(alert["event"]),
        location=geocode(alert["areaDesc"]),
        severity=map_nws_severity(alert["severity"]),
        urgency=alert["urgency"],
        certainty=alert["certainty"],
    )

# Free-text reports: LLM API extraction (handles messy, narrative input)
def extract_from_freetext(text: str) -> ParsedFields:
    response = llm_client.chat(
        messages=[{
            "role": "user",
            "content": f"""Extract structured fields from this emergency report.
            Return JSON with: incident_type, location, injuries, hazards,
            agencies_needed, severity_estimate, key_details.

            Report: {text}"""
        }],
    )
    return ParsedFields.parse(response)
```

**Why hybrid:** Rule-based extraction is transparent and fast for structured API data (NWS already returns typed fields). LLM extraction handles the messy, unstructured stuff — narrative dispatch reports, field updates, uploaded PDFs with free-text descriptions. The explainability panel can distinguish: *"This field was extracted by rule from NWS API"* vs. *"This field was extracted by AI from a free-text report (confidence: medium)."* That separation is a strong HCAI talking point — using AI where it adds value while keeping deterministic logic where transparency matters most.

### Priority Scoring

```python
def compute_priority(incident: Incident) -> PriorityScore:
    L = assess_life_threat(incident)      # 0–10, weight: 0.30
    S = assess_severity(incident)         # 0–10, weight: 0.20
    H = assess_hazards(incident)          # 0–10, weight: 0.15
    T = assess_time_sensitivity(incident) # 0–10, weight: 0.15
    R = assess_resource_load(incident)    # 0–10, weight: 0.10
    V = assess_vulnerable_pop(incident)   # 0–10, weight: 0.10

    score = (L*0.30 + S*0.20 + H*0.15 + T*0.15 + R*0.10 + V*0.10) * 10
    # → yields 0–100

    confidence = compute_confidence(incident)  # SEPARATE from priority

    return PriorityScore(
        value=round(score),
        confidence=confidence,
        breakdown={"life_threat": L, "severity": S, ...}
    )
```

**Key design decision:** Confidence modulates how the score is *displayed and flagged*, but does NOT suppress the priority score itself. A catastrophic, unconfirmed event still shows as high priority — with a visible low-confidence warning. The human decides whether to act on unconfirmed information.

```
Display:  CRITICAL — Priority 94/100 | Confidence: 78%
```

### Incident Fusion

```python
FUSION_CONFIG = {
    "geo_radius_m": 500,               # meters
    "time_window_s": 1800,             # 30 minutes
    "entity_overlap_threshold": 0.3,
    "fusion_threshold": 0.6,           # combined score to merge
    "weights": {
        "geo": 0.4,
        "temporal": 0.3,
        "semantic": 0.3,
    }
}
```

When a new event arrives:

1. **Geospatial match** — within configurable radius of an existing incident?
2. **Temporal match** — within time window of last update?
3. **Semantic match** — extracted entities overlap? (same road, type, agencies)
4. **Threshold** — if combined score exceeds threshold → merge; otherwise → new incident

```
Match Score = w1 * geo_proximity + w2 * temporal_proximity + w3 * entity_overlap

If match_score > FUSION_THRESHOLD → attach event to existing incident
Else                              → create new Incident Object
```

All thresholds are configurable and documented. During the demo, show what happens when you tighten or loosen fusion — strong HCAI talking point about system transparency.

---

## Temporal Intelligence — Delta Tracking

Every Incident Object maintains an ordered timeline:

```
incident.timeline = [
    {ts: "13:02:17", type: "created",    summary: "Vehicle collision reported, I-27 NB"},
    {ts: "13:04:33", type: "evidence",   summary: "Two injuries reported (source: dispatch)"},
    {ts: "13:05:01", type: "evidence",   summary: "Northbound lanes closed (source: TxDOT)"},
    {ts: "13:07:44", type: "evidence",   summary: "EMS requested additional unit"},
    {ts: "13:09:12", type: "escalation", summary: "Fuel leak identified"},
    {ts: "13:11:08", type: "escalation", summary: "⚠️ Fire hazard reported — FD requested"},
]
```

When a responder opens an incident they've seen before:

```
Changes since your last view (13:05):
  • Fuel leak confirmed (13:09)
  • Fire department requested (13:11)
  • Northbound closure expanded to Exit 4 (13:11)
  • Priority: 72 → 94 (+22)
```

Tracked per-session with a `last_viewed_at` timestamp.

---

## Role-Specific Views

Two roles for the capstone prototype (pattern is extensible):

| Role | Highlighted Fields | De-emphasized |
|---|---|---|
| **Fire/Rescue** | Hazmat, hydrants, building access, wind, evacuation zones, entrapment | Traffic routing, crowd control |
| **EMS** | Casualties, triage status, hospital access, staging, road closures | Hazmat detail, perimeter |

Each role is a **filter configuration**, not a separate system:

```python
ROLE_FILTERS = {
    "fire": {
        "highlight": ["hazmat", "hydrants", "building_access", "wind", "evacuation"],
        "show": ["casualties", "road_closures", "staging"],
        "suppress": ["crowd_control", "traffic_routing"]
    },
    "ems": {
        "highlight": ["casualties", "triage", "hospital_access", "staging"],
        "show": ["road_closures", "hazmat"],
        "suppress": ["perimeter", "crowd_control"]
    }
}
```

The full vision (police, transportation, EOC) is described in the proposal; the prototype demonstrates two roles with a clear extension pattern.

---

## Explainability Panel

For every incident, the panel answers three questions:

1. **What do we know?** — Structured summary of current state
2. **How do we know it?** — Provenance chain: source → timestamp → confirmation status
3. **How confident are we?** — Confidence score with breakdown

```
┌─────────────────────────────────────────────┐
│  INCIDENT #1247 — Structure Fire            │
│  Priority: 94/100    Confidence: 78%        │
├─────────────────────────────────────────────┤
│  WHY THIS PRIORITY:                         │
│    Threat to life:  9/10  (entrapment)      │
│    Severity:        8/10  (structure fire)   │
│    Hazards:         7/10  (fuel leak)        │
│    Time sensitivity: 9/10 (active fire)      │
│    Resources:       6/10  (3 units)          │
│    Vulnerable:      5/10  (residential)      │
├─────────────────────────────────────────────┤
│  DATA SOURCES (3):                          │
│    ✓ Dispatch CAD    — 13:02  (primary)     │
│    ✓ Field report    — 13:09  (confirming)  │
│    ✓ TxDOT feed      — 13:05  (supporting)  │
│    ✗ No contradicting sources               │
├─────────────────────────────────────────────┤
│  LIMITATIONS:                               │
│    • Casualty count unconfirmed             │
│    • Building type inferred, not verified   │
│    • No direct sensor data                  │
└─────────────────────────────────────────────┘
```

---

## Database Schema

```sql
-- One row per real-world event
CREATE TABLE incidents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    status        TEXT DEFAULT 'active',   -- active | monitoring | resolved
    incident_type TEXT,
    location_lat  REAL,
    location_lng  REAL,
    location_desc TEXT,
    priority      INTEGER,                 -- 0–100
    confidence    REAL,                    -- 0.0–1.0 (separate from priority)
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Every raw normalized report
CREATE TABLE events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id     TEXT,
    source_type   TEXT,                    -- 'nws' | 'traffic' | 'cad' | 'manual'
    raw_text      TEXT,
    parsed_fields TEXT,                    -- JSON string
    confidence    REAL,
    provenance    TEXT,                    -- JSON string {origin, received_at, ...}
    received_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Links events to incidents (many-to-one)
CREATE TABLE incident_events (
    incident_id   INTEGER REFERENCES incidents(id),
    event_id      INTEGER REFERENCES events(id),
    attached_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    match_score   REAL,                    -- fusion confidence
    PRIMARY KEY (incident_id, event_id)
);

-- State changes for the timeline / delta view
CREATE TABLE timeline_entries (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id   INTEGER REFERENCES incidents(id),
    entry_type    TEXT,                    -- 'created' | 'evidence' | 'escalation' | 'resolved'
    summary       TEXT,
    delta_fields  TEXT,                    -- JSON string — what changed
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Registered feed metadata
CREATE TABLE sources (
    id            TEXT PRIMARY KEY,        -- 'nws' | 'txdot' | 'cad_sim' | 'manual'
    name          TEXT,
    source_type   TEXT,
    reliability   REAL DEFAULT 0.8,        -- base reliability rating 0–1
    last_polled   TIMESTAMP,
    status        TEXT DEFAULT 'active'
);
```

> **Note:** SQLite stores JSON as TEXT. Use Python's `json.loads()`/`json.dumps()` in the application layer. No extensions needed.

---

## Data Sources

| Source | Type | Access | Ingestion |
|---|---|---|---|
| **NWS Weather API** | Live | Free, no key, `api.weather.gov` | Polled every 60s for active Lubbock alerts |
| **Traffic** | Simulated | Team-authored PDFs uploaded to system | PDF upload → LLM extraction |
| **CAD / Dispatch** | Simulated | Team-authored PDFs uploaded to system | PDF upload → LLM extraction |
| **Field Reports** | Manual | Web form on the dashboard or PDF upload | On submission |

**Strategy:** NWS is the anchor — live weather alerts for Lubbock are real, free, no auth. Everything else is simulated. Team members create realistic reports offline and upload them as PDFs for ingestion. The LLM API is part of the **production pipeline** — it extracts entities and summarizes free-text content from ingested reports at runtime.

### Simulated Data (Team-Authored PDFs)

Team members create realistic emergency reports offline — 911 dispatch narratives, field reports, multi-agency updates — and save them as PDFs. These are uploaded to the system for ingestion, where they're processed through the same pipeline as any other data source:

1. **PDF ingestion** — extract text from uploaded PDF
2. **Normalization** — convert to standard Event envelope
3. **LLM extraction** — pull structured fields from the free-text content (incident type, location, injuries, hazards, agencies)
4. **Fusion + scoring** — rule-based classification, priority scoring, and incident matching

Demo scenarios are structured as timed sequences of PDF uploads to show the system fusing reports, escalating priority, and updating the timeline in real time:

```
Scenario: "I-27 Flash Flood Pileup"
  t+0:00  Upload: NWS Flash Flood Warning (Lubbock County)
  t+2:00  Upload: Traffic report — I-27 NB lanes blocked near Exit 6
  t+3:00  Upload: CAD dispatch — Vehicle rollover I-27 NB, 2 injuries
  t+5:00  Upload: Field report — Standing water ~1ft, vehicles stalled
  t+7:00  Upload: CAD update — Fuel leak from overturned tanker
  t+9:00  Upload: Field report — Fire hazard, requesting FD
```

The system processes each upload exactly like it would process real data — demonstrating ingestion, extraction, fusion, and priority updates live.

---

## Project Structure

```
RRIS/
├── backend/
│   ├── main.py                 # FastAPI app, routes, WebSocket
│   ├── models.py               # Pydantic schemas (Event, Incident, etc.)
│   ├── db.py                   # SQLite setup + queries
│   ├── ingestion/
│   │   ├── normalizer.py       # Raw → Event envelope
│   │   ├── nws.py              # NWS API poller
│   │   ├── pdf_ingest.py       # PDF text extraction + upload handler
│   │   └── simulator.py        # Timed replay of scenario uploads
│   ├── intelligence/
│   │   ├── extraction.py       # Entity extraction (hybrid: rules + LLM)
│   │   ├── llm_client.py       # LLM API wrapper (extraction + summarization)
│   │   ├── fusion.py           # Incident fusion engine (rule-based)
│   │   └── priority.py         # Priority scorer (rule-based)
│   └── config.py               # Thresholds, weights, fusion params
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Dashboard.jsx       # Incident list + timeline + deltas
│   │   │   ├── MapView.jsx         # Leaflet map + markers + overlays
│   │   │   ├── ExplainPanel.jsx    # Provenance + confidence + breakdown
│   │   │   ├── IncidentCard.jsx    # Single incident summary
│   │   │   └── RoleFilter.jsx      # Role-based view toggle
│   │   ├── hooks/
│   │   │   └── useWebSocket.js     # WebSocket connection + state
│   │   └── utils/
│   │       └── priorityColors.js   # Color mapping for priority levels
│   └── public/
├── data/
│   ├── scenarios/              # Timed scenario definitions (JSON)
│   ├── uploads/                # Team-authored simulated PDFs
│   └── fixtures/               # Static test data
├── docs/
│   └── ARCHITECTURE.md         # This file
├── Proposal/                   # Project proposal (final)
├── requirements.txt
├── package.json
├── LICENSE
└── README.md
```

---

## Development Timeline

| Week | Course Topic | Build Focus | Deliverable |
|---|---|---|---|
| 1 | Orientation & Technical Setup | Team formation, project definition | — |
| 2 | Project Scoping & Management | Proposal, repo setup, architecture | **Proposal (due Aug 30)** |
| 3 | Code Basics & Proposal Checkpoint | Backend skeleton: FastAPI + SQLite + Event schema + NWS poller | Working API with NWS ingestion |
| 4 | Human-Centered Design | Intelligence layer: extraction, fusion, priority scoring | Incidents fusing from multiple sources |
| 5 | LLM & Modern AI | Wire LLM API for extraction/summarization; build PDF ingestion pipeline | LLM-powered extraction working end-to-end |
| 6 | System Integration & Midterm Review | Frontend: React + Leaflet + WebSocket + Dashboard | **Midterm progress report** |
| 7 | Evaluation, Ethics & Communication | Explainability panel, role filters, delta tracking, polish | Feature-complete system |
| 8 | Presentation & Reflection | Demo video, final report, code cleanup | **Final report + demo video** |

---

## Scope Boundaries

### Must Deliver
- Ingestion from 2–3 sources (NWS live + simulated CAD/dispatch)
- Normalizer + Event envelope schema
- Entity extraction (rule-based)
- Incident fusion engine with configurable thresholds
- Priority scoring with confidence/severity separation
- Map overlay with incident markers and clusters
- Incident dashboard with timeline
- Explainability panel (sources, confidence, limitations)
- Demo with realistic simulated scenarios

### Should Deliver
- Delta tracking ("what changed since last view")
- Two role-specific view filters (Fire + EMS)

### Future Work (describe in report, don't build)
- Full role suite (Police, Transportation, EOC)
- Provenance engine with contradiction detection
- Real CAD/dispatch integration
- Mobile-optimized responder view
- Multi-agency shared operating picture
- Historical incident analytics

---

## Cost

Everything in this stack is **free**:
- NWS API: free, no key
- Leaflet + OpenStreetMap: free, no key
- FastAPI + SQLite + React: open source
- LLM API: used for runtime extraction/summarization — moderate call volume during demo; free-tier or university credits sufficient for development + presentation

---

## HCAI Alignment

This architecture was designed around human-centered AI principles from the ground up:

| Principle | How RRIS Implements It |
|---|---|
| **Transparency** | Hybrid intelligence — LLM handles extraction/summarization (flagged as AI-generated with confidence), while classification, scoring, and fusion use explainable rule-based logic |
| **Human-in-the-loop** | AI recommends priority; humans confirm and adjust. No automated dispatch or resource allocation |
| **Explainability** | Dedicated panel showing *why* the system scored an incident, *what data* supports it, and *where the limitations are* |
| **Confidence separation** | Severity and confidence are independent axes — the system never silently suppresses uncertain but critical information |
| **Provenance** | Every data point traces back to its source, timestamp, and confirmation status |
| **Configurability** | Fusion thresholds, priority weights, and role filters are tunable parameters, not hardcoded assumptions — users can see and adjust system behavior |
| **Ethical design** | No real emergency data used; simulated scenarios for development and demo; role-based views respect need-to-know without creating information silos |
