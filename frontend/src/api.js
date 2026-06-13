const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

async function apiRequest(path, options = {}) {
  const isFormData = options.body instanceof FormData
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: isFormData ? options.headers : {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const message = data?.detail?.message || data?.detail || data?.message || 'Request gagal'
    const error = new Error(typeof message === 'string' ? message : JSON.stringify(message))
    error.payload = data
    throw error
  }

  return data
}

const jsonBody = (payload, method) => ({ method, body: JSON.stringify(payload) })

export const listAlternatives = () => apiRequest('/alternatives')
export const createAlternative = (payload) => apiRequest('/alternatives', jsonBody(payload, 'POST'))
export const updateAlternative = (id, payload) => apiRequest(`/alternatives/${id}`, jsonBody(payload, 'PUT'))
export const deleteAlternative = (id) => apiRequest(`/alternatives/${id}`, { method: 'DELETE' })

export const listCriteria = () => apiRequest('/criteria')
export const createCriterion = (payload) => apiRequest('/criteria', jsonBody(payload, 'POST'))
export const updateCriterion = (id, payload) => apiRequest(`/criteria/${id}`, jsonBody(payload, 'PUT'))
export const deleteCriterion = (id) => apiRequest(`/criteria/${id}`, { method: 'DELETE' })

export const listScores = () => apiRequest('/scores')
export const createScore = (payload) => apiRequest('/scores', jsonBody(payload, 'POST'))
export const updateScore = (id, payload) => apiRequest(`/scores/${id}`, jsonBody(payload, 'PUT'))
export const deleteScore = (id) => apiRequest(`/scores/${id}`, { method: 'DELETE' })
export const getScoreMatrix = () => apiRequest('/scores/matrix')

export const calculateVikor = (v) => apiRequest(`/vikor/calculate?v=${v}`)
export const getRanking = (v) => apiRequest(`/vikor/ranking?v=${v}`)
export const getCompromise = (v) => apiRequest(`/vikor/compromise?v=${v}`)

export const deleteData = (payload) => apiRequest('/maintenance/data', jsonBody(payload, 'DELETE'))

export const previewCsvImport = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return apiRequest('/import/csv/preview', { method: 'POST', body: formData })
}

export const commitCsvImport = (file, mapping) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('payload', JSON.stringify(mapping))
  return apiRequest('/import/csv/commit', { method: 'POST', body: formData })
}
