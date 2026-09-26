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
| Backend | Python 3.10+, FastAPI, Pydantic |
| Frontend | React 19, Vite, Leaflet.js, Recharts |
| AI | Rule-based extraction + optional LLM refinement |
| Real-time | WebSocket (FastAPI native) |

## Team

| Member | Role |
|--------|------|
| Derrick Hawkins | Project Coordinator / Research / Simulated Data |
| Benjamin Duske | Architecture / UI/UX |
| Marc Griffin | Data / Classification / Priority Scoring |
| Nicholas Kelly | Research / Priority Scoring / UI/UX |

---

## Setup and Run Instructions

These instructions will get RRIS running on your computer from scratch. You need two things running at the same time: the **backend** (Python server that processes reports) and the **frontend** (the web page you see in your browser). Each runs in its own terminal window.

### What You Need Installed First

Before you start, make sure you have these installed on your computer:

1. **Python 3.10 or newer**
   - Check if you have it: open a terminal and type `python3 --version`
   - If you see something like `Python 3.10.12` or higher, you're good
   - If not, download from https://www.python.org/downloads/

2. **Node.js 18 or newer**
   - Check if you have it: open a terminal and type `node --version`
   - If you see something like `v18.0.0` or higher, you're good
   - If not, download from https://nodejs.org/ (choose the LTS version)

3. **Git**
   - Check if you have it: open a terminal and type `git --version`
   - If not, download from https://git-scm.com/downloads

### Step 1: Clone the Repository

Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
git clone https://github.com/BenDuske/RRIS.git
cd RRIS
```

If you already cloned it before, just pull the latest changes:

```bash
cd RRIS
git pull origin main
```

### Step 2: Set Up the Backend (Python)

You only need to do steps 2a and 2b **once**. After that, skip to step 2c.

**2a. Create a virtual environment**

This creates an isolated Python environment so the project's packages don't interfere with anything else on your system.

On Mac/Linux:
```bash
python3 -m venv .venv
```

On Windows:
```bash
python -m venv .venv
```

**2b. Install the Python dependencies**

First, activate the virtual environment:

On Mac/Linux:
```bash
source .venv/bin/activate
```

On Windows (Command Prompt):
```bash
.venv\Scripts\activate
```

On Windows (PowerShell):
```bash
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` appear at the beginning of your terminal prompt. That means it's active.

Now install the dependencies:
```bash
pip install -r requirements.txt
```

**2c. Start the backend server**

Make sure your virtual environment is activated (you should see `(.venv)` in your prompt). If not, run the activate command from step 2b again.

```bash
uvicorn backend.main:app --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Leave this terminal open and running.** The backend needs to stay running the entire time.

### Step 3: Set Up the Frontend (React)

**Open a second terminal window.** The backend is running in the first one — don't close it.

Navigate to the project folder again, then into the frontend directory:

```bash
cd RRIS/frontend
```

