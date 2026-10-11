import apiClient from './api'

export const deploymentAPI = {
  // List deployments
  list: (params = {}) =>
    apiClient.get('/deployment/', { params }),

  // Get single deployment
  get: (id) =>
    apiClient.get(`/deployment/${id}/`),

  // Create deployment
  create: (data) =>
    apiClient.post('/deployment/', data),

  // Update deployment
  update: (id, data) =>
    apiClient.patch(`/deployment/${id}/`, data),
}

export default deploymentAPI