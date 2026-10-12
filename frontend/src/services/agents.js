import apiClient from './api'

export const agentsAPI = {
  // List agents
  list: (params = {}) =>
    apiClient.get('/agents/', { params }),

  // Get single agent
  get: (id) =>
    apiClient.get(`/agents/${id}/`),

  // Create agent
  create: (data) =>
    apiClient.post('/agents/', data),

  // Update agent
  update: (id, data) =>
    apiClient.patch(`/agents/${id}/`, data),

  // Get agent candidates
  candidates: (id) =>
    apiClient.get(`/agents/${id}/candidates/`),

  // Agent statistics
  statistics: (id) =>
    apiClient.get(`/agents/${id}/statistics/`),
}

export default agentsAPI