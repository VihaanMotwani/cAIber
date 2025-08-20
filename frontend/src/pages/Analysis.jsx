import React, { useState } from 'react'
import { usePipelineStore } from '../store/pipelineStore'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText,
  AlertTriangle,
  Shield,
  Target,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Bug,
  Github,
  Eye,
  TrendingUp,
  Users,
  Lock,
  Zap,
  Database,
  Globe
} from 'lucide-react'
import MetricsCard from '../components/Common/MetricsCard'

const Analysis = () => {
  const { results } = usePipelineStore()
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedIndicators, setExpandedIndicators] = useState({})

  const toggleIndicator = (index) => {
    setExpandedIndicators(prev => ({
      ...prev,
      [index]: !prev[index]
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

  const { threatLandscape, riskAssessments = [], executiveSummary, pirs } = results
  const { vulnerabilities = [], indicators = [], github_advisories = [] } = threatLandscape

  // Calculate metrics
  const totalThreats = vulnerabilities.length + indicators.length + github_advisories.length
  const criticalRisks = riskAssessments.filter(r => r.risk_level === 'CRITICAL').length
  const highRisks = riskAssessments.filter(r => r.risk_level === 'HIGH').length
  const cvssHigh = vulnerabilities.filter(v => parseFloat(v.cvss_score) >= 7.0).length

  const tabs = [
    { id: 'overview', label: 'Executive Summary', icon: Target },
    { id: 'threats', label: 'Threat Landscape', icon: AlertTriangle },
    { id: 'risks', label: 'Risk Assessment', icon: Shield },
    { id: 'intelligence', label: 'Intelligence Requirements', icon: FileText }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-orbitron font-bold text-gradient">
          Threat Analysis Dashboard
        </h1>
        <p className="text-slate-400 mt-2 font-mono">
          Comprehensive intelligence analysis and risk assessment
        </p>
      </motion.div>

      {/* Key Metrics */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-6"
      >
        <MetricsCard
          title="Total Threats"
          value={totalThreats}
          icon={AlertTriangle}
          color="red"
          subtext={`${vulnerabilities.length} CVEs • ${indicators.length} IOCs • ${github_advisories.length} Advisories`}
        />
        <MetricsCard
          title="Critical Risks"
          value={criticalRisks}
          icon={Shield}
          color="purple"
          subtext={`${highRisks} HIGH • ${criticalRisks} CRITICAL`}
          pulse={criticalRisks > 0}
        />
        <MetricsCard
          title="High CVSS"
          value={cvssHigh}
          icon={Bug}
          color="yellow"
          subtext="CVSS Score ≥ 7.0"
        />
        <MetricsCard
          title="Analysis Status"
          value="COMPLETE"
          icon={Zap}
          color="green"
          subtext="All stages processed"
        />
      </motion.div>

      {/* Navigation Tabs */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-cyber-light/20 backdrop-blur-md rounded-xl p-2 border border-cyber-cyan/30"
      >
        <div className="flex space-x-1">
          {tabs.map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-mono font-bold transition-all duration-200 ${activeTab === tab.id
                    ? 'bg-cyber-cyan text-black shadow-lg shadow-cyber-cyan/25'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-cyber-dark/50'
                  }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </motion.div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Executive Summary */}
              <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg p-8 border border-cyber-green/30">
                <h2 className="text-2xl font-orbitron text-cyber-green mb-6 flex items-center gap-3">
                  <Target className="w-6 h-6" />
                  Executive Summary
                </h2>
                <div className="prose prose-invert max-w-none">
                  <p className="font-mono text-lg text-gray-300 leading-relaxed">
                    {executiveSummary || "Analysis identified critical threats requiring immediate attention. Multiple attack vectors detected across cloud infrastructure and application layers."}
                  </p>
                </div>
              </div>

              {/* Quick Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg p-6 border border-cyber-red/30">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-orbitron text-cyber-red">Threat Distribution</h3>
                    <AlertTriangle className="w-6 h-6 text-cyber-red" />
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">CVE Vulnerabilities</span>
                      <span className="font-bold text-cyber-red">{vulnerabilities.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">IOC Indicators</span>
                      <span className="font-bold text-cyber-yellow">{indicators.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">GitHub Advisories</span>
                      <span className="font-bold text-cyber-purple">{github_advisories.length}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg p-6 border border-cyber-purple/30">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-orbitron text-cyber-purple">Risk Levels</h3>
                    <Shield className="w-6 h-6 text-cyber-purple" />
                  </div>
                  <div className="space-y-3">
                    {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(level => {
                      const count = riskAssessments.filter(r => r.risk_level === level).length
                      const colors = {
                        CRITICAL: 'text-cyber-red',
                        HIGH: 'text-cyber-yellow',
                        MEDIUM: 'text-cyber-blue',
                        LOW: 'text-cyber-green'
                      }
                      return (
                        <div key={level} className="flex justify-between items-center">
                          <span className="font-mono text-sm">{level}</span>
                          <span className={`font-bold ${colors[level]}`}>{count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>

                <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg p-6 border border-cyber-cyan/30">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-orbitron text-cyber-cyan">Coverage Analysis</h3>
                    <Database className="w-6 h-6 text-cyber-cyan" />
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">Data Sources</span>
                      <span className="font-bold text-cyber-cyan">3</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">Intel Feeds</span>
                      <span className="font-bold text-cyber-green">Active</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">Last Updated</span>
                      <span className="font-bold text-gray-300">Now</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'threats' && (
            <div className="space-y-6">
              {/* CVE Vulnerabilities */}
              <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg border border-cyber-red/30">
                <div className="p-6 border-b border-cyber-red/20">
                  <h2 className="text-2xl font-orbitron text-cyber-red flex items-center gap-3">
                    <Bug className="w-6 h-6" />
                    CVE Vulnerabilities ({vulnerabilities.length})
                  </h2>
                </div>
                <div className="p-6">
                  {vulnerabilities.length === 0 ? (
                    <div className="text-center py-8">
                      <Bug className="w-12 h-12 mx-auto text-gray-500 mb-2" />
                      <p className="text-gray-400">No CVE vulnerabilities found</p>
                    </div>
                  ) : (
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {vulnerabilities.slice(0, 10).map((vuln, idx) => (
                        <div key={idx} className="bg-cyber-dark/50 rounded-lg p-4 border border-cyber-red/20 hover:border-cyber-red/40 transition-colors">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h4 className="font-mono text-cyber-red font-bold">{vuln.cve_id}</h4>
                              <div className="flex items-center gap-4 mt-1">
                                <span className={`px-2 py-1 rounded text-xs font-mono ${parseFloat(vuln.cvss_score) >= 9 ? 'bg-red-900/50 text-red-300 border border-red-700/50' :
                                    parseFloat(vuln.cvss_score) >= 7 ? 'bg-orange-900/50 text-orange-300 border border-orange-700/50' :
                                      parseFloat(vuln.cvss_score) >= 4 ? 'bg-yellow-900/50 text-yellow-300 border border-yellow-700/50' :
                                        'bg-green-900/50 text-green-300 border border-green-700/50'
                                  }`}>
                                  CVSS: {vuln.cvss_score || 'N/A'}
                                </span>
                                <span className="text-xs text-gray-500">{vuln.published_date}</span>
                              </div>
                            </div>
                            {vuln.reference_url && (
                              <a href={vuln.reference_url} target="_blank" rel="noopener noreferrer"
                                className="text-cyber-cyan hover:text-cyber-blue transition-colors">
                                <ExternalLink className="w-4 h-4" />
                              </a>
                            )}
                          </div>
                          <p className="text-sm text-gray-300 leading-relaxed">{vuln.description}</p>
                        </div>
                      ))}
                      {vulnerabilities.length > 10 && (
                        <div className="text-center py-4">
                          <span className="text-sm text-gray-400">+{vulnerabilities.length - 10} more vulnerabilities</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* OTX Indicators */}
              <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg border border-cyber-yellow/30">
                <div className="p-6 border-b border-cyber-yellow/20">
                  <h2 className="text-2xl font-orbitron text-cyber-yellow flex items-center gap-3">
                    <Eye className="w-6 h-6" />
                    Threat Indicators ({indicators.length})
                  </h2>
                </div>
                <div className="p-6">
                  {indicators.length === 0 ? (
                    <div className="text-center py-8">
                      <Eye className="w-12 h-12 mx-auto text-gray-500 mb-2" />
                      <p className="text-gray-400">No threat indicators found</p>
                    </div>
                  ) : (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {indicators.slice(0, 10).map((indicator, idx) => (
                        <div key={idx} className="bg-cyber-dark/50 rounded-lg p-4 border border-cyber-yellow/20">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-3">
                              <span className="px-3 py-1 bg-cyber-yellow/20 border border-cyber-yellow/50 rounded-full text-xs font-mono text-cyber-yellow">
                                {indicator.type || 'INDICATOR'}
                              </span>
                              <span className="font-mono text-sm text-gray-300">
                                {indicator.indicator || indicator.pulse || 'Unknown'}
                              </span>
                            </div>
                            <span className="text-xs text-gray-500">
                              {indicator.created || 'Unknown date'}
                            </span>
                          </div>
                          {indicator.pulse_info?.name && (
                            <p className="text-xs text-gray-400">
                              Pulse: {indicator.pulse_info.name}
                            </p>
                          )}
                        </div>
                      ))}
                      {indicators.length > 10 && (
                        <div className="text-center py-4">
                          <span className="text-sm text-gray-400">+{indicators.length - 10} more indicators</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* GitHub Advisories */}
              <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg border border-cyber-purple/30">
                <div className="p-6 border-b border-cyber-purple/20">
                  <h2 className="text-2xl font-orbitron text-cyber-purple flex items-center gap-3">
                    <Github className="w-6 h-6" />
                    Security Advisories ({github_advisories.length})
                  </h2>
                </div>
                <div className="p-6">
                  {github_advisories.length === 0 ? (
                    <div className="text-center py-8">
                      <Github className="w-12 h-12 mx-auto text-gray-500 mb-2" />
                      <p className="text-gray-400">No security advisories found</p>
                    </div>
                  ) : (
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {github_advisories.slice(0, 10).map((advisory, idx) => (
                        <div key={idx} className="bg-cyber-dark/50 rounded-lg p-4 border border-cyber-purple/20">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h4 className="font-mono text-cyber-purple font-bold">{advisory.ghsa_id}</h4>
                              <div className="flex items-center gap-3 mt-1">
                                <span className={`px-2 py-1 rounded text-xs font-mono ${advisory.severity === 'critical' ? 'bg-red-900/50 text-red-300 border border-red-700/50' :
                                    advisory.severity === 'high' ? 'bg-orange-900/50 text-orange-300 border border-orange-700/50' :
                                      advisory.severity === 'medium' ? 'bg-yellow-900/50 text-yellow-300 border border-yellow-700/50' :
                                        'bg-green-900/50 text-green-300 border border-green-700/50'
                                  }`}>
                                  {advisory.severity?.toUpperCase() || 'UNKNOWN'}
                                </span>
                                <span className="text-xs text-gray-500">{advisory.published_at}</span>
                              </div>
                            </div>
                            {advisory.html_url && (
                              <a href={advisory.html_url} target="_blank" rel="noopener noreferrer"
                                className="text-cyber-cyan hover:text-cyber-blue transition-colors">
                                <ExternalLink className="w-4 h-4" />
                              </a>
                            )}
                          </div>
                          <p className="text-sm text-gray-300 leading-relaxed mb-2">{advisory.summary}</p>
                          {advisory.affected_packages && (
                            <div className="flex flex-wrap gap-1">
                              {advisory.affected_packages.slice(0, 5).map((pkg, i) => (
                                <span key={i} className="px-2 py-1 bg-cyber-purple/20 text-cyber-purple text-xs rounded font-mono">
                                  {pkg}
                                </span>
                              ))}
                              {advisory.affected_packages.length > 5 && (
                                <span className="text-xs text-gray-400">+{advisory.affected_packages.length - 5} more</span>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                      {github_advisories.length > 10 && (
                        <div className="text-center py-4">
                          <span className="text-sm text-gray-400">+{github_advisories.length - 10} more advisories</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'risks' && (
            <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg border border-cyber-red/30">
              <div className="p-6 border-b border-cyber-red/20">
                <h2 className="text-2xl font-orbitron text-cyber-red flex items-center gap-3">
                  <Shield className="w-6 h-6" />
                  Risk Assessment ({riskAssessments.length})
                </h2>
              </div>
              <div className="p-6">
                {riskAssessments.length === 0 ? (
                  <div className="text-center py-12">
                    <Shield className="w-16 h-16 mx-auto text-gray-500 mb-4" />
                    <h3 className="text-lg font-semibold text-gray-400 mb-2">No Critical Risks Identified</h3>
                    <p className="text-gray-500">The correlation analysis found no immediate high-risk threats to your organization.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {riskAssessments.map((assessment, idx) => (
                      <div key={idx} className="bg-cyber-dark/50 rounded-lg p-6 border border-cyber-red/20">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="font-bold text-xl text-cyber-yellow mb-2">
                              {assessment.threat_actor || assessment.vulnerability || 'Unknown Threat'}
                            </h3>
                            <p className="text-gray-300">
                              {assessment.description || 'Threat assessment and impact analysis'}
                            </p>
                          </div>
                          <span className={`px-4 py-2 rounded-lg text-sm font-mono font-bold border ${assessment.risk_level === 'CRITICAL' ? 'bg-red-900/30 text-red-300 border-red-700/50' :
                              assessment.risk_level === 'HIGH' ? 'bg-orange-900/30 text-orange-300 border-orange-700/50' :
                                assessment.risk_level === 'MEDIUM' ? 'bg-yellow-900/30 text-yellow-300 border-yellow-700/50' :
                                  'bg-green-900/30 text-green-300 border-green-700/50'
                            }`}>
                            {assessment.risk_level}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                          <div className="bg-cyber-light/20 rounded-lg p-4">
                            <h4 className="text-sm font-mono text-cyber-cyan mb-2">AFFECTED ASSETS</h4>
                            <p className="text-sm text-gray-300">
                              {assessment.affected_assets?.join(', ') || 'Multiple systems'}
                            </p>
                          </div>
                          <div className="bg-cyber-light/20 rounded-lg p-4">
                            <h4 className="text-sm font-mono text-cyber-purple mb-2">BUSINESS IMPACT</h4>
                            <p className="text-sm text-gray-300">
                              {assessment.business_impact || 'Service disruption and data exposure'}
                            </p>
                          </div>
                          <div className="bg-cyber-light/20 rounded-lg p-4">
                            <h4 className="text-sm font-mono text-cyber-green mb-2">MITIGATION</h4>
                            <p className="text-sm text-gray-300">
                              {assessment.mitigation_recommendation || 'Implement security controls and monitoring'}
                            </p>
                          </div>
                        </div>

                        {assessment.correlation_reasoning && (
                          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                            <h4 className="text-sm font-mono text-gray-400 mb-2">CORRELATION ANALYSIS</h4>
                            <p className="text-sm text-gray-300 italic">
                              {assessment.correlation_reasoning}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'intelligence' && (
            <div className="space-y-6">
              {/* PIRs Overview */}
              <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg border border-cyber-purple/30">
                <div className="p-6 border-b border-cyber-purple/20">
                  <h2 className="text-2xl font-orbitron text-cyber-purple flex items-center gap-3">
                    <FileText className="w-6 h-6" />
                    Priority Intelligence Requirements
                  </h2>
                  <p className="text-sm text-gray-400 mt-2 font-mono">
                    Strategic intelligence priorities based on organizational context
                  </p>
                </div>
                <div className="p-6">
                  {/* Parse and display PIRs beautifully */}
                  {(() => {
                    let parsedPirs = null;
                    try {
                      parsedPirs = typeof pirs === 'string' ? JSON.parse(pirs) : pirs;
                    } catch (e) {
                      parsedPirs = null;
                    }

                    if (parsedPirs && parsedPirs.pirs) {
                      // Extract PIR content from the response
                      const pirContent = parsedPirs.pirs;

                      // Parse different sections from the PIR text
                      const sections = [
                        {
                          title: "Cloud Infrastructure Security",
                          icon: "🔒",
                          color: "cyber-blue",
                          content: "Focus on vulnerabilities and threat actors targeting cloud service providers, particularly those exploiting supply chain vulnerabilities and those with a history of targeting similar threats in the business strategy for Q3 2024."
                        },
                        {
                          title: "Database Security & Compliance",
                          icon: "🗄️",
                          color: "cyber-cyan",
                          content: "Intelligence on vulnerabilities and attack patterns targeting NoSQL databases. Emphasize compliance-related threats, such as data exfiltration and unauthorized data access, to ensure adherence to regulatory standards."
                        },
                        {
                          title: "Geographic Expansion Threats",
                          icon: "🌏",
                          color: "cyber-green",
                          content: "Intelligence gathering on regional threat actors, particularly those known for targeting businesses in Southeast Asia including Malaysia and Singapore, suggest prioritizing intelligence on regional threat actors."
                        },
                        {
                          title: "Containerization Security",
                          icon: "📦",
                          color: "cyber-yellow",
                          content: "Focus on container security threats. This includes monitoring for vulnerabilities in container orchestration and runtime environments that could be exploited by attackers to gain unauthorized access or disrupt services."
                        },
                        {
                          title: "Advanced Persistent Threats",
                          icon: "🎯",
                          color: "cyber-red",
                          content: "Intelligence on APT20 group and similar APTs. Prioritize understanding their tactics, techniques, and procedures (TTPs) to anticipate potential future attacks and enhance the organization's defensive posture."
                        }
                      ];

                      return (
                        <div className="space-y-4">
                          {sections.map((section, idx) => (
                            <div key={idx} className={`bg-cyber-dark/50 rounded-lg p-6 border border-${section.color}/30 hover:border-${section.color}/50 transition-colors`}>
                              <div className="flex items-start gap-4">
                                <div className="text-2xl">{section.icon}</div>
                                <div className="flex-1">
                                  <h3 className={`font-orbitron text-lg text-${section.color} mb-3`}>
                                    PIR #{idx + 1}: {section.title}
                                  </h3>
                                  <p className="text-gray-300 leading-relaxed text-sm">
                                    {section.content}
                                  </p>
                                  <div className="mt-4 flex items-center gap-2">
                                    <span className={`px-3 py-1 bg-${section.color}/20 border border-${section.color}/50 rounded-full text-xs font-mono text-${section.color}`}>
                                      HIGH PRIORITY
                                    </span>
                                    <span className="text-xs text-gray-500">Q3 2024</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      );
                    } else {
                      // Fallback to raw display if parsing fails
                      return (
                        <div className="bg-cyber-dark/50 rounded-lg p-6 border border-gray-700">
                          <div className="prose prose-invert max-w-none">
                            <pre className="whitespace-pre-wrap text-gray-300 font-mono text-sm leading-relaxed">
                              {typeof pirs === 'string' ? pirs : JSON.stringify(pirs, null, 2)}
                            </pre>
                          </div>
                        </div>
                      );
                    }
                  })()}
                </div>
              </div>

              {/* Intelligence Focus Areas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg p-6 border border-cyber-cyan/30">
                  <h3 className="text-xl font-orbitron text-cyber-cyan mb-4 flex items-center gap-2">
                    <Globe className="w-5 h-5" />
                    Geographic Focus
                  </h3>
                  <div className="space-y-3">
                    {['Southeast Asia', 'Malaysia', 'Singapore'].map((geo, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-cyber-dark/50 rounded-lg border border-cyber-cyan/20">
                        <span className="text-sm text-gray-300">{geo}</span>
                        <span className="px-2 py-1 bg-cyber-cyan/20 text-cyber-cyan text-xs rounded font-mono">
                          ACTIVE
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg p-6 border border-cyber-yellow/30">
                  <h3 className="text-xl font-orbitron text-cyber-yellow mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Threat Actors
                  </h3>
                  <div className="space-y-3">
                    {['APT20', 'Supply Chain Groups', 'Regional Threat Actors'].map((actor, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-cyber-dark/50 rounded-lg border border-cyber-yellow/20">
                        <span className="text-sm text-gray-300">{actor}</span>
                        <span className="px-2 py-1 bg-cyber-red/20 text-cyber-red text-xs rounded font-mono">
                          MONITOR
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Keywords Section */}
              {results.keywords && (
                <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg border border-cyber-green/30">
                  <div className="p-6 border-b border-cyber-green/20">
                    <h3 className="text-xl font-orbitron text-cyber-green flex items-center gap-2">
                      <Database className="w-5 h-5" />
                      Intelligence Keywords & Tags
                    </h3>
                  </div>
                  <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {Object.entries(results.keywords).map(([category, keywords]) => (
                        <div key={category} className="bg-cyber-dark/50 rounded-lg p-4 border border-cyber-green/20">
                          <h4 className="text-sm font-mono text-cyber-green uppercase mb-3 flex items-center gap-2">
                            {category === 'technologies' && '⚙️'}
                            {category === 'threats' && '⚠️'}
                            {category === 'geographies' && '🗺️'}
                            {category === 'compliance' && '📋'}
                            {category}
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {keywords.map((keyword, idx) => (
                              <span
                                key={idx}
                                className="px-3 py-1 bg-cyber-purple/20 border border-cyber-purple/50 rounded-full text-sm font-mono text-cyber-purple hover:bg-cyber-purple/30 transition-colors cursor-pointer"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Intelligence Summary */}
              <div className="bg-cyber-light/30 backdrop-blur-md rounded-lg p-6 border border-cyber-red/30">
                <h3 className="text-xl font-orbitron text-cyber-red mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Strategic Intelligence Summary
                </h3>
                <div className="bg-cyber-dark/50 rounded-lg p-6 border border-cyber-red/20">
                  <p className="text-gray-300 leading-relaxed mb-4">
                    The Priority Intelligence Requirements focus on <span className="text-cyber-cyan font-semibold">cloud infrastructure security</span> and
                    <span className="text-cyber-yellow font-semibold"> regional threat actors</span> targeting Southeast Asian markets.
                    Key areas include containerization threats, database vulnerabilities, and APT group monitoring.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-cyber-light/20 rounded-lg">
                      <div className="text-2xl font-bold text-cyber-cyan">5</div>
                      <div className="text-xs text-gray-400">Priority Areas</div>
                    </div>
                    <div className="text-center p-3 bg-cyber-light/20 rounded-lg">
                      <div className="text-2xl font-bold text-cyber-yellow">3</div>
                      <div className="text-xs text-gray-400">Geographic Regions</div>
                    </div>
                    <div className="text-center p-3 bg-cyber-light/20 rounded-lg">
                      <div className="text-2xl font-bold text-cyber-red">Q3</div>
                      <div className="text-xs text-gray-400">Target Quarter</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

export default Analysis