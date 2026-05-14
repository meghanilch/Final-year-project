import axios from 'axios'

const rawApiBase = import.meta.env.VITE_API_BASE_URL || ''
const normalizedApiBase = rawApiBase
  ? `${rawApiBase.startsWith('http') ? rawApiBase : `https://${rawApiBase}`}`.replace(/\/$/, '')
  : ''

const api = axios.create({
  baseURL: normalizedApiBase ? `${normalizedApiBase}/api/v1` : '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export const scanURL = (url) =>
  api.post('/scan/url/', { url }).then(r => r.data)

export const scanEmail = (subject, body, sender = '') =>
  api.post('/scan/email/', { subject, body, sender }).then(r => r.data)

export const getHistory = (params = {}) =>
  api.get('/history/', { params }).then(r => r.data)

export const deleteHistoryItem = (id) =>
  api.delete(`/history/${id}`).then(r => r.data)

export const clearHistory = () =>
  api.delete('/history/').then(r => r.data)

export const getStats = () =>
  api.get('/stats/').then(r => r.data)

export default api
