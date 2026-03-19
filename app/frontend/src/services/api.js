/**
 * api.js
 * ------
 * All communication with the FastAPI backend goes through here.
 * This way, if the API URL changes, we only update one file.
 */

const BASE_URL = '/api'

// -------------------------------------------------------------------
// Predictions
// -------------------------------------------------------------------

export async function getPredictions({ date, isHoliday, isLocalEvent, tempMax, precipMm }) {
  const params = new URLSearchParams({ target_date: date })
  if (isHoliday)    params.append('is_holiday', 'true')
  if (isLocalEvent) params.append('is_local_event', 'true')
  if (tempMax   != null) params.append('temperature_max', tempMax)
  if (precipMm  != null) params.append('precipitation_mm', precipMm)

  const res = await fetch(`${BASE_URL}/predictions?${params}`)
  if (!res.ok) throw new Error('Error fetching predictions')
  return res.json()
}

// -------------------------------------------------------------------
// Products
// -------------------------------------------------------------------

export async function getProducts() {
  const res = await fetch(`${BASE_URL}/products`)
  if (!res.ok) throw new Error('Error fetching products')
  return res.json()
}

export async function createProduct(payload) {
  const res = await fetch(`${BASE_URL}/products`, {
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
  const res = await fetch(`${BASE_URL}/logs`, {
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

  const res = await fetch(`${BASE_URL}/logs?${params}`)
  if (!res.ok) throw new Error('Error fetching logs')
  return res.json()
}