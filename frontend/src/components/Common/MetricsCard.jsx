import React from 'react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

const MetricsCard = ({ title, value, icon: Icon, color = 'cyan', subtext, pulse = false }) => {
  const colorClasses = {
    cyan: 'border-cyber-cyan text-cyber-cyan shadow-cyber-cyan/30',
    purple: 'border-cyber-purple text-cyber-purple shadow-cyber-purple/30',
    green: 'border-cyber-green text-cyber-green shadow-cyber-green/30',
    red: 'border-cyber-red text-cyber-red shadow-cyber-red/30',
    yellow: 'border-cyber-yellow text-cyber-yellow shadow-cyber-yellow/30',
    blue: 'border-cyber-blue text-cyber-blue shadow-cyber-blue/30',
  }

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className={clsx(
        "relative bg-cyber-light/30 backdrop-blur-md rounded-lg p-6 border-2 shadow-lg transition-all duration-300",
        colorClasses[color],
        pulse && "animate-pulse"
      )}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-gradient-to-br from-transparent via-current to-transparent" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className="p-2 bg-current/10 rounded-lg">
            {Icon && <Icon className="w-6 h-6" />}
          </div>
        </div>
        
        <div>
          <p className="text-xs font-mono text-gray-400 uppercase tracking-wider">
            {title}
          </p>
          <p className="text-3xl font-orbitron font-bold mt-1">
            {value}
          </p>
          {subtext && (
            <p className="text-xs font-mono text-gray-500 mt-2">
              {subtext}
            </p>
          )}
        </div>
      </div>

      {/* Corner Accent */}
      <div className="absolute top-0 right-0 w-12 h-12">
        <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-br from-current/20 to-transparent transform rotate-45 origin-top-right" />
      </div>
    </motion.div>
  )
}

export default MetricsCard