(Or if you're already in the RRIS folder: `cd frontend`)

**3a. Install the JavaScript dependencies** (only needed once)

```bash
npm install
```

This will take a minute the first time. You'll see a progress bar.

**3b. Start the frontend development server**

```bash
npm run dev
```

You should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Step 4: Open in Your Browser

Open your web browser (Chrome, Firefox, Edge — any modern browser) and go to:

```
http://localhost:5173
```

You should see the RRIS dashboard with:
- A dark header bar saying "RRIS — Rapid Response Information System"
- A sidebar on the left with a JSON text box and buttons
- A map of Lubbock, Texas on the right
- "0 Active Incidents" in the sidebar

If the map shows but the header says **"Disconnected"** in red — that's OK. It means the WebSocket connection didn't establish, but the app still works. The data loads via normal HTTP requests.

---

## Running the Demo

The demo simulates a multi-agency emergency: a flash flood on I-27 in Lubbock causes a multi-vehicle pileup, which escalates when a tanker truck overturns and leaks fuel.

### One-Click Demo

1. Click the green **"Run Demo"** button in the sidebar
2. Watch the sidebar — reports arrive every 3 seconds:
   - **Report 1:** NWS Flash Flood Warning (creates Incident #1)
   - **Report 2:** TxDOT traffic blockage on I-27 (creates Incident #2)
   - **Report 3:** 911 Dispatch — vehicle rollover, 2 injuries (fuses into Incident #2, priority jumps)
   - **Report 4:** Field report — standing water, stalled vehicles (fuses into Incident #2)
   - **Report 5:** 911 Dispatch — fuel leak from tanker, HazMat dispatched (fuses into Incident #2, escalation)
   - **Report 6:** Field report — fire hazard, requesting Fire Department (fuses into Incident #2)

3. After all 6 reports: you should see 2 incidents
   - **Incident #1:** "Flooding / Road Hazard" — priority ~8 (low, single NWS source)
   - **Incident #2:** "HazMat Incident" — priority ~80 (critical, 5 fused sources)

### Exploring the Results

**Click on an incident** in the sidebar to see the detail panel below the map:

- **Timeline:** Every report that contributed, with timestamps, source labels (911 Dispatch, TxDOT Traffic, Field Report, NWS Weather), and escalation markers
- **Priority Breakdown:** Bar chart showing how each factor (Severity, Injuries, Hazards, Agencies, Confidence) contributes to the overall score
- **Data Sources:** Each individual report with the specific details it contributed (injuries, hazards, agencies, severity estimate) shown as colored tags
- **Limitations:** Honest disclosure of what the AI doesn't know (e.g., "Injury count not confirmed by all sources")

**Try the human-in-the-loop controls** at the bottom of the detail panel:

- Click **"Confirm"** to accept the AI's recommended priority
- Click **"Adjust"** to override the priority with your own value (type a number 0-100 and click "Set")

### Submitting Your Own Report

You can type or paste your own JSON report into the text box in the sidebar. Here's the format:

```json
{
  "source_id": "my_report_001",
  "source_type": "cad",
  "raw_text": "Structure fire reported at 2500 Broadway, Lubbock. Smoke visible. Engine 4 dispatched.",
  "lat": 33.5630,
  "lng": -101.8469,
  "address": "2500 Broadway, Lubbock, TX",
  "confidence": 0.9
}
```

**Field descriptions:**

| Field | What It Means | Example Values |
|-------|---------------|----------------|
| `source_id` | Unique ID for this report | `"cad_00142"`, `"nws_001"`, `"field_007"` |
| `source_type` | Where the report came from | `"cad"` (911), `"nws"` (weather), `"traffic"`, `"manual"` (field) |
| `raw_text` | The actual report text | Any description of the emergency |
| `lat` | Latitude (decimal degrees) | `33.5779` |
| `lng` | Longitude (decimal degrees) | `-101.8552` |
| `address` | Human-readable location | `"I-27 NB near Exit 6, Lubbock, TX"` |
| `confidence` | How reliable this source is (0.0 to 1.0) | `0.85` |

Click **"Submit"** to send it. If the location is within ~150 meters of an existing incident and within the time window, it will fuse into that incident. Otherwise, it creates a new one.

### Resetting

- **"Clear All"** button: Removes all incidents so you can start fresh
- **"Reset"** button: Resets the text box back to the example JSON
- **"Run Demo"** automatically clears all incidents before starting, so you can click it multiple times

---

## Stopping the Servers

When you're done:

1. Go to the terminal running the **frontend** and press `Ctrl + C`
2. Go to the terminal running the **backend** and press `Ctrl + C`

---

## Troubleshooting

**"command not found: python3"**
Try `python` instead of `python3`. On Windows, Python usually installs as just `python`.

**"command not found: pip"**
Make sure your virtual environment is activated (you should see `(.venv)` in your prompt). If that doesn't work, try `pip3` instead of `pip`.

**"command not found: uvicorn"**
Make sure your virtual environment is activated, then run `pip install -r requirements.txt` again.

**"command not found: npm"**
You need to install Node.js. Download it from https://nodejs.org/

**Backend starts but frontend can't connect**
Make sure the backend is running on port 8000 (the default). Check that you see `Uvicorn running on http://127.0.0.1:8000` in the backend terminal.

**Map tiles don't load / show gray squares**
Your internet connection might be blocking the Esri tile server. The map requires an internet connection to load the basemap tiles. The incident markers and data will still work without tiles.

**"Port 5173 is in use"**
Another program is using that port. Either close it, or run the frontend on a different port:
```bash
npm run dev -- --port 3000
```
Then open `http://localhost:3000` in your browser instead.

**"ModuleNotFoundError: No module named 'backend'"**
You need to run the backend from the project root directory (the RRIS folder), not from inside the backend folder. Make sure you're in the folder that contains both `backend/` and `frontend/`.

---

## Project Structure

```
RRIS/
├── backend/
│   ├── main.py                 # FastAPI app — endpoints, WebSocket, enrichment
│   ├── models.py               # Pydantic schemas (Event, Incident, Location, etc.)
│   ├── config.py               # Thresholds, weights, fusion parameters
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── normalizer.py       # Raw JSON report → Event object
│   │   ├── nws.py              # NWS API poller (Lubbock County)
│   │   ├── pdf_ingest.py       # PDF text extraction
│   │   └── __init__.py
│   └── intelligence/
│       ├── extraction.py       # Entity extraction (rule-based + optional LLM)
│       ├── fusion.py           # Incident fusion engine (spatial + temporal matching)
│       ├── priority.py         # Weighted priority scorer
│       ├── confidence.py       # Source confidence scoring
│       ├── explainability.py   # Builds explainability data for transparency
│       ├── llm_client.py       # Optional LLM integration client
│       └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main layout (sidebar + map + detail panel)
│   │   ├── components/
│   │   │   ├── Dashboard.jsx   # Incident list sorted by priority
│   │   │   ├── MapView.jsx     # Leaflet map with incident markers
│   │   │   ├── ExplainPanel.jsx # Timeline, priority breakdown, sources, confirm/adjust
│   │   │   ├── IncidentCard.jsx # Single incident summary card with delta badges
│   │   │   ├── ReportSubmit.jsx # JSON input form, demo runner, clear button
│   │   │   └── RoleFilter.jsx  # Role-based view toggle (All/Fire/EMS)
│   │   ├── data/
│   │   │   ├── demoScenario.js # 6-report I-27 Flash Flood Pileup demo sequence
│   │   │   └── mockIncidents.js # Static mock data (not used in live mode)
│   │   └── utils/
│   │       └── priorityColors.js # Color tiers, icons, source labels, role filters
│   ├── package.json
│   └── vite.config.js          # Dev server config with backend proxy
├── Media/                      # Screenshots and demo recordings
├── Proposal/                   # Project proposal document
├── ROADMAP.md                  # Development roadmap (phases 1-5)
├── ARCHITECTURE.md             # System architecture document
├── requirements.txt            # Python dependencies
├── .gitignore
├── LICENSE
└── README.md
```

---

## License

[MIT](LICENSE)
