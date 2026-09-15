# RRIS — Rapid Response Information System

An AI-assisted emergency incident information system that consolidates multiple emergency reports into a unified, prioritized incident picture for first responders.

## Overview

During emergencies, personnel receive information from 911 dispatch, field reports, weather services, traffic systems, and other sources. These reports can be incomplete, duplicated, delayed, or formatted differently. RRIS combines related reports into a single incident view, classifies and scores priority using a hybrid AI approach (LLM extraction + rule-based scoring), and keeps the human decision-maker in control.

**Key features:**
- Incident fusion — combines related reports into unified records
- 8-category classification (Fire, Medical, Transportation, Weather, HazMat, Infrastructure, Public Safety, Rescue)
- Weighted priority scoring with separate severity and confidence indicators
- Explainability panel — shows *why* the system scored an incident the way it did
- Human confirmation/adjustment — AI recommends, humans decide
- Map-based unified incident view (Leaflet.js)

**Demo area:** Lubbock, Texas (simulated data — no real 911/CAD access).

## Tech Stack

| Layer | Tools |
|-------|-------|
| Backend | Python, FastAPI |
| Frontend | React, Leaflet.js |
| Data/ML | pandas, NumPy, scikit-learn |
| Database | SQLite (dev) / PostgreSQL (optional) |
| AI | LLM API for extraction/summarization |
| DevOps | GitHub, Jupyter/Anaconda |

## Project Structure

```
RRIS/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── models.py               # Pydantic schemas (legacy location)
│   ├── config.py               # Thresholds, weights, fusion params
│   ├── ingestion/
│   │   ├── models.py           # Pydantic schemas (Event, Incident, etc.)
│   │   ├── normalizer.py       # Raw report → Event envelope
│   │   ├── nws.py              # NWS API poller (Lubbock County)
│   │   └── pdf_ingest.py       # PDF text extraction (stub)
│   └── intelligence/
│       ├── extraction.py       # Entity extraction (stub)
│       ├── fusion.py           # Incident fusion engine (stub)
│       ├── priority.py         # Priority scorer (stub)
│       ├── confidence.py       # Confidence scoring (stub)
│       └── explainability.py   # Explainability logic (stub)
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main layout (sidebar + map + detail panel)
│   │   ├── components/
│   │   │   ├── Dashboard.jsx   # Incident list sorted by priority
│   │   │   ├── MapView.jsx     # Leaflet map with markers + overlays
│   │   │   ├── ExplainPanel.jsx # Timeline, priority breakdown, sources, limitations
│   │   │   ├── IncidentCard.jsx # Single incident summary card
│   │   │   └── RoleFilter.jsx  # Role-based view toggle (All/Fire/EMS)
│   │   ├── data/
│   │   │   └── mockIncidents.js # Simulated incident data for development
│   │   └── utils/
│   │       └── priorityColors.js # Color tiers, labels, role filter configs
│   └── package.json
├── Media/                      # Screenshots and demo assets
├── Proposal/                   # Project proposal (final)
├── ARCHITECTURE.md             # Full system architecture document
├── LICENSE
└── README.md
```

## Team

| Member | Role |
|--------|------|
| Derrick Hawkins | Project Coordinator / Research / Simulated Data |
| Benjamin Duske | Architecture / UI/UX |
| Marc Griffin | Data / Classification / Priority Scoring |
| Nicholas Kelly | Research / Priority Scoring / UI/UX |

## Timeline

- **Phase 1** — Proposal and Planning *(due Aug 30)*
- **Phase 2** — Data and Intelligence
- **Phase 3** — Incident Fusion and Updates
- **Phase 4** — Interface and Integration
- **Final** — Testing and Presentation

---

## Getting Started

### Prerequisites

- [Git](https://git-scm.com/downloads)
- [Node.js](https://nodejs.org/) (v18 or later) — required for the frontend
- A GitHub account with access to this repository

### Clone the repo

```bash
git clone https://github.com/BenDuske/RRIS.git
cd RRIS
```

### Sync your local copy

Before starting any work, always pull the latest changes:

```bash
git pull origin main
```

### Running the Frontend (UI)

The frontend is a React app using Vite. To run it locally:

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies (only needed the first time or after package.json changes)
npm install

# 3. Start the development server
npm run dev
```

The dashboard will open at **http://localhost:5173**. It currently runs on mock data — no backend connection needed yet.

**What you'll see:**
- Left sidebar with incident cards sorted by priority
- Map centered on Lubbock with color-coded incident markers
- Click any incident to view the explainability panel (timeline, priority breakdown, data sources, limitations)
- Role filter toggle in the header (All Fields / Fire / EMS)

### Git Workflow

```bash
# 1. Pull latest before you start
git pull origin main

# 2. Create a branch for your work
git checkout -b your-name/short-description
#    e.g.  git checkout -b marc/classification-engine

# 3. Do your work, then stage and commit
git add .
git commit -m "brief description of what you did"

# 4. Push your branch
git push origin your-name/short-description

# 5. Open a Pull Request on GitHub to merge into main
#    (or coordinate with the team on merge strategy)
```

### Quick Reference

| Task | Command |
|------|---------|
| Clone | `git clone https://github.com/BenDuske/RRIS.git` |
| Pull latest | `git pull origin main` |
| Check status | `git status` |
| See branches | `git branch -a` |
| Switch branch | `git checkout branch-name` |
| New branch | `git checkout -b your-name/feature` |
| Stage all | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push origin branch-name` |
| View log | `git log --oneline -10` |
| Run frontend | `cd frontend && npm install && npm run dev` |

---

## License

[MIT](LICENSE)
