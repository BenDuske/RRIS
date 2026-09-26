import { useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import {
  getPriorityTier, getConfidenceLabel, formatTime, SOURCE_LABELS,
} from "../utils/priorityColors";

const API_URL = "http://localhost:8000";

function Timeline({ timeline }) {
  const typeStyles = {
    created: { color: "#2563eb", icon: "●" },
    evidence: { color: "#16a34a", icon: "◆" },
    escalation: { color: "#dc2626", icon: "▲" },
    resolved: { color: "#6b7280", icon: "■" },
  };

  return (
    <div>
      <h4 style={{ margin: "0 0 8px", fontSize: "13px", color: "#374151" }}>Timeline</h4>
      <div style={{ borderLeft: "2px solid #e5e7eb", paddingLeft: "12px" }}>
        {(timeline || []).map((entry, i) => {
          const style = typeStyles[entry.type] || typeStyles.evidence;
          const sourceLabel = entry.source_type
            ? SOURCE_LABELS[entry.source_type] || entry.source_type
            : null;
          return (
            <div key={i} style={{ marginBottom: "8px", fontSize: "12px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ color: style.color, fontSize: "10px" }}>{style.icon}</span>
                <span style={{ color: "#9ca3af", fontFamily: "monospace", fontSize: "11px" }}>
                  {formatTime(entry.created_at)}
                </span>
                <span style={{ fontSize: "9px", textTransform: "uppercase", color: style.color, fontWeight: 600 }}>
                  {entry.type}
                </span>
                {sourceLabel && (
                  <span style={{ fontSize: "9px", color: "#9ca3af", backgroundColor: "#f3f4f6", padding: "1px 4px", borderRadius: "3px" }}>
                    {sourceLabel}
                  </span>
                )}
              </div>
              <div style={{ color: "#374151", marginTop: "2px", marginLeft: "16px" }}>
                {entry.summary}
              </div>
            </div>
          );
        })}
        {(!timeline || timeline.length === 0) && (
          <div style={{ color: "#9ca3af", fontSize: "12px" }}>No timeline data</div>
        )}
      </div>
    </div>
  );
}

function PriorityBreakdown({ breakdown, priority }) {
  const labels = {
    severity: "Severity",
    injuries: "Injuries",
    hazards: "Hazards",
    agencies: "Agencies",
    confidence: "Confidence",
    agencies_needed: "Agencies",
  };

  const weights = {
    severity: 45,
    injuries: 25,
    hazards: 15,
    agencies: 10,
    confidence: 5,
    agencies_needed: 10,
  };

  if (!breakdown) return null;

  const data = Object.entries(breakdown).map(([key, value]) => ({
    name: labels[key] || key,
    score: value,
    weight: weights[key] || 0,
  }));

  return (
    <div>
      <h4 style={{ margin: "0 0 4px", fontSize: "13px", color: "#374151" }}>
        Priority Breakdown — {priority}/100
      </h4>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} layout="vertical" margin={{ left: 0, right: 12, top: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" domain={[0, 10]} ticks={[0, 2, 4, 6, 8, 10]} fontSize={10} />
          <YAxis type="category" dataKey="name" width={72} fontSize={11} />
          <Tooltip
            formatter={(value, name, props) =>
              [`${value}/10 (weight: ${props.payload.weight}%)`, "Score"]
            }
          />
          <Bar dataKey="score" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.score >= 8 ? "#dc2626" : entry.score >= 5 ? "#ea580c" : "#2563eb"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function Sources({ events }) {
  return (
    <div>
      <h4 style={{ margin: "0 0 8px", fontSize: "13px", color: "#374151" }}>
        Data Sources ({(events || []).length})
      </h4>
      {(events || []).map((event, i) => {
        const sourceLabel = SOURCE_LABELS[event.source_type] || event.source_type;
        const confirmed = event.provenance?.last_confirmed;
        return (
          <div
            key={i}
            style={{
              fontSize: "12px",
              marginBottom: "8px",
              padding: "8px",
              backgroundColor: "#f9fafb",
              borderRadius: "6px",
              border: "1px solid #f3f4f6",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong>{sourceLabel}</strong>
              <span style={{ fontFamily: "monospace", fontSize: "11px", color: "#9ca3af" }}>
                {formatTime(event.timestamp)}
              </span>
            </div>
            <div style={{ color: "#6b7280", marginTop: "4px" }}>
              {event.parsed_fields?.key_details || event.raw_text?.slice(0, 120)}
            </div>

            {event.parsed_fields && (
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "6px" }}>
                {event.parsed_fields.incident_type && (
                  <Tag label="Type" value={event.parsed_fields.incident_type} />
                )}
                {event.parsed_fields.injuries != null && (
                  <Tag label="Injuries" value={event.parsed_fields.injuries} color="#dc2626" />
                )}
                {(event.parsed_fields.hazards || []).map((h, j) => (
                  <Tag key={j} label="Hazard" value={h} color="#ea580c" />
                ))}
                {(event.parsed_fields.agencies_needed || []).map((a, j) => (
                  <Tag key={j} label="Agency" value={a} color="#2563eb" />
                ))}
                {event.parsed_fields.severity_estimate != null && (
                  <Tag label="Sev" value={`${event.parsed_fields.severity_estimate}/10`} />
                )}
              </div>
            )}

            <div style={{ display: "flex", gap: "12px", marginTop: "4px", fontSize: "11px" }}>
              <span>
                Confidence:{" "}
                <strong
                  style={{
                    color:
                      event.confidence >= 0.8
                        ? "#16a34a"
                        : event.confidence >= 0.5
                          ? "#ca8a04"
                          : "#dc2626",
                  }}
                >
                  {Math.round(event.confidence * 100)}%
                </strong>
              </span>
              <span style={{ color: confirmed ? "#16a34a" : "#ca8a04" }}>
                {confirmed ? "Confirmed" : "Unconfirmed"}
              </span>
              {(event.provenance?.supporting_sources || []).length > 0 && (
                <span style={{ color: "#2563eb" }}>
                  +{event.provenance.supporting_sources.length} corroborating
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Tag({ label, value, color }) {
  return (
    <span
      style={{
        fontSize: "10px",
        padding: "1px 6px",
        borderRadius: "3px",
        backgroundColor: color ? `${color}10` : "#f3f4f6",
        color: color || "#374151",
        border: `1px solid ${color || "#e5e7eb"}20`,
      }}
    >
      {label}: <strong>{value}</strong>
    </span>
  );
}

function Limitations({ limitations }) {
  if (!limitations || limitations.length === 0) return null;
  return (
    <div>
      <h4 style={{ margin: "0 0 8px", fontSize: "13px", color: "#374151" }}>Limitations</h4>
      <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "12px", color: "#6b7280" }}>
        {limitations.map((lim, i) => (
          <li key={i} style={{ marginBottom: "4px" }}>{lim}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ExplainPanel({ incident }) {
  const [adjusting, setAdjusting] = useState(false);
  const [newPriority, setNewPriority] = useState("");

  if (!incident) {
    return (
      <div
        style={{
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#9ca3af",
          fontSize: "14px",
        }}
      >
        Select an incident to view details
      </div>
    );
  }

  const tier = getPriorityTier(incident.priority);
  const delta = incident.priority_delta || 0;

  async function handleConfirm() {
    try {
      await fetch(`${API_URL}/incidents/${incident.id}/confirm`, { method: "POST" });
    } catch { /* handled via WebSocket update */ }
  }

  async function handleAdjust() {
    const val = parseInt(newPriority, 10);
    if (isNaN(val) || val < 0 || val > 100) return;
    try {
      await fetch(`${API_URL}/incidents/${incident.id}/adjust`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ priority: val }),
      });
      setAdjusting(false);
      setNewPriority("");
    } catch { /* handled via WebSocket update */ }
  }

  return (
    <div style={{ padding: "16px", overflowY: "auto", height: "100%" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "16px",
          paddingBottom: "12px",
          borderBottom: "2px solid #e5e7eb",
        }}
      >
        <div>
          <h3 style={{ margin: 0, fontSize: "16px", color: "#111" }}>
            Incident #{incident.id} — {incident.incident_type}
          </h3>
          <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "2px" }}>
            {incident.location?.address}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: "6px", justifyContent: "flex-end" }}>
            <span style={{ fontSize: "24px", fontWeight: 700, color: tier.color }}>
              {incident.priority}
              <span style={{ fontSize: "14px", color: "#9ca3af" }}>/100</span>
            </span>
            {delta !== 0 && (
              <span
                style={{
                  fontSize: "13px",
                  fontWeight: 700,
                  color: delta > 0 ? "#dc2626" : "#16a34a",
                }}
              >
                {delta > 0 ? "+" : ""}{delta}
              </span>
            )}
          </div>
          <div style={{ fontSize: "11px", color: "#6b7280" }}>
            Confidence: {Math.round(incident.confidence * 100)}% ({getConfidenceLabel(incident.confidence)})
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <Timeline timeline={incident.timeline} />
          <Limitations limitations={incident.limitations} />
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <PriorityBreakdown breakdown={incident.priority_breakdown} priority={incident.priority} />
          <Sources events={incident.events} />
        </div>
      </div>

      <div
        style={{
          marginTop: "16px",
          padding: "10px 14px",
          backgroundColor: incident.confirmed ? "#f0fdf4" : "#eff6ff",
          borderRadius: "6px",
          border: `1px solid ${incident.confirmed ? "#bbf7d0" : "#bfdbfe"}`,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        {incident.confirmed ? (
          <span style={{ fontSize: "12px", color: "#16a34a", fontWeight: 600 }}>
            Human confirmed — priority {incident.priority}
            {incident.human_priority != null && ` (adjusted from AI recommendation)`}
          </span>
        ) : (
          <span style={{ fontSize: "12px", color: "#1e40af" }}>
            AI recommends priority <strong>{incident.priority}</strong>. Human confirmation required.
          </span>
        )}
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          {adjusting ? (
            <>
              <input
                type="number"
                min="0"
                max="100"
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value)}
                placeholder="0-100"
                style={{
                  width: "60px",
                  padding: "4px 8px",
                  fontSize: "12px",
                  border: "1px solid #d1d5db",
                  borderRadius: "4px",
                }}
              />
              <button onClick={handleAdjust} style={confirmBtnStyle}>
                Set
              </button>
              <button onClick={() => setAdjusting(false)} style={adjustBtnStyle}>
                Cancel
              </button>
            </>
          ) : (
            <>
              {!incident.confirmed && (
                <button onClick={handleConfirm} style={confirmBtnStyle}>
                  Confirm
                </button>
              )}
              <button onClick={() => setAdjusting(true)} style={adjustBtnStyle}>
                Adjust
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

const confirmBtnStyle = {
  padding: "4px 12px",
  fontSize: "12px",
  backgroundColor: "#2563eb",
  color: "#fff",
  border: "none",
  borderRadius: "4px",
  cursor: "pointer",
};

const adjustBtnStyle = {
  padding: "4px 12px",
  fontSize: "12px",
  backgroundColor: "#fff",
  color: "#374151",
  border: "1px solid #d1d5db",
  borderRadius: "4px",
  cursor: "pointer",
};
