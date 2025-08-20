import React, { useState } from 'react'
import { AlertTriangle, Bug, Github, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import { motion } from 'framer-motion'

const ThreatLandscapeView = ({ threatLandscape }) => {
  const [expandedSection, setExpandedSection] = useState('vulnerabilities')
  
  const { vulnerabilities = [], indicators = [], github_advisories = [], total_items = 0 } = threatLandscape

  const sections = [
    {
      id: 'vulnerabilities',
      title: 'CVE Vulnerabilities',
      icon: Bug,
      data: vulnerabilities,
      color: 'red',
      count: vulnerabilities.length
    },
    {
      id: 'indicators',
      title: 'OTX Threat Indicators',
      icon: AlertTriangle,
      data: indicators,
      color: 'yellow',
      count: indicators.length
    },
    {
      id: 'github',
      title: 'GitHub Security Advisories',
      icon: Github,
      data: github_advisories,
      color: 'purple',
      count: github_advisories.length
    }
  ]

  return (
    <div className="space-y-4">
      <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg p-6 border border-cyber-green/30">
        <h2 className="text-2xl font-orbitron text-cyber-green mb-4 flex items-center justify-between">
          <span className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6" />
            Threat Landscape
          </span>
          <span className="text-lg font-mono">
            {total_items} Total Threats
          </span>
        </h2>

        <div className="grid grid-cols-3 gap-4 mb-6">
          {sections.map(section => (
            <motion.button
              key={section.id}
              whileHover={{ scale: 1.02 }}
              onClick={() => setExpandedSection(section.id)}
              className={`p-4 rounded-lg border transition-all duration-200 ${
                expandedSection === section.id
                  ? `bg-cyber-${section.color}/20 border-cyber-${section.color} shadow-lg`
                  : 'bg-cyber-dark/30 border-gray-700 hover:border-gray-500'
              }`}
            >
              <section.icon className={`w-8 h-8 mx-auto mb-2 text-cyber-${section.color}`} />
              <p className="font-mono text-sm">{section.title}</p>
              <p className="text-2xl font-bold mt-1">{section.count}</p>
            </motion.button>
          ))}
        </div>

        {/* Expanded Section Content */}
        {sections.map(section => (
          expandedSection === section.id && section.data.length > 0 && (
            <motion.div
              key={section.id}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar"
            >
              {section.id === 'vulnerabilities' && vulnerabilities.map((vuln, idx) => (
                <div key={idx} className="bg-cyber-dark/50 rounded-lg p-4 border border-cyber-red/20">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-mono text-cyber-red">{vuln.cve_id}</h4>
                      <p className="text-sm text-gray-300 mt-1">{vuln.description}</p>
                      <div className="flex gap-4 mt-2 text-xs text-gray-500">
                        <span>CVSS: {vuln.cvss_score || 'N/A'}</span>
                        <span>Published: {vuln.published_date}</span>
                      </div>
                    </div>
                    {vuln.reference_url && (
                      <a href={vuln.reference_url} target="_blank" rel="noopener noreferrer" 
                         className="text-cyber-cyan hover:text-cyber-blue">
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                </div>
              ))}

              {section.id === 'indicators' && indicators.map((indicator, idx) => (
                <div key={idx} className="bg-cyber-dark/50 rounded-lg p-4 border border-cyber-yellow/20">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-mono text-cyber-yellow">{indicator.type}</h4>
                      <p className="text-sm text-gray-300 mt-1">{indicator.indicator}</p>
                      <div className="flex gap-4 mt-2 text-xs text-gray-500">
                        <span>Pulse: {indicator.pulse_info?.name || 'Unknown'}</span>
                        <span>Created: {indicator.created}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {section.id === 'github' && github_advisories.map((advisory, idx) => (
                <div key={idx} className="bg-cyber-dark/50 rounded-lg p-4 border border-cyber-purple/20">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-mono text-cyber-purple">{advisory.ghsa_id}</h4>
                      <p className="text-sm text-gray-300 mt-1">{advisory.summary}</p>
                      <div className="flex gap-4 mt-2 text-xs text-gray-500">
                        <span>Severity: {advisory.severity}</span>
                        <span>Published: {advisory.published_at}</span>
                      </div>
                      {advisory.affected_packages && (
                        <div className="mt-2">
                          <span className="text-xs text-gray-400">Packages: </span>
                          {advisory.affected_packages.map((pkg, i) => (
                            <span key={i} className="text-xs bg-cyber-purple/20 px-2 py-1 rounded ml-1">
                              {pkg}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    {advisory.html_url && (
                      <a href={advisory.html_url} target="_blank" rel="noopener noreferrer"
                         className="text-cyber-cyan hover:text-cyber-blue">
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </motion.div>
          )
        ))}
      </div>
    </div>
  )
}

export default ThreatLandscapeView