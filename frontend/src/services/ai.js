import apiClient from './api'

export const aiAPI = {
  // Providers
  providers: () => apiClient.get('/ai/providers/'),
  testProvider: (id) => apiClient.post(`/ai/providers/${id}/test/`),
  
  // Conversations
  conversations: (params = {}) => apiClient.get('/ai/conversations/', { params }),
  createConversation: (data) => apiClient.post('/ai/conversations/', data),
  getConversation: (id) => apiClient.get(`/ai/conversations/${id}/`),
  
  // Messages
  sendMessage: (conversationId, message) =>
    apiClient.post(`/ai/conversations/${conversationId}/send_message/`, { message }),
  
  // Tools
  approveTool: (toolId) => apiClient.post(`/ai/tools/${toolId}/approve/`),
  
  // Jobs
  generateCV: (candidateId, jobId = null, language = 'English') =>
    apiClient.post('/ai/jobs/generate_cv/', {
      candidate_id: candidateId,
      job_id: jobId,
      language,
    }),
  
  // Logs
  logs: (params = {}) => apiClient.get('/ai/logs/', { params }),
}

export default aiAPI