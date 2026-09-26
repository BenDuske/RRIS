# RRIS — Core Loop Roadmap

**Goal:** End-to-end prototype — input to output, not just code on GitHub.

Prove the core loop: match reports, update priority, display on map. Everything else is secondary until this demo runs.

---

## Current State

**Frontend (working, but on mock data):**
- Dashboard with incident cards sorted by priority
- Leaflet map with color-coded markers, popups, fly-to
- ExplainPanel with timeline, priority breakdown chart, sources, limitations
- Role filter toggle (All/Fire/EMS)
- Confirm/Adjust buttons (rendered but not wired)

**Backend (designed, but broken):**
- Pydantic models, SQLite schema, FastAPI endpoints — all real code
- Normalizer, extraction, confidence, priority, explainability — logic exists
- Fusion engine truncated at line 62; `process_event()` missing
- Import paths broken across multiple files
- `db.py` has full CRUD but nothing calls it
- Frontend and backend are not connected

---

## Phase 1: Fix the Backend

**Goal:** `uvicorn backend.main:app` runs without crashing. POST a report, GET it back.

| Task | File | Detail |
|------|------|--------|
| Complete fusion engine | `fusion.py` | Finish `find_matching_incident()` (geo+time+type match); write `process_event()` — fuse or create, recalculate priority/confidence, return incident |
| Fix import: config path | `fusion.py:9` | `from backend.intelligence.config` → `from backend.config` (config lives at `backend/config.py`) |
| Fix import: normalizer | `normalizer.py:2` | `from ingestion.models` → correct module path |
| Fix import: LLM function | `extraction.py:4` | `extract_structured_fields_with_llm` doesn't exist; wire to `llm.extract_fields()` or rename |
| Fix import: explainability | `main.py:7` | `get_incident_with_explainability` → `build_incident_explainability` |
| Wire SQLite or commit to in-memory | `main.py`, `fusion.py` | Pick one. SQLite preferred (schema ready, survives restart). |

**Test:** Start server → POST JSON to `/ingest` → GET `/incidents` → see the incident.

**Time estimate:** 3–4 hours

---

## Phase 2: JSON Report Submission UI

**Goal:** Paste a structured JSON report in the frontend; it hits `/ingest` and the incident appears on the map.

| Task | Detail |
|------|--------|
| Add "Submit Report" panel | `<textarea>` for JSON, Submit button, pre-filled example template |
| Connect frontend to backend | `fetch("http://localhost:8000/ingest", { method: "POST", body: jsonText })` |
| Replace mock data with live data | `useEffect` → `GET /incidents` on load and after each submission; store in React state |
| Wire WebSocket | Connect to `ws://localhost:8000/ws`; listen for `incident_update`; update state in real time |

**Test:** Paste a JSON report → incident appears on map and in sidebar within seconds.

**Time estimate:** 2–3 hours

---

## Phase 3: Report Matching Demo

**Goal:** Two reports about the same event combine. One report about a different event stays separate.

### Demo script

1. **Report A:** Vehicle collision at 33.535, -101.845
   - "Multi-vehicle collision I-27 NB near Exit 6, 2 injuries"
2. **Report B:** Same location (~100m away), 3 minutes later
   - "Fuel leak from overturned tanker, fire hazard, requesting FD"
3. **Expected result:** Both fuse into one incident. Priority escalates. Timeline shows both entries. Sources panel shows both with individual confidence.
4. **Report C:** Medical call at 33.584, -101.847
   - "Adult male collapsed near Buddy Holly & Broadway"
5. **Expected result:** Separate incident. Two pins on map. Two cards in sidebar.

### Fusion logic

Already mostly written. Haversine distance < threshold AND time delta < threshold AND type/location overlap → merge. `fusion.py` has haversine, config has thresholds. Complete the matching logic.

**Time estimate:** 1–2 hours (logic mostly exists)

---

## Phase 4: Priority Recalculation + Transparency

**Goal:** Priority visibly changes as reports arrive. Users see why and can override.

| Task | Detail |
|------|--------|
| Priority delta display | When priority changes after a new report, show "+22" in the incident card and timeline |
| Per-source attribution | In ExplainPanel sources section, show which details came from which report; mark rule-based vs. AI extractions |
| Wire Confirm/Reject | Confirm locks current priority; Adjust opens inline editor to override. Demonstrates human-in-the-loop. |
| Timeline entries from live data | Each fused report generates a timeline entry showing what changed |

**Time estimate:** 2–3 hours

---

## Phase 5: Demo Polish

**Goal:** Smooth 5-minute live demo.

| Task | Detail |
|------|--------|
| Pre-built scenario script | JSON file with 5–6 timed reports (the "I-27 Flash Flood Pileup" from ARCHITECTURE.md). Python script that POSTs sequentially, or a "Load Scenario" button in UI. |
| Visual feedback | Flash incident card on update, pulse map marker, auto-scroll to updated incident |
| Error handling | Malformed JSON → clear error message, not a crash |
| LLM optional | Rule-based extractor works for demo. LLM refines if key is available. Don't block on this. |

**Time estimate:** 1–2 hours

---

## What NOT to Build

The instructor said stop building outward. Skip these:

- PDF ingestion (paste JSON instead)
- NWS live polling (submit weather reports as JSON)
- User auth / roles (role filter already works visually)
- Docker / deployment
- Database migrations beyond init
- LLM integration (rule-based is sufficient; LLM is a stretch goal)

---

## Total Effort

| Phase | Hours |
|-------|-------|
| 1 — Fix Backend | 3–4 |
| 2 — JSON Submission UI | 2–3 |
| 3 — Report Matching | 1–2 |
| 4 — Priority + Transparency | 2–3 |
| 5 — Demo Polish | 1–2 |
| **Total** | **~10–14** |

The architecture is solid. This is wiring, not redesign.

---

## JSON Report Template (for Phase 2 text box)

```json
{
  "source_id": "cad_00142",
  "source_type": "cad",
  "raw_text": "Vehicle collision reported I-27 NB near Exit 6. Multiple vehicles. 2 injuries. Northbound lanes blocked.",
  "lat": 33.5351,
  "lng": -101.8452,
  "address": "I-27 NB near Exit 6, Lubbock, TX",
  "confidence": 0.85
}
```

The backend normalizer already accepts this shape and converts it to an Event envelope. No LLM needed — rule-based extraction handles classification, hazards, agencies, and severity from the `raw_text`.
