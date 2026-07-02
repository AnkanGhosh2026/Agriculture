// import { useState } from 'react';
// import { Calculator, TrendingUp, BarChart3 } from 'lucide-react';

// export default function YieldPrediction() {
//   const [formData, setFormData] = useState({
//     crop_type: 'wheat',
//     area_hectares: 10,
//     soil_ph: 6.5,
//     rainfall_mm: 500,
//     fertilizer_kg: 200
//   });

//   const [loading, setLoading] = useState(false);
//   const [result, setResult] = useState(null);
//   const [error, setError] = useState(null);

//   const handleChange = (e) => {
//     const { name, value } = e.target;
//     setFormData(prev => ({
//       ...prev,
//       [name]: name === 'crop_type' ? value : Number(value)
//     }));
//   };

//   const predictYield = async () => {
//     setLoading(true);
//     setError(null);

//     try {
//       const res = await fetch('http://127.0.0.1:8000/api/v1/yield-prediction/predict', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(formData),
//       });

//       if (!res.ok) throw new Error('Yield prediction failed.');

//       const json = await res.json();
//       setResult(json);
//     } catch (err) {
//       setError(err.message);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
//       <div style={{ textAlign: 'center', marginBottom: '40px' }}>
//         <h1>Crop Yield Predictor</h1>
//         <p>Estimate your harvest yield based on soil, weather, and farm size using our ML regression models.</p>
//       </div>

//       <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
//         <div className="glass-panel card">
//           <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
//             <Calculator color="var(--primary-color)" /> Farm Parameters
//           </h3>

//           <div style={{ marginBottom: '16px' }}>
//             <label>Crop Type</label>
//             <select name="crop_type" value={formData.crop_type} onChange={handleChange}>
//               <option value="wheat">Wheat</option>
//               <option value="corn">Corn</option>
//               <option value="rice">Rice</option>
//               <option value="soybean">Soybean</option>
//             </select>
//           </div>

//           <div style={{ marginBottom: '16px' }}>
//             <label>Area (Hectares)</label>
//             <input type="number" name="area_hectares" value={formData.area_hectares} onChange={handleChange} step="0.1" />
//           </div>

//           <div style={{ marginBottom: '16px' }}>
//             <label>Soil pH</label>
//             <input type="number" name="soil_ph" value={formData.soil_ph} onChange={handleChange} step="0.1" min="0" max="14" />
//           </div>

//           <div style={{ marginBottom: '16px' }}>
//             <label>Expected Rainfall (mm)</label>
//             <input type="number" name="rainfall_mm" value={formData.rainfall_mm} onChange={handleChange} />
//           </div>

//           <div style={{ marginBottom: '24px' }}>
//             <label>Fertilizer Application (kg)</label>
//             <input type="number" name="fertilizer_kg" value={formData.fertilizer_kg} onChange={handleChange} />
//           </div>

//           <button 
//             className="btn" 
//             onClick={predictYield}
//             disabled={loading}
//             style={{ width: '100%' }}
//           >
//             {loading ? <div className="spinner" /> : <><TrendingUp size={20} /> Predict Yield</>}
//           </button>

//           {error && <div style={{ marginTop: '16px', color: 'var(--error)' }}>{error}</div>}
//         </div>

//         <div>
//           {result ? (
//             <div className="glass-panel card animate-fade-in" style={{ background: 'linear-gradient(180deg, rgba(30,30,30,0.8), rgba(46,125,50,0.1))' }}>
//               <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
//                 <BarChart3 color="var(--primary-color)" /> Prediction Results
//               </h3>

//               <div style={{ textAlign: 'center', margin: '40px 0' }}>
//                 <div style={{ fontSize: '3rem', fontWeight: 'bold', background: 'linear-gradient(90deg, #81c784, #aed581)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
//                   {result.predicted_yield_tons.toFixed(1)}
//                 </div>
//                 <div style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>Total Tons</div>
//               </div>

