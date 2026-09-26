import { MapContainer, TileLayer, CircleMarker, Circle, Popup, useMap } from "react-leaflet";
import { getPriorityTier, INCIDENT_ICONS } from "../utils/priorityColors";
import { useEffect } from "react";
import "leaflet/dist/leaflet.css";

function FlyToSelected({ incident }) {
  const map = useMap();
  useEffect(() => {
    if (incident) {
      map.flyTo([incident.location.lat, incident.location.lng], 14, { duration: 0.8 });
    }
  }, [incident, map]);
  return null;
}

export default function MapView({ incidents, selectedId, onSelect }) {
  const selected = incidents.find((i) => i.id === selectedId);

  return (
    <MapContainer
      center={[33.5779, -101.8552]}
      zoom={12}
      style={{ height: "100%", width: "100%", borderRadius: "8px" }}
    >
      <TileLayer
        attribution='Tiles &copy; Esri'
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
      />
      <FlyToSelected incident={selected} />

      {incidents.map((incident) => {
        const tier = getPriorityTier(incident.priority);
        const isSelected = incident.id === selectedId;
        const icon = INCIDENT_ICONS[incident.incident_type] || "📋";

        return (
          <CircleMarker
            key={incident.id}
            center={[incident.location.lat, incident.location.lng]}
            radius={isSelected ? 14 : 10}
            pathOptions={{
              color: tier.color,
              fillColor: tier.color,
              fillOpacity: isSelected ? 0.8 : 0.5,
              weight: isSelected ? 3 : 2,
            }}
            eventHandlers={{ click: () => onSelect(incident.id) }}
          >
            <Popup>
              <div style={{ minWidth: "180px" }}>
                <strong>
                  {icon} {incident.incident_type}
                </strong>
                <br />
                <span style={{ fontSize: "12px", color: "#6b7280" }}>
                  {incident.location.address}
                </span>
                <hr style={{ margin: "6px 0", border: "none", borderTop: "1px solid #e5e7eb" }} />
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                  <span>
                    Priority:{" "}
                    <strong style={{ color: tier.color }}>{incident.priority}/100</strong>
                  </span>
                  <span>Conf: {Math.round(incident.confidence * 100)}%</span>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}

      {selected && selected.location.radius > 100 && (
        <Circle
          center={[selected.location.lat, selected.location.lng]}
          radius={selected.location.radius}
          pathOptions={{
            color: getPriorityTier(selected.priority).color,
            fillOpacity: 0.08,
            weight: 1,
            dashArray: "6 4",
          }}
        />
      )}
    </MapContainer>
  );
}
