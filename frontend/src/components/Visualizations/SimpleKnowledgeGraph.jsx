import React, { useRef, useEffect, useState } from 'react'
import * as d3 from 'd3'
import { ZoomIn, ZoomOut, RefreshCw } from 'lucide-react'

const SimpleKnowledgeGraph = ({ graphData, onRefresh }) => {
  const svgRef = useRef()
  const [selectedNode, setSelectedNode] = useState(null)
  const [zoomBehavior, setZoomBehavior] = useState(null)
  
  // Mock data if no graphData provided
  const data = graphData || {
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
      case 'asset': return '#8b5cf6'
      case 'compliance': return '#f59e0b'
      case 'threat': return '#ef4444'
      default: return '#64748b'
    }
  }

  useEffect(() => {
    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    const width = 800
    const height = 600

    // Create zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform)
      })
    
    // Apply zoom to SVG
    svg.call(zoom)
    setZoomBehavior(zoom)
    
    // Create container group for all graph elements
    const container = svg.append('g')

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))

    const link = container.append("g")
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("stroke", "#00ff41")
      .attr("stroke-opacity", 0.3)
      .attr("stroke-width", 2)

    const node = container.append("g")
      .selectAll("g")
      .data(data.nodes)
      .join("g")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))

    node.append("circle")
      .attr("r", d => d.size || 10)
      .attr("fill", d => getNodeColor(d.type))
      .attr("stroke", "#00ff41")
      .attr("stroke-width", 2)
      .on("click", (event, d) => {
        setSelectedNode(d)
      })

    node.append("text")
      .text(d => d.label)
      .attr("x", 0)
      .attr("y", d => (d.size || 10) + 20)
      .attr("text-anchor", "middle")
      .attr("fill", "#00ff41")
      .attr("font-size", "12px")
      .attr("font-family", "Space Mono, monospace")

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y)

      node.attr("transform", d => `translate(${d.x},${d.y})`)
    })

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event, d) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }

    return () => {
      simulation.stop()
    }
  }, [data])

  const handleZoomIn = () => {
    const svg = d3.select(svgRef.current)
    if (zoomBehavior) {
      svg.transition().call(zoomBehavior.scaleBy, 1.5)
    }
  }

  const handleZoomOut = () => {
    const svg = d3.select(svgRef.current)
    if (zoomBehavior) {
      svg.transition().call(zoomBehavior.scaleBy, 0.67)
    }
  }

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh()
    }
  }

  const handleReset = () => {
    const svg = d3.select(svgRef.current)
    if (zoomBehavior) {
      svg.transition().call(zoomBehavior.transform, d3.zoomIdentity)
    }
  }

  return (
    <div className="relative w-full h-full">
      <div className="w-full h-[600px] bg-black rounded-xl border border-matrix-darkgreen relative overflow-hidden">
        <svg
          ref={svgRef}
          width="100%"
          height="100%"
          viewBox="0 0 800 600"
          className="w-full h-full"
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
                { type: 'asset', color: '#8b5cf6', label: 'ASSETS' },
                { type: 'compliance', color: '#f59e0b', label: 'COMPLIANCE' },
                { type: 'threat', color: '#ef4444', label: 'THREATS' }
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

export default SimpleKnowledgeGraph