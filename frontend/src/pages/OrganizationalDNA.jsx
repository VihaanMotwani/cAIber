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

  // Always try to fetch data, but handle empty state gracefully
  useEffect(() => {
    fetchGraphData()
  }, [])

  const fetchGraphData = async () => {
    setLoading(true)
    
    // Define mock data at function scope so it's accessible in both try and catch blocks
    const mockData = {
      nodes: [
        { id: 'org-root', label: 'TechCorp Inc.', type: 'organization', size: 25 },
        
        // Technologies
        { id: 'cloud', label: 'Cloud Infrastructure', type: 'technology', size: 18 },
        { id: 'aws', label: 'AWS', type: 'technology', size: 12 },
        { id: 'azure', label: 'Azure', type: 'technology', size: 10 },
        { id: 'k8s', label: 'Kubernetes', type: 'technology', size: 12 },
        { id: 'docker', label: 'Docker', type: 'technology', size: 8 },
        { id: 'postgres', label: 'PostgreSQL', type: 'technology', size: 10 },
        { id: 'redis', label: 'Redis', type: 'technology', size: 8 },
        
        // Critical Assets
        { id: 'assets-root', label: 'Critical Assets', type: 'asset', size: 18 },
        { id: 'customer-db', label: 'Customer Database', type: 'asset', size: 15 },
        { id: 'payment-sys', label: 'Payment System', type: 'asset', size: 15 },
        { id: 'auth-service', label: 'Auth Service', type: 'asset', size: 12 },
        { id: 'api-gateway', label: 'API Gateway', type: 'asset', size: 12 },
        
        // Compliance
        { id: 'compliance-root', label: 'Compliance Framework', type: 'compliance', size: 15 },
        { id: 'gdpr', label: 'GDPR', type: 'compliance', size: 10 },
        { id: 'pci-dss', label: 'PCI-DSS', type: 'compliance', size: 10 },
        { id: 'sox', label: 'SOX', type: 'compliance', size: 8 },
        { id: 'hipaa', label: 'HIPAA', type: 'compliance', size: 8 },
        
        // Threat Landscape
        { id: 'threats-root', label: 'Threat Landscape', type: 'threat', size: 15 },
        { id: 'ransomware', label: 'Ransomware Risk', type: 'threat', size: 10 },
        { id: 'supply-chain', label: 'Supply Chain Attack', type: 'threat', size: 10 },
        { id: 'phishing', label: 'Phishing Campaign', type: 'threat', size: 8 },
        { id: 'insider', label: 'Insider Threat', type: 'threat', size: 8 },
      ],
      links: [
        // Organization connections
        { source: 'org-root', target: 'cloud' },
        { source: 'org-root', target: 'assets-root' },
        { source: 'org-root', target: 'compliance-root' },
        { source: 'org-root', target: 'threats-root' },
        
        // Technology connections
        { source: 'cloud', target: 'aws' },
        { source: 'cloud', target: 'azure' },
        { source: 'cloud', target: 'k8s' },
        { source: 'k8s', target: 'docker' },
        { source: 'aws', target: 'postgres' },
        { source: 'aws', target: 'redis' },
        
        // Asset connections
        { source: 'assets-root', target: 'customer-db' },
        { source: 'assets-root', target: 'payment-sys' },
        { source: 'assets-root', target: 'auth-service' },
        { source: 'assets-root', target: 'api-gateway' },
        { source: 'customer-db', target: 'postgres' },
        { source: 'auth-service', target: 'redis' },
        
        // Compliance connections
        { source: 'compliance-root', target: 'gdpr' },
        { source: 'compliance-root', target: 'pci-dss' },
        { source: 'compliance-root', target: 'sox' },
        { source: 'compliance-root', target: 'hipaa' },
        { source: 'customer-db', target: 'gdpr' },
        { source: 'payment-sys', target: 'pci-dss' },
        
        // Threat connections
        { source: 'threats-root', target: 'ransomware' },
        { source: 'threats-root', target: 'supply-chain' },
        { source: 'threats-root', target: 'phishing' },
        { source: 'threats-root', target: 'insider' },
        { source: 'ransomware', target: 'customer-db' },
        { source: 'supply-chain', target: 'docker' },
        { source: 'phishing', target: 'auth-service' },
      ]
    }

    try {
      // Fetch real data from the backend
      console.log('Fetching organizational DNA...')
      const graphData = await api.getOrganizationalDNA()
      console.log('Received graph data:', graphData)
      
      // Debug: Log what we received
      console.log('🔍 Received graph data:', graphData)
      console.log('🔍 Nodes length:', graphData?.nodes?.length)
      console.log('🔍 Has data flag:', graphData?.has_data)
      
      // Check if we got real data or need to show empty state
      if (!graphData || graphData.has_data === false || !graphData.nodes || graphData.nodes.length === 0) {
        console.log('❌ No organizational DNA data available')
        setGraphData(null)
        setStats({
          totalNodes: 0,
          technologies: 0,
          assets: 0,
          threats: 0,
          compliance: 0
        })
        return
      }
      
      console.log('✅ Setting graph data with', graphData.nodes.length, 'nodes')
      
      // Use real data since we passed validation
      setGraphData(graphData)
      
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
        const nodeTypes = graphData.nodes.reduce((acc, node) => {
          acc[node.type] = (acc[node.type] || 0) + 1
          return acc
        }, {})
        
        setStats({
          totalNodes: graphData.nodes.length,
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

  // Show empty state only if explicitly no data
  if (!graphData) {
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
              Upload documents and run analysis to build the knowledge graph
            </p>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg border border-slate-700">
              <Play className="w-4 h-4 text-primary-500" />
              <span className="text-sm text-slate-300 font-mono">
                Go to Dashboard → Upload Documents → Run Analysis
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-3 font-mono">
              This will extract entities and relationships from your uploaded documents
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