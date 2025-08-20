import React from 'react'
import { motion } from 'framer-motion'
import { ArrowDown, Target, Shield, Lock, AlertTriangle, Eye, Trash2 } from 'lucide-react'

const AttackPathViewer = ({ attackPath }) => {
  const getStrideIcon = (classification) => {
    switch (classification) {
      case 'Spoofing': return Shield
      case 'Tampering': return Lock
      case 'Repudiation': return Eye
      case 'Information Disclosure': return AlertTriangle
      case 'Denial of Service': return Trash2
      case 'Elevation of Privilege': return Target
      default: return Shield
    }
  }

  const getStrideColor = (classification) => {
    switch (classification) {
      case 'Spoofing': return 'text-cyber-blue border-cyber-blue'
      case 'Tampering': return 'text-cyber-purple border-cyber-purple'
      case 'Repudiation': return 'text-cyber-cyan border-cyber-cyan'
      case 'Information Disclosure': return 'text-cyber-yellow border-cyber-yellow'
      case 'Denial of Service': return 'text-cyber-red border-cyber-red'
      case 'Elevation of Privilege': return 'text-cyber-green border-cyber-green'
      default: return 'text-gray-400 border-gray-400'
    }
  }

  return (
    <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg p-8 border border-cyber-red/30">
      <h2 className="text-2xl font-orbitron text-cyber-red mb-2">Attack Path Analysis</h2>
      <p className="text-gray-400 mb-8">{attackPath.path_description}</p>

      <div className="relative">
        {/* Attack Path Steps */}
        {attackPath.steps.map((step, idx) => {
          const StrideIcon = getStrideIcon(step.stride_classification)
          const strideColor = getStrideColor(step.stride_classification)
          
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.2 }}
              className="relative"
            >
              {/* Connector Line */}
              {idx > 0 && (
                <div className="absolute -top-8 left-12 w-0.5 h-8 bg-gradient-to-b from-cyber-red/50 to-cyber-red" />
              )}

              {/* Step Card */}
              <div className="flex gap-6 mb-8">
                {/* Step Number */}
                <div className="flex-shrink-0">
                  <div className="w-24 h-24 rounded-full bg-cyber-dark border-2 border-cyber-red flex items-center justify-center relative">
                    <span className="text-3xl font-orbitron font-bold text-cyber-red">
                      {step.step}
                    </span>
                    {idx < attackPath.steps.length - 1 && (
                      <ArrowDown className="absolute -bottom-10 left-1/2 transform -translate-x-1/2 w-6 h-6 text-cyber-red" />
                    )}
                  </div>
                </div>

                {/* Step Details */}
                <div className="flex-1 bg-cyber-dark/50 rounded-lg p-6 border border-gray-700">
                  <div className="mb-4">
                    <h3 className="text-lg font-bold text-white mb-2">
                      {step.action}
                    </h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* MITRE ATT&CK */}
                    <div className="bg-cyber-light/30 rounded-lg p-4 border border-cyber-cyan/30">
                      <div className="text-xs text-cyber-cyan font-mono mb-1">MITRE ATT&CK</div>
                      <div className="font-mono text-sm text-white">
                        {step.mitre_attack}
                      </div>
                    </div>

                    {/* STRIDE */}
                    <div className="bg-cyber-light/30 rounded-lg p-4 border border-cyber-purple/30">
                      <div className="text-xs text-cyber-purple font-mono mb-1">STRIDE</div>
                      <div className="flex items-center gap-2">
                        <StrideIcon className={`w-5 h-5 ${strideColor}`} />
                        <span className="font-mono text-sm text-white">
                          {step.stride_classification}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Justification */}
                  <div className="mt-4 p-3 bg-gray-800/50 rounded border border-gray-700">
                    <p className="text-xs text-gray-400 italic">
                      {step.justification}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}

        {/* Final Impact */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: attackPath.steps.length * 0.2 }}
          className="mt-8 p-6 bg-gradient-to-r from-cyber-red/20 to-cyber-purple/20 rounded-lg border border-cyber-red/50"
        >
          <div className="flex items-center justify-center gap-4">
            <Target className="w-8 h-8 text-cyber-red" />
            <div className="text-center">
              <p className="text-xl font-orbitron text-white">IMPACT ACHIEVED</p>
              <p className="text-sm text-gray-400 mt-1">
                Attacker successfully compromises target system
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default AttackPathViewer