import React, { useState } from 'react'
import { usePipelineStore } from '../store/pipelineStore'
import { motion } from 'framer-motion'
import { FileText, AlertTriangle, Shield, Target, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import ThreatLandscapeView from '../components/Visualizations/ThreatLandscapeView'
import RiskMatrix from '../components/Visualizations/RiskMatrix'

const Analysis = () => {
  const { results } = usePipelineStore()
  const [expandedSections, setExpandedSections] = useState({
    pirs: true,
    threats: true,
    risks: true,
    summary: true
  })

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  if (!results || !results.threatLandscape) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Shield className="w-16 h-16 mx-auto text-gray-500 mb-4" />
          <h2 className="text-2xl font-orbitron text-gray-400">No Analysis Results</h2>
          <p className="text-gray-500 mt-2 font-mono">Run a pipeline analysis first to see results</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-orbitron font-bold bg-gradient-to-r from-cyber-cyan to-cyber-purple bg-clip-text text-transparent">
          Threat Analysis Results
        </h1>
        <p className="text-gray-400 mt-2 font-mono">
          Comprehensive threat intelligence and risk assessment
        </p>
      </motion.div>

      {/* Executive Summary */}
      {results.executiveSummary && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-cyber-light/30 backdrop-blur-md rounded-lg border border-cyber-cyan/30"
        >
          <div 
            className="p-6 cursor-pointer flex items-center justify-between"
            onClick={() => toggleSection('summary')}
          >
            <h2 className="text-2xl font-orbitron text-cyber-cyan flex items-center gap-3">
              <Target className="w-6 h-6" />
              Executive Summary
            </h2>
            {expandedSections.summary ? <ChevronUp /> : <ChevronDown />}
          </div>
          {expandedSections.summary && (
            <div className="px-6 pb-6">
              <p className="font-mono text-gray-300 leading-relaxed">
                {results.executiveSummary}
              </p>
            </div>
          )}
        </motion.div>
      )}

      {/* PIRs Section */}
      {results.pirs && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-cyber-light/30 backdrop-blur-md rounded-lg border border-cyber-purple/30"
        >
          <div 
            className="p-6 cursor-pointer flex items-center justify-between"
            onClick={() => toggleSection('pirs')}
          >
            <h2 className="text-2xl font-orbitron text-cyber-purple flex items-center gap-3">
              <FileText className="w-6 h-6" />
              Priority Intelligence Requirements
            </h2>
            {expandedSections.pirs ? <ChevronUp /> : <ChevronDown />}
          </div>
          {expandedSections.pirs && (
            <div className="px-6 pb-6">
              <div className="bg-cyber-dark/50 rounded-lg p-4 font-mono text-sm">
                <pre className="whitespace-pre-wrap text-gray-300">
                  {typeof results.pirs === 'string' ? results.pirs : JSON.stringify(results.pirs, null, 2)}
                </pre>
              </div>
              {results.keywords && (
                <div className="mt-4">
                  <p className="text-sm text-gray-400 mb-2">Extracted Keywords:</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(results.keywords).map(([category, keywords]) => (
                      <div key={category} className="space-y-2">
                        <p className="text-xs text-cyber-cyan font-mono">{category}:</p>
                        <div className="flex flex-wrap gap-2">
                          {keywords.map((keyword, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1 bg-cyber-purple/20 border border-cyber-purple/50 rounded-full text-xs font-mono"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </motion.div>
      )}

      {/* Threat Landscape */}
      {results.threatLandscape && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <ThreatLandscapeView threatLandscape={results.threatLandscape} />
        </motion.div>
      )}

      {/* Risk Assessments */}
      {results.riskAssessments && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-cyber-light/30 backdrop-blur-md rounded-lg border border-cyber-red/30"
        >
          <div 
            className="p-6 cursor-pointer flex items-center justify-between"
            onClick={() => toggleSection('risks')}
          >
            <h2 className="text-2xl font-orbitron text-cyber-red flex items-center gap-3">
              <Shield className="w-6 h-6" />
              Risk Assessments ({results.riskAssessments.length})
            </h2>
            {expandedSections.risks ? <ChevronUp /> : <ChevronDown />}
          </div>
          {expandedSections.risks && (
            <div className="px-6 pb-6 space-y-4">
              {results.riskAssessments.length === 0 ? (
                <div className="text-center py-8">
                  <Shield className="w-16 h-16 mx-auto text-gray-500 mb-4" />
                  <h3 className="text-lg font-semibold text-gray-400">No Critical Risks Identified</h3>
                  <p className="text-gray-500 mt-2">The correlation analysis found no immediate high-risk threats to your organization.</p>
                </div>
              ) : (
                <>
                  <RiskMatrix assessments={results.riskAssessments} />
                  {results.riskAssessments.map((assessment, idx) => (
                <div 
                  key={idx}
                  className="bg-cyber-dark/50 rounded-lg p-4 border border-cyber-red/20"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-bold text-lg text-cyber-yellow">
                      {assessment.threat_actor || assessment.vulnerability || 'Unknown Threat'}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-mono ${
                      assessment.risk_level === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/50' :
                      assessment.risk_level === 'HIGH' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/50' :
                      assessment.risk_level === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50' :
                      'bg-green-500/20 text-green-400 border border-green-500/50'
                    }`}>
                      {assessment.risk_level}
                    </span>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <p className="text-gray-300">
                      <span className="text-cyber-cyan">Affected Assets:</span> {assessment.affected_assets?.join(', ') || 'N/A'}
                    </p>
                    <p className="text-gray-300">
                      <span className="text-cyber-purple">Business Impact:</span> {assessment.business_impact || 'N/A'}
                    </p>
                    <p className="text-gray-300">
                      <span className="text-cyber-green">Mitigation:</span> {assessment.mitigation_recommendation || 'N/A'}
                    </p>
                    {assessment.correlation_reasoning && (
                      <p className="text-gray-400 italic text-xs mt-2">
                        {assessment.correlation_reasoning}
                      </p>
                    )}
                  </div>
                </div>
              ))}
                </>
              )}
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}

export default Analysis