import { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, AlertTriangle, Leaf } from 'lucide-react';

export default function DiseaseDetection() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [cropType, setCropType] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setResults(null);
      setError(null);
    }
  };

  const handleDragOver = (e) => e.preventDefault();
  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setResults(null);
      setError(null);
    }
  };

  const analyzeImage = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    if (cropType) formData.append('crop_type', cropType);

    try {
      // In production, configure CORS/proxy correctly
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/disease-detection/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Analysis failed. Please try again.');

      const data = await res.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1>AI Crop Disease Detection</h1>
        <p>Upload a clear photo of a crop leaf to instantly identify potential diseases and get actionable insights.</p>
      </div>

      <div className="glass-panel card">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>

          <div>
            <label>Crop Type (Optional)</label>
            <input
              type="text"
              placeholder="e.g. Tomato, Apple, Corn..."
              value={cropType}
              onChange={(e) => setCropType(e.target.value)}
              style={{ marginBottom: '20px' }}
            />

            <div
              className="upload-zone"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadCloud size={48} color="var(--primary-color)" style={{ marginBottom: '16px' }} />
              <p>Drag and drop an image here, or <strong>click to browse</strong></p>
              <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>Supports JPG, PNG</p>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/jpeg, image/png"
                style={{ display: 'none' }}
              />
            </div>

            <button
              className="btn"
              onClick={analyzeImage}
              disabled={!file || loading}
              style={{ width: '100%', marginTop: '20px' }}
            >
              {loading ? <div className="spinner" /> : <><Leaf size={20} /> Analyze Plant</>}
            </button>
          </div>

          <div>
            {preview ? (
              <div style={{ textAlign: 'center' }}>
                <img src={preview} alt="Crop preview" className="image-preview" />
              </div>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.2)', borderRadius: '12px' }}>
                <p>Image preview will appear here</p>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div style={{ marginTop: '20px', padding: '16px', background: 'rgba(207, 102, 121, 0.1)', border: '1px solid var(--error)', borderRadius: '8px', color: 'var(--error)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={20} />
            {error}
          </div>
        )}

        {results && (
          <div className="animate-fade-in" style={{ marginTop: '30px', borderTop: '1px solid var(--glass-border)', paddingTop: '20px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 color="var(--primary-color)" /> Analysis Results
            </h3>

            <p><strong>Status:</strong> {results.is_healthy ? <span style={{ color: 'var(--primary-color)' }}>Healthy</span> : <span style={{ color: 'var(--accent)' }}>Disease Detected</span>}</p>
            <p><strong>Model:</strong> {results.model_version}</p>

            <div style={{ marginTop: '20px' }}>
              <h4>Top Predictions</h4>
              {results.predictions.slice(0, 3).map((pred, i) => (
                <div key={i} style={{ marginBottom: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span>{pred.disease_name}</span>
                    <span style={{ fontWeight: 'bold' }}>{(pred.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="result-bar-container">
                    <div
                      className="result-bar"
                      style={{
                        width: `${pred.confidence * 100}%`,
                        background: i === 0 ? (pred.is_healthy ? 'var(--primary-color)' : 'var(--accent)') : '#555'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {!results.is_healthy && results.predictions[0].treatment_recommendation && (
              <div style={{ marginTop: '20px', padding: '16px', background: 'rgba(255, 179, 0, 0.1)', borderLeft: '4px solid var(--accent)', borderRadius: '4px' }}>
                <h4>Recommended Action</h4>
                <p style={{ margin: 0 }}>{results.predictions[0].treatment_recommendation}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
