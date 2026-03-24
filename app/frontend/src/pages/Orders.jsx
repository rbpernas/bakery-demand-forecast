import { useState, useEffect } from 'react'
import {
  getOrders, getCustomers, createCustomer, createOrder, cancelOrder, getProducts
} from '../services/api'

const ORDER_TYPE_LABELS = {
  once:     'Puntual',
  daily:    'Cada día',
  weekdays: 'Días laborables',
  weekends: 'Fines de semana',
}

function today() {
  return new Date().toISOString().split('T')[0]
}

export default function Orders() {
  const [orders, setOrders]       = useState([])
  const [customers, setCustomers] = useState([])
  const [products, setProducts]   = useState([])
  const [status, setStatus]       = useState(null)
  const [tab, setTab]             = useState('orders') // 'orders' | 'new_order' | 'new_customer'

  // New customer form
  const [custName, setCustName]   = useState('')
  const [custPhone, setCustPhone] = useState('')

  // New order form
  const [customerId, setCustomerId]   = useState('')
  const [productId, setProductId]     = useState('')
  const [quantity, setQuantity]       = useState(1)
  const [orderType, setOrderType]     = useState('once')
  const [startDate, setStartDate]     = useState(today())
  const [endDate, setEndDate]         = useState('')
  const [orderNotes, setOrderNotes]   = useState('')

  async function loadData() {
    const [o, c, p] = await Promise.all([getOrders(), getCustomers(), getProducts()])
    setOrders(o)
    setCustomers(c)
    setProducts(p)
    if (c.length > 0) setCustomerId(c[0].customer_id)
    if (p.length > 0) setProductId(p[0].product_id)
  }

  useEffect(() => { loadData() }, [])

  async function handleCreateCustomer() {
    setStatus(null)
    if (!custName.trim()) {
      setStatus({ type: 'error', message: 'El nombre es obligatorio.' })
      return
    }
    try {
      await createCustomer({ name: custName.trim(), phone: custPhone || null })
      setStatus({ type: 'success', message: `Cliente "${custName}" añadido.` })
      setCustName('')
      setCustPhone('')
      loadData()
      setTab('orders')
    } catch (e) {
      setStatus({ type: 'error', message: e.message })
    }
  }

  async function handleCreateOrder() {
    setStatus(null)
    try {
      await createOrder({
        customer_id: parseInt(customerId),
        product_id:  parseInt(productId),
        quantity:    parseInt(quantity),
        order_type:  orderType,
        start_date:  startDate,
        end_date:    endDate || null,
        notes:       orderNotes || null,
      })
      setStatus({ type: 'success', message: 'Pedido guardado correctamente.' })
      setOrderNotes('')
      setQuantity(1)
      loadData()
      setTab('orders')
    } catch (e) {
      setStatus({ type: 'error', message: e.message })
    }
  }

  async function handleCancel(order) {
    if (!window.confirm(`¿Cancelar el pedido de ${order.customer_name}?`)) return
    try {
      await cancelOrder(order.order_id)
      setStatus({ type: 'success', message: 'Pedido cancelado.' })
      loadData()
    } catch (e) {
      setStatus({ type: 'error', message: e.message })
    }
  }

  return (
    <>
      <h1 className="page-title">Pedidos y reservas</h1>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        <button className={`btn ${tab === 'orders' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('orders')}>
          Pedidos activos ({orders.length})
        </button>
        <button className={`btn ${tab === 'new_order' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('new_order')}>
          + Nuevo pedido
        </button>
        <button className={`btn ${tab === 'new_customer' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('new_customer')}>
          + Nuevo cliente
        </button>
      </div>

      {status && (
        <div className={`alert ${status.type}`} style={{ marginBottom: 16 }}>
          {status.message}
        </div>
      )}

      {/* Active orders list */}
      {tab === 'orders' && (
        <div className="card">
          <h2>Pedidos activos</h2>
          {orders.length === 0 ? (
            <p style={{ color: '#999' }}>No hay pedidos activos todavía.</p>
          ) : (
            <table className="prediction-table">
              <thead>
                <tr>
                  <th>Cliente</th>
                  <th>Teléfono</th>
                  <th>Producto</th>
                  <th>Cantidad</th>
                  <th>Tipo</th>
                  <th>Desde</th>
                  <th>Hasta</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {orders.map(o => (
                  <tr key={o.order_id}>
                    <td>{o.customer_name}</td>
                    <td>{o.customer_phone ?? '—'}</td>
                    <td>{o.product_name}</td>
                    <td>{o.quantity}</td>
                    <td><span className="badge low">{ORDER_TYPE_LABELS[o.order_type]}</span></td>
                    <td>{o.start_date}</td>
                    <td>{o.end_date ?? '—'}</td>
                    <td>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '4px 12px', fontSize: '0.8rem' }}
                        onClick={() => handleCancel(o)}
                      >
                        Cancelar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* New order form */}
      {tab === 'new_order' && (
        <div className="card">
          <h2>Nuevo pedido</h2>
          {customers.length === 0 ? (
            <div className="alert info">
              Primero añade un cliente usando el botón "+ Nuevo cliente".
            </div>
          ) : (
            <>
              <div className="form-grid">
                <div className="form-group">
                  <label>Cliente</label>
                  <select value={customerId} onChange={e => setCustomerId(e.target.value)}>
                    {customers.map(c => (
                      <option key={c.customer_id} value={c.customer_id}>
                        {c.name} {c.phone ? `(${c.phone})` : ''}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Producto</label>
                  <select value={productId} onChange={e => setProductId(e.target.value)}>
                    {products.map(p => (
                      <option key={p.product_id} value={p.product_id}>{p.name}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Cantidad</label>
                  <input type="number" min="1" value={quantity} onChange={e => setQuantity(e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Tipo de pedido</label>
                  <select value={orderType} onChange={e => setOrderType(e.target.value)}>
                    <option value="once">Puntual (un solo día)</option>
                    <option value="daily">Cada día</option>
                    <option value="weekdays">Días laborables</option>
                    <option value="weekends">Fines de semana</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Fecha de inicio</label>
                  <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Fecha de fin (opcional)</label>
                  <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
                </div>
              </div>
              <div className="form-group" style={{ marginTop: 12 }}>
                <label>Notas</label>
                <input type="text" placeholder="Ej: recoger antes de las 9h" value={orderNotes} onChange={e => setOrderNotes(e.target.value)} />
              </div>
              <div style={{ marginTop: 16 }}>
                <button className="btn btn-primary" onClick={handleCreateOrder}>Guardar pedido</button>
              </div>
            </>
          )}
        </div>
      )}

      {/* New customer form */}
      {tab === 'new_customer' && (
        <div className="card">
          <h2>Nuevo cliente</h2>
          <div className="form-grid">
            <div className="form-group">
              <label>Nombre</label>
              <input type="text" placeholder="Ej: María García" value={custName} onChange={e => setCustName(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Teléfono (opcional)</label>
              <input type="text" placeholder="Ej: 612 345 678" value={custPhone} onChange={e => setCustPhone(e.target.value)} />
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            <button className="btn btn-primary" onClick={handleCreateCustomer}>Añadir cliente</button>
          </div>
        </div>
      )}
    </>
  )
}