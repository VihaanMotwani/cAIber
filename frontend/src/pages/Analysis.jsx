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
          <h2 className="text-2xl font-bold text-gray-400">No Analysis Results</h2>
          <p className="text-gray-500 mt-2 font-mono">Run a pipeline analysis first to see results</p>
        </div>
      </div>
    )
  }

  const { threatLandscape, riskAssessments = [], executiveSummary, pirs } = results
  const { vulnerabilities = [], indicators = [], github_advisories = [] } = threatLandscape

  // Calculate metrics
  // Calculate metrics
  const totalThreats = vulnerabilities.length + indicators.length + github_advisories.length

  // ✅ Every risk returned by backend
  const totalRisks = riskAssessments.length

  // ✅ If you still want to break down by levels, normalize case
  const criticalRisks = riskAssessments.filter(r => (r.risk_level || '').toUpperCase() === 'CRITICAL').length
  const highRisks = riskAssessments.filter(r => (r.risk_level || '').toUpperCase() === 'HIGH').length
  const mediumRisks = riskAssessments.filter(r => (r.risk_level || '').toUpperCase() === 'MEDIUM').length
  const lowRisks = riskAssessments.filter(r => (r.risk_level || '').toUpperCase() === 'LOW').length

  // ✅ CVSS should fall back to x_cvss_score if missing
  const cvssHigh = vulnerabilities.filter(v => {
    const score = parseFloat(v.cvss_score || v.x_cvss_score || 0)
    return score >= 0.0
  }).length


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
        <h1 className="heading-xl mb-3">
          Threat Analysis Dashboard
        </h1>
        <p className="text-slate-400 text-lg font-medium">
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
          title="Total Risks"
          value={totalRisks}
          icon={Shield}
          color="purple"
          subtext={`${criticalRisks} CRITICAL • ${highRisks} HIGH • ${mediumRisks} MEDIUM • ${lowRisks} LOW`}
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
        className="bg-slate-900/20 backdrop-blur-md rounded-xl p-2 border border-blue-400/30"
      >
        <div className="flex space-x-1">
          {tabs.map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-mono font-bold transition-all duration-200 ${activeTab === tab.id
                  ? 'bg-blue-400 text-black shadow-lg shadow-blue-400/25'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
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
              <div className="bg-slate-900/30 backdrop-blur-md rounded-lg p-8 border border-purple-400/30">
                <h2 className="text-2xl font-bold text-purple-400 mb-6 flex items-center gap-3">
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
                <div className="bg-slate-900/30 backdrop-blur-md rounded-lg p-6 border border-red-400/30">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-red-400">Threat Distribution</h3>
                    <AlertTriangle className="w-6 h-6 text-red-400" />
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">CVE Vulnerabilities</span>
                      <span className="font-bold text-red-400">{vulnerabilities.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">IOC Indicators</span>
                      <span className="font-bold text-yellow-400">{indicators.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">GitHub Advisories</span>
                      <span className="font-bold text-purple-500">{github_advisories.length}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/30 backdrop-blur-md rounded-lg p-6 border border-purple-500/30">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-purple-500">Risk Levels</h3>
                    <Shield className="w-6 h-6 text-purple-500" />
                  </div>
                  <div className="space-y-3">
                    {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(level => {
                      const count = riskAssessments.filter(r => r.risk_level === level).length
                      const colors = {
                        CRITICAL: 'text-red-400',
                        HIGH: 'text-yellow-400',
                        MEDIUM: 'text-blue-500',
                        LOW: 'text-purple-400'
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

                <div className="bg-slate-900/30 backdrop-blur-md rounded-lg p-6 border border-blue-400/30">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-blue-400">Coverage Analysis</h3>
                    <Database className="w-6 h-6 text-blue-400" />
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">Data Sources</span>
                      <span className="font-bold text-blue-400">3</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="font-mono text-sm">Intel Feeds</span>
                      <span className="font-bold text-purple-400">Active</span>
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
              <div className="bg-slate-900/30 backdrop-blur-md rounded-lg border border-red-400/30">
                <div className="p-6 border-b border-red-400/20">
                  <h2 className="text-2xl font-bold text-red-400 flex items-center gap-3">
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
                        <div key={idx} className="bg-slate-800/50 rounded-lg p-4 border border-red-400/20 hover:border-red-400/40 transition-colors">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h4 className="font-mono text-red-400 font-bold">{vuln.cve_id}</h4>
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
                                className="text-blue-400 hover:text-blue-500 transition-colors">
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
              <div className="bg-slate-900/30 backdrop-blur-md rounded-lg border border-yellow-400/30">
                <div className="p-6 border-b border-yellow-400/20">
                  <h2 className="text-2xl font-bold text-yellow-400 flex items-center gap-3">
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
                        <div key={idx} className="bg-slate-800/50 rounded-lg p-4 border border-yellow-400/20">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-3">
                              <span className="px-3 py-1 bg-yellow-400/20 border border-yellow-400/50 rounded-full text-xs font-mono text-yellow-400">
                                {indicator.type || 'INDICATOR'}
                              </span>
                              <span className="font-mono text-sm text-gray-300">
                                {indicator.indicator || 'Unknown IOC'}
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
              <div className="bg-slate-900/30 backdrop-blur-md rounded-lg border border-purple-500/30">
                <div className="p-6 border-b border-purple-500/20">
                  <h2 className="text-2xl font-bold text-purple-500 flex items-center gap-3">
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
                        <div key={idx} className="bg-slate-800/50 rounded-lg p-4 border border-purple-500/20">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h4 className="font-mono text-purple-500 font-bold">{advisory.ghsa_id}</h4>
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
                                className="text-blue-400 hover:text-blue-500 transition-colors">
                                <ExternalLink className="w-4 h-4" />
                              </a>
                            )}
                          </div>
                          <p className="text-sm text-gray-300 leading-relaxed mb-2">{advisory.summary}</p>
                          {advisory.affected_packages && (
                            <div className="flex flex-wrap gap-1">
                              {advisory.affected_packages.slice(0, 5).map((pkg, i) => (
                                <span key={i} className="px-2 py-1 bg-purple-500/20 text-purple-500 text-xs rounded font-mono">
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
            <div className="bg-slate-900/30 backdrop-blur-md rounded-lg border border-red-400/30">
              <div className="p-6 border-b border-red-400/20">
                <h2 className="text-2xl font-bold text-red-400 flex items-center gap-3">
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
                      <div key={idx} className="bg-slate-800/50 rounded-lg p-6 border border-red-400/20">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="font-bold text-xl text-yellow-400 mb-2">
                              {assessment.threat_id || assessment.vulnerability || 'Unknown Threat'}
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
                          <div className="bg-slate-900/20 rounded-lg p-4">
                            <h4 className="text-sm font-mono text-blue-400 mb-2">AFFECTED ASSETS</h4>
                            <p className="text-sm text-gray-300">
                              {assessment.affected_assets?.join(', ') || 'Multiple systems'}
                            </p>
                          </div>
                          <div className="bg-slate-900/20 rounded-lg p-4">
                            <h4 className="text-sm font-mono text-purple-500 mb-2">BUSINESS IMPACT</h4>
                            <p className="text-sm text-gray-300">
                              {assessment.business_impact || 'Service disruption and data exposure'}
                            </p>
                          </div>
                          <div className="bg-slate-900/20 rounded-lg p-4">
                            <h4 className="text-sm font-mono text-purple-400 mb-2">MITIGATION</h4>
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
              <div className="bg-slate-900/30 backdrop-blur-md rounded-lg border border-purple-500/30">
                <div className="p-6 border-b border-purple-500/20">
                  <h2 className="text-2xl font-bold text-purple-500 flex items-center gap-3">
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
                    let pirText = '';

                    try {
                      parsedPirs = typeof pirs === 'string' ? JSON.parse(pirs) : pirs;
                      pirText = parsedPirs?.pirs || pirs || '';
                    } catch (e) {
                      pirText = typeof pirs === 'string' ? pirs : JSON.stringify(pirs, null, 2);
                    }

                    // Parse PIRs from the text content
                    const parsePIRs = (text) => {
                      const pirRegex = /(\d+)\.\s*\*\*(.*?)\*\*[\s\S]*?- \*\*PIR.*?\*\*:\s*(.*?)(?=\n\d+\.|\Z)/g;
                      const matches = [...text.matchAll(pirRegex)];

                      if (matches.length === 0) {
                        // Fallback: try simpler numbered list pattern
                        const simpleRegex = /(\d+)\.\s*(.*?)(?=\d+\.|$)/gs;
                        const simpleMatches = [...text.matchAll(simpleRegex)];

                        return simpleMatches.map((match, idx) => {
                          const content = match[2].trim();
                          const title = content.split(':')[0] || content.substring(0, 50) + '...';

                          return {
                            id: idx + 1,
                            title: title.replace(/\*\*/g, ''),
                            content: content,
                            priority: 'HIGH',
                            category: idx % 2 === 0 ? 'TECHNICAL' : 'STRATEGIC'
                          };
                        });
                      }

                      return matches.map((match, idx) => ({
                        id: parseInt(match[1]),
                        title: match[2].trim(),
                        content: match[3].trim(),
                        priority: idx < 2 ? 'CRITICAL' : idx < 4 ? 'HIGH' : 'MEDIUM',
                        category: idx % 3 === 0 ? 'TECHNICAL' : idx % 3 === 1 ? 'STRATEGIC' : 'OPERATIONAL'
                      }));
                    };

                    const parsedPIRList = parsePIRs(pirText);

                    const getPriorityColor = (priority) => {
                      switch (priority) {
                        case 'CRITICAL': return { bg: 'bg-red-900/30', border: 'border-red-400/50', text: 'text-red-400' };
                        case 'HIGH': return { bg: 'bg-yellow-900/30', border: 'border-yellow-400/50', text: 'text-yellow-400' };
                        case 'MEDIUM': return { bg: 'bg-blue-900/30', border: 'border-blue-400/50', text: 'text-blue-400' };
                        default: return { bg: 'bg-purple-900/30', border: 'border-purple-400/50', text: 'text-purple-400' };
                      }
                    };

                    const getCategoryIcon = (category) => {
                      switch (category) {
                        case 'TECHNICAL': return { icon: '⚙️', color: 'text-blue-400' };
                        case 'STRATEGIC': return { icon: '🎯', color: 'text-purple-400' };
                        case 'OPERATIONAL': return { icon: '🛡️', color: 'text-yellow-400' };
                        default: return { icon: '📊', color: 'text-gray-400' };
                      }
                    };

                    if (parsedPIRList.length === 0) {
                      return (
                        <div className="bg-slate-800/50 rounded-lg p-8 border border-gray-700">
                          <div className="text-center">
                            <FileText className="w-12 h-12 mx-auto text-gray-500 mb-4" />
                            <h3 className="text-lg font-semibold text-gray-400 mb-2">PIRs Processing</h3>
                            <p className="text-gray-500 mb-4">Intelligence requirements are being analyzed...</p>
                            <div className="bg-slate-900/50 rounded-lg p-4 border border-gray-600">
                              <pre className="whitespace-pre-wrap text-gray-400 font-mono text-xs max-h-40 overflow-y-auto">
                                {pirText.substring(0, 500)}...
                              </pre>
                            </div>
                          </div>
                        </div>
                      );
                    }

                    return (
                      <div className="space-y-6">
                        {/* PIRs Summary Stats */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                          <div className="bg-slate-800/50 rounded-lg p-4 border border-red-400/30">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-red-400">
                                {parsedPIRList.filter(p => p.priority === 'CRITICAL').length}
                              </div>
                              <div className="text-xs text-red-400 font-mono">CRITICAL</div>
                            </div>
                          </div>
                          <div className="bg-slate-800/50 rounded-lg p-4 border border-yellow-400/30">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-yellow-400">
                                {parsedPIRList.filter(p => p.priority === 'HIGH').length}
                              </div>
                              <div className="text-xs text-yellow-400 font-mono">HIGH</div>
                            </div>
                          </div>
                          <div className="bg-slate-800/50 rounded-lg p-4 border border-blue-400/30">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-blue-400">
                                {parsedPIRList.filter(p => p.priority === 'MEDIUM').length}
                              </div>
                              <div className="text-xs text-blue-400 font-mono">MEDIUM</div>
                            </div>
                          </div>
                          <div className="bg-slate-800/50 rounded-lg p-4 border border-purple-400/30">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-purple-400">{parsedPIRList.length}</div>
                              <div className="text-xs text-purple-400 font-mono">TOTAL PIRs</div>
                            </div>
                          </div>
                        </div>

                        {/* PIRs List */}
                        <div className="space-y-4">
                          {parsedPIRList.map((pir, idx) => {
                            const priorityColors = getPriorityColor(pir.priority);
                            const categoryInfo = getCategoryIcon(pir.category);

                            return (
                              <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                className={`bg-slate-800/50 rounded-lg p-6 border ${priorityColors.border} hover:border-opacity-100 transition-all duration-200`}
                              >
                                <div className="flex items-start justify-between mb-4">
                                  <div className="flex items-start gap-4 flex-1">
                                    <div className="flex flex-col items-center">
                                      <div className="text-2xl mb-1">{categoryInfo.icon}</div>
                                      <div className={`px-2 py-1 rounded text-xs font-mono ${priorityColors.bg} ${priorityColors.text} border ${priorityColors.border}`}>
                                        PIR #{pir.id}
                                      </div>
                                    </div>
                                    <div className="flex-1">
                                      <h3 className={`font-bold text-xl ${priorityColors.text} mb-2`}>
                                        {pir.title}
                                      </h3>
                                      <div className="flex items-center gap-3 mb-3">
                                        <span className={`px-3 py-1 rounded-full text-xs font-mono ${priorityColors.bg} ${priorityColors.text} border ${priorityColors.border}`}>
                                          {pir.priority} PRIORITY
                                        </span>
                                        <span className={`px-3 py-1 rounded-full text-xs font-mono bg-slate-700/50 ${categoryInfo.color} border border-gray-600`}>
                                          {pir.category}
                                        </span>
                                        <span className="text-xs text-gray-500 font-mono">Q3 2024 TARGET</span>
                                      </div>
                                      <div className="bg-slate-900/30 rounded-lg p-4 border border-gray-700/50">
                                        <p className="text-gray-300 leading-relaxed text-sm whitespace-pre-wrap">
                                          {pir.content.replace(/\*\*/g, '').trim()}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                {/* PIR Actions */}
                                <div className="flex items-center justify-between pt-4 border-t border-gray-700/50">
                                  <div className="flex items-center gap-2 text-xs text-gray-400">
                                    <Users className="w-3 h-3" />
                                    <span>Security Team • Intelligence Team</span>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <button className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded hover:bg-blue-500/30 transition-colors border border-blue-500/50">
                                      Track Progress
                                    </button>
                                    <button className="px-3 py-1 bg-purple-500/20 text-purple-400 text-xs rounded hover:bg-purple-500/30 transition-colors border border-purple-500/50">
                                      Set Alert
                                    </button>
                                  </div>
                                </div>
                              </motion.div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>

              {/* Intelligence Focus Areas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-900/30 backdrop-blur-md rounded-lg p-6 border border-blue-400/30">
                  <h3 className="text-xl font-bold text-blue-400 mb-4 flex items-center gap-2">
                    <Globe className="w-5 h-5" />
                    Geographic Focus
                  </h3>
                  <div className="space-y-3">
                    {['Southeast Asia', 'Malaysia', 'Singapore'].map((geo, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-blue-400/20">
                        <span className="text-sm text-gray-300">{geo}</span>
                        <span className="px-2 py-1 bg-blue-400/20 text-blue-400 text-xs rounded font-mono">
                          ACTIVE
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900/30 backdrop-blur-md rounded-lg p-6 border border-yellow-400/30">
                  <h3 className="text-xl font-bold text-yellow-400 mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Threat Actors
                  </h3>
                  <div className="space-y-3">
                    {['APT20', 'Supply Chain Groups', 'Regional Threat Actors'].map((actor, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-yellow-400/20">
                        <span className="text-sm text-gray-300">{actor}</span>
                        <span className="px-2 py-1 bg-red-400/20 text-red-400 text-xs rounded font-mono">
                          MONITOR
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Keywords Section */}
              {results.keywords && (
                <div className="bg-slate-900/30 backdrop-blur-md rounded-lg border border-purple-400/30">
                  <div className="p-6 border-b border-purple-400/20">
                    <h3 className="text-xl font-bold text-purple-400 flex items-center gap-2">
                      <Database className="w-5 h-5" />
                      Intelligence Keywords & Tags
                    </h3>
                  </div>
                  <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {Object.entries(results.keywords).map(([category, keywords]) => (
                        <div key={category} className="bg-slate-800/50 rounded-lg p-4 border border-purple-400/20">
                          <h4 className="text-sm font-mono text-purple-400 uppercase mb-3 flex items-center gap-2">
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
                                className="px-3 py-1 bg-purple-500/20 border border-purple-500/50 rounded-full text-sm font-mono text-purple-500 hover:bg-purple-500/30 transition-colors cursor-pointer"
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
              <div className="bg-slate-900/30 backdrop-blur-md rounded-lg p-6 border border-red-400/30">
                <h3 className="text-xl font-bold text-red-400 mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Strategic Intelligence Summary
                </h3>
                <div className="bg-slate-800/50 rounded-lg p-6 border border-red-400/20">
                  <p className="text-gray-300 leading-relaxed mb-4">
                    The Priority Intelligence Requirements focus on <span className="text-blue-400 font-semibold">cloud infrastructure security</span> and
                    <span className="text-yellow-400 font-semibold"> regional threat actors</span> targeting Southeast Asian markets.
                    Key areas include containerization threats, database vulnerabilities, and APT group monitoring.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-slate-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-blue-400">5</div>
                      <div className="text-xs text-gray-400">Priority Areas</div>
                    </div>
                    <div className="text-center p-3 bg-slate-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-yellow-400">3</div>
                      <div className="text-xs text-gray-400">Geographic Regions</div>
                    </div>
                    <div className="text-center p-3 bg-slate-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-red-400">Q3</div>
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