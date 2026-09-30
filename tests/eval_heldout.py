"""Held-out evaluation reports.

Written AFTER the keyword/severity tuning on tests/eval_reports.py and never used
to tune anything. Run once and report the numbers as-is.
Same tuple format as eval_reports.EVAL_REPORTS.
"""
from tests.eval_reports import FIRE, HAZ, MED, TRAF, FLOOD

HELDOUT_REPORTS = [
    ("cad", "House fire on 34th Street, flames through the roof, neighbors report a child may be inside. Engine 7 dispatched.", FIRE, "Critical", None),
    ("manual", "Dumpster fire behind restaurant, extinguished by staff. Engine checking for extension. No injuries.", FIRE, "Low", 0),
    ("cad", "Propane tank leaking at a home, strong odor, residents evacuated. HazMat and fire department requested.", HAZ, "High", None),
    ("manual", "Diesel spill on parking lot, about 10 gallons, contained with absorbent. No injuries.", HAZ, "Low", 0),
    ("cad", "Man having a seizure at bus stop, conscious now, EMS on the way.", None, "Moderate", None),
    ("cad", "Child not breathing after choking, parent performing CPR, EMS dispatched.", MED, "Critical", 1),
    ("manual", "Patient with a sprained wrist from a fall, stable, refusing transport.", MED, "Info", 1),
    ("cad", "Head-on collision on Highway 84, 3 injuries, one driver pinned in the vehicle. EMS and fire dispatched.", TRAF, "Critical", 3),
    ("traffic", "Disabled vehicle blocking right lane on Loop 289, expect delays.", TRAF, "Low", None),
    ("cad", "Motorcycle crash on Slide Road, rider conscious with a leg injury, 1 injured, EMS responding.", TRAF, "Moderate", 1),
    ("nws", "Flash Flood Warning issued for Lubbock County. Low water crossings will flood. Do not drive through flooded roads.", FLOOD, "High", None),
    ("manual", "Street flooding on Avenue Q, water over the curb, several parked cars affected, no people in danger.", FLOOD, "Low", None),
    ("cad", "Armed robbery in progress at convenience store, suspect has a weapon. Police dispatched.", None, "High", None),
    ("cad", "Traffic signal out at 19th and University, police directing traffic.", None, "Low", None),
    ("manual", "Report of a loose dog near the park, no one hurt.", None, "Info", None),
]
