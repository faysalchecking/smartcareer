import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { authAPI } from '../services/auth'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user'

export const AuthContext = createContext(null)

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY))
  } catch {
    return null
  }
}

function clearSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY)
    const storedUser = readStoredUser()

    if (token && storedUser) {
      setUser(storedUser)
    } else {
      clearSession()
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(async (email, password) => {
    try {
      const { data } = await authAPI.login(email, password)

      localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token)
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token)
      localStorage.setItem(USER_KEY, JSON.stringify(data.user))
      setUser(data.user)

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error:
          error.response?.data?.error ||
          error.response?.data?.detail ||
          'Login failed. Please try again.',
      }
    }
  }, [])

  const logout = useCallback(async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

    try {
      if (refreshToken) {
        // Revokes the refresh token on the server, so it cannot be reused after logout.
        await authAPI.logout(refreshToken)
      }
    } catch {
      // The token may already be expired. The local session is cleared regardless.
    }

    clearSession()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: Boolean(user),
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}