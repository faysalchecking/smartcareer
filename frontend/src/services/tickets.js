import apiClient from './api'

export const ticketsAPI = {
  // List tickets
  list: (params = {}) =>
    apiClient.get('/tickets/', { params }),

  // Get single ticket
  get: (id) =>
    apiClient.get(`/tickets/${id}/`),

  // Create ticket
  create: (data) =>
    apiClient.post('/tickets/', data),

  // Update ticket
  update: (id, data) =>
    apiClient.patch(`/tickets/${id}/`, data),
}

export default ticketsAPI