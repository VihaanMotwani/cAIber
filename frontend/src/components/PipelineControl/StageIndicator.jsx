import React from 'react'
import { CheckCircle, Circle, Loader } from 'lucide-react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

const StageIndicator = ({ stage, title, description, status, isActive, icon: Icon }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-cyber-green" />
      case 'running':
        return <Loader className="w-6 h-6 text-cyber-yellow animate-spin" />
      default:
        return <Circle className="w-6 h-6 text-gray-500" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'border-cyber-green shadow-cyber-green/50'
      case 'running':
        return 'border-cyber-yellow shadow-cyber-yellow/50 animate-pulse'
      case 'error':
        return 'border-cyber-red shadow-cyber-red/50'
      default:
        return 'border-gray-600'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: stage * 0.1 }}
      className={clsx(
        "relative bg-cyber-light/30 backdrop-blur-md rounded-lg p-6 border-2 transition-all duration-300",
        getStatusColor(),
        isActive && "shadow-lg scale-105"
      )}
    >
      {/* Stage Number */}
      <div className="absolute -top-3 -right-3 w-8 h-8 bg-cyber-dark rounded-full border-2 border-cyber-cyan flex items-center justify-center">
        <span className="font-mono font-bold text-sm">{stage}</span>
      </div>

      {/* Content */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          {Icon && <Icon className="w-8 h-8 text-cyber-cyan" />}
          {getStatusIcon()}
        </div>
        
        <div>
          <h3 className="font-orbitron font-bold text-lg text-white">
            {title}
          </h3>
          <p className="text-sm text-gray-400 mt-1 font-mono">
            {description}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ 
              width: status === 'completed' ? '100%' : status === 'running' ? '60%' : '0%' 
            }}
            transition={{ duration: 0.5 }}
            className={clsx(
              "h-full rounded-full",
              status === 'completed' && "bg-cyber-green",
              status === 'running' && "bg-cyber-yellow",
              status === 'error' && "bg-cyber-red",
              status === 'pending' && "bg-gray-600"
            )}
          />
        </div>

        {/* Status Text */}
        <div className="text-xs font-mono text-gray-500">
          {status === 'running' && 'Processing...'}
          {status === 'completed' && 'Complete'}
          {status === 'pending' && 'Waiting'}
          {status === 'error' && 'Failed'}
        </div>
      </div>

      {/* Active Indicator */}
      {isActive && (
        <div className="absolute inset-0 rounded-lg pointer-events-none">
          <div className="absolute inset-0 rounded-lg bg-cyber-cyan/10 animate-pulse" />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="w-32 h-32 rounded-full bg-cyber-cyan/20 animate-ping" />
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default StageIndicator