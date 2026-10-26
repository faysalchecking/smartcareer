import api from './api'

export const authAPI = {
  login: (email, password) => api.post('/auth/login/', { email, password }),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me/'),
}