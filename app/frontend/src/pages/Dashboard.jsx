import { useState, useEffect } from 'react'
import { getPredictions } from '../services/api'

// Returns tomorrow's date in YYYY-MM-DD format
function tomorrow() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
}

export default function Dashboard() {
  const [date, setDate]               = useState(tomorrow())
  const [isHoliday, setIsHoliday]     = useState(false)
  const [isLocalEvent, setIsLocalEvent] = useState(false)
  const [tempMax, setTempMax]         = useState('')
  const [precipMm, setPrecipMm]       = useState('')
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState(null)
  const [weatherInfo, setWeatherInfo] = useState(null)

  // Load weather forecast automatically on first render  
  useEffect(() => {
    fetch('/api/weather/')
      .then(r => r.json())
      .then(data => {
        if (data.available) {
          setTempMax(data.temperature_max?.toString() ?? '')
          setPrecipMm(data.precipitation_mm?.toString() ?? '')
          setWeatherInfo(data)
        }
      })
      .catch(() => {})
  }, [])

  async function fetchPredictions() {
    setLoading(true)
    setError(null)
    try {
      const data = await getPredictions({
        date,
        isHoliday,
        isLocalEvent,
        tempMax:   tempMax   !== '' ? parseFloat(tempMax)   : null,
        precipMm:  precipMm  !== '' ? parseFloat(precipMm)  : null,
      })
      setPredictions(data)
    } catch (e) {
      setError('No se ha podido conectar con el servidor. ¿Está el backend en marcha?')
    } finally {
      setLoading(false)
    }
  }

  // Load predictions automatically on first render
  useEffect(() => { fetchPredictions() }, [])

  const categoryLabel = {
    bread:  'Pan',
    pastry: 'Bollería',
    coca:   'Coca',
  }

  return (
    <>
      <h1 className="page-title">Previsión de producción</h1>

      {weatherInfo?.available && (
        <div className="alert info">
          🌤️ Tiempo previsto para mañana: <strong>{weatherInfo.temperature_max}°C</strong>,{' '}
          precipitación <strong>{weatherInfo.precipitation_mm} mm</strong> — cargado automáticamente.
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <h2>Parámetros del día</h2>
        <div className="form-grid">
          <div className="form-group">
            <label>Fecha</label>
            <input
              type="date"
              value={date}
              onChange={e => setDate(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Temperatura máxima (°C)</label>
            <input
              type="number"
              placeholder="Ej: 24"
              value={tempMax}
              onChange={e => setTempMax(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Precipitación (mm)</label>
            <input
              type="number"
              placeholder="Ej: 0"
              value={precipMm}
              onChange={e => setPrecipMm(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ justifyContent: 'flex-end', gap: 12 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={isHoliday}
                onChange={e => setIsHoliday(e.target.checked)}
              />
              Día festivo
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={isLocalEvent}
                onChange={e => setIsLocalEvent(e.target.checked)}
              />
              Evento local (feria, romería...)
            </label>
          </div>
        </div>
        <div style={{ marginTop: 16 }}>
          <button className="btn btn-primary" onClick={fetchPredictions}>
            Calcular previsión
          </button>
        </div>
      </div>

      {/* Results */}
      {error && <div className="alert error">{error}</div>}
      {loading && <div className="loading">Calculando...</div>}

      {!loading && predictions.length > 0 && (
        <div className="card">
          <h2>Producción recomendada</h2>
          <table className="prediction-table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Categoría</th>
                <th>Unidades</th>
                <th>Confianza</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map(p => (
                <tr key={p.product}>
                  <td>{p.product}</td>
                  <td>{p.category ?? '—'}</td>
                  <td><span className="units">{p.units}</span></td>
                  <td>
                    <span className={`badge ${p.confidence}`}>
                      {p.confidence === 'low'    && 'Baja'}
                      {p.confidence === 'medium' && 'Media'}
                      {p.confidence === 'high'   && 'Alta'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p style={{ marginTop: 12, fontSize: '0.82rem', color: '#999' }}>
            La confianza es baja al principio porque no hay datos históricos todavía.
            Mejorará con cada día registrado.
          </p>
        </div>
      )}
    </>
  )
}