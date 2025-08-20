import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePipelineStore } from '../store/pipelineStore'
import { Activity, Shield, AlertTriangle, Database, Zap, Clock, Play, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

const Dashboard = () => {
  const navigate = useNavigate()
  const { 
    status, 
    currentStage, 
    stageProgress, 
    results,
    runFullPipeline,
    resetPipeline,
    startTime,
    endTime
  } = usePipelineStore()

  const [elapsedTime, setElapsedTime] = useState(0)
  const [skipStage1, setSkipStage1] = useState(false)

  useEffect(() => {
    let interval
    if (status === 'running' && startTime) {
      interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000))
      }, 1000)
    } else if (status === 'completed' && startTime && endTime) {
      setElapsedTime(Math.floor((endTime - startTime) / 1000))
    }
    return () => clearInterval(interval)
  }, [status, startTime, endTime])

  const handleRunAnalysis = () => {
    resetPipeline()
    runFullPipeline()
  }

  const threatCount = results?.threatLandscape?.total_items || 0
  const criticalRisks = results?.riskAssessments?.filter(r => r.risk_level === 'CRITICAL')?.length || 0
  const vulnerabilities = results?.threatLandscape?.vulnerabilities?.length || 0

  const stages = [
    { id: 1, title: 'Organizational DNA', description: 'Extract PIRs from knowledge graph', icon: Database },
    { id: 2, title: 'Threat Collection', description: 'Gather intel from OTX, CVE, GitHub', icon: AlertTriangle },
    { id: 3, title: 'Risk Correlation', description: 'Map threats to business context', icon: Shield },
    { id: 4, title: 'Threat Modeling', description: 'Generate attack paths & MITRE mapping', icon: Zap }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-semibold text-gradient mb-2">
          Threat Intelligence Dashboard
        </h1>
        <p className="text-slate-400">
          Comprehensive threat analysis and risk assessment platform
        </p>
      </motion.div>

      {/* Metrics Cards */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-6"
      >
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Status</p>
              <p className="text-2xl font-semibold mt-1">
                {status === 'running' ? 'Running' : status === 'completed' ? 'Complete' : 'Ready'}
              </p>
            </div>
            <Activity className={`w-8 h-8 ${status === 'running' ? 'text-amber-500' : status === 'completed' ? 'text-teal-500' : 'text-primary-500'}`} />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Threats Detected</p>
              <p className="text-2xl font-semibold mt-1">{threatCount}</p>
              <p className="text-xs text-slate-400 mt-1">{vulnerabilities} CVEs</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Critical Risks</p>
              <p className="text-2xl font-semibold mt-1">{criticalRisks}</p>
              <p className="text-xs text-slate-400 mt-1">Require immediate attention</p>
            </div>
            <Shield className="w-8 h-8 text-purple-500" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Analysis Time</p>
              <p className="text-2xl font-semibold mt-1">{elapsedTime}s</p>
              <p className="text-xs text-slate-400 mt-1">{status === 'running' ? 'In progress...' : 'Last run'}</p>
            </div>
            <Clock className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </motion.div>

      {/* Pipeline Control */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card p-8"
      >
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold mb-4">Pipeline Control Center</h2>
          
          <div className="flex justify-center">
            <button
              onClick={handleRunAnalysis}
              disabled={status === 'running'}
              className="btn-primary flex items-center gap-3 text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-5 h-5" />
              {status === 'running' ? 'Analysis Running...' : 'Initiate Threat Analysis'}
            </button>
          </div>

          <div className="mt-6">
            <label className="flex items-center justify-center gap-2 text-sm text-slate-400">
              <input
                type="checkbox"
                checked={skipStage1}
                onChange={(e) => setSkipStage1(e.target.checked)}
                className="rounded border-slate-600 bg-slate-800 text-primary-600 focus:ring-primary-500"
              />
              Skip DNA Building (Use Cached Data)
            </label>
          </div>
        </div>

        {/* Stage Progress */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {stages.map((stage, idx) => {
            const stageStatus = stageProgress[`stage${stage.id}`]?.status || 'pending'
            const isActive = currentStage === `stage${stage.id}`
            
            return (
              <div key={stage.id} className={`relative p-4 rounded-lg border transition-all ${
                stageStatus === 'completed' ? 'bg-teal-900/20 border-teal-700/50' :
                isActive ? 'bg-primary-900/20 border-primary-600/50' :
                'bg-slate-800/50 border-slate-700'
              }`}>
                <div className="flex items-center gap-3 mb-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                    stageStatus === 'completed' ? 'bg-teal-600 text-white' :
                    isActive ? 'bg-primary-600 text-white' :
                    'bg-slate-700 text-slate-400'
                  }`}>
                    {stage.id}
                  </div>
                  <stage.icon className={`w-5 h-5 ${
                    stageStatus === 'completed' ? 'text-teal-400' :
                    isActive ? 'text-primary-400' :
                    'text-slate-500'
                  }`} />
                </div>
                <h3 className="font-medium mb-1">{stage.title}</h3>
                <p className="text-xs text-slate-400">{stage.description}</p>
                
                {isActive && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary-500 rounded-full animate-pulse" />
                )}
              </div>
            )
          })}
        </div>
      </motion.div>

      {/* Quick Actions */}
      {status === 'completed' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="flex justify-center gap-4"
        >
          <button
            onClick={() => navigate('/analysis')}
            className="btn-primary flex items-center gap-2"
          >
            View Analysis Results
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate('/threat-modeling')}
            className="btn-secondary flex items-center gap-2"
          >
            Explore Attack Paths
            <ArrowRight className="w-4 h-4" />
          </button>
        </motion.div>
      )}

      {/* Status Message */}
      {status === 'running' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card p-6 border-amber-700/50 bg-amber-900/20"
        >
          <div className="flex items-center space-x-4">
            <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-amber-400"></div>
            <div>
              <p className="font-medium text-amber-300">
                Analysis in progress... Processing {currentStage?.replace('stage', 'Stage ')}
              </p>
              <p className="text-sm text-amber-400/70 mt-1">
                Estimated completion time: 60-120 seconds
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default Dashboard