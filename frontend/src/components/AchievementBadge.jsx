import React from 'react'
import './AchievementBadge.css'

function AchievementBadge({ achievement, unlocked = false }) {
  return (
    <div className={`achievement-badge ${unlocked ? 'unlocked' : 'locked'}`}>
      <div className="achievement-icon">{achievement.icon || '🏆'}</div>
      <div className="achievement-info">
        <div className="achievement-name">{achievement.name}</div>
        <div className="achievement-description">{achievement.description}</div>
        {unlocked && achievement.xp_reward && (
          <div className="achievement-xp">+{achievement.xp_reward} XP</div>
        )}
      </div>
      {unlocked && <div className="unlocked-check">✓</div>}
    </div>
  )
}

export default AchievementBadge

