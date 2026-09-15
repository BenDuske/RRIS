import { getPriorityTier, getConfidenceLabel, formatTimeShort, INCIDENT_ICONS } from "../utils/priorityColors";

export default function IncidentCard({ incident, isSelected, onSelect }) {
  const tier = getPriorityTier(incident.priority);
  const icon = INCIDENT_ICONS[incident.incident_type] || "📋";
  const confLabel = getConfidenceLabel(incident.confidence);

  return (
    <div
      onClick={() => onSelect(incident.id)}
      style={{
        padding: "12px 14px",
        marginBottom: "8px",
        borderRadius: "8px",
        border: isSelected ? `2px solid ${tier.color}` : "1px solid #e5e7eb",
        backgroundColor: isSelected ? tier.bg : "#fff",
        cursor: "pointer",
        transition: "all 0.15s ease",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "18px" }}>{icon}</span>
          <div>
            <div style={{ fontWeight: 600, fontSize: "14px", color: "#111" }}>
              {incident.incident_type}
            </div>
            <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "2px" }}>
              {incident.location.address}
            </div>
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div
            style={{
              fontWeight: 700,
              fontSize: "18px",
              color: tier.color,
              lineHeight: 1,
            }}
          >
            {incident.priority}
          </div>
          <div style={{ fontSize: "10px", color: "#9ca3af", textTransform: "uppercase" }}>
            {tier.label}
          </div>
        </div>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: "8px",
          fontSize: "11px",
          color: "#6b7280",
        }}
      >
        <div style={{ display: "flex", gap: "12px" }}>
          <span>
            Confidence:{" "}
            <strong style={{ color: incident.confidence >= 0.8 ? "#16a34a" : incident.confidence >= 0.5 ? "#ca8a04" : "#dc2626" }}>
              {Math.round(incident.confidence * 100)}%
            </strong>{" "}
            ({confLabel})
          </span>
          <span>{incident.events.length} source{incident.events.length !== 1 ? "s" : ""}</span>
        </div>
        <span>{formatTimeShort(incident.updated_at)}</span>
      </div>

      {incident.status === "monitoring" && (
        <div
          style={{
            marginTop: "6px",
            fontSize: "10px",
            color: "#2563eb",
            fontWeight: 500,
            textTransform: "uppercase",
            letterSpacing: "0.5px",
          }}
        >
          Monitoring
        </div>
      )}
    </div>
  );
}
