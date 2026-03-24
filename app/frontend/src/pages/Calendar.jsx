import { useState, useEffect } from 'react'
import { getLoggedDates, getDayDetail, getOrdersForDay } from '../services/api'

const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const DAYS   = ['L','M','X','J','V','S','D']
const ORDER_TYPE_LABELS = { once: 'Puntual', daily: 'Cada día', weekdays: 'Lab.', weekends: 'Finde' }

function isoDate(year, month, day) {
  return `${year}-${String(month+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`
}

export default function Calendar() {
  const now = new Date()
  const [year, setYear]               = useState(now.getFullYear())
  const [month, setMonth]             = useState(now.getMonth())
  const [loggedDates, setLoggedDates] = useState(new Set())
  const [selectedDate, setSelectedDate] = useState(null)
  const [detail, setDetail]           = useState(null)
  const [loading, setLoading]         = useState(false)

  const minYear = now.getFullYear() - 1
  const maxYear = now.getFullYear() + 1

  useEffect(() => {
    getLoggedDates().then(dates => setLoggedDates(new Set(dates)))
  }, [])

  useEffect(() => {
    if (!selectedDate) return
    setLoading(true)
    Promise.all([
      getDayDetail(selectedDate),
      getOrdersForDay(selectedDate),
    ])
    .then(([d, o]) => {
      setDetail({ ...d, orders: o.orders })
    })
    .finally(() => setLoading(false))
  }, [selectedDate])

  function prevMonth() {
    if (month === 0) {
      if (year > minYear) { setYear(y => y-1); setMonth(11) }
    } else {
      setMonth(m => m-1)
    }
    setSelectedDate(null)
    setDetail(null)
  }

  function nextMonth() {
    if (month === 11) {
      if (year < maxYear) { setYear(y => y+1); setMonth(0) }
    } else {
      setMonth(m => m+1)
    }
    setSelectedDate(null)
    setDetail(null)
  }

  const firstDay    = new Date(year, month, 1).getDay()
  const offset      = firstDay === 0 ? 6 : firstDay - 1
  const daysInMonth = new Date(year, month+1, 0).getDate()
  const cells       = []
  for (let i = 0; i < offset; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)

  const todayIso = now.toISOString().split('T')[0]

  return (
    <>
      <h1 className="page-title">Histórico</h1>

      <div style={{ display: 'grid', gridTemplateColumns: selectedDate ? '1fr 1fr' : '1fr', gap: 20 }}>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <button className="btn btn-secondary" style={{ padding: '4px 12px' }}
              onClick={prevMonth} disabled={year === minYear && month === 0}>‹</button>
            <span style={{ fontWeight: 700, fontSize: '1rem' }}>{MONTHS[month]} {year}</span>
            <button className="btn btn-secondary" style={{ padding: '4px 12px' }}
              onClick={nextMonth} disabled={year === maxYear && month === 11}>›</button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4, marginBottom: 4 }}>
            {DAYS.map(d => (
              <div key={d} style={{ textAlign: 'center', fontSize: '0.75rem', fontWeight: 700, color: '#999' }}>{d}</div>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4 }}>
            {cells.map((day, i) => {
              if (!day) return <div key={`empty-${i}`} />
              const iso        = isoDate(year, month, day)
              const hasData    = loggedDates.has(iso)
              const isToday    = iso === todayIso
              const isSelected = iso === selectedDate
              return (
                <div
                  key={iso}
                  onClick={() => setSelectedDate(iso)}
                  style={{
                    textAlign:    'center',
                    padding:      '8px 4px',
                    borderRadius: 8,
                    fontSize:     '0.85rem',
                    fontWeight:   hasData ? 700 : 400,
                    cursor:       'pointer',
                    background:   isSelected ? '#b5541c' : hasData ? '#fdebd8' : 'transparent',
                    color:        isSelected ? '#fff' : isToday ? '#b5541c' : hasData ? '#7a3510' : '#aaa',
                    border:       isToday && !isSelected ? '2px solid #b5541c' : '2px solid transparent',
                  }}
                >
                  {day}
                </div>
              )
            })}
          </div>

          <div style={{ marginTop: 12, fontSize: '0.8rem', color: '#999', display: 'flex', gap: 16 }}>
            <span><span style={{ background: '#fdebd8', padding: '2px 8px', borderRadius: 4 }}>■</span> Con datos</span>
            <span><span style={{ border: '2px solid #b5541c', padding: '2px 6px', borderRadius: 4 }}>■</span> Hoy</span>
          </div>
        </div>

        {selectedDate && (
          <div>
            {loading && <div className="loading">Cargando...</div>}
            {!loading && detail && (
              <>
                <div className="card">
                  <h2>📅 {selectedDate}</h2>
                  <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', fontSize: '0.9rem', marginBottom: 8 }}>
                    {detail.temperature_max != null && <span>🌡️ {detail.temperature_max}°C</span>}
                    {detail.precipitation_mm != null && <span>🌧️ {detail.precipitation_mm} mm</span>}
                    {detail.is_holiday ? <span className="badge medium">Festivo</span> : null}
                    {detail.is_local_event ? <span className="badge low">Evento local</span> : null}
                  </div>
                  {detail.event_notes && <p style={{ fontSize: '0.85rem', color: '#666' }}>📝 {detail.event_notes}</p>}
                  {detail.notes && <p style={{ fontSize: '0.85rem', color: '#666' }}>💬 {detail.notes}</p>}
                  {detail.logs && detail.logs.length === 0 && detail.orders && detail.orders.length === 0 && (
                    <p style={{ color: '#999' }}>Sin datos ni pedidos para este día.</p>
                  )}
                </div>

                {detail.logs && detail.logs.length > 0 && (
                  <div className="card">
                    <h2>Producción y ventas</h2>
                    <table className="prediction-table">
                      <thead>
                        <tr>
                          <th>Producto</th>
                          <th>Producidas</th>
                          <th>Vendidas</th>
                          <th>Tiradas</th>
                          <th>Agotado</th>
                        </tr>
                      </thead>
                      <tbody>
                        {detail.logs.map(l => (
                          <tr key={l.product}>
                            <td>{l.product}</td>
                            <td>{l.units_produced}</td>
                            <td>{l.units_sold}</td>
                            <td style={{ color: l.units_wasted > 0 ? '#b5541c' : 'inherit' }}>{l.units_wasted}</td>
                            <td>{l.sold_out ? '✅' : '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {detail.orders && detail.orders.length > 0 && (
                  <div className="card">
                    <h2>Pedidos del día</h2>
                    <table className="prediction-table">
                      <thead>
                        <tr>
                          <th>Cliente</th>
                          <th>Producto</th>
                          <th>Cantidad</th>
                          <th>Tipo</th>
                        </tr>
                      </thead>
                      <tbody>
                        {detail.orders.map(o => (
                          <tr key={o.order_id}>
                            <td>{o.customer_name}</td>
                            <td>{o.product_name}</td>
                            <td>{o.quantity}</td>
                            <td><span className="badge low">{ORDER_TYPE_LABELS[o.order_type]}</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </>
  )
}