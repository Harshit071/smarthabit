import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Layout.css'

function Layout({ children }) {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-brand">Smart Habit Tracker</div>
        <div className="nav-links">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
            Dashboard
          </Link>
          <Link to="/habits" className={location.pathname === '/habits' ? 'active' : ''}>
            Habits
          </Link>
          <Link to="/goals" className={location.pathname === '/goals' ? 'active' : ''}>
            Goals
          </Link>
          <Link to="/analytics" className={location.pathname === '/analytics' ? 'active' : ''}>
            Analytics
          </Link>
        </div>
        <div className="nav-user">
          <span>{user?.full_name || user?.email}</span>
          <button onClick={logout} className="logout-btn">Logout</button>
        </div>
      </nav>
      <main className="main-content">{children}</main>
    </div>
  )
}

export default Layout

