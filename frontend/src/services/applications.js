import apiClient from './api'

export const applicationsAPI = {
  // List applications
  list: (params = {}) =>
    apiClient.get('/applications/', { params }),

  // Get single application
  get: (id) =>
    apiClient.get(`/applications/${id}/`),

  // Create application
  create: (data) =>
    apiClient.post('/applications/', data),

  // Submit screening answers
  submitAnswers: (id, answers) =>
    apiClient.post(`/applications/${id}/submit_screening_answers/`, { answers }),

  // Shortlist
  shortlist: (id, reason) =>
    apiClient.post(`/applications/${id}/shortlist/`, { reason }),

  // Reject
  reject: (id, reason) =>
    apiClient.post(`/applications/${id}/reject/`, { reason }),

  // Get screening questions for job
  getQuestions: (jobId) =>
    apiClient.get('/applications/questions/', { params: { job: jobId } }),

  // Get shortlists
  getShortlists: (params = {}) =>
    apiClient.get('/applications/shortlists/', { params }),
}

export default applicationsAPI