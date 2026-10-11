import apiClient from './api'

export const medicalAPI = {
  // List medical exams
  list: (params = {}) =>
    apiClient.get('/medical/', { params }),

  // Get single exam
  get: (id) =>
    apiClient.get(`/medical/${id}/`),

  // Create exam
  create: (data) =>
    apiClient.post('/medical/', data),

  // Update exam
  update: (id, data) =>
    apiClient.patch(`/medical/${id}/`, data),

  // Get medical centers
  centers: (params = {}) =>
    apiClient.get('/medical/centers/', { params }),
}

export default medicalAPI