import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

const MapChart = ({ data }) => {
  const center = [14.7167, -17.4677] // Sénégal
  
  return (
    <div style={{ height: '400px', width: '100%' }}>
      <MapContainer 
        center={center} 
        zoom={7} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        {data.map((region, idx) => (
          <CircleMarker
            key={idx}
            center={[region.latitude, region.longitude]}
            radius={Math.sqrt(region.count) * 2}
            fillColor="#667eea"
            fillOpacity={0.6}
            stroke={false}
          >
            <Popup>
              <strong>{region.name}</strong><br />
              {region.count} questions
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}

export default MapChart
