import React from 'react'
import './XPDisplay.css'

function XPDisplay({ xp, level, xpToNext }) {
  const xpForCurrentLevel = level * 100
  const xpForNextLevel = (level + 1) * 100
  const progress = ((xp - xpForCurrentLevel) / (xpForNextLevel - xpForCurrentLevel)) * 100

  return (
    <div className="xp-display">
      <div className="xp-header">
        <div className="level-badge">
          <span className="level-label">Level</span>
          <span className="level-number">{level}</span>
        </div>
        <div className="xp-info">
          <span className="xp-amount">{xp} XP</span>
          <span className="xp-to-next">{xpToNext} XP to next level</span>
        </div>
      </div>
      <div className="xp-progress-bar">
        <div 
          className="xp-progress-fill" 
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>
    </div>
  )
}

export default XPDisplay

