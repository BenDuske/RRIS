import asyncio
import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SCENARIOS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "scenarios")

BUILTIN_SCENARIOS = {
    "i27_flash_flood_pileup": {
        "name": "I-27 Flash Flood Pileup",
        "description": "Multi-vehicle crash during flash flooding on I-27",
        "events": [
            {
                "delay_seconds": 0,
                "source_id": "nws_flash_flood_001",
                "source_type": "nws",
                "raw_text": "Flash Flood Warning for Lubbock County until 3:00 PM CDT. Heavy rain producing 1-2 inches per hour. Low water crossings may flood. Avoid unnecessary travel.",
                "lat": 33.5779,
                "lng": -101.8552,
                "address": "Lubbock County, TX",
                "radius": 5000,
                "confidence": 1.0,
            },
            {
                "delay_seconds": 120,
                "source_id": "txdot_i27_001",
                "source_type": "traffic",
                "raw_text": "TxDOT: I-27 NB lanes blocked between Exit 4 and Exit 6 due to standing water and vehicle incident. Expect significant delays. Seek alternate routes.",
                "lat": 33.5351,
                "lng": -101.8452,
                "address": "I-27 NB near Exit 6, Lubbock, TX",
                "radius": 300,
                "confidence": 0.95,
            },
            {
                "delay_seconds": 180,
                "source_id": "cad_00142",
                "source_type": "cad",
                "raw_text": "Vehicle collision I-27 NB near Exit 6. Multiple vehicles involved including overturned SUV. At least 2 injuries reported, one possibly critical. Northbound lanes fully blocked. EMS and PD dispatched.",
                "lat": 33.5351,
                "lng": -101.8452,
                "address": "I-27 NB near Exit 6, Lubbock, TX",
                "radius": 200,
                "confidence": 0.85,
            },
            {
                "delay_seconds": 300,
                "source_id": "field_00087",
                "source_type": "manual",
                "raw_text": "Field unit on scene. Standing water approximately 1 foot deep across all lanes. Multiple vehicles stalled. Overturned SUV confirmed. 2 patients being treated, 1 with possible spinal injury. Traffic backing up to Exit 2.",
                "lat": 33.5351,
                "lng": -101.8452,
                "address": "I-27 NB near Exit 6, Lubbock, TX",
                "radius": 200,
                "confidence": 0.92,
            },
            {
                "delay_seconds": 420,
                "source_id": "cad_00142_update",
                "source_type": "cad",
                "raw_text": "Update: Fuel leak confirmed from overturned tanker trailer at I-27 NB crash scene. Fire hazard present. Requesting Fire Department and HazMat response. Expand closure to Exit 3.",
                "lat": 33.5351,
                "lng": -101.8452,
                "address": "I-27 NB near Exit 6, Lubbock, TX",
                "radius": 500,
                "confidence": 0.9,
            },
            {
                "delay_seconds": 540,
                "source_id": "field_00088",
                "source_type": "manual",
                "raw_text": "Fire department on scene. Fuel leak contained but not stopped. Setting up foam suppression. All lanes I-27 NB closed Exit 3 through Exit 8. Requesting additional EMS unit for third patient found in stalled vehicle.",
                "lat": 33.5351,
                "lng": -101.8452,
                "address": "I-27 NB Exit 3-8, Lubbock, TX",
                "radius": 800,
                "confidence": 0.95,
            },
        ],
    },
    "structure_fire_ave_q": {
        "name": "Structure Fire — Ave Q Residential",
        "description": "Residential structure fire with possible entrapment",
        "events": [
            {
                "delay_seconds": 0,
                "source_id": "cad_00145",
                "source_type": "cad",
                "raw_text": "911 call: Smoke visible from 2-story residential structure, 2400 block Ave Q. Caller reports occupants may still be inside. Engine 5 and Ladder 2 dispatched.",
                "lat": 33.5622,
                "lng": -101.8307,
                "address": "2400 block Ave Q, Lubbock, TX",
                "radius": 100,
                "confidence": 0.7,
            },
            {
                "delay_seconds": 120,
                "source_id": "field_00089",
                "source_type": "manual",
                "raw_text": "Engine 5 on scene. Active fire second floor, heavy smoke from all windows. Primary search in progress for occupants. Second alarm requested. Exposure risk to adjacent residence on south side.",
                "lat": 33.5622,
                "lng": -101.8307,
                "address": "2400 block Ave Q, Lubbock, TX",
                "radius": 100,
                "confidence": 0.95,
            },
            {
                "delay_seconds": 240,
                "source_id": "field_00090",
                "source_type": "manual",
                "raw_text": "Primary search complete — all occupants accounted for, 2 adults and 1 child evacuated prior to arrival. No injuries. Fire extending to attic space. Transitioning to defensive operations. Power company requested to cut service.",
                "lat": 33.5622,
                "lng": -101.8307,
                "address": "2400 block Ave Q, Lubbock, TX",
                "radius": 150,
                "confidence": 0.98,
            },
        ],
    },
    "medical_downtown": {
        "name": "Medical Emergency — Downtown",
        "description": "Medical call at Buddy Holly Ave intersection",
        "events": [
            {
                "delay_seconds": 0,
                "source_id": "cad_00138",
                "source_type": "cad",
                "raw_text": "Medical emergency. Adult male collapsed near intersection of Buddy Holly Ave and Broadway. Bystander reports patient is conscious and breathing but disoriented. EMS unit 4 dispatched.",
                "lat": 33.5845,
                "lng": -101.8469,
                "address": "Buddy Holly Ave & Broadway, Lubbock, TX",
                "radius": 50,
                "confidence": 0.9,
            },
            {
                "delay_seconds": 90,
                "source_id": "field_00085",
                "source_type": "manual",
                "raw_text": "EMS on scene. Patient is a 58-year-old male, alert and oriented, complaining of chest pain and dizziness. Vitals stable. Transporting to UMC emergency department. Scene clear.",
                "lat": 33.5845,
                "lng": -101.8469,
                "address": "Buddy Holly Ave & Broadway, Lubbock, TX",
                "radius": 50,
                "confidence": 0.95,
            },
        ],
    },
}


