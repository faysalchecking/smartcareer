import apiClient from './api'

export const tasksAPI = {
  // List tasks
  list: (params = {}) =>
    apiClient.get('/tasks/', { params }),

  // Get single task
  get: (id) =>
    apiClient.get(`/tasks/${id}/`),

  // Create task
  create: (data) =>
    apiClient.post('/tasks/', data),

  // Update task
  update: (id, data) =>
    apiClient.patch(`/tasks/${id}/`, data),

  // My tasks
  myTasks: (params = {}) =>
    apiClient.get('/tasks/my_tasks/', { params }),

  // Today's tasks
  today: () =>
    apiClient.get('/tasks/today/'),

  // Overdue tasks
  overdue: () =>
    apiClient.get('/tasks/overdue/'),

  // Complete task
  complete: (id, notes = '') =>
    apiClient.post(`/tasks/${id}/complete/`, { notes }),

  // Add comment
  addComment: (id, comment) =>
    apiClient.post(`/tasks/${id}/add_comment/`, { comment }),

  // Statistics
  statistics: () =>
    apiClient.get('/tasks/statistics/'),
}

export default tasksAPI