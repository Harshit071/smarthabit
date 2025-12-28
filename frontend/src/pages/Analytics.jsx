import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../services/api'
import './Analytics.css'

function Analytics() {
  const [selectedHabit, setSelectedHabit] = useState(null)

  const { data: habits } = useQuery({
    queryKey: ['habits'],
    queryFn: async () => {
      const response = await api.get('/api/habits')
      return response.data
    },
  })

  const { data: weeklyStats } = useQuery({
    queryKey: ['weekly-stats', selectedHabit],
    queryFn: async () => {
      if (!selectedHabit) return null
      const response = await api.get(`/api/analytics/habits/${selectedHabit}/weekly`)
      return response.data
    },
    enabled: !!selectedHabit,
  })

  const { data: monthlyStats } = useQuery({
    queryKey: ['monthly-stats', selectedHabit],
    queryFn: async () => {
      if (!selectedHabit) return null
      const response = await api.get(`/api/analytics/habits/${selectedHabit}/monthly`)
      return response.data
    },
    enabled: !!selectedHabit,
  })

  const { data: trend } = useQuery({
    queryKey: ['consistency-trend', selectedHabit],
    queryFn: async () => {
      if (!selectedHabit) return null
      const response = await api.get(`/api/analytics/habits/${selectedHabit}/consistency-trend?days=30`)
      return response.data
    },
    enabled: !!selectedHabit,
  })

  if (!habits || habits.length === 0) {
    return (
      <div className="analytics">
        <h1>Analytics</h1>
        <p>No habits available. Create a habit to see analytics.</p>
      </div>
    )
  }

  if (!selectedHabit && habits.length > 0) {
    setSelectedHabit(habits[0].id)
  }

  const weeklyChartData = weeklyStats ? [
    { name: 'Done', value: weeklyStats.stats.done },
    { name: 'Skipped', value: weeklyStats.stats.skipped },
    { name: 'Missed', value: weeklyStats.stats.missed },
  ] : []

  const monthlyChartData = monthlyStats ? [
    { name: 'Done', value: monthlyStats.stats.done },
    { name: 'Skipped', value: monthlyStats.stats.skipped },
    { name: 'Missed', value: monthlyStats.stats.missed },
  ] : []

  return (
    <div className="analytics">
      <h1>Analytics</h1>
      
      <div className="habit-selector">
        <label>Select Habit:</label>
        <select
          value={selectedHabit || ''}
          onChange={(e) => setSelectedHabit(parseInt(e.target.value))}
        >
          {habits.map(habit => (
            <option key={habit.id} value={habit.id}>{habit.name}</option>
          ))}
        </select>
      </div>

      {selectedHabit && (
        <>
          <div className="chart-section">
            <h2>Weekly Statistics</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weeklyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#3498db" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-section">
            <h2>Monthly Statistics</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#27ae60" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {trend && trend.trend && (
            <div className="chart-section">
              <h2>Consistency Trend (Last 30 Days)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trend.trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="completions" stroke="#667eea" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Analytics

