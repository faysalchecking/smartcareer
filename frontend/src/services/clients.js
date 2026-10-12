import apiClient from './api'

export const clientsAPI = {
  // List clients
  list: (params = {}) =>
    apiClient.get('/clients/', { params }),

  // Get single client
  get: (id) =>
    apiClient.get(`/clients/${id}/`),

  // Create client
  create: (data) =>
    apiClient.post('/clients/', data),

  // Update client
  update: (id, data) =>
    apiClient.patch(`/clients/${id}/`, data),

  // Get client jobs
  jobs: (id) =>
    apiClient.get(`/clients/${id}/jobs/`),

  // Get client invoices
  invoices: (id) =>
    apiClient.get(`/clients/${id}/invoices/`),

  // Client statistics
  statistics: (id) =>
    apiClient.get(`/clients/${id}/statistics/`),
}

export default clientsAPI