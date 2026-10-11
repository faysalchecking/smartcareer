import apiClient from './api'

export const notificationsAPI = {
  // List notifications
  list: (params = {}) =>
    apiClient.get('/notifications/notifications/', { params }),

  // Unread notifications
  unread: () =>
    apiClient.get('/notifications/notifications/unread/'),

  // Mark as read
  markAsRead: (id) =>
    apiClient.post(`/notifications/notifications/${id}/mark_as_read/`),

  // Mark all as read
  markAllAsRead: () =>
    apiClient.post('/notifications/notifications/mark_all_as_read/'),
}

export default notificationsAPI