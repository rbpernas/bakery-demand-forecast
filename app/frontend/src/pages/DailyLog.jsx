import { useState, useEffect } from 'react'
import { getProducts, createLog } from '../services/api'

function today() {
  return new Date().toISOString().split('T')[0]
}

export default function DailyLog() {
  const [products, setProducts] = useState([])
  const [status, setStatus]     = useState(null)  // { type, message }

  // One row per product
  const [entries, setEntries] = useState([])

  useEffect(() => {
    getProducts().then(data => {
      setProducts(data)
      setEntries(data.map(p => ({
        product_id:     p.product_id,
        name:           p.name,
        units_produced: '',
        units_sold:     '',
        units_wasted:   '',
        sold_out:       false,
      })))
    })
  }, [])

  const [date, setDate]               = useState(today())
  const [isHoliday, setIsHoliday]     = useState(false)
  const [isLocalEvent, setIsLocalEvent] = useState(false)
  const [tempMax, setTempMax]         = useState('')
  const [precipMm, setPrecipMm]       = useState('')
  const [notes, setNotes]             = useState('')

  function updateEntry(productId, field, value) {
    setEntries(prev =>
      prev.map(e => e.product_id === productId ? { ...e, [field]: value } : e)
    )
  }

  async function handleSubmit() {
    setStatus(null)
    const filled = entries.filter(e => e.units_produced !== '')
    if (filled.length === 0) {
      setStatus({ type: 'error', message: 'Rellena al menos un producto.' })
      return
    }

    try {
      for (const entry of filled) {
        await createLog({
          date,
          product_id:      entry.product_id,
          units_produced:  parseInt(entry.units_produced) || 0,
          units_sold:      parseInt(entry.units_sold)     || 0,
          units_wasted:    parseInt(entry.units_wasted)   || 0,
          sold_out:        entry.sold_out,
          is_holiday:      isHoliday,
          is_local_event:  isLocalEvent,
          temperature_max: tempMax   !== '' ? parseFloat(tempMax)  : null,
          precipitation_mm: precipMm !== '' ? parseFloat(precipMm) : null,
          notes:           notes || null,
        })
      }
      setStatus({ type: 'success', message: `Registro guardado para ${filled.length} producto(s).` })
    } catch (e) {
      setStatus({ type: 'error', message: e.message })
    }
  }

  return (
    <>
      <h1 className="page-title">Registro diario</h1>

      {/* Day info */}
      <div className="card">
        <h2>Información del día</h2>
        <div className="form-grid">
          <div className="form-group">
            <label>Fecha</label>
            <input type="date" value={date} onChange={e => setDate(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Temperatura máxima (°C)</label>
            <input type="number" placeholder="Ej: 22" value={tempMax} onChange={e => setTempMax(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Precipitación (mm)</label>
            <input type="number" placeholder="Ej: 0" value={precipMm} onChange={e => setPrecipMm(e.target.value)} />
          </div>
          <div className="form-group" style={{ justifyContent: 'flex-end', gap: 12 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input type="checkbox" checked={isHoliday} onChange={e => setIsHoliday(e.target.checked)} />
              Día festivo
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input type="checkbox" checked={isLocalEvent} onChange={e => setIsLocalEvent(e.target.checked)} />
              Evento local
            </label>
          </div>
        </div>
        <div className="form-group" style={{ marginTop: 12 }}>
          <label>Notas del día</label>
          <input type="text" placeholder="Ej: Mercado semanal, vino gente de fuera..." value={notes} onChange={e => setNotes(e.target.value)} />
        </div>
      </div>

      {/* Products table */}
      <div className="card">
        <h2>Producción y ventas</h2>
        <table className="prediction-table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Producidos</th>
              <th>Vendidos</th>
              <th>Tirados</th>
              <th>Se agotó</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(entry => (
              <tr key={entry.product_id}>
                <td>{entry.name}</td>
                <td>
                  <input
                    type="number" min="0" style={{ width: 70 }}
                    value={entry.units_produced}
                    onChange={e => updateEntry(entry.product_id, 'units_produced', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="number" min="0" style={{ width: 70 }}
                    value={entry.units_sold}
                    onChange={e => updateEntry(entry.product_id, 'units_sold', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="number" min="0" style={{ width: 70 }}
                    value={entry.units_wasted}
                    onChange={e => updateEntry(entry.product_id, 'units_wasted', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={entry.sold_out}
                    onChange={e => updateEntry(entry.product_id, 'sold_out', e.target.checked)}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {status && (
          <div className={`alert ${status.type}`} style={{ marginTop: 16 }}>
            {status.message}
          </div>
        )}

        <div style={{ marginTop: 16 }}>
          <button className="btn btn-primary" onClick={handleSubmit}>
            Guardar registro
          </button>
        </div>
      </div>
    </>
  )
}