import { useState, useEffect, useRef, useCallback } from "react";
import Dashboard from "./components/Dashboard";
import MapView from "./components/MapView";
import ExplainPanel from "./components/ExplainPanel";
import RoleFilter from "./components/RoleFilter";
import ReportSubmit from "./components/ReportSubmit";

const API_URL = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws";

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [activeRole, setActiveRole] = useState("all");
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  const fetchIncidents = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/incidents`);
      if (res.ok) {
        setIncidents(await res.json());
      }
    } catch {
      /* backend not running yet */
    }
  }, []);

  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  useEffect(() => {
    let ws;
    let reconnectTimer;

    function connect() {
      ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        reconnectTimer = setTimeout(connect, 3000);
      };
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === "incident_update") {
          setIncidents((prev) => {
            const idx = prev.findIndex((i) => i.id === msg.incident.id);
            if (idx >= 0) {
              const next = [...prev];
              next[idx] = msg.incident;
              return next;
            }
            return [...prev, msg.incident];
          });
        }
      };
    }

    connect();
    return () => {
      clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

  const selected = incidents.find((i) => i.id === selectedId);
  const activeSources = new Set(
    incidents.flatMap((i) => (i.events || []).map((e) => e.source_type))
  );

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        backgroundColor: "#f8fafc",
      }}
    >
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
          <h1
            style={{
              margin: 0,
              fontSize: "16px",
              fontWeight: 700,
              letterSpacing: "1px",
            }}
          >
            RRIS
          </h1>
          <span style={{ fontSize: "12px", color: "#94a3b8" }}>
            Rapid Response Information System
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <RoleFilter activeRole={activeRole} onRoleChange={setActiveRole} />
          <div style={{ fontSize: "11px", color: "#94a3b8" }}>
            {incidents.length} incident{incidents.length !== 1 ? "s" : ""} ·{" "}
            {activeSources.size} source{activeSources.size !== 1 ? "s" : ""}
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "4px",
              fontSize: "11px",
              color: connected ? "#22c55e" : "#ef4444",
            }}
          >
            <span
              style={{
                display: "inline-block",
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: connected ? "#22c55e" : "#ef4444",
              }}
            />
            {connected ? "Live" : "Disconnected"}
          </div>
        </div>
      </header>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        <div
          style={{
            width: "360px",
            flexShrink: 0,
            borderRight: "1px solid #e5e7eb",
            backgroundColor: "#fff",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <ReportSubmit onSubmitted={fetchIncidents} />
          <div style={{ flex: 1, overflow: "hidden" }}>
            <Dashboard
              incidents={incidents}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          </div>
        </div>

        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div style={{ flex: 1, minHeight: "300px" }}>
            <MapView
              incidents={incidents}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          </div>

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
