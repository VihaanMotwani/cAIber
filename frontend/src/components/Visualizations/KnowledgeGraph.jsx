import React, { useRef, useCallback, useState, useEffect } from 'react'
import ForceGraph3D from 'react-force-graph-3d'
import ForceGraph2D from 'react-force-graph-2d'
import { Maximize2, Minimize2, ZoomIn, ZoomOut, RotateCw } from 'lucide-react'

const KnowledgeGraph = ({ graphData, is3D = true }) => {
  const fgRef = useRef()
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })
  const [highlightNodes, setHighlightNodes] = useState(new Set())
  const [highlightLinks, setHighlightLinks] = useState(new Set())
  const [hoverNode, setHoverNode] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)

  useEffect(() => {
    const handleResize = () => {
      const container = document.getElementById('graph-container')
      if (container) {
        setDimensions({
          width: container.clientWidth,
          height: container.clientHeight
        })
      }
    }
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Mock data if no graphData provided
  const data = graphData || {
    nodes: [
      { id: 'org', label: 'Organization', type: 'root', val: 20, color: '#0ea5e9' },
      { id: 'tech', label: 'Technology Stack', type: 'technology', val: 15, color: '#14b8a6' },
      { id: 'aws', label: 'AWS Cloud', type: 'technology', val: 10, color: '#14b8a6' },
      { id: 'k8s', label: 'Kubernetes', type: 'technology', val: 10, color: '#14b8a6' },
      { id: 'db', label: 'PostgreSQL', type: 'technology', val: 8, color: '#14b8a6' },
      { id: 'assets', label: 'Critical Assets', type: 'asset', val: 15, color: '#8b5cf6' },
      { id: 'data', label: 'Customer Data', type: 'asset', val: 12, color: '#8b5cf6' },
      { id: 'api', label: 'Payment API', type: 'asset', val: 10, color: '#8b5cf6' },
      { id: 'compliance', label: 'Compliance', type: 'compliance', val: 12, color: '#f59e0b' },
      { id: 'gdpr', label: 'GDPR', type: 'compliance', val: 8, color: '#f59e0b' },
      { id: 'pci', label: 'PCI-DSS', type: 'compliance', val: 8, color: '#f59e0b' },
      { id: 'threats', label: 'Known Threats', type: 'threat', val: 12, color: '#ef4444' },
      { id: 'ransom', label: 'Ransomware', type: 'threat', val: 8, color: '#ef4444' },
      { id: 'phish', label: 'Phishing', type: 'threat', val: 8, color: '#ef4444' },
    ],
    links: [
      { source: 'org', target: 'tech', value: 3 },
      { source: 'org', target: 'assets', value: 3 },
      { source: 'org', target: 'compliance', value: 2 },
      { source: 'org', target: 'threats', value: 2 },
      { source: 'tech', target: 'aws', value: 2 },
      { source: 'tech', target: 'k8s', value: 2 },
      { source: 'tech', target: 'db', value: 2 },
      { source: 'assets', target: 'data', value: 2 },
      { source: 'assets', target: 'api', value: 2 },
      { source: 'compliance', target: 'gdpr', value: 1 },
      { source: 'compliance', target: 'pci', value: 1 },
      { source: 'threats', target: 'ransom', value: 1 },
      { source: 'threats', target: 'phish', value: 1 },
      { source: 'data', target: 'gdpr', value: 1 },
      { source: 'api', target: 'pci', value: 1 },
    ]
  }

  const handleNodeHover = node => {
    highlightNodes.clear()
    highlightLinks.clear()
    if (node) {
      highlightNodes.add(node)
      node.neighbors?.forEach(neighbor => highlightNodes.add(neighbor))
      node.links?.forEach(link => highlightLinks.add(link))
    }

    setHoverNode(node)
    setHighlightNodes(new Set(highlightNodes))
    setHighlightLinks(new Set(highlightLinks))
  }

  const handleNodeClick = useCallback(node => {
    setSelectedNode(node)
    // Center camera on node
    if (fgRef.current) {
      const distance = 200
      const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z || 0)
      
      fgRef.current.cameraPosition(
        { x: node.x * distRatio, y: node.y * distRatio, z: (node.z || 0) * distRatio },
        node,
        3000
      )
    }
  }, [])

  const handleZoomIn = () => {
    if (fgRef.current) {
      fgRef.current.zoom(1.2, 500)
    }
  }

  const handleZoomOut = () => {
    if (fgRef.current) {
      fgRef.current.zoom(0.8, 500)
    }
  }

  const handleReset = () => {
    if (fgRef.current) {
      fgRef.current.centerAt(0, 0, 1000)
      fgRef.current.zoom(1, 500)
    }
  }

  const paintNode = useCallback((node, ctx) => {
    const label = node.label || node.id
    const fontSize = 12
    ctx.font = `${fontSize}px Inter`
    
    // Node circle
    ctx.fillStyle = node === hoverNode ? '#0ea5e9' : (node.color || '#64748b')
    ctx.beginPath()
    ctx.arc(node.x, node.y, node.val || 5, 0, 2 * Math.PI, false)
    ctx.fill()

    // Node label
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillStyle = '#e2e8f0'
    ctx.fillText(label, node.x, node.y + (node.val || 5) + fontSize)
  }, [hoverNode])

  const Graph = is3D ? ForceGraph3D : ForceGraph2D

  return (
    <div className="relative w-full h-full">
      <div id="graph-container" className="w-full h-[600px] bg-slate-900 rounded-xl border border-purple-500/40">
        <Graph
          ref={fgRef}
          graphData={data}
          width={dimensions.width}
          height={dimensions.height}
          backgroundColor="#0f172a00"
          nodeLabel="label"
          nodeAutoColorBy="type"
          nodeVal="val"
          nodeOpacity={0.9}
          linkWidth={link => highlightLinks.has(link) ? 3 : 1}
          linkOpacity={0.3}
          linkColor={() => '#475569'}
          onNodeHover={handleNodeHover}
          onNodeClick={handleNodeClick}
          {...(is3D ? {
            nodeThreeObject: node => {
              // Custom 3D node rendering can be added here
              return null
            }
          } : {
            nodeCanvasObject: paintNode,
            nodeCanvasObjectMode: () => 'replace'
          })}
        />
      </div>

      {/* Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <button
          onClick={handleZoomIn}
          className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={handleReset}
          className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          title="Reset View"
        >
          <RotateCw className="w-4 h-4" />
        </button>
      </div>

      {/* Node Info Panel */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 max-w-sm">
          <div className="card p-4">
            <h3 className="font-semibold text-primary-400 mb-2">{selectedNode.label}</h3>
            <div className="space-y-1 text-sm">
              <p><span className="text-slate-500">Type:</span> {selectedNode.type}</p>
              <p><span className="text-slate-500">Connections:</span> {selectedNode.neighbors?.length || 0}</p>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute top-4 left-4">
        <div className="card p-3">
          <h4 className="text-xs font-semibold text-slate-400 mb-2">Node Types</h4>
          <div className="space-y-1">
            {[
              { type: 'technology', color: '#14b8a6', label: 'Technology' },
              { type: 'asset', color: '#8b5cf6', label: 'Assets' },
              { type: 'compliance', color: '#f59e0b', label: 'Compliance' },
              { type: 'threat', color: '#ef4444', label: 'Threats' }
            ].map(item => (
              <div key={item.type} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-xs text-slate-400">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default KnowledgeGraph