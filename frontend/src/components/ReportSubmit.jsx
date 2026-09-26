import { useState, useRef } from "react";
import demoScenario from "../data/demoScenario";

const EXAMPLE_REPORT = JSON.stringify(
  {
    source_id: "cad_00142",
    source_type: "cad",
    raw_text:
      "Vehicle collision reported I-27 NB near Exit 6. Multiple vehicles. 2 injuries. Northbound lanes blocked.",
    lat: 33.5351,
    lng: -101.8452,
    address: "I-27 NB near Exit 6, Lubbock, TX",
    confidence: 0.85,
  },
  null,
  2
);

const API_URL = "";

export default function ReportSubmit({ onSubmitted }) {
  const [text, setText] = useState(EXAMPLE_REPORT);
  const [status, setStatus] = useState(null);
  const [collapsed, setCollapsed] = useState(false);
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoStep, setDemoStep] = useState(-1);
  const demoAbort = useRef(false);

  async function submitReport(report) {
    const res = await fetch(`${API_URL}/ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(report),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function handleSubmit() {
    setStatus(null);
    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch {
      setStatus({ ok: false, msg: "Invalid JSON" });
      return;
    }
    try {
      const data = await submitReport(parsed);
      setStatus({
        ok: true,
        msg: `Incident #${data.incident_id} — priority ${data.incident_priority}, ${data.event_count} report(s)`,
      });
      if (onSubmitted) onSubmitted(data);
    } catch (e) {
      setStatus({ ok: false, msg: `Connection failed: ${e.message}` });
    }
  }

  async function clearAll() {
    try {
      await fetch(`${API_URL}/reset`, { method: "POST" });
      setStatus({ ok: true, msg: "All incidents cleared" });
      if (onSubmitted) onSubmitted();
    } catch {
      setStatus({ ok: false, msg: "Failed to clear" });
    }
  }

  async function runDemo() {
    await clearAll();
    setDemoRunning(true);
    demoAbort.current = false;
    setDemoStep(0);

    for (let i = 0; i < demoScenario.length; i++) {
      if (demoAbort.current) break;
      const step = demoScenario[i];

      if (step.delay > 0) {
        await new Promise((r) => setTimeout(r, step.delay));
      }
      if (demoAbort.current) break;

      setDemoStep(i);
      try {
        await submitReport(step.report);
      } catch {
        /* continue even if one fails */
      }
      if (onSubmitted) onSubmitted();
    }

    setDemoRunning(false);
    setDemoStep(-1);
  }

  function stopDemo() {
    demoAbort.current = true;
    setDemoRunning(false);
    setDemoStep(-1);
  }

  if (collapsed) {
    return (
      <div
        style={{
          padding: "8px 12px",
          borderBottom: "1px solid #e5e7eb",
          backgroundColor: "#f8fafc",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span
          style={{ cursor: "pointer", fontSize: "12px", color: "#2563eb", fontWeight: 600 }}
          onClick={() => setCollapsed(false)}
        >
          + Submit Report
        </span>
        {!demoRunning && (
          <button onClick={runDemo} style={demoBtnStyle}>
            Run Demo
          </button>
        )}
      </div>
    );
  }

  return (
    <div style={{ padding: "12px", borderBottom: "1px solid #e5e7eb", backgroundColor: "#f8fafc" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
        <span style={{ fontSize: "11px", fontWeight: 600, textTransform: "uppercase", color: "#374151", letterSpacing: "0.5px" }}>
          Submit Report (JSON)
        </span>
        <button
          onClick={() => setCollapsed(true)}
          style={{ background: "none", border: "none", fontSize: "16px", cursor: "pointer", color: "#9ca3af", lineHeight: 1 }}
        >
          ×
        </button>
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        spellCheck={false}
        style={{
          width: "100%",
          height: "120px",
          fontFamily: "monospace",
          fontSize: "11px",
          padding: "8px",
          border: "1px solid #d1d5db",
          borderRadius: "6px",
          resize: "vertical",
          backgroundColor: "#fff",
          boxSizing: "border-box",
        }}
      />

      <div style={{ display: "flex", gap: "8px", alignItems: "center", marginTop: "8px", flexWrap: "wrap" }}>
        <button onClick={handleSubmit} style={submitBtnStyle}>
          Submit
        </button>
        <button onClick={() => setText(EXAMPLE_REPORT)} style={resetBtnStyle}>
          Reset
        </button>
        <button onClick={clearAll} style={{ ...resetBtnStyle, color: "#dc2626", borderColor: "#fca5a5" }}>
          Clear All
        </button>
        <div style={{ flex: 1 }} />
        {demoRunning ? (
          <button onClick={stopDemo} style={{ ...demoBtnStyle, backgroundColor: "#dc2626" }}>
            Stop Demo
          </button>
        ) : (
          <button onClick={runDemo} style={demoBtnStyle}>
            Run Demo
          </button>
        )}
      </div>

      {status && (
        <div style={{ fontSize: "11px", color: status.ok ? "#16a34a" : "#dc2626", marginTop: "6px" }}>
          {status.msg}
        </div>
      )}

      {demoRunning && demoStep >= 0 && (
        <div style={{ marginTop: "8px" }}>
          <div style={{ fontSize: "11px", color: "#374151", fontWeight: 600, marginBottom: "4px" }}>
            Demo: {demoStep + 1}/{demoScenario.length}
          </div>
          <div style={{ display: "flex", gap: "2px" }}>
            {demoScenario.map((step, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  height: "4px",
                  borderRadius: "2px",
                  backgroundColor: i <= demoStep ? "#2563eb" : "#e5e7eb",
                  transition: "background-color 0.3s",
                }}
              />
            ))}
          </div>
          <div style={{ fontSize: "10px", color: "#6b7280", marginTop: "4px" }}>
            {demoScenario[demoStep].label}
          </div>
        </div>
      )}
    </div>
  );
}

const submitBtnStyle = {
  padding: "6px 16px",
  fontSize: "12px",
  fontWeight: 600,
  backgroundColor: "#2563eb",
  color: "#fff",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer",
};

const resetBtnStyle = {
  padding: "6px 12px",
  fontSize: "12px",
  backgroundColor: "#fff",
  color: "#6b7280",
  border: "1px solid #d1d5db",
  borderRadius: "6px",
  cursor: "pointer",
};

const demoBtnStyle = {
  padding: "6px 14px",
  fontSize: "12px",
  fontWeight: 600,
  backgroundColor: "#16a34a",
  color: "#fff",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer",
};
