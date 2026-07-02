import { useState } from 'react';
import { MapPin, CloudRain, Sun, Thermometer, Droplets, Calendar, Wind } from 'lucide-react';

export default function WeatherInsights() {
  const [locationSearch, setLocationSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchWeather = async () => {
    if (!locationSearch) {
      setError('Please provide a location to search.');
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);

    try {
      // 1. Geocode the location using OpenStreetMap Nominatim
      const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(locationSearch)}&format=json&limit=1`);
      if (!geoRes.ok) throw new Error('Failed to search for location.');

      const geoData = await geoRes.json();
      if (!geoData || geoData.length === 0) {
        throw new Error('Location not found. Please try a different search term.');
      }

      const lat = geoData[0].lat;
      const lon = geoData[0].lon;
      const displayName = geoData[0].display_name.split(',')[0];

      // 2. Fetch weather insights from backend
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/weather/insights?latitude=${lat}&longitude=${lon}`
      );
      if (!res.ok) throw new Error('Failed to fetch weather insights from backend.');

      const json = await res.json();
      // Use the friendly city name instead of lat/lon string
      json.location = displayName;
      setData(json);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1>Hyper-Local Weather Insights</h1>
        <p>Get AI-driven agricultural insights based on current weather conditions for your farm's location.</p>
      </div>

      <div className="glass-panel card">
        <div style={{ marginBottom: '20px' }}>
          <label>Location Search</label>
          <input
            type="text"
            placeholder="e.g. London, Mumbai, New York..."
            value={locationSearch}
            onChange={(e) => setLocationSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchWeather()}
          />
        </div>

        <button
          className="btn"
          onClick={fetchWeather}
          disabled={loading || !locationSearch}
          style={{ width: '100%' }}
        >
          {loading ? <div className="spinner" /> : <><MapPin size={20} /> Get Farm Insights</>}
        </button>

        {error && (
          <div style={{ marginTop: '20px', padding: '16px', background: 'rgba(207, 102, 121, 0.1)', color: 'var(--error)', borderRadius: '8px' }}>
            {error}
          </div>
        )}

        {data && (
          <div className="animate-fade-in" style={{ marginTop: '30px', borderTop: '1px solid var(--glass-border)', paddingTop: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
                <MapPin color="var(--primary-color)" /> {data.location}
              </h3>
              <div style={{ background: 'rgba(255,255,255,0.1)', padding: '6px 12px', borderRadius: '20px', fontSize: '0.9rem' }}>
                {data.current_condition}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginBottom: '30px' }}>
              <div className="glass-panel" style={{ padding: '20px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <Thermometer size={32} color="var(--accent)" style={{ marginBottom: '12px' }} />
                <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{data.current_temp_c}°C</div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Current Temp</div>
              </div>
              <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <h4 style={{ color: 'var(--secondary-color)', marginBottom: '12px', display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <Sun size={18} /> Farming Advisory
                </h4>
                <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.6', fontSize: '0.95rem' }}>
                  {data.farming_advisory.map((adv, i) => (
                    <li key={i} style={{ marginBottom: '8px' }}>{adv}</li>
                  ))}
                </ul>
              </div>
            </div>

            {data.forecast && data.forecast.length > 0 && (
              <div>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <Calendar size={18} /> 3-Day Forecast
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                  {data.forecast.map((day, idx) => (
                    <div key={idx} className="glass-panel" style={{ padding: '16px', textAlign: 'center', fontSize: '0.9rem' }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '8px', color: 'var(--primary-color)' }}>{day.date}</div>
                      <div style={{ marginBottom: '4px' }}>{day.condition}</div>
                      <div style={{ fontWeight: 'bold' }}>
                        {day.temp_max_c}° <span style={{ color: 'var(--text-muted)', fontWeight: 'normal' }}>{day.temp_min_c}°</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'center', gap: '4px', alignItems: 'center', marginTop: '8px', color: 'var(--text-muted)' }}>
                        <Droplets size={14} color="#64b5f6" /> {day.precipitation_mm}mm  |  <Wind size={14} color="#aed581" /> {day.humidity_pct}% Hum
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
