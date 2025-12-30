import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import LinkHabitsModal from '../components/LinkHabitsModal' // Import the new modal component
import './Goals.css'

function Goals() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [showLinkHabitsModal, setShowLinkHabitsModal] = useState(false) // State for modal visibility
  const [selectedGoalForLinking, setSelectedGoalForLinking] = useState(null) // State to pass goal to modal

  const { data: goals, isLoading } = useQuery({
    queryKey: ['goals'],
    queryFn: async () => {
      const response = await api.get('/api/goals')
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/api/goals', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['goals'])
      setShowForm(false)
      setFormData({ name: '', description: '', target_value: '', unit: '' })
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate({
      ...formData,
      target_value: parseFloat(formData.target_value)
    })
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="goals">
      <div className="goals-header">
        <h1>My Goals</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? 'Cancel' : '+ New Goal'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="goal-form">
          <input
            type="text"
            placeholder="Goal name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
          <textarea
            placeholder="Description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <div className="form-row">
            <input
              type="number"
              placeholder="Target value"
              value={formData.target_value}
              onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Unit (e.g., days, times)"
              value={formData.unit}
              onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
            />
          </div>
          <button type="submit" className="btn-primary">Create Goal</button>
        </form>
      )}

      <div className="goals-grid">
        {goals?.map(goal => {
          const progress = (goal.current_value / goal.target_value) * 100
          return (
            <div key={goal.id} className={`goal-card ${goal.is_completed ? 'completed' : ''}`}>
              <div className="goal-header">
                <h3>{goal.name}</h3>
                <button className="btn-secondary btn-edit-goal" onClick={() => {
                  setSelectedGoalForLinking(goal)
                  setShowLinkHabitsModal(true)
                }}>
                  Edit
                </button>
                {goal.is_completed && <span className="completed-badge">✓ Completed</span>}
              </div>
              <p className="goal-description">{goal.description}</p>
              <div className="goal-progress">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${Math.min(100, progress)}%` }}
                  />
                </div>
                <div className="progress-text">
                  {goal.current_value.toFixed(1)} / {goal.target_value} {goal.unit || ''}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {selectedGoalForLinking && (
        <LinkHabitsModal
          show={showLinkHabitsModal}
          onClose={() => setShowLinkHabitsModal(false)}
          goal={selectedGoalForLinking}
        />
      )}
    </div>
  )
}

export default Goals

