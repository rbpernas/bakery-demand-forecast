import { useState, useEffect } from 'react'
import { getSummary, getDaily } from '../services/api'

const CATEGORY_LABELS = { bread: 'Pan', pastry: 'Bollería', coca: 'Coca' }

function Bar({ value, max, color }) {
  const pct = max > 0 ? (value / max) * 100 : 0
  return (
    <div style={{ background: '#f0ede8', borderRadius: 4, height: 12, flex: 1 }}>
      <div style={{ width: `${pct}%`, background: color, height: '100%', borderRadius: 4, transition: 'width 0.4s' }} />
    </div>
  )
}

export default function Trends() {
  const [summary, setSummary] = useState([])
  const [daily, setDaily]     = useState([])
  const [days, setDays]       = useState(30)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([getSummary(days), getDaily(days)])
      .then(([s, d]) => { setSummary(s); setDaily(d) })
      .catch(e => console.error('Stats error:', e))
      .finally(() => setLoading(false))
  }, [days])

  const maxWasted   = Math.max(...summary.map(s => s.total_wasted), 1)
  const maxProduced = Math.max(...summary.map(s => s.total_produced), 1)
  const maxDailyWaste = Math.max(...daily.map(d => d.total_wasted), 1)

  return (
    <>
      <h1 className="page-title">Tendencias</h1>

      {/* Period selector */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <span style={{ fontWeight: 600, fontSize: '0.9rem', color: '#555' }}>Período:</span>
        {[7, 14, 30].map(d => (
          <button
            key={d}
            className={`btn ${days === d ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 16px' }}
            onClick={() => setDays(d)}
          >
            {d} días
          </button>
        ))}
      </div>

      {loading && <div className="loading">Cargando datos...</div>}

      {!loading && summary.length === 0 && (
        <div className="alert info">No hay datos registrados todavía.</div>
      )}

      {!loading && summary.length > 0 && (
        <>
          {/* Waste per product */}
          <div className="card">
            <h2>Desperdicio por producto</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {summary.map(s => (
                <div key={s.product} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ width: 90, fontSize: '0.9rem', fontWeight: 600 }}>{s.product}</span>
                  <Bar value={s.total_wasted} max={maxWasted} color="#e07b39" />
                  <span style={{ width: 80, fontSize: '0.85rem', color: '#666', textAlign: 'right' }}>
                    {s.total_wasted} uds ({s.waste_pct}%)
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Sales vs produced */}
          <div className="card">
            <h2>Vendido vs producido (últimos {days} días)</h2>
            <table className="prediction-table">
              <thead>
                <tr>
                  <th>Producto</th>
                  <th>Categoría</th>
                  <th>Producidas</th>
                  <th>Vendidas</th>
                  <th>Tiradas</th>
                  <th>Días agotado</th>
                </tr>
              </thead>
              <tbody>
                {summary.map(s => (
                  <tr key={s.product}>
                    <td>{s.product}</td>
                    <td>{CATEGORY_LABELS[s.category] ?? s.category}</td>
                    <td>{s.total_produced}</td>
                    <td>{s.total_sold}</td>
                    <td style={{ color: s.total_wasted > 0 ? '#b5541c' : 'inherit', fontWeight: s.total_wasted > 0 ? 600 : 400 }}>
                      {s.total_wasted}
                    </td>
                    <td>
                      <span className={`badge ${s.days_sold_out > 3 ? 'medium' : 'low'}`}>
                        {s.days_sold_out} / {s.days_recorded}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Daily waste chart */}
          <div className="card">
            <h2>Desperdicio diario</h2>
            <div style={{ overflowX: 'auto' }}>
              <div style={{
                display: 'flex',
                alignItems: 'flex-end',
                gap: 3,
                height: 140,
                minWidth: daily.length * 20,
                paddingBottom: 24,
                position: 'relative',
              }}>
                {daily.map(d => {
                  const pct = maxDailyWaste > 0 ? (d.total_wasted / maxDailyWaste) : 0
                  const barHeight = Math.max(pct * 110, d.total_wasted > 0 ? 4 : 0)
                  const shortDate = d.date.slice(5)
                  return (
                    <div
                      key={d.date}
                      style={{ flex: 1, minWidth: 16, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-end', height: '100%' }}
                    >
                      <div
                        title={`${d.date}: ${d.total_wasted} tiradas`}
                        style={{
                          width: '100%',
                          height: barHeight,
                          background: d.total_wasted > 0 ? '#e07b39' : '#f0ede8',
                          borderRadius: '3px 3px 0 0',
                        }}
                      />
                      <span style={{
                        fontSize: '0.55rem',
                        color: '#999',
                        marginTop: 3,
                        transform: 'rotate(-45deg)',
                        whiteSpace: 'nowrap',
                        transformOrigin: 'top left',
                        position: 'absolute',
                        bottom: 0,
                      }}>
                        {shortDate}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
            <p style={{ fontSize: '0.82rem', color: '#999', marginTop: 8 }}>
              Cada barra representa el total de unidades tiradas ese día. Pasa el ratón por encima para ver el detalle.
            </p>
          </div>
        </>
      )}
    </>
  )
}