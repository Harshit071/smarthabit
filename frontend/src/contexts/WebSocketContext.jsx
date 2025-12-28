import React, { createContext, useContext, useEffect, useState, useRef } from 'react'
import { useAuth } from './AuthContext'

const WebSocketContext = createContext()

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider')
  }
  return context
}

export function WebSocketProvider({ children }) {
  const { user } = useAuth()
  const [events, setEvents] = useState([])
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  useEffect(() => {
    if (!user) return

    const connect = () => {
      const token = localStorage.getItem('token')
      const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws?token=${token}`
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
          reconnectTimeoutRef.current = null
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setEvents(prev => [...prev, data])
          
          // Handle different event types
          if (data.type === 'habit_at_risk') {
            // Show notification
            console.warn('Habit at risk:', data.data)
          } else if (data.type === 'nudge') {
            // Show nudge notification
            console.info('Nudge:', data.data)
          } else if (data.type === 'habit_logged') {
            // Update UI with new streak
            console.info('Habit logged:', data.data)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        // Reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, 3000)
      }
    }

    connect()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [user])

  const sendMessage = (message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }

  return (
    <WebSocketContext.Provider value={{ events, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  )
}

