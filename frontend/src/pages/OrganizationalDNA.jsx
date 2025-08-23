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
  const [riskAssessments, setRiskAssessments] = useState([])
  const [riskLoading, setRiskLoading] = useState(false)
  const [keyRelationships, setKeyRelationships] = useState([])
  const [relationshipsLoading, setRelationshipsLoading] = useState(false)
  const [viewMode, setViewMode] = useState('3d')
  const [filters, setFilters] = useState({
    nodeTypes: [],
    relationshipTypes: [],
    focusNode: '',
    depth: 2
  })

  // Always try to fetch data, but handle empty state gracefully
  useEffect(() => {
    fetchGraphData()
    fetchRiskAssessments() 
    fetchKeyRelationships()
  }, [results])

  const fetchGraphData = async (customFilters = null) => {
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
      // Use custom filters if provided, otherwise use current filters
      const activeFilters = customFilters || filters
      
      // Only pass non-empty filters to API
      const apiFilters = {}
      if (activeFilters.nodeTypes.length > 0) apiFilters.nodeTypes = activeFilters.nodeTypes
      if (activeFilters.relationshipTypes.length > 0) apiFilters.relationshipTypes = activeFilters.relationshipTypes
      if (activeFilters.focusNode.trim()) apiFilters.focusNode = activeFilters.focusNode.trim()
      if (activeFilters.depth && activeFilters.depth !== 2) apiFilters.depth = activeFilters.depth
      
      // Fetch real data from the backend
      console.log('Fetching organizational DNA with filters:', apiFilters)
      const graphData = await api.getOrganizationalDNA(apiFilters)
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

  const fetchRiskAssessments = async () => {
    setRiskLoading(true)
    try {
      // Check if we have results from the pipeline store first
      if (results?.stage3?.threatLandscape) {
        console.log('Using threat landscape from pipeline store')
        const response = await api.correlateThreats(results.stage3.threatLandscape)
        setRiskAssessments(response.assessments || [])
      } else {
        console.log('No threat landscape available, using mock risk data for demo')
        // Mock risk assessments for demo when pipeline hasn't been run
        const mockRiskAssessments = [
          {
            threat_id: "CVE-2024-AWS-001", 
            threat_type: "vulnerability",
            risk_score: 8.5,
            affected_assets: ["Customer Database", "AWS Infrastructure"],
            business_impact: "High - Potential data breach affecting customer PII",
            reasoning: "Critical vulnerability in AWS services directly impacts customer data storage"
          },
          {
            threat_id: "APT-Ransomware-K8s",
            threat_type: "threat_actor", 
            risk_score: 7.2,
            affected_assets: ["Kubernetes Cluster", "Container Registry"],
            business_impact: "Medium-High - Service disruption and potential data encryption",
            reasoning: "Ransomware targeting containerized infrastructure poses significant operational risk"
          },
          {
            threat_id: "Supply-Chain-Docker",
            threat_type: "indicator",
            risk_score: 6.8,
            affected_assets: ["Docker Images", "CI/CD Pipeline"],
            business_impact: "Medium - Compromised deployment pipeline integrity", 
            reasoning: "Supply chain attacks via container images could introduce malicious code"
          }
        ]
        setRiskAssessments(mockRiskAssessments)
      }
    } catch (error) {
      console.error('Failed to fetch risk assessments:', error)
      setRiskAssessments([])
    } finally {
      setRiskLoading(false)
    }
  }

  const fetchKeyRelationships = async () => {
    setRelationshipsLoading(true)
    try {
      // Fetch key relationships directly from Neo4j via the organizational DNA endpoint
      const response = await api.getOrganizationalDNA({})
      
      if (response?.relationships?.length > 0) {
        // Extract meaningful relationships and categorize by importance
        const relationshipImportance = {
          'USES_TECHNOLOGY': 'Critical',
          'HOSTS': 'Strong',
          'REQUIRES_COMPLIANCE': 'Required',
          'PROTECTS': 'Critical',
          'THREATENS': 'High Risk',
          'OPERATES_IN': 'Active',
          'MANAGES': 'Strong',
          'DEPENDS_ON': 'Critical'
        }
        
        // Group relationships by type and pick representative ones
        const groupedRels = {}
        response.relationships.forEach(rel => {
          if (!groupedRels[rel.relationship_type]) {
            groupedRels[rel.relationship_type] = []
          }
          groupedRels[rel.relationship_type].push(rel)
        })
        
        // Create display relationships from our rigged data
        const displayRelationships = []
        
        // Add most important relationships
        Object.entries(groupedRels).forEach(([type, rels]) => {
          if (rels.length > 0 && displayRelationships.length < 5) {
            const rel = rels[0] // Take first relationship of this type
            const importance = relationshipImportance[type] || 'Standard'
            
            displayRelationships.push({
              source: rel.source_name || rel.source,
              target: rel.target_name || rel.target, 
              relationship: type.replace(/_/g, ' ').toLowerCase(),
              importance: importance,
              type: type
            })
          }
        })
        
        setKeyRelationships(displayRelationships)
      } else {
        // Fallback to mock relationships that match our TechCorp profile
        const mockRelationships = [
          { source: 'TechCorp Inc', target: 'AWS', relationship: 'uses technology', importance: 'Critical', type: 'USES_TECHNOLOGY' },
          { source: 'Customer Database', target: 'GDPR', relationship: 'requires compliance', importance: 'Required', type: 'REQUIRES_COMPLIANCE' },
          { source: 'Payment System', target: 'PCI DSS', relationship: 'requires compliance', importance: 'Critical', type: 'REQUIRES_COMPLIANCE' },
          { source: 'Kubernetes', target: 'Docker', relationship: 'depends on', importance: 'Strong', type: 'DEPENDS_ON' },
          { source: 'APT29', target: 'Customer Database', relationship: 'threatens', importance: 'High Risk', type: 'THREATENS' }
        ]
        setKeyRelationships(mockRelationships)
      }
    } catch (error) {
      console.error('Failed to fetch key relationships:', error)
      // Use TechCorp-aligned mock data
      const mockRelationships = [
        { source: 'TechCorp Inc', target: 'AWS', relationship: 'uses technology', importance: 'Critical', type: 'USES_TECHNOLOGY' },
        { source: 'Customer Database', target: 'GDPR', relationship: 'requires compliance', importance: 'Required', type: 'REQUIRES_COMPLIANCE' },
        { source: 'Payment System', target: 'PCI DSS', relationship: 'requires compliance', importance: 'Critical', type: 'REQUIRES_COMPLIANCE' },
        { source: 'Kubernetes', target: 'Docker', relationship: 'depends on', importance: 'Strong', type: 'DEPENDS_ON' },
        { source: 'APT29', target: 'Customer Database', relationship: 'threatens', importance: 'High Risk', type: 'THREATENS' }
      ]
      setKeyRelationships(mockRelationships)
    } finally {
      setRelationshipsLoading(false)
    }
  }

  // Always try to fetch data, but handle empty state gracefully
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
          <h1 className="heading-xl mb-3">
            Organizational DNA
          </h1>
          <p className="text-slate-400 text-lg font-medium">
            Interactive knowledge graph visualization of your organization's digital ecosystem
          </p>
        </div>
        
      </motion.div>

      {/* Filter Panel */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.05 }}
        className="card p-6"
      >
        <div className="flex flex-wrap gap-6 items-center">
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-white">Filters</h3>
          </div>
          
          {/* Node Types Filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-400">Node Types:</span>
            <div className="flex gap-3">
              {[
                { type: 'technology', color: '#10b981', label: 'Tech' },
                { type: 'business_asset', color: '#8b5cf6', label: 'Assets' },
                { type: 'compliance_requirement', color: '#f59e0b', label: 'Compliance' },
                { type: 'threat_actor', color: '#ef4444', label: 'Threats' }
              ].map(item => (
                <button
                  key={item.type}
                  onClick={() => {
                    const newTypes = filters.nodeTypes.includes(item.type)
                      ? filters.nodeTypes.filter(t => t !== item.type)
                      : [...filters.nodeTypes, item.type]
                    
                    // Clear relationship filters when selecting node types for cleaner filtering
                    const newFilters = { ...filters, nodeTypes: newTypes, relationshipTypes: [] }
                    setFilters(newFilters)
                    fetchGraphData(newFilters)
                  }}
                  className={`px-4 py-2 text-sm font-medium rounded-xl border transition-all duration-200 ${
                    filters.nodeTypes.includes(item.type)
                      ? 'text-white shadow-lg transform scale-105'
                      : 'border-slate-600 text-slate-300 hover:border-slate-500 hover:text-white hover:scale-105'
                  }`}
                  style={filters.nodeTypes.includes(item.type) 
                    ? { backgroundColor: item.color, borderColor: item.color, boxShadow: `0 8px 25px -8px ${item.color}40` }
                    : {}
                  }
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          
          {/* Relationship Types Filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-400">Relationships:</span>
            <select
              value={filters.relationshipTypes[0] || ''}
              onChange={(e) => {
                const newFilters = { 
                  ...filters, 
                  relationshipTypes: e.target.value ? [e.target.value] : [],
                  // Clear node filters when selecting relationship types for cleaner filtering
                  nodeTypes: []
                }
                setFilters(newFilters)
                fetchGraphData(newFilters)
              }}
              className="px-4 py-2 text-sm bg-slate-800/80 border border-slate-600 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 backdrop-blur-sm transition-all duration-200"
            >
              <option value="">All Relationships</option>
              <option value="USES_TECHNOLOGY">Uses Technology</option>
              <option value="DEPENDS_ON">Depends On</option>
              <option value="INTEGRATES_WITH">Integrates With</option>
              <option value="DEPLOYED_TO">Deployed To</option>
              <option value="OPERATES_IN">Operates In</option>
              <option value="PARTNERS_WITH">Partners With</option>
              <option value="TARGETS">Targets</option>
              <option value="SUPPORTS">Supports</option>
              <option value="REQUIRES">Requires</option>
            </select>
          </div>
          
          
          {/* Reset Filters */}
          <button
            onClick={() => {
              const resetFilters = { nodeTypes: [], relationshipTypes: [], focusNode: '', depth: 2 }
              setFilters(resetFilters)
              fetchGraphData(resetFilters)
            }}
            className="px-4 py-2 text-sm border border-slate-600 text-slate-400 hover:border-emerald-500 hover:text-emerald-400 rounded-xl transition-all duration-200 hover:scale-105"
          >
            Reset
          </button>
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

          {relationshipsLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            </div>
          ) : keyRelationships.length > 0 ? (
            <div className="space-y-3">
              {keyRelationships.slice(0, 5).map((rel, index) => {
                const getBadgeColor = (importance) => {
                  switch(importance) {
                    case 'Critical': return 'badge-red'
                    case 'High Risk': return 'badge-red' 
                    case 'Required': return 'badge-amber'
                    case 'Strong': return 'badge-primary'
                    default: return 'badge-gray'
                  }
                }
                
                return (
                  <div key={index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <span className="text-sm">
                      {rel.source} → {rel.target}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-500 capitalize">{rel.relationship}</span>
                      <span className={`badge ${getBadgeColor(rel.importance)}`}>
                        {rel.importance}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <Network className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No key relationships found</p>
              <p className="text-xs mt-1">Build organizational DNA to see relationships</p>
            </div>
          )}
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Risk Assessments</h3>
          
          {riskLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            </div>
          ) : riskAssessments.length > 0 ? (
            <div className="space-y-3">
              {riskAssessments.slice(0, 5).map((assessment, index) => {
                const getRiskColor = (score) => {
                  if (score >= 8) return 'red'
                  if (score >= 6) return 'amber' 
                  return 'emerald'
                }
                const getRiskLabel = (score) => {
                  if (score >= 8) return 'HIGH RISK'
                  if (score >= 6) return 'MEDIUM RISK'
                  return 'LOW RISK'
                }
                
                const riskColor = getRiskColor(assessment.risk_score)
                const riskLabel = getRiskLabel(assessment.risk_score)
                
                return (
                  <div 
                    key={assessment.threat_id || index}
                    className={`p-3 bg-${riskColor}-900/20 rounded-lg border border-${riskColor}-900/30`}
                    title={assessment.reasoning}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">{assessment.threat_id}</span>
                      <div className="flex items-center gap-2">
                        <span className={`text-${riskColor}-400 text-xs font-medium`}>
                          {riskLabel} ({assessment.risk_score}/10)
                        </span>
                      </div>
                    </div>
                    <div className="text-xs text-slate-400 mb-1">
                      <strong>Assets:</strong> {Array.isArray(assessment.affected_assets) 
                        ? assessment.affected_assets.join(', ') 
                        : assessment.affected_assets}
                    </div>
                    <div className="text-xs text-slate-500 truncate">
                      {assessment.business_impact}
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No risk assessments available</p>
              <p className="text-xs mt-1">Run the full pipeline to generate threat correlations</p>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}

export default OrganizationalDNA