//               <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '20px' }}>
//                 <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
//                   <span style={{ color: 'var(--text-muted)' }}>Confidence Interval</span>
//                   <strong>±{result.confidence_interval_tons.toFixed(1)} tons</strong>
//                 </div>
//                 <div style={{ display: 'flex', justifyContent: 'space-between' }}>
//                   <span style={{ color: 'var(--text-muted)' }}>Yield per Hectare</span>
//                   <strong>{(result.predicted_yield_tons / formData.area_hectares).toFixed(2)} t/ha</strong>
//                 </div>
//               </div>
//             </div>
//           ) : (
//             <div className="glass-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', padding: '40px', textAlign: 'center' }}>
//               <BarChart3 size={48} style={{ opacity: 0.5, marginBottom: '16px' }} />
//               <p>Enter your farm parameters and click predict to see estimated harvest yields.</p>
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }


import { useState } from 'react';
import { Calculator, TrendingUp, BarChart3 } from 'lucide-react';

export default function YieldPrediction() {
  const [formData, setFormData] = useState({
    crop_type: 'wheat',
    area_hectares: 10,
    soil_ph: 6.5,
    rainfall_mm: 500,
    fertilizer_kg: 200
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'crop_type' ? value : Number(value)
    }));
  };

  const predictYield = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/yield-prediction/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => null);
        throw new Error(errBody?.detail ? JSON.stringify(errBody.detail) : 'Yield prediction failed.');
      }

      const json = await res.json();
      setResult(json);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1>Crop Yield Predictor</h1>
        <p>Estimate your harvest yield based on soil, weather, and farm size using our ML regression models.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
        <div className="glass-panel card">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
            <Calculator color="var(--primary-color)" /> Farm Parameters
          </h3>

          <div style={{ marginBottom: '16px' }}>
            <label>Crop Type</label>
            <select name="crop_type" value={formData.crop_type} onChange={handleChange}>
              <option value="wheat">Wheat</option>
              <option value="corn">Corn</option>
              <option value="rice">Rice</option>
              <option value="soybean">Soybean</option>
            </select>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label>Area (Hectares)</label>
            <input type="number" name="area_hectares" value={formData.area_hectares} onChange={handleChange} step="0.1" />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label>Soil pH</label>
            <input type="number" name="soil_ph" value={formData.soil_ph} onChange={handleChange} step="0.1" min="0" max="14" />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label>Expected Rainfall (mm)</label>
            <input type="number" name="rainfall_mm" value={formData.rainfall_mm} onChange={handleChange} />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label>Fertilizer Application (kg)</label>
            <input type="number" name="fertilizer_kg" value={formData.fertilizer_kg} onChange={handleChange} />
          </div>

          <button
            className="btn"
            onClick={predictYield}
            disabled={loading}
            style={{ width: '100%' }}
          >
            {loading ? <div className="spinner" /> : <><TrendingUp size={20} /> Predict Yield</>}
          </button>

          {error && <div style={{ marginTop: '16px', color: 'var(--error)' }}>{error}</div>}
        </div>

        <div>
          {result ? (
            <div className="glass-panel card animate-fade-in" style={{ background: 'linear-gradient(180deg, rgba(30,30,30,0.8), rgba(46,125,50,0.1))' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                <BarChart3 color="var(--primary-color)" /> Prediction Results
              </h3>

              <div style={{ textAlign: 'center', margin: '40px 0' }}>
                <div style={{ fontSize: '3rem', fontWeight: 'bold', background: 'linear-gradient(90deg, #81c784, #aed581)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                  {result.predicted_yield_tonnes.toFixed(1)}
                </div>
                <div style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>Total Tons</div>
              </div>

              <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Yield per Hectare</span>
                  <strong>{result.predicted_yield_per_hectare.toFixed(2)} t/ha</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Prediction Source</span>
                  <strong style={{ textTransform: 'capitalize' }}>
                    {result.prediction_source === 'trained_model' ? 'ML Model' : 'Estimate (heuristic)'}
                  </strong>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', padding: '40px', textAlign: 'center' }}>
              <BarChart3 size={48} style={{ opacity: 0.5, marginBottom: '16px' }} />
              <p>Enter your farm parameters and click predict to see estimated harvest yields.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}