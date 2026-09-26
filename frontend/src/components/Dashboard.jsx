import { useEffect, useRef, useState } from "react";
import IncidentCard from "./IncidentCard";

export default function Dashboard({ incidents, selectedId, onSelect }) {
  const sorted = [...incidents].sort((a, b) => b.priority - a.priority);
  const [recentlyUpdated, setRecentlyUpdated] = useState(new Set());
  const prevRef = useRef({});
  const containerRef = useRef(null);

  useEffect(() => {
    const newUpdates = new Set();
    for (const inc of incidents) {
      const prev = prevRef.current[inc.id];
      if (prev && (prev.priority !== inc.priority || prev.events?.length !== inc.events?.length)) {
        newUpdates.add(inc.id);
      }
      prevRef.current[inc.id] = { priority: inc.priority, events: inc.events };
    }
    if (newUpdates.size > 0) {
      setRecentlyUpdated(newUpdates);
      const timer = setTimeout(() => setRecentlyUpdated(new Set()), 3000);
      return () => clearTimeout(timer);
    }
  }, [incidents]);

  useEffect(() => {
    if (recentlyUpdated.size > 0 && containerRef.current) {
      const firstId = [...recentlyUpdated][0];
      const el = containerRef.current.querySelector(`[data-incident-id="${firstId}"]`);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [recentlyUpdated]);

  return (
    <div ref={containerRef} style={{ height: "100%", overflowY: "auto", padding: "12px" }}>
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
        <div key={incident.id} data-incident-id={incident.id}>
          <IncidentCard
            incident={incident}
            isSelected={incident.id === selectedId}
            onSelect={onSelect}
            isUpdated={recentlyUpdated.has(incident.id)}
          />
        </div>
      ))}
      {incidents.length === 0 && (
        <div style={{ textAlign: "center", color: "#9ca3af", fontSize: "13px", marginTop: "40px" }}>
          No incidents. Submit a report or run the demo.
        </div>
      )}
    </div>
  );
}
