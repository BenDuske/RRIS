import { useState } from "react";

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

const API_URL = "http://localhost:8000";

export default function ReportSubmit({ onSubmitted }) {
  const [text, setText] = useState(EXAMPLE_REPORT);
  const [status, setStatus] = useState(null);
  const [collapsed, setCollapsed] = useState(false);

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
      const res = await fetch(`${API_URL}/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });
      if (!res.ok) {
        const err = await res.text();
        setStatus({ ok: false, msg: `Server error: ${err}` });
        return;
      }
      const data = await res.json();
      setStatus({
        ok: true,
        msg: `Incident #${data.incident_id} — priority ${data.incident_priority}, ${data.event_count} report(s)`,
      });
      if (onSubmitted) onSubmitted(data);
    } catch (e) {
      setStatus({ ok: false, msg: `Connection failed: ${e.message}` });
    }
  }

  if (collapsed) {
    return (
      <div
        style={{
          padding: "8px 12px",
          borderBottom: "1px solid #e5e7eb",
          backgroundColor: "#f8fafc",
          cursor: "pointer",
          fontSize: "12px",
          color: "#2563eb",
          fontWeight: 600,
        }}
        onClick={() => setCollapsed(false)}
      >
        + Submit Report
      </div>
    );
  }

  return (
    <div
      style={{
        padding: "12px",
        borderBottom: "1px solid #e5e7eb",
        backgroundColor: "#f8fafc",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "8px",
        }}
      >
        <span
          style={{
            fontSize: "11px",
            fontWeight: 600,
            textTransform: "uppercase",
            color: "#374151",
            letterSpacing: "0.5px",
          }}
        >
          Submit Report (JSON)
        </span>
        <button
          onClick={() => setCollapsed(true)}
          style={{
            background: "none",
            border: "none",
            fontSize: "16px",
            cursor: "pointer",
            color: "#9ca3af",
            lineHeight: 1,
          }}
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
          height: "140px",
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

      <div
        style={{
          display: "flex",
          gap: "8px",
          alignItems: "center",
          marginTop: "8px",
        }}
      >
        <button
          onClick={handleSubmit}
          style={{
            padding: "6px 16px",
            fontSize: "12px",
            fontWeight: 600,
            backgroundColor: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          Submit
        </button>
        <button
          onClick={() => setText(EXAMPLE_REPORT)}
          style={{
            padding: "6px 12px",
            fontSize: "12px",
            backgroundColor: "#fff",
            color: "#6b7280",
            border: "1px solid #d1d5db",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          Reset
        </button>
        {status && (
          <span
            style={{
              fontSize: "11px",
              color: status.ok ? "#16a34a" : "#dc2626",
              flex: 1,
            }}
          >
            {status.msg}
          </span>
        )}
      </div>
    </div>
  );
}
