import React, { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useWebSocket } from '../contexts/WebSocketContext'
import XPDisplay from '../components/XPDisplay'
import AchievementBadge from '../components/AchievementBadge'
import Confetti from '../components/Confetti'
import api from '../services/api'
import './Dashboard.css'

function Dashboard() {
  const { events } = useWebSocket()
  const [notifications, setNotifications] = useState([])
  const [showConfetti, setShowConfetti] = useState(false)
  const [levelUp, setLevelUp] = useState(false)

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await api.get('/api/analytics/dashboard')
      return response.data
    },
  })

  const { data: gamificationStats, isLoading: gamificationLoading } = useQuery({
    queryKey: ['gamification-stats'],
    queryFn: async () => {
      const response = await api.get('/api/gamification/stats')
      return response.data
    },
  })

  useEffect(() => {
    // Process WebSocket events for notifications
    const latestEvents = events.slice(-5)
    const newNotifications = latestEvents.filter(e => 
      e.type === 'habit_at_risk' || e.type === 'nudge' || e.type === 'goal_completed' || e.type === 'habit_logged'
    )
    
    // Check for level up or achievements
    latestEvents.forEach(event => {
      if (event.type === 'habit_logged' && event.data) {
        if (event.data.leveled_up) {
          setLevelUp(true)
          setShowConfetti(true)
          setTimeout(() => setLevelUp(false), 5000)
        }
        if (event.data.achievements_unlocked && event.data.achievements_unlocked.length > 0) {
          setShowConfetti(true)
        }
      }
    })
    
    setNotifications(newNotifications)
  }, [events])

  if (statsLoading || gamificationLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <Confetti trigger={showConfetti} />
      
      {levelUp && (
        <div className="level-up-popup">
          <div className="level-up-content">
            <h2>🎉 Level Up! 🎉</h2>
            <p>You've reached Level {gamificationStats?.level || 1}!</p>
          </div>
        </div>
      )}

      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p className="dashboard-subtitle">Track your progress and achievements</p>
      </div>

      {/* XP and Level Display */}
      {gamificationStats && (
        <XPDisplay
          xp={gamificationStats.total_xp || 0}
          level={gamificationStats.level || 1}
          xpToNext={gamificationStats.xp_to_next_level || 100}
        />
      )}

      {/* Notifications */}
      {notifications.length > 0 && (
        <div className="notifications-section">
          <h2>Recent Activity</h2>
          {notifications.map((event, idx) => (
            <div key={idx} className={`notification ${event.type}`}>
              <strong>{event.type.replace('_', ' ').toUpperCase()}</strong>
              <p>{JSON.stringify(event.data)}</p>
            </div>
          ))}
        </div>
      )}

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <h3>Total Habits</h3>
          <p className="stat-value">{stats?.total_habits || 0}</p>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <h3>Active Habits</h3>
          <p className="stat-value">{stats?.active_habits || 0}</p>
        </div>
        <div className="stat-card warning">
          <div className="stat-icon">⚠️</div>
          <h3>At Risk</h3>
          <p className="stat-value">{stats?.at_risk_habits || 0}</p>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔥</div>
          <h3>Total Streak</h3>
          <p className="stat-value">{stats?.total_streak || 0} days</p>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <h3>Consistency</h3>
          <p className="stat-value">{stats?.average_consistency?.toFixed(1) || 0}%</p>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <h3>Today's Completions</h3>
          <p className="stat-value">{stats?.today_completions || 0}</p>
        </div>
      </div>

      {/* Achievements Section */}
      {gamificationStats && gamificationStats.achievements && gamificationStats.achievements.length > 0 && (
        <div className="achievements-section">
          <h2>Your Achievements</h2>
          <div className="achievements-grid">
            {gamificationStats.achievements.map((achievement) => (
              <AchievementBadge
                key={achievement.id}
                achievement={achievement}
                unlocked={true}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
