import React, { useState } from 'react'
import { Play, RotateCcw, Settings, Zap } from 'lucide-react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

const PipelineControl = ({ onRunAnalysis, isRunning, isCompleted }) => {
  const [showOptions, setShowOptions] = useState(false)
  const [config, setConfig] = useState({
    skipStage1: false,
    autonomousMode: true,
    fastMode: false
  })

  const handleRun = () => {
    onRunAnalysis(config)
    setShowOptions(false)
  }

  return (
    <div className="bg-cyber-light/20 backdrop-blur-md rounded-xl p-8 border border-cyber-cyan/30">
      <div className="flex flex-col items-center space-y-6">
        <h2 className="text-3xl font-orbitron font-bold text-cyber-cyan">
          Pipeline Control Center
        </h2>
        
        <div className="flex flex-col items-center space-y-4">
          {/* Main Control Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRun}
            disabled={isRunning}
            className={clsx(
              "relative px-12 py-6 rounded-lg font-orbitron font-bold text-xl transition-all duration-300",
              "transform hover:shadow-2xl",
              isRunning 
                ? "bg-gray-700 cursor-not-allowed opacity-50"
                : "bg-gradient-to-r from-cyber-cyan via-cyber-blue to-cyber-purple hover:shadow-cyber-cyan/50",
              "before:absolute before:inset-0 before:rounded-lg before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent",
              "before:transform before:-skew-x-12 before:animate-scan"
            )}
          >
            <span className="relative z-10 flex items-center gap-3">
              {isRunning ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-white"></div>
                  ANALYZING...
                </>
              ) : (
                <>
                  <Zap className="w-6 h-6" />
                  INITIATE THREAT ANALYSIS
                </>
              )}
            </span>
          </motion.button>

          {/* Configuration Toggle */}
          <button
            onClick={() => setShowOptions(!showOptions)}
            className="flex items-center gap-2 px-4 py-2 text-sm font-mono text-gray-400 hover:text-cyber-cyan transition-colors"
          >
            <Settings className="w-4 h-4" />
            Advanced Options
          </button>
        </div>

        {/* Advanced Options */}
        {showOptions && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="w-full max-w-md space-y-3 pt-4 border-t border-cyber-cyan/20"
          >
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={config.skipStage1}
                onChange={(e) => setConfig({ ...config, skipStage1: e.target.checked })}
                className="w-4 h-4 rounded border-cyber-cyan bg-cyber-dark text-cyber-cyan focus:ring-cyber-cyan"
              />
              <span className="font-mono text-sm">Skip DNA Building (Use Cached)</span>
            </label>
            
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={config.autonomousMode}
                onChange={(e) => setConfig({ ...config, autonomousMode: e.target.checked })}
                className="w-4 h-4 rounded border-cyber-cyan bg-cyber-dark text-cyber-cyan focus:ring-cyber-cyan"
              />
              <span className="font-mono text-sm">Autonomous Correlation Agent</span>
            </label>
            
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={config.fastMode}
                onChange={(e) => setConfig({ ...config, fastMode: e.target.checked })}
                className="w-4 h-4 rounded border-cyber-cyan bg-cyber-dark text-cyber-cyan focus:ring-cyber-cyan"
              />
              <span className="font-mono text-sm">Fast Mode (Limited Sources)</span>
            </label>
          </motion.div>
        )}

        {/* Status Indicators */}
        <div className="flex gap-8 pt-4">
          <div className="text-center">
            <div className="text-2xl font-bold font-mono text-cyber-green">4</div>
            <div className="text-xs text-gray-400">STAGES</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold font-mono text-cyber-yellow">3</div>
            <div className="text-xs text-gray-400">SOURCES</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold font-mono text-cyber-purple">AI</div>
            <div className="text-xs text-gray-400">POWERED</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PipelineControl