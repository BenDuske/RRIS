export function getPriorityTier(priority) {
  if (priority >= 80) return { label: "Critical", color: "#dc2626", bg: "#fef2f2" };
  if (priority >= 60) return { label: "High", color: "#ea580c", bg: "#fff7ed" };
  if (priority >= 40) return { label: "Moderate", color: "#ca8a04", bg: "#fefce8" };
  if (priority >= 20) return { label: "Low", color: "#2563eb", bg: "#eff6ff" };
  return { label: "Info", color: "#6b7280", bg: "#f9fafb" };
}

export function getConfidenceLabel(confidence) {
  if (confidence >= 0.8) return "High";
  if (confidence >= 0.5) return "Medium";
  return "Low";
}

export function formatTime(isoString) {
  return new Date(isoString).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export function formatTimeShort(isoString) {
  return new Date(isoString).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

export const INCIDENT_ICONS = {
  Fire: "🔥",
  "Structure Fire": "🔥",
  Medical: "🏥",
  "Medical Emergency": "🏥",
  Transportation: "🚗",
  "Traffic Incident": "🚗",
  Weather: "⛈️",
  HazMat: "☢️",
  "HazMat Incident": "☢️",
  "Flooding / Road Hazard": "🌊",
  Infrastructure: "🏗️",
  "Public Safety": "🛡️",
  Rescue: "🚁",
};

export const SOURCE_LABELS = {
  cad: "911 Dispatch",
  nws: "NWS Weather",
  traffic: "TxDOT Traffic",
  manual: "Field Report",
  pdf: "PDF Upload",
};

export const ROLE_FILTERS = {
  all: {
    label: "All Fields",
    highlight: [],
    suppress: [],
  },
  fire: {
    label: "Fire / Rescue",
    highlight: ["hazards", "severity_estimate", "key_details"],
    suppress: [],
  },
  ems: {
    label: "EMS",
    highlight: ["injuries", "key_details"],
    suppress: [],
  },
};
