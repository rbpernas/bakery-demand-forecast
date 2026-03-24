/**
 * api.js
 * ------
 * All communication with the FastAPI backend goes through here.
 */

const BASE_URL = 'http://localhost:8000'
// -------------------------------------------------------------------
// Predictions
// -------------------------------------------------------------------

export async function getPredictions({ date, isHoliday, isLocalEvent, tempMax, precipMm }) {
  const params = new URLSearchParams({ target_date: date })
  if (isHoliday)    params.append('is_holiday', 'true')
  if (isLocalEvent) params.append('is_local_event', 'true')
  if (tempMax   != null) params.append('temperature_max', tempMax)
  if (precipMm  != null) params.append('precipitation_mm', precipMm)

  const res = await fetch(`${BASE_URL}/predictions/?${params}`)
  if (!res.ok) throw new Error('Error fetching predictions')
  return res.json()
}

// -------------------------------------------------------------------
// Products
// -------------------------------------------------------------------

export async function getProducts() {
  const res = await fetch(`${BASE_URL}/products/`)
  if (!res.ok) throw new Error('Error fetching products')
  return res.json()
}

export async function createProduct(payload) {
  const res = await fetch(`${BASE_URL}/products/`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error creating product')
  }
  return res.json()
}

export async function deactivateProduct(productId) {
  const res = await fetch(`${BASE_URL}/products/${productId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Error deactivating product')
  return res.json()
}

// -------------------------------------------------------------------
// Logs
// -------------------------------------------------------------------

export async function createLog(payload) {
  const res = await fetch(`${BASE_URL}/logs/`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error saving log')
  }
  return res.json()
}

export async function getLogs({ dateFrom, dateTo, productId } = {}) {
  const params = new URLSearchParams()
  if (dateFrom)  params.append('date_from', dateFrom)
  if (dateTo)    params.append('date_to', dateTo)
  if (productId) params.append('product_id', productId)

  const res = await fetch(`${BASE_URL}/logs/?${params}`)
  if (!res.ok) throw new Error('Error fetching logs')
  return res.json()
}

// -------------------------------------------------------------------
// Stats
// -------------------------------------------------------------------

export async function getSummary(days = 30) {
  const res = await fetch(`${BASE_URL}/stats/summary/?days=${days}`)
  if (!res.ok) throw new Error('Error fetching summary')
  return res.json()
}

export async function getDaily(days = 30) {
  const res = await fetch(`${BASE_URL}/stats/daily/?days=${days}`)
  if (!res.ok) throw new Error('Error fetching daily stats')
  return res.json()
}


// -------------------------------------------------------------------
// Orders
// -------------------------------------------------------------------

export async function getOrders() {
  const res = await fetch(`${BASE_URL}/orders/`)
  if (!res.ok) throw new Error('Error fetching orders')
  return res.json()
}

export async function getOrdersForDay(date) {
  const res = await fetch(`${BASE_URL}/orders/day/?target_date=${date}`)
  if (!res.ok) throw new Error('Error fetching orders for day')
  return res.json()
}

export async function getCustomers() {
  const res = await fetch(`${BASE_URL}/orders/customers/`)
  if (!res.ok) throw new Error('Error fetching customers')
  return res.json()
}

export async function createCustomer(payload) {
  const res = await fetch(`${BASE_URL}/orders/customers/`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error creating customer')
  }
  return res.json()
}

export async function createOrder(payload) {
  const res = await fetch(`${BASE_URL}/orders/`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error creating order')
  }
  return res.json()
}

export async function cancelOrder(orderId) {
  const res = await fetch(`${BASE_URL}/orders/${orderId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Error cancelling order')
  return res.json()
}

// -------------------------------------------------------------------
// History
// -------------------------------------------------------------------

export async function getLoggedDates() {
  const res = await fetch(`${BASE_URL}/logs/dates/`)
  if (!res.ok) throw new Error('Error fetching logged dates')
  return res.json()
}

export async function getDayDetail(date) {
  const res = await fetch(`${BASE_URL}/logs/day/?date=${date}`)
  if (!res.ok) throw new Error('Error fetching day detail')
  return res.json()
}