import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../services/api'
import './LinkHabitsModal.css'

const LinkHabitsModal = ({ show, onClose, goal }) => {
  const queryClient = useQueryClient()
  const [selectedHabits, setSelectedHabits] = useState([])

  // Fetch all available habits
  const { data: allHabits, isLoading: isLoadingHabits } = useQuery({
    queryKey: ['allHabits'],
    queryFn: async () => {
      const response = await api.get('/api/habits')
      return response.data
    },
    enabled: show, // Only fetch when modal is open
  })

  // Mutation to update goal with linked habits
  const linkHabitsMutation = useMutation({
    mutationFn: async (updatedGoal) => {
      const response = await api.put(`/api/goals/${updatedGoal.id}`, updatedGoal)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['goals'])
      onClose()
    },
  })

  useEffect(() => {
    if (show && goal) {
      // Initialize selected habits based on goal.linked_habits (if any)
      // Assuming goal object will have a linked_habit_ids array or similar
      setSelectedHabits(goal.linked_habits?.map(h => h.id) || [])
    }
  }, [show, goal])

  const handleCheckboxChange = (habitId) => {
    setSelectedHabits(prevSelected =>
      prevSelected.includes(habitId)
        ? prevSelected.filter(id => id !== habitId)
        : [...prevSelected, habitId]
    )
  }

  const handleSave = () => {
    // Assuming your backend expects a list of habit_ids to link
    linkHabitsMutation.mutate({
      ...goal,
      linked_habit_ids: selectedHabits,
    })
  }

  if (!show) return null

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Link Habits to "{goal?.name}"</h2>
        {isLoadingHabits ? (
          <div>Loading habits...</div>
        ) : (
          <div className="habit-list">
            {allHabits?.map(habit => (
              <label key={habit.id} className="checkbox-item">
                <input
                  type="checkbox"
                  checked={selectedHabits.includes(habit.id)}
                  onChange={() => handleCheckboxChange(habit.id)}
                />
                {habit.name}
              </label>
            ))}
          </div>
        )}
        <div className="modal-actions">
          <button onClick={handleSave} className="btn-primary" disabled={linkHabitsMutation.isLoading}>
            {linkHabitsMutation.isLoading ? 'Saving...' : 'Save Changes'}
          </button>
          <button onClick={onClose} className="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  )
}

export default LinkHabitsModal

