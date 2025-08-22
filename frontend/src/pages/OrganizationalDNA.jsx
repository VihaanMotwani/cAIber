import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Network, Building2, Shield, Database, AlertCircle, Layers, Play } from 'lucide-react'
import SimpleKnowledgeGraph from '../components/Visualizations/SimpleKnowledgeGraph'
import { api } from '../api/apiClient'
import { usePipelineStore } from '../store/pipelineStore'

const OrganizationalDNA = () => {
  const { results, stageProgress } = usePipelineStore()
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({
    totalNodes: 0,
    technologies: 0,
    assets: 0,
    threats: 0,
    compliance: 0
  })
  const [viewMode, setViewMode] = useState('3d')

  // Check if Stage 1 (PIR generation + DNA building) has completed
  const hasStage1Completed = stageProgress.stage1.status === 'completed' || results?.pirs

  useEffect(() => {
    // Only fetch graph data if Stage 1 has completed
    if (hasStage1Completed) {
      fetchGraphData()
    }
  }, [hasStage1Completed])

  const fetchGraphData = async () => {
    setLoading(true)
    try {
      // Fetch real data from the backend
      console.log('Fetching organizational DNA...')
      const graphData = await api.getOrganizationalDNA()
      console.log('Received graph data:', graphData)
      
      // If the API call fails or returns no data, use mock as fallback
      const mockData = graphData || {
        nodes: [
          { id: 'org-root', label: 'TechCorp Inc.', type: 'organization', val: 25, color: '#0ea5e9' },
          
          // Technologies
          { id: 'cloud', label: 'Cloud Infrastructure', type: 'technology', val: 18, color: '#14b8a6' },
          { id: 'aws', label: 'AWS', type: 'technology', val: 12, color: '#14b8a6' },
          { id: 'azure', label: 'Azure', type: 'technology', val: 10, color: '#14b8a6' },
          { id: 'k8s', label: 'Kubernetes', type: 'technology', val: 12, color: '#14b8a6' },
          { id: 'docker', label: 'Docker', type: 'technology', val: 8, color: '#14b8a6' },
          { id: 'postgres', label: 'PostgreSQL', type: 'technology', val: 10, color: '#14b8a6' },
          { id: 'redis', label: 'Redis', type: 'technology', val: 8, color: '#14b8a6' },
          
          // Critical Assets
          { id: 'assets-root', label: 'Critical Assets', type: 'asset', val: 18, color: '#8b5cf6' },
          { id: 'customer-db', label: 'Customer Database', type: 'asset', val: 15, color: '#8b5cf6' },
          { id: 'payment-sys', label: 'Payment System', type: 'asset', val: 15, color: '#8b5cf6' },
          { id: 'auth-service', label: 'Auth Service', type: 'asset', val: 12, color: '#8b5cf6' },
          { id: 'api-gateway', label: 'API Gateway', type: 'asset', val: 12, color: '#8b5cf6' },
          
          // Compliance
          { id: 'compliance-root', label: 'Compliance Framework', type: 'compliance', val: 15, color: '#f59e0b' },
          { id: 'gdpr', label: 'GDPR', type: 'compliance', val: 10, color: '#f59e0b' },
          { id: 'pci-dss', label: 'PCI-DSS', type: 'compliance', val: 10, color: '#f59e0b' },
          { id: 'sox', label: 'SOX', type: 'compliance', val: 8, color: '#f59e0b' },
          { id: 'hipaa', label: 'HIPAA', type: 'compliance', val: 8, color: '#f59e0b' },
          
          // Threat Landscape
          { id: 'threats-root', label: 'Threat Landscape', type: 'threat', val: 15, color: '#ef4444' },
          { id: 'ransomware', label: 'Ransomware Risk', type: 'threat', val: 10, color: '#ef4444' },
          { id: 'supply-chain', label: 'Supply Chain Attack', type: 'threat', val: 10, color: '#ef4444' },
          { id: 'phishing', label: 'Phishing Campaign', type: 'threat', val: 8, color: '#ef4444' },
          { id: 'insider', label: 'Insider Threat', type: 'threat', val: 8, color: '#ef4444' },
        ],
        links: [
          // Organization connections
          { source: 'org-root', target: 'cloud', value: 5 },
          { source: 'org-root', target: 'assets-root', value: 5 },
          { source: 'org-root', target: 'compliance-root', value: 4 },
          { source: 'org-root', target: 'threats-root', value: 3 },
          
          // Technology connections
          { source: 'cloud', target: 'aws', value: 3 },
          { source: 'cloud', target: 'azure', value: 3 },
          { source: 'cloud', target: 'k8s', value: 3 },
          { source: 'k8s', target: 'docker', value: 2 },
          { source: 'aws', target: 'postgres', value: 2 },
          { source: 'aws', target: 'redis', value: 2 },
          
          // Asset connections
          { source: 'assets-root', target: 'customer-db', value: 3 },
          { source: 'assets-root', target: 'payment-sys', value: 3 },
          { source: 'assets-root', target: 'auth-service', value: 3 },
          { source: 'assets-root', target: 'api-gateway', value: 3 },
          { source: 'customer-db', target: 'postgres', value: 2 },
          { source: 'auth-service', target: 'redis', value: 2 },
          
          // Compliance connections
          { source: 'compliance-root', target: 'gdpr', value: 2 },
          { source: 'compliance-root', target: 'pci-dss', value: 2 },
          { source: 'compliance-root', target: 'sox', value: 2 },
          { source: 'compliance-root', target: 'hipaa', value: 2 },
          { source: 'customer-db', target: 'gdpr', value: 2 },
          { source: 'payment-sys', target: 'pci-dss', value: 2 },
          
          // Threat connections
          { source: 'threats-root', target: 'ransomware', value: 2 },
          { source: 'threats-root', target: 'supply-chain', value: 2 },
          { source: 'threats-root', target: 'phishing', value: 2 },
          { source: 'threats-root', target: 'insider', value: 2 },
          { source: 'ransomware', target: 'customer-db', value: 1 },
          { source: 'supply-chain', target: 'docker', value: 1 },
          { source: 'phishing', target: 'auth-service', value: 1 },
        ]
      }
      
      const finalData = graphData || mockData
      setGraphData(finalData)
      
      // Use stats from API if available, otherwise calculate from nodes
      if (graphData?.stats) {
        setStats({
          totalNodes: graphData.stats.totalNodes || 0,
          technologies: graphData.stats.technologies || 0,
          assets: (graphData.stats.business_assets || 0) + (graphData.stats.business_initiatives || 0),
          threats: (graphData.stats.threats || 0) + (graphData.stats.vulnerabilities || 0),
          compliance: graphData.stats.compliance || 0,
          organizations: graphData.stats.organizations || 0,
          geographies: graphData.stats.geographies || 0
        })
      } else {
        // Fallback to calculating from nodes
        const nodeTypes = finalData.nodes.reduce((acc, node) => {
          acc[node.type] = (acc[node.type] || 0) + 1
          return acc
        }, {})
        
        setStats({
          totalNodes: finalData.nodes.length,
          technologies: nodeTypes.technology || 0,
          assets: nodeTypes.asset || 0,
          threats: nodeTypes.threat || 0,
          compliance: nodeTypes.compliance || 0
        })
      }
      
    } catch (error) {
      console.error('Failed to fetch graph data:', error)
      console.log('Using mock data as fallback')
      // Set mock data as fallback
      setGraphData(mockData)
      setStats({
        totalNodes: mockData.nodes.length,
        technologies: 7,
        assets: 4,
        threats: 4,
        compliance: 4
      })
    } finally {
      setLoading(false)
    }
  }

  // Show empty state if Stage 1 hasn't been completed
  if (!hasStage1Completed) {
    return (
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-between items-start"
        >
          <div>
            <h1 className="text-3xl font-semibold text-gradient">
              Organizational DNA
            </h1>
            <p className="text-slate-400 mt-2">
              Interactive knowledge graph visualization of your organization's digital ecosystem
            </p>
          </div>
        </motion.div>

        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <Network className="w-16 h-16 mx-auto text-gray-500 mb-4" />
            <h2 className="text-2xl font-orbitron text-gray-400 mb-2">Organizational DNA Not Built</h2>
            <p className="text-gray-500 font-mono mb-4">
              The knowledge graph is built during Stage 1 of the threat analysis pipeline
            </p>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg border border-slate-700">
              <Play className="w-4 h-4 text-primary-500" />
              <span className="text-sm text-slate-300 font-mono">
                Go to Dashboard → Click "Initiate Threat Analysis"
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-3 font-mono">
              This will extract entities and relationships from your documents
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-start"
      >
        <div>
          <h1 className="text-3xl font-semibold text-gradient">
            Organizational DNA
          </h1>
          <p className="text-slate-400 mt-2">
            Interactive knowledge graph visualization of your organization's digital ecosystem
          </p>
        </div>
        
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-5 gap-4"
      >
        <div className="card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Total Nodes</p>
              <p className="text-2xl font-semibold mt-1">{stats.totalNodes}</p>
            </div>
            <Network className="w-8 h-8 text-primary-500" />
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Technologies</p>
              <p className="text-2xl font-semibold mt-1">{stats.technologies}</p>
            </div>
            <Layers className="w-8 h-8 text-teal-500" />
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Critical Assets</p>
              <p className="text-2xl font-semibold mt-1">{stats.assets}</p>
            </div>
            <Database className="w-8 h-8 text-purple-500" />
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Compliance</p>
              <p className="text-2xl font-semibold mt-1">{stats.compliance}</p>
            </div>
            <Shield className="w-8 h-8 text-amber-500" />
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Threats</p>
              <p className="text-2xl font-semibold mt-1">{stats.threats}</p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </motion.div>

      {/* Knowledge Graph */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="card p-6"
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Knowledge Graph Visualization</h2>
          <div className="flex items-center gap-4 text-sm text-slate-400">
            <span>Click nodes to explore • Hover for connections • Scroll to zoom</span>
          </div>
        </div>
        
        {loading ? (
          <div className="flex items-center justify-center h-[600px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500 mx-auto"></div>
              <p className="text-slate-400 mt-4">Loading knowledge graph...</p>
            </div>
          </div>
        ) : (
          <SimpleKnowledgeGraph 
            graphData={graphData} 
            onRefresh={fetchGraphData}
          />
        )}
      </motion.div>

      {/* Insights Panel */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-2 gap-6"
      >
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Key Relationships</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <span className="text-sm">Cloud Infrastructure → Critical Assets</span>
              <span className="badge badge-primary">Strong</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <span className="text-sm">Customer Data → GDPR Compliance</span>
              <span className="badge badge-primary">Required</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <span className="text-sm">Payment System → PCI-DSS</span>
              <span className="badge badge-primary">Critical</span>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Risk Indicators</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-red-900/20 rounded-lg border border-red-900/30">
              <span className="text-sm">Ransomware → Customer Database</span>
              <span className="text-red-400 text-xs font-medium">HIGH RISK</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-amber-900/20 rounded-lg border border-amber-900/30">
              <span className="text-sm">Supply Chain → Docker Dependencies</span>
              <span className="text-amber-400 text-xs font-medium">MEDIUM RISK</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-amber-900/20 rounded-lg border border-amber-900/30">
              <span className="text-sm">Phishing → Auth Service</span>
              <span className="text-amber-400 text-xs font-medium">MEDIUM RISK</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default OrganizationalDNA