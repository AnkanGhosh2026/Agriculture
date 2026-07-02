import { Routes, Route, Link, useLocation } from 'react-router-dom';
import DiseaseDetection from './pages/DiseaseDetection';
import WeatherInsights from './pages/WeatherInsights';
import YieldPrediction from './pages/YieldPrediction';

function App() {
  const location = useLocation();

  return (
    <>
      <header className="glass-header animate-fade-in">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ 
              width: '40px', height: '40px', borderRadius: '10px', 
              background: 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontWeight: 'bold', fontSize: '1.2rem', color: 'white'
            }}>
              Ag
            </div>
            <h2 style={{ margin: 0, fontSize: '1.5rem', background: 'linear-gradient(90deg, #fff, #ddd)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              CropSense
            </h2>
          </div>
          
          <nav className="nav-links">
            <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>Disease Detection</Link>
            <Link to="/weather" className={`nav-link ${location.pathname === '/weather' ? 'active' : ''}`}>Weather Insights</Link>
            <Link to="/yield" className={`nav-link ${location.pathname === '/yield' ? 'active' : ''}`}>Yield Prediction</Link>
          </nav>
        </div>
      </header>

      <main className="container" style={{ flex: 1, padding: '40px 20px' }}>
        <Routes>
          <Route path="/" element={<DiseaseDetection />} />
          <Route path="/weather" element={<WeatherInsights />} />
          <Route path="/yield" element={<YieldPrediction />} />
        </Routes>
      </main>

      <footer style={{ borderTop: '1px solid var(--glass-border)', padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <p>© 2026 CropSense. AI Agriculture Platform.</p>
      </footer>
    </>
  );
}

export default App;
