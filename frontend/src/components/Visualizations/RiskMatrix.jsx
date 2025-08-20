import React from 'react'
import { motion } from 'framer-motion'

const RiskMatrix = ({ assessments }) => {
  const riskLevels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
  const impactLevels = ['Low', 'Medium', 'High', 'Critical']
  const likelihoodLevels = ['Rare', 'Unlikely', 'Possible', 'Likely', 'Certain']

  // Count risks by level
  const riskCounts = riskLevels.reduce((acc, level) => {
    acc[level] = assessments.filter(a => a.risk_level === level).length
    return acc
  }, {})

  // Create matrix data
  const matrixData = []
  for (let i = 4; i >= 0; i--) {
    for (let j = 0; j < 5; j++) {
      const risk = calculateRiskLevel(j, i)
      const count = assessments.filter(a => {
        // Mock calculation for demo
        return a.risk_level === risk
      }).length
      matrixData.push({ x: j, y: i, risk, count })
    }
  }

  function calculateRiskLevel(likelihood, impact) {
    const score = (likelihood + 1) * (impact + 1)
    if (score >= 16) return 'CRITICAL'
    if (score >= 10) return 'HIGH'
    if (score >= 5) return 'MEDIUM'
    return 'LOW'
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'CRITICAL': return 'bg-red-500/40 border-red-500'
      case 'HIGH': return 'bg-orange-500/40 border-orange-500'
      case 'MEDIUM': return 'bg-yellow-500/40 border-yellow-500'
      case 'LOW': return 'bg-green-500/40 border-green-500'
      default: return 'bg-gray-700/40 border-gray-600'
    }
  }

  return (
    <div className="bg-cyber-dark/50 rounded-lg p-6">
      <h3 className="text-lg font-orbitron text-cyber-cyan mb-4">Risk Matrix</h3>
      
      <div className="grid grid-cols-6 gap-1">
        {/* Y-axis labels */}
        <div className="col-span-1 flex flex-col justify-between py-2">
          <div className="text-xs text-gray-500 -rotate-90 origin-center">Impact</div>
          {impactLevels.reverse().map((level, idx) => (
            <div key={idx} className="text-xs text-gray-400 text-right pr-2 h-12 flex items-center justify-end">
              {level}
            </div>
          ))}
        </div>

        {/* Matrix Grid */}
        <div className="col-span-5">
          <div className="grid grid-cols-5 gap-1">
            {matrixData.map((cell, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.01 }}
                className={`h-12 rounded border ${getRiskColor(cell.risk)} flex items-center justify-center relative group cursor-pointer`}
              >
                {cell.count > 0 && (
                  <span className="text-white font-bold">{cell.count}</span>
                )}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                  {cell.risk} Risk
                </div>
              </motion.div>
            ))}
          </div>
          
          {/* X-axis labels */}
          <div className="grid grid-cols-5 gap-1 mt-2">
            {likelihoodLevels.map((level, idx) => (
              <div key={idx} className="text-xs text-gray-400 text-center">
                {level}
              </div>
            ))}
          </div>
          <div className="text-xs text-gray-500 text-center mt-1">Likelihood</div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-4 mt-6 pt-4 border-t border-gray-700">
        {riskLevels.map(level => (
          <div key={level} className="flex items-center gap-2">
            <div className={`w-4 h-4 rounded ${getRiskColor(level)}`} />
            <span className="text-xs text-gray-400">{level} ({riskCounts[level]})</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default RiskMatrix