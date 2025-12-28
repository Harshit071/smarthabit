import React, { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const AuthContext = createContext()

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)
      
      const response = await api.post('/api/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      const { access_token } = response.data
      
      if (!access_token) {
        throw new Error('No access token received')
      }
      
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      await fetchUser()
      navigate('/')
    } catch (error) {
      // Extract error message properly
      let errorMessage = 'Invalid email or password'
      
      if (error.response) {
        // Handle different error response formats
        const data = error.response.data
        
        if (data) {
          if (typeof data.detail === 'string') {
            errorMessage = data.detail
          } else if (Array.isArray(data.detail)) {
            // FastAPI validation errors come as array
            errorMessage = data.detail.map(err => {
              if (typeof err === 'string') return err
              if (err.msg) return err.msg
              if (err.loc && err.msg) return `${err.loc.join('.')}: ${err.msg}`
              return JSON.stringify(err)
            }).join(', ')
          } else if (typeof data === 'string') {
            errorMessage = data
          } else if (data.message) {
            errorMessage = data.message
          } else {
            // Fallback: stringify if it's an object
            errorMessage = JSON.stringify(data)
          }
        } else if (error.response.status === 401) {
          errorMessage = 'Invalid email or password'
        } else if (error.response.status === 422) {
          errorMessage = 'Invalid form data. Please check your email and password.'
        } else {
          errorMessage = `Server error: ${error.response.status}`
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      throw new Error(errorMessage)
    }
  }

  const register = async (email, password, fullName) => {
    try {
      // Step 1: Register the user
      const response = await api.post('/api/auth/register', {
        email,
        password,
        full_name: fullName
      })
      
      // Step 2: If registration successful, automatically log in
      if (response.data) {
        try {
          await login(email, password)
        } catch (loginError) {
          // If auto-login fails, still show success but redirect to login
          console.warn('Auto-login failed after registration:', loginError)
          // Registration was successful, just navigate to login
          navigate('/login')
          throw new Error('Registration successful! Please login with your credentials.')
        }
      }
    } catch (error) {
      // Extract error message properly
      let errorMessage = 'Registration failed. Please try again.'
      
      if (error.response) {
        // Server responded with error
        if (error.response.data) {
          if (typeof error.response.data.detail === 'string') {
            errorMessage = error.response.data.detail
          } else if (typeof error.response.data === 'string') {
            errorMessage = error.response.data
          } else if (error.response.data.message) {
            errorMessage = error.response.data.message
          }
        } else {
          errorMessage = `Server error: ${error.response.status} ${error.response.statusText || ''}`
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      throw new Error(errorMessage)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
    navigate('/login')
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

