import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import {
  getPriorityTier, getConfidenceLabel, formatTime, SOURCE_LABELS,
} from "../utils/priorityColors";

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
        {timeline.map((entry, i) => {
          const style = typeStyles[entry.type] || typeStyles.evidence;
          return (
            <div key={i} style={{ marginBottom: "8px", fontSize: "12px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ color: style.color, fontSize: "10px" }}>{style.icon}</span>
                <span style={{ color: "#9ca3af", fontFamily: "monospace", fontSize: "11px" }}>
                  {formatTime(entry.created_at)}
                </span>
                <span
                  style={{
                    fontSize: "9px",
                    textTransform: "uppercase",
                    color: style.color,
                    fontWeight: 600,
                  }}
                >
                  {entry.type}
                </span>
              </div>
              <div style={{ color: "#374151", marginTop: "2px", marginLeft: "16px" }}>
                {entry.summary}
              </div>
            </div>
          );
        })}
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
    life_threat: "Life Threat",
    time_sensitivity: "Time Sens.",
    resource_load: "Resources",
    vulnerable_pop: "Vulnerable",
    agencies_needed: "Agencies",
  };

  const weights = {
    severity: 45,
    injuries: 25,
    hazards: 15,
    agencies: 10,
    confidence: 5,
    life_threat: 30,
    time_sensitivity: 15,
    resource_load: 10,
    vulnerable_pop: 10,
    agencies_needed: 10,
  };

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
        Data Sources ({events.length})
      </h4>
      {events.map((event, i) => {
        const sourceLabel = SOURCE_LABELS[event.source_type] || event.source_type;
        const confirmed = event.provenance.last_confirmed;
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
              {event.parsed_fields.key_details || event.raw_text.slice(0, 120)}
            </div>
            <div
              style={{
                display: "flex",
                gap: "12px",
                marginTop: "4px",
                fontSize: "11px",
              }}
            >
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
                {confirmed ? "✓ Confirmed" : "○ Unconfirmed"}
              </span>
              {event.provenance.supporting_sources.length > 0 && (
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

function Limitations({ limitations }) {
  if (!limitations || limitations.length === 0) return null;
  return (
    <div>
      <h4 style={{ margin: "0 0 8px", fontSize: "13px", color: "#374151" }}>
        Limitations
      </h4>
      <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "12px", color: "#6b7280" }}>
        {limitations.map((lim, i) => (
          <li key={i} style={{ marginBottom: "4px" }}>{lim}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ExplainPanel({ incident }) {
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
            {incident.location.address}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "24px", fontWeight: 700, color: tier.color }}>
            {incident.priority}
            <span style={{ fontSize: "14px", color: "#9ca3af" }}>/100</span>
          </div>
          <div style={{ fontSize: "11px", color: "#6b7280" }}>
            Confidence: {Math.round(incident.confidence * 100)}% ({getConfidenceLabel(incident.confidence)})
          </div>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
        }}
      >
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
          backgroundColor: "#eff6ff",
          borderRadius: "6px",
          border: "1px solid #bfdbfe",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ fontSize: "12px", color: "#1e40af" }}>
          AI recommends priority <strong>{incident.priority}</strong>. Human confirmation required.
        </span>
        <div style={{ display: "flex", gap: "8px" }}>
          <button
            style={{
              padding: "4px 12px",
              fontSize: "12px",
              backgroundColor: "#2563eb",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Confirm
          </button>
          <button
            style={{
              padding: "4px 12px",
              fontSize: "12px",
              backgroundColor: "#fff",
              color: "#374151",
              border: "1px solid #d1d5db",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Adjust
          </button>
        </div>
      </div>
    </div>
  );
}
