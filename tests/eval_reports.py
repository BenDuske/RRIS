"""Hand-labeled evaluation set for RRIS.

Each entry: (source_type, raw_text, expected_type, expected_tier, expected_injuries)
  expected_type     : one of the system categories, or None for out-of-scope reports
  expected_tier     : Info < Low < Moderate < High < Critical (what a responder would want)
  expected_injuries : int, or None when no count is stated
Labels were written from a responder point of view, independent of the scoring code.
"""

FIRE, HAZ, MED, TRAF, FLOOD = (
    "Structure Fire", "HazMat Incident", "Medical Emergency",
    "Traffic Incident", "Flooding / Road Hazard",
)

EVAL_REPORTS = [
    # --- Structure fire ---
    ("cad", "Smoke visible from 2-story residential structure. Caller says occupants may still be inside. Engine 5 dispatched.", FIRE, "Critical", None),
    ("manual", "Active fire second floor, heavy smoke from all windows. Second alarm requested. No injuries.", FIRE, "High", 0),
    ("cad", "Structure fire at strip mall, fully involved, exposure risk to adjacent businesses. Engine 3 and Ladder 2 dispatched.", FIRE, "High", None),
    ("cad", "Small kitchen fire in apartment, occupant extinguished it. Engine responding to check. No injuries.", FIRE, "Low", 0),
    ("manual", "Smoke visible from attic vent, residents evacuated safely. 1 minor smoke inhalation, patient stable.", FIRE, "Moderate", 1),
    ("cad", "Building fire downtown, heavy smoke visible, two people trapped on third floor.", FIRE, "Critical", None),
    # --- HazMat ---
    ("cad", "Fuel leak from overturned tanker on highway. Fire hazard present. Requesting HazMat and Fire Department.", HAZ, "Critical", None),
    ("manual", "Chemical spill at warehouse loading dock, strong fumes, workers evacuating. HazMat requested.", HAZ, "High", None),
    ("cad", "Small gasoline spill at gas station pump, attendant has it contained. No injuries.", HAZ, "Low", 0),
    ("manual", "Toxic chemical odor reported near school, 3 students dizzy. HazMat and EMS requested.", HAZ, "Critical", 3),
    ("cad", "Fuel spill from damaged vehicle, leaking into storm drain. Fire department dispatched.", HAZ, "High", None),
    ("manual", "Hazmat team on scene, leak contained and stable. No injuries.", HAZ, "Low", 0),
    # --- Medical ---
    ("cad", "Medical emergency. Adult male collapsed, unconscious, not breathing. EMS unit 4 dispatched.", MED, "Critical", None),
    ("cad", "Adult male collapsed near intersection, conscious and breathing but disoriented. EMS dispatched.", MED, "Moderate", None),
    ("manual", "Patient 58-year-old male, chest pain and dizziness, vitals stable. Transporting to UMC.", MED, "Moderate", 1),
    ("cad", "Woman fell in grocery store, conscious, minor ankle injury. EMS requested.", MED, "Low", 1),
    ("manual", "Mass casualty incident at stadium, multiple patients down, EMS requesting mutual aid.", MED, "Critical", None),
    ("cad", "Patient with severe allergic reaction, difficulty breathing, life-threatening. EMS dispatched.", MED, "Critical", 1),
    ("manual", "Patient refused transport, minor cut on hand, stable.", MED, "Info", 1),
    # --- Traffic ---
    ("cad", "Vehicle collision I-27 NB. Multiple vehicles. 2 injuries. Northbound lanes blocked.", TRAF, "High", 2),
    ("traffic", "I-27 NB lanes blocked due to vehicle incident. Expect significant delays.", TRAF, "Low", None),
    ("cad", "Minor fender bender in parking lot, non-injury, vehicles moved.", TRAF, "Info", 0),
    ("cad", "Rollover crash on highway, driver trapped in vehicle, critical injuries. EMS and fire dispatched.", TRAF, "Critical", None),
    ("cad", "Two-vehicle collision at intersection, 1 injury, both lanes blocked.", TRAF, "Moderate", 1),
    ("manual", "Multi-vehicle pileup in dust storm, at least 4 injuries, several vehicles overturned.", TRAF, "Critical", 4),
    ("traffic", "Stalled vehicle on shoulder, traffic moving normally.", TRAF, "Info", None),
    # --- Flooding ---
    ("nws", "Flash Flood Warning for Lubbock County until 3:00 PM. Heavy rain producing 1-2 inches per hour. Low water crossings may flood.", FLOOD, "High", None),
    ("manual", "Standing water across all lanes approximately 1 foot deep. Multiple vehicles stalled.", FLOOD, "Moderate", None),
    ("manual", "Low water crossing flooded on County Road, barricades placed. No vehicles involved.", FLOOD, "Low", None),
    ("cad", "Vehicle stalled in flood water, driver trapped, water rising. Swift water rescue requested.", FLOOD, "Critical", None),
    ("manual", "Street flooding reported, water receding, no injuries.", FLOOD, "Info", 0),
    # --- Out of scope for the current taxonomy (system should abstain, not guess) ---
    ("cad", "Shots fired reported near apartment complex, suspect fled on foot. Police dispatched.", None, "High", None),
    ("cad", "Power outage affecting 200 homes, utility crew en route.", None, "Low", None),
    ("manual", "Suspicious person reported near elementary school, no threat observed.", None, "Low", None),
    ("cad", "Noise complaint at residence, caller says loud music.", None, "Info", None),
    # --- Phrasing variety ---
    ("manual", "Crash on Loop 289 westbound, car versus pole, driver conscious, 1 injured, EMS on scene.", TRAF, "Moderate", 1),
    ("cad", "Grass fire near highway spreading toward homes, engines responding. Active fire.", FIRE, "High", None),
    ("manual", "Two patients with minor injuries from bicycle collision, both stable and conscious.", TRAF, "Low", 2),
    ("cad", "Caller reports strong smell of natural gas in apartment hallway, evacuating building. Fire department dispatched.", HAZ, "High", None),
    ("manual", "Elderly woman found unresponsive at home, no pulse, CPR in progress. Critical.", MED, "Critical", None),
]
