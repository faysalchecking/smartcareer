import apiClient from './api'

export const alertsAPI = {
  // List alerts
  list: (params = {}) =>
    apiClient.get('/alerts/alerts/', { params }),

  // Get single alert
  get: (id) =>
    apiClient.get(`/alerts/alerts/${id}/`),

  // Active alerts
  active: () =>
    apiClient.get('/alerts/alerts/active/'),

  // Acknowledge alert
  acknowledge: (id) =>
    apiClient.post(`/alerts/alerts/${id}/acknowledge/`),

  // Escalate alert
  escalate: (id, level, escalated_to_id) =>
    apiClient.post(`/alerts/alerts/${id}/escalate/`, { level, escalated_to_id }),

  // Statistics
  statistics: () =>
    apiClient.get('/alerts/alerts/statistics/'),

  // Rules
  rules: () =>
    apiClient.get('/alerts/rules/'),
}

export default alertsAPI