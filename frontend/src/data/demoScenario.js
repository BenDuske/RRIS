const demoScenario = [
  {
    label: "NWS Flash Flood Warning",
    delay: 0,
    report: {
      source_id: "nws_flash_flood_001",
      source_type: "nws",
      raw_text:
        "Flash Flood Warning for Lubbock County until 3:00 PM CDT. Heavy rain producing 1-2 inches per hour. Low water crossings may flood. Avoid travel if possible.",
      lat: 33.5779,
      lng: -101.8552,
      address: "Lubbock County, TX",
      confidence: 1.0,
    },
  },
  {
    label: "Traffic report — I-27 NB blocked",
    delay: 3000,
    report: {
      source_id: "txdot_i27_001",
      source_type: "traffic",
      raw_text:
        "TxDOT: I-27 NB lanes blocked between Exit 4 and Exit 6. Standing water on roadway. Expect significant delays. Seek alternate routes.",
      lat: 33.5351,
      lng: -101.8452,
      address: "I-27 NB near Exit 6, Lubbock, TX",
      confidence: 0.9,
    },
  },
  {
    label: "CAD — Vehicle rollover, 2 injuries",
    delay: 3000,
    report: {
      source_id: "cad_00142",
      source_type: "cad",
      raw_text:
        "Vehicle collision I-27 NB near Exit 6. Rollover involving semi-truck and two passenger vehicles. 2 injuries reported, one possibly critical. Northbound lanes fully blocked.",
      lat: 33.5355,
      lng: -101.8448,
      address: "I-27 NB near Exit 6, Lubbock, TX",
      confidence: 0.85,
    },
  },
  {
    label: "Field report — standing water, stalled vehicles",
    delay: 3000,
    report: {
      source_id: "field_00086",
      source_type: "manual",
      raw_text:
        "Field unit on scene. Standing water approximately 1 foot deep across all NB lanes. Multiple vehicles stalled in floodwater. Requesting barricades and traffic diversion.",
      lat: 33.5349,
      lng: -101.8455,
      address: "I-27 NB near Exit 6, Lubbock, TX",
      confidence: 0.8,
    },
  },
  {
    label: "CAD update — fuel leak from tanker",
    delay: 3000,
    report: {
      source_id: "cad_00143",
      source_type: "cad",
      raw_text:
        "Update: Fuel leak confirmed from overturned tanker truck. Diesel fuel entering floodwater. HazMat team dispatched. Expanding perimeter to 500 meters.",
      lat: 33.5353,
      lng: -101.845,
      address: "I-27 NB near Exit 6, Lubbock, TX",
      confidence: 0.92,
    },
  },
  {
    label: "Field report — fire hazard, requesting FD",
    delay: 3000,
    report: {
      source_id: "field_00087",
      source_type: "manual",
      raw_text:
        "Fire hazard present — diesel fumes accumulating near overturned tanker. Requesting Fire Department for standby. One patient critical, EMS requesting additional unit. Second alarm conditions.",
      lat: 33.5352,
      lng: -101.8451,
      address: "I-27 NB near Exit 6, Lubbock, TX",
      confidence: 0.95,
    },
  },
];

export default demoScenario;
