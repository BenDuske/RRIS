import { useState } from "react";
import Dashboard from "./components/Dashboard";
import MapView from "./components/MapView";
import ExplainPanel from "./components/ExplainPanel";
import RoleFilter from "./components/RoleFilter";
import mockIncidents from "./data/mockIncidents";

export default function App() {
  const [selectedId, setSelectedId] = useState(null);
  const [activeRole, setActiveRole] = useState("all");

  const selected = mockIncidents.find((i) => i.id === selectedId);
  const activeSources = new Set(mockIncidents.flatMap((i) => i.events.map((e) => e.source_type)));

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", fontFamily: "'Inter', system-ui, -apple-system, sans-serif", backgroundColor: "#f8fafc" }}>
      {/* Header */}
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "8px 16px",
          backgroundColor: "#0f172a",
          color: "#fff",
          flexShrink: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <h1 style={{ margin: 0, fontSize: "16px", fontWeight: 700, letterSpacing: "1px" }}>
            RRIS
          </h1>
          <span style={{ fontSize: "12px", color: "#94a3b8" }}>
            Rapid Response Information System
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <RoleFilter activeRole={activeRole} onRoleChange={setActiveRole} />
          <div style={{ fontSize: "11px", color: "#94a3b8" }}>
            Sources: {activeSources.size} active
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "4px",
              fontSize: "11px",
              color: "#22c55e",
            }}
          >
            <span style={{ display: "inline-block", width: "6px", height: "6px", borderRadius: "50%", backgroundColor: "#22c55e" }} />
            Live
          </div>
        </div>
      </header>

      {/* Main content: sidebar + map */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left sidebar — incident list */}
        <div
          style={{
            width: "320px",
            flexShrink: 0,
            borderRight: "1px solid #e5e7eb",
            backgroundColor: "#fff",
            overflow: "hidden",
          }}
        >
          <Dashboard
            incidents={mockIncidents}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>

        {/* Right side — map + detail panel */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          {/* Map */}
          <div style={{ flex: 1, minHeight: "300px" }}>
            <MapView
              incidents={mockIncidents}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          </div>

          {/* Explainability panel */}
          {selected && (
            <div
              style={{
                height: "340px",
                flexShrink: 0,
                borderTop: "2px solid #e5e7eb",
                backgroundColor: "#fff",
                overflow: "hidden",
              }}
            >
              <ExplainPanel incident={selected} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
