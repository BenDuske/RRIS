import { ROLE_FILTERS } from "../utils/priorityColors";

export default function RoleFilter({ activeRole, onRoleChange }) {
  return (
    <div style={{ display: "flex", gap: "4px" }}>
      {Object.entries(ROLE_FILTERS).map(([key, filter]) => (
        <button
          key={key}
          onClick={() => onRoleChange(key)}
          style={{
            padding: "4px 10px",
            fontSize: "12px",
            fontWeight: activeRole === key ? 600 : 400,
            backgroundColor: activeRole === key ? "#1e40af" : "#f3f4f6",
            color: activeRole === key ? "#fff" : "#374151",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            transition: "all 0.15s ease",
          }}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}
