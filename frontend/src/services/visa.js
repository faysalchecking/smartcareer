import apiClient from './api'

export const visaAPI = {
  // Visa applications
  applications: {
    list: (params = {}) =>
      apiClient.get('/visa/applications/', { params }),
    
    get: (id) =>
      apiClient.get(`/visa/applications/${id}/`),
    
    create: (data) =>
      apiClient.post('/visa/applications/', data),
    
    update: (id, data) =>
      apiClient.patch(`/visa/applications/${id}/`, data),
  },

  // Embassy clearance
  embassy: {
    list: (params = {}) =>
      apiClient.get('/visa/embassy/', { params }),
    
    get: (id) =>
      apiClient.get(`/visa/embassy/${id}/`),
    
    update: (id, data) =>
      apiClient.patch(`/visa/embassy/${id}/`, data),
  },

  // Visa types
  types: () =>
    apiClient.get('/visa/types/'),
}

export default visaAPI