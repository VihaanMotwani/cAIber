import React, { useState } from 'react'
import { usePipelineStore } from '../store/pipelineStore'
import { motion } from 'framer-motion'
import { Target, AlertTriangle, ChevronRight, Layers, Lock } from 'lucide-react'
import AttackPathViewer from '../components/Visualizations/AttackPathViewer'

const ThreatModeling = () => {
  const { results } = usePipelineStore()
  const [selectedPath, setSelectedPath] = useState(0)

  if (!results?.threatModel?.attack_paths) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Target className="w-16 h-16 mx-auto text-gray-500 mb-4" />
          <h2 className="text-2xl font-bold text-gray-400">No Threat Model Available</h2>
          <p className="text-gray-500 mt-2 font-mono">Complete a full pipeline analysis to generate threat models</p>
        </div>
      </div>
    )
  }

  const attackPaths = results.threatModel.attack_paths

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="heading-xl mb-3">
          Threat Modeling & Attack Paths
        </h1>
        <p className="text-slate-400 text-lg font-medium">
          MITRE ATT&CK and STRIDE analysis of potential attack vectors
        </p>
      </motion.div>

      {/* Attack Path Selector */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="card p-6"
      >
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5" />
          Attack Scenarios ({attackPaths.length})
        </h2>
        
        <div className="space-y-2">
          {attackPaths.map((path, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedPath(idx)}
              className={`w-full text-left p-4 rounded-lg border transition-all duration-200 ${
                selectedPath === idx 
                  ? 'bg-red-400/20 border-red-400 shadow-lg shadow-red-400/30' 
                  : 'bg-slate-800/30 border-gray-700 hover:border-red-400/50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-mono text-sm text-yellow-400">Scenario #{idx + 1}</p>
                  <p className="text-gray-300 mt-1">{path.path_description}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {path.steps.length} steps • {path.steps.filter(s => s.stride_classification === 'Elevation of Privilege').length} privilege escalations
                  </p>
                </div>
                <ChevronRight className={`w-5 h-5 transition-transform ${
                  selectedPath === idx ? 'rotate-90 text-red-400' : 'text-gray-500'
                }`} />
              </div>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Selected Attack Path Visualization */}
      {selectedPath !== null && attackPaths[selectedPath] && (
        <motion.div
          key={selectedPath}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <AttackPathViewer attackPath={attackPaths[selectedPath]} />
        </motion.div>
      )}

      {/* MITRE ATT&CK Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-slate-900/30 backdrop-blur-md rounded-lg p-6 border border-purple-400/30"
      >
        <h2 className="text-xl font-bold text-purple-400 mb-4 flex items-center gap-2">
          <Lock className="w-5 h-5" />
          MITRE ATT&CK Coverage
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from(new Set(
            attackPaths.flatMap(path => 
              path.steps.map(step => step.mitre_attack.split(':')[0])
            )
          )).map((tactic, idx) => (
            <div key={idx} className="bg-slate-800/50 rounded-lg p-3 border border-purple-400/20">
              <p className="text-xs text-purple-400 font-mono uppercase tracking-wider">{tactic}</p>
              <p className="text-2xl font-bold text-white mt-1">
                {attackPaths.flatMap(path => 
                  path.steps.filter(step => step.mitre_attack.includes(tactic))
                ).length}
              </p>
              <p className="text-xs text-gray-500">techniques</p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* STRIDE Analysis */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="bg-slate-900/30 backdrop-blur-md rounded-lg p-6 border border-blue-400/30"
      >
        <h2 className="text-xl font-bold text-blue-400 mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          STRIDE Classification
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {['Spoofing', 'Tampering', 'Repudiation', 'Information Disclosure', 'Denial of Service', 'Elevation of Privilege'].map((stride) => {
            const count = attackPaths.flatMap(path => 
              path.steps.filter(step => step.stride_classification === stride)
            ).length
            
            return (
              <div key={stride} className="bg-slate-800/50 rounded-lg p-3 border border-blue-400/20">
                <p className="text-xs text-blue-400 font-mono tracking-wider">{stride}</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <p className="text-2xl font-bold text-white">{count}</p>
                  <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-400 to-blue-500"
                      style={{ width: `${Math.min(100, count * 20)}%` }}
                    />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </motion.div>
    </div>
  )
}

export default ThreatModeling