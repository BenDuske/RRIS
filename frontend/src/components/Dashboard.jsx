import IncidentCard from "./IncidentCard";

export default function Dashboard({ incidents, selectedId, onSelect }) {
  const sorted = [...incidents].sort((a, b) => b.priority - a.priority);

  return (
    <div
      style={{
        height: "100%",
        overflowY: "auto",
        padding: "12px",
      }}
    >
      <div
        style={{
          fontSize: "11px",
          color: "#9ca3af",
          marginBottom: "8px",
          textTransform: "uppercase",
          letterSpacing: "0.5px",
        }}
      >
        {incidents.length} Active Incident{incidents.length !== 1 ? "s" : ""}
      </div>
      {sorted.map((incident) => (
        <IncidentCard
          key={incident.id}
          incident={incident}
          isSelected={incident.id === selectedId}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
