import { useState, useEffect } from 'react'
import { getProducts, createProduct, deactivateProduct } from '../services/api'

const CATEGORY_LABELS = {
  bread:  'Pan',
  pastry: 'Bollería',
  coca:   'Coca',
}

export default function Products() {
  const [products, setProducts] = useState([])
  const [status, setStatus]     = useState(null)

  // New product form
  const [name, setName]         = useState('')
  const [category, setCategory] = useState('bread')
  const [unitCost, setUnitCost] = useState('')

  async function loadProducts() {
    const data = await getProducts()
    setProducts(data)
  }

  useEffect(() => { loadProducts() }, [])

  async function handleCreate() {
    setStatus(null)
    if (!name.trim()) {
      setStatus({ type: 'error', message: 'El nombre del producto es obligatorio.' })
      return
    }
    try {
      await createProduct({
        name:      name.trim(),
        category,
        unit_cost: unitCost !== '' ? parseFloat(unitCost) : null,
      })
      setStatus({ type: 'success', message: `"${name}" añadido correctamente.` })
      setName('')
      setUnitCost('')
      loadProducts()
    } catch (e) {
      setStatus({ type: 'error', message: e.message })
    }
  }

  async function handleDeactivate(product) {
    if (!window.confirm(`¿Desactivar "${product.name}"? El historial se conservará.`)) return
    try {
      await deactivateProduct(product.product_id)
      setStatus({ type: 'success', message: `"${product.name}" desactivado.` })
      loadProducts()
    } catch (e) {
      setStatus({ type: 'error', message: e.message })
    }
  }

  return (
    <>
      <h1 className="page-title">Productos</h1>

      {/* Current products */}
      <div className="card">
        <h2>Catálogo activo</h2>
        <table className="prediction-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Categoría</th>
              <th>Coste unitario</th>
              <th>Añadido el</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {products.map(p => (
              <tr key={p.product_id}>
                <td>{p.name}</td>
                <td>{CATEGORY_LABELS[p.category] ?? p.category}</td>
                <td>{p.unit_cost != null ? `${p.unit_cost.toFixed(2)} €` : '—'}</td>
                <td>{p.created_at}</td>
                <td>
                  <button
                    className="btn btn-danger"
                    style={{ padding: '4px 12px', fontSize: '0.8rem' }}
                    onClick={() => handleDeactivate(p)}
                  >
                    Desactivar
                  </button>
                </td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr><td colSpan={5} style={{ color: '#999', textAlign: 'center' }}>Sin productos</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add new product */}
      <div className="card">
        <h2>Añadir producto nuevo</h2>
        <div className="form-grid">
          <div className="form-group">
            <label>Nombre</label>
            <input
              type="text"
              placeholder="Ej: ensaimada"
              value={name}
              onChange={e => setName(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Categoría</label>
            <select value={category} onChange={e => setCategory(e.target.value)}>
              <option value="bread">Pan</option>
              <option value="pastry">Bollería</option>
              <option value="coca">Coca</option>
            </select>
          </div>
          <div className="form-group">
            <label>Coste unitario (€) — opcional</label>
            <input
              type="number"
              placeholder="Ej: 0.45"
              value={unitCost}
              onChange={e => setUnitCost(e.target.value)}
            />
          </div>
        </div>

        {status && (
          <div className={`alert ${status.type}`} style={{ marginTop: 16 }}>
            {status.message}
          </div>
        )}

        <div style={{ marginTop: 16 }}>
          <button className="btn btn-primary" onClick={handleCreate}>
            Añadir producto
          </button>
        </div>
      </div>
    </>
  )
}