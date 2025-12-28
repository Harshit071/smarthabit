import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useWebSocket } from '../contexts/WebSocketContext'
import Confetti from '../components/Confetti'
import api from '../services/api'
import './Habits.css'

function Habits() {
  const queryClient = useQueryClient()
  const { events } = useWebSocket()
  const [showForm, setShowForm] = useState(false)
  const [showConfetti, setShowConfetti] = useState(false)
  const [xpGained, setXpGained] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    frequency: 'daily',
    difficulty: 'medium',
    priority: 'medium'
  })

  const { data: habits, isLoading } = useQuery({
    queryKey: ['habits'],
    queryFn: async () => {
      const response = await api.get('/api/habits')
      return response.data
    },
  })

  // Listen for XP gains from WebSocket
  useEffect(() => {
    events.forEach(event => {
      if (event.type === 'habit_logged' && event.data?.xp_earned) {
        setXpGained(event.data.xp_earned)
        setShowConfetti(true)
        setTimeout(() => {
          setXpGained(null)
          setShowConfetti(false)
        }, 3000)
      }
    })
  }, [events])

  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/api/habits', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['habits'])
      setShowForm(false)
      setFormData({ name: '', description: '', frequency: 'daily', difficulty: 'medium', priority: 'medium' })
    },
  })

  const logMutation = useMutation({
    mutationFn: async ({ habitId, date, status }) => {
      const response = await api.post('/api/habit-logs', {
        habit_id: habitId,
        log_date: date,
        status: status
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['habits'])
      queryClient.invalidateQueries(['dashboard-stats'])
      queryClient.invalidateQueries(['gamification-stats'])
    },
  })

  const handleLog = (habitId, status) => {
    const today = new Date().toISOString().split('T')[0]
    logMutation.mutate({ habitId, date: today, status })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const getDifficultyColor = (difficulty) => {
    switch(difficulty) {
      case 'easy': return '#27ae60'
      case 'medium': return '#f39c12'
      case 'hard': return '#e74c3c'
      default: return '#7f8c8d'
    }
  }

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'high': return '#e74c3c'
      case 'medium': return '#f39c12'
      case 'low': return '#95a5a6'
      default: return '#7f8c8d'
    }
  }

  if (isLoading) {
    return (
      <div className="habits-loading">
        <div className="loading-spinner"></div>
        <p>Loading your habits...</p>
      </div>
    )
  }

  return (
    <div className="habits">
      <Confetti trigger={showConfetti} />
      
      {xpGained && (
        <div className="xp-notification">
          <span className="xp-icon">✨</span>
          <span className="xp-text">+{xpGained} XP</span>
        </div>
      )}

      <div className="habits-header">
        <div>
          <h1>My Habits</h1>
          <p className="habits-subtitle">Build your daily routine, one habit at a time</p>
        </div>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className={`btn-primary ${showForm ? 'btn-cancel' : ''}`}
        >
          {showForm ? '✕ Cancel' : '+ New Habit'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="habit-form">
          <div className="form-group">
            <label>Habit Name</label>
            <input
              type="text"
              placeholder="e.g., DSA Practice"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Description (Optional)</label>
            <textarea
              placeholder="e.g., Solve 4-5 DSA questions daily"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows="3"
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Frequency</label>
              <select
                value={formData.frequency}
                onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>
            <div className="form-group">
              <label>Difficulty</label>
              <select
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
              >
                <option value="easy">Easy (10 XP)</option>
                <option value="medium">Medium (20 XP)</option>
                <option value="hard">Hard (30 XP)</option>
              </select>
            </div>
            <div className="form-group">
              <label>Priority</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          <button type="submit" className="btn-submit">Create Habit</button>
        </form>
      )}

      {habits && habits.length === 0 && !showForm && (
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <h2>No habits yet</h2>
          <p>Create your first habit to start tracking your progress!</p>
          <button onClick={() => setShowForm(true)} className="btn-primary">
            Create Your First Habit
          </button>
        </div>
      )}

      <div className="habits-grid">
        {habits?.map(habit => {
          const consistencyPercent = Math.min(100, habit.consistency_score || 0)
          const streakPercent = habit.current_streak > 0 ? Math.min(100, (habit.current_streak / 30) * 100) : 0
          
          return (
            <div 
              key={habit.id} 
              className={`habit-card ${habit.status === 'at_risk' ? 'at-risk' : ''} ${habit.status === 'active' ? 'active' : ''}`}
            >
              <div className="habit-card-header">
                <div className="habit-title-section">
                  <h3>{habit.name}</h3>
                  <div className="habit-badges">
                    <span 
                      className="difficulty-badge"
                      style={{ backgroundColor: getDifficultyColor(habit.difficulty) }}
                    >
                      {habit.difficulty}
                    </span>
                    <span 
                      className="priority-badge"
                      style={{ backgroundColor: getPriorityColor(habit.priority) }}
                    >
                      {habit.priority}
                    </span>
                  </div>
                </div>
                <span className={`status-badge ${habit.status}`}>
                  {habit.status === 'at_risk' ? '⚠️ At Risk' : habit.status}
                </span>
              </div>

              {habit.description && (
                <p className="habit-description">{habit.description}</p>
              )}

              <div className="habit-stats">
                <div className="stat-item">
                  <div className="stat-label">🔥 Streak</div>
                  <div className="stat-value-large">{habit.current_streak}</div>
                  <div className="progress-ring">
                    <svg width="60" height="60">
                      <circle
                        cx="30"
                        cy="30"
                        r="25"
                        fill="none"
                        stroke="#e0e0e0"
                        strokeWidth="4"
                      />
                      <circle
                        cx="30"
                        cy="30"
                        r="25"
                        fill="none"
                        stroke="#f39c12"
                        strokeWidth="4"
                        strokeDasharray={`${2 * Math.PI * 25}`}
                        strokeDashoffset={`${2 * Math.PI * 25 * (1 - streakPercent / 100)}`}
                        strokeLinecap="round"
                        transform="rotate(-90 30 30)"
                      />
                    </svg>
                  </div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">📊 Consistency</div>
                  <div className="stat-value-large">{consistencyPercent.toFixed(0)}%</div>
                  <div className="progress-bar-mini">
                    <div 
                      className="progress-fill-mini"
                      style={{ width: `${consistencyPercent}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="habit-actions">
                <button
                  onClick={() => handleLog(habit.id, 'done')}
                  className="btn-success"
                  disabled={logMutation.isLoading}
                >
                  <span className="btn-icon">✓</span>
                  Done
                </button>
                <button
                  onClick={() => handleLog(habit.id, 'skipped')}
                  className="btn-warning"
                  disabled={logMutation.isLoading}
                >
                  <span className="btn-icon">⊘</span>
                  Skip
                </button>
              </div>

              <div className="habit-footer">
                <span className="completions">✅ {habit.total_completions} completions</span>
                <span className="best-streak">🏆 Best: {habit.longest_streak} days</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default Habits