class ScenarioPlayer:
    def __init__(self, on_event_callback=None):
        self.on_event = on_event_callback
        self.running = False
        self._task = None

    async def play(self, scenario_key: str, speed: float = 1.0):
        scenario = BUILTIN_SCENARIOS.get(scenario_key)
        if not scenario:
            path = os.path.join(SCENARIOS_DIR, f"{scenario_key}.json")
            if os.path.exists(path):
                with open(path) as f:
                    scenario = json.load(f)
            else:
                raise ValueError(f"Scenario '{scenario_key}' not found")

        logger.info(f"Playing scenario: {scenario['name']} (speed: {speed}x)")
        self.running = True

        for i, event_data in enumerate(scenario["events"]):
            if not self.running:
                logger.info("Scenario playback stopped")
                return

            delay = event_data["delay_seconds"] / speed
            if i > 0:
                prev_delay = scenario["events"][i - 1]["delay_seconds"] / speed
                wait = delay - prev_delay
            else:
                wait = 0

            if wait > 0:
                logger.info(f"  Waiting {wait:.0f}s before next event...")
                await asyncio.sleep(wait)

            report = {k: v for k, v in event_data.items() if k != "delay_seconds"}
            report["timestamp"] = datetime.now(timezone.utc).isoformat()

            logger.info(f"  [{i+1}/{len(scenario['events'])}] Injecting: {report['source_id']} ({report['source_type']})")

            if self.on_event:
                await self.on_event(report)

        self.running = False
        logger.info(f"Scenario complete: {scenario['name']}")

    def stop(self):
        self.running = False

    def start_background(self, scenario_key: str, speed: float = 1.0):
        self._task = asyncio.create_task(self.play(scenario_key, speed))
        return self._task

    @staticmethod
    def list_scenarios() -> list[dict]:
        scenarios = []
        for key, s in BUILTIN_SCENARIOS.items():
            scenarios.append({
                "key": key,
                "name": s["name"],
                "description": s["description"],
                "event_count": len(s["events"]),
                "duration_seconds": s["events"][-1]["delay_seconds"] if s["events"] else 0,
            })

        os.makedirs(SCENARIOS_DIR, exist_ok=True)
        for f in os.listdir(SCENARIOS_DIR):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(SCENARIOS_DIR, f)) as fh:
                        data = json.load(fh)
                    scenarios.append({
                        "key": f.removesuffix(".json"),
                        "name": data.get("name", f),
                        "description": data.get("description", ""),
                        "event_count": len(data.get("events", [])),
                        "duration_seconds": data["events"][-1]["delay_seconds"] if data.get("events") else 0,
                        "source": "file",
                    })
                except Exception:
                    pass
        return scenarios
