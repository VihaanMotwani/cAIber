import React, { useRef, useEffect, useState, useCallback } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { ZoomIn, ZoomOut, RefreshCw, RotateCw } from 'lucide-react'

const ReactForceGraph = ({ graphData, onRefresh }) => {
  const fgRef = useRef()
  const [selectedNode, setSelectedNode] = useState(null)
  
  // Debug the data
  console.log('ReactForceGraph received data:', graphData)
  if (graphData?.nodes) {
    console.log('First node:', graphData.nodes[0])
    console.log('First link:', graphData.links[0])
    console.log('Node count:', graphData.nodes.length)
    console.log('Link count:', graphData.links.length)
  }
  
  // Limit data for performance - take top nodes by size
  let processedData = graphData
  if (graphData && graphData.nodes && graphData.nodes.length > 50) {
    const topNodes = graphData.nodes
      .sort((a, b) => (b.size || 0) - (a.size || 0))
      .slice(0, 50)
    
    const nodeIds = new Set(topNodes.map(n => n.id))
    const filteredLinks = graphData.links.filter(link => 
      nodeIds.has(link.source) && nodeIds.has(link.target)
    )
    
    processedData = {
      nodes: topNodes,
      links: filteredLinks
    }
    console.log('Limited to top 50 nodes:', processedData.nodes.length, 'nodes,', processedData.links.length, 'links')
  }
  
  // Mock data if no graphData provided
  const data = processedData || {
    nodes: [
      { id: 'org-root', label: 'TechCorp Inc.', type: 'organization', size: 25 },
      { id: 'cloud', label: 'Cloud Infrastructure', type: 'technology', size: 18 },
      { id: 'aws', label: 'AWS', type: 'technology', size: 12 },
      { id: 'k8s', label: 'Kubernetes', type: 'technology', size: 12 },
      { id: 'assets-root', label: 'Critical Assets', type: 'asset', size: 18 },
      { id: 'customer-db', label: 'Customer Database', type: 'asset', size: 15 },
      { id: 'payment-sys', label: 'Payment System', type: 'asset', size: 15 },
      { id: 'compliance-root', label: 'Compliance', type: 'compliance', size: 15 },
      { id: 'gdpr', label: 'GDPR', type: 'compliance', size: 10 },
      { id: 'threats-root', label: 'Threats', type: 'threat', size: 15 },
      { id: 'ransomware', label: 'Ransomware', type: 'threat', size: 10 },
    ],
    links: [
      { source: 'org-root', target: 'cloud' },
      { source: 'org-root', target: 'assets-root' },
      { source: 'org-root', target: 'compliance-root' },
      { source: 'org-root', target: 'threats-root' },
      { source: 'cloud', target: 'aws' },
      { source: 'cloud', target: 'k8s' },
      { source: 'assets-root', target: 'customer-db' },
      { source: 'assets-root', target: 'payment-sys' },
      { source: 'compliance-root', target: 'gdpr' },
      { source: 'threats-root', target: 'ransomware' },
      { source: 'customer-db', target: 'gdpr' },
      { source: 'ransomware', target: 'customer-db' },
    ]
  }

  const getNodeColor = (type) => {
    switch (type) {
      case 'organization': return '#00ff41'
      case 'technology': return '#14b8a6'
      case 'business_asset': return '#8b5cf6'
      case 'asset': return '#8b5cf6'
      case 'compliance': return '#f59e0b'
      case 'compliance_requirement': return '#f59e0b'
      case 'threat': return '#ef4444'
      case 'threat_actor': return '#ef4444'
      case 'vulnerability': return '#dc2626'
      case 'business_initiative': return '#8b5cf6'
      case 'geography': return '#f59e0b'
      default: return '#64748b'
    }
  }

  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node)
  }, [])

  const handleZoomIn = () => {
    if (fgRef.current) {
      fgRef.current.zoom(fgRef.current.zoom() * 1.5)
    }
  }

  const handleZoomOut = () => {
    if (fgRef.current) {
      fgRef.current.zoom(fgRef.current.zoom() / 1.5)
    }
  }

  const handleReset = () => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400)
    }
  }

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh()
    }
  }

  return (
    <div className="relative w-full h-full">
      <div className="w-full h-[600px] bg-black rounded-xl border border-matrix-darkgreen relative overflow-hidden">
        <ForceGraph2D
          ref={fgRef}
          graphData={data}
          width={800}
          height={600}
          backgroundColor="#000000"
          nodeLabel="label"
          nodeId="id"
          nodeVal={(node) => Math.max((node.size || 10), 5)}
          nodeColor={(node) => getNodeColor(node.type)}
          nodeRelSize={6}
          linkColor={() => '#00ff41'}
          linkOpacity={0.6}
          linkWidth={1}
          onNodeClick={handleNodeClick}
          enableNodeDrag={true}
          enableZoomInteraction={true}
          enablePanInteraction={true}
          cooldownTicks={100}
          d3AlphaDecay={0.02}
          d3VelocityDecay={0.3}
          onEngineStop={() => {
            setTimeout(() => {
              fgRef.current?.zoomToFit(400, 50)
            }, 100)
          }}
        />

        {/* Controls */}
        <div className="absolute top-4 right-4 flex flex-col gap-2">
          <button
            onClick={handleZoomIn}
            className="p-2 bg-matrix-darkgray hover:bg-matrix-darkgreen rounded-lg transition-colors border border-matrix-darkgreen"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4 text-matrix-green" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2 bg-matrix-darkgray hover:bg-matrix-darkgreen rounded-lg transition-colors border border-matrix-darkgreen"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4 text-matrix-green" />
          </button>
          <button
            onClick={handleReset}
            className="p-2 bg-matrix-darkgray hover:bg-matrix-darkgreen rounded-lg transition-colors border border-matrix-darkgreen"
            title="Reset Zoom"
          >
            <RotateCw className="w-4 h-4 text-matrix-green" />
          </button>
          <button
            onClick={handleRefresh}
            className="p-2 bg-matrix-darkgray hover:bg-matrix-darkgreen rounded-lg transition-colors border border-matrix-darkgreen"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4 text-matrix-green" />
          </button>
        </div>

        {/* Legend */}
        <div className="absolute top-4 left-4">
          <div className="card p-3">
            <h4 className="text-xs font-mono font-bold text-matrix-green mb-2">NODE TYPES</h4>
            <div className="space-y-1">
              {[
                { type: 'technology', color: '#14b8a6', label: 'TECHNOLOGY' },
                { type: 'business_asset', color: '#8b5cf6', label: 'ASSETS' },
                { type: 'compliance_requirement', color: '#f59e0b', label: 'COMPLIANCE' },
                { type: 'threat_actor', color: '#ef4444', label: 'THREATS' }
              ].map(item => (
                <div key={item.type} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full border border-matrix-green" style={{ backgroundColor: item.color }} />
                  <span className="text-xs text-matrix-green font-mono">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Node Info Panel */}
        {selectedNode && (
          <div className="absolute bottom-4 left-4 max-w-sm">
            <div className="card p-4">
              <h3 className="font-mono font-bold text-matrix-green mb-2">{selectedNode.label}</h3>
              <div className="space-y-1 text-sm">
                <p><span className="text-matrix-darkgreen">TYPE:</span> <span className="text-matrix-green font-mono">{selectedNode.type.toUpperCase()}</span></p>
                <p><span className="text-matrix-darkgreen">SIZE:</span> <span className="text-matrix-green font-mono">{selectedNode.size}</span></p>
              </div>
              <button 
                onClick={() => setSelectedNode(null)}
                className="mt-2 text-xs text-matrix-darkgreen hover:text-matrix-green font-mono"
              >
                [CLOSE]
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ReactForceGraph