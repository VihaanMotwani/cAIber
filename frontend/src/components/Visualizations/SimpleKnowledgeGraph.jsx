import React, { useRef, useEffect, useState } from 'react'
import * as d3 from 'd3'
import { ZoomIn, ZoomOut, RefreshCw, RotateCw } from 'lucide-react'

const SimpleKnowledgeGraph = ({ graphData, onRefresh }) => {
  const svgRef = useRef()
  const [selectedNode, setSelectedNode] = useState(null)
  
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
      case 'organization': return '#60a5fa'
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

  useEffect(() => {
    if (!svgRef.current || !data || !data.nodes || !data.links) {
      console.log('SimpleKnowledgeGraph: Missing data', {
        hasRef: !!svgRef.current,
        hasData: !!data,
        nodeCount: data?.nodes?.length,
        linkCount: data?.links?.length
      })
      return
    }

    console.log('SimpleKnowledgeGraph: Rendering with', data.nodes.length, 'nodes and', data.links.length, 'links')

    // Check if this is a filtered view (fewer nodes than normal)
    const isFiltered = data.nodes.length < 100
    
    let nodesToRender, linksToRender
    
    if (isFiltered) {
      // For filtered views, show ALL nodes even if not connected
      // This allows seeing isolated nodes when filtering
      nodesToRender = data.nodes
      linksToRender = data.links
      console.log('Filtered view: showing all', nodesToRender.length, 'nodes')
    } else {
      // For full view, only show connected nodes to reduce clutter
      const connectedNodeIds = new Set()
      data.links.forEach(link => {
        connectedNodeIds.add(link.source)
        connectedNodeIds.add(link.target)
      })
      
      nodesToRender = data.nodes.filter(node => connectedNodeIds.has(node.id))
      linksToRender = data.links.filter(link => 
        connectedNodeIds.has(link.source) && connectedNodeIds.has(link.target)
      )
      console.log('Full view: filtered to', nodesToRender.length, 'connected nodes only')
    }

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    const width = 800
    const height = 600

    // Create container for zoom/pan
    const container = svg.append('g')

    // Create zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform)
      })

    // Apply zoom to SVG
    svg.call(zoom)

    // Store zoom behavior for controls
    svg.node().zoomBehavior = zoom

    // Create simulation
    const simulation = d3.forceSimulation(nodesToRender)
      .force("link", d3.forceLink(linksToRender).id(d => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(d => (d.size || 10) + 5))

    // Create links
    const link = container.append("g")
      .selectAll("line")
      .data(linksToRender)
      .join("line")
      .attr("stroke", "#3b82f6")
      .attr("stroke-opacity", 0.4)
      .attr("stroke-width", 1.5)

    // Create nodes
    const node = container.append("g")
      .selectAll("g")
      .data(nodesToRender)
      .join("g")
      .style("cursor", "pointer")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))

    // Add circles
    node.append("circle")
      .attr("r", d => Math.max((d.size || 10) / 2, 8))
      .attr("fill", d => getNodeColor(d.type))
      .attr("stroke", "#3b82f6")
      .attr("stroke-width", 1.5)
      .on("click", (event, d) => {
        event.stopPropagation()
        setSelectedNode(d)
        console.log('Clicked node:', d)
      })

    // Add labels
    node.append("text")
      .text(d => d.label.length > 15 ? d.label.substring(0, 15) + '...' : d.label)
      .attr("x", 0)
      .attr("y", d => Math.max((d.size || 10) / 2, 8) + 15)
      .attr("text-anchor", "middle")
      .attr("fill", "#60a5fa")
      .attr("font-size", "10px")
      .attr("font-family", "Space Mono, monospace")
      .style("pointer-events", "none")

    // Update positions on tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y)

      node.attr("transform", d => `translate(${d.x},${d.y})`)
    })

    // Drag functions
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

    // Cleanup
    return () => {
      simulation.stop()
    }
  }, [data])

  const handleZoomIn = () => {
    const svg = d3.select(svgRef.current)
    const zoom = svg.node()?.zoomBehavior
    if (zoom) {
      svg.transition().call(zoom.scaleBy, 1.5)
    }
  }

  const handleZoomOut = () => {
    const svg = d3.select(svgRef.current)
    const zoom = svg.node()?.zoomBehavior
    if (zoom) {
      svg.transition().call(zoom.scaleBy, 0.67)
    }
  }

  const handleResetZoom = () => {
    const svg = d3.select(svgRef.current)
    const zoom = svg.node()?.zoomBehavior
    if (zoom) {
      svg.transition().call(zoom.transform, d3.zoomIdentity)
    }
  }

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh()
    }
  }

  return (
    <div className="relative w-full h-full">
      <div className="w-full h-[600px] bg-black rounded-xl border border-blue-500/40 relative overflow-hidden">
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
            className="p-2 bg-blue-900/20 hover:bg-blue-800/30 rounded-lg transition-colors border border-blue-500/40"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4 text-blue-400" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2 bg-blue-900/20 hover:bg-blue-800/30 rounded-lg transition-colors border border-blue-500/40"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4 text-blue-400" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-2 bg-blue-900/20 hover:bg-blue-800/30 rounded-lg transition-colors border border-blue-500/40"
            title="Reset Zoom"
          >
            <RotateCw className="w-4 h-4 text-blue-400" />
          </button>
          <button
            onClick={handleRefresh}
            className="p-2 bg-blue-900/20 hover:bg-blue-800/30 rounded-lg transition-colors border border-blue-500/40"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4 text-blue-400" />
          </button>
        </div>

        {/* Legend */}
        <div className="absolute top-4 left-4">
          <div className="card p-3">
            <h4 className="text-xs font-mono font-bold text-blue-400 mb-2">NODE TYPES</h4>
            <div className="space-y-1">
              {[
                { type: 'technology', color: '#14b8a6', label: 'TECHNOLOGY' },
                { type: 'business_asset', color: '#8b5cf6', label: 'ASSETS' },
                { type: 'compliance_requirement', color: '#f59e0b', label: 'COMPLIANCE' },
                { type: 'threat_actor', color: '#ef4444', label: 'THREATS' }
              ].map(item => (
                <div key={item.type} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full border border-blue-400" style={{ backgroundColor: item.color }} />
                  <span className="text-xs text-blue-300 font-mono">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Node Info Panel */}
        {selectedNode && (
          <div className="absolute bottom-4 left-4 max-w-sm">
            <div className="card p-4">
              <h3 className="font-mono font-bold text-blue-400 mb-2">{selectedNode.label}</h3>
              <div className="space-y-1 text-sm">
                <p><span className="text-blue-500">TYPE:</span> <span className="text-blue-300 font-mono">{selectedNode.type.toUpperCase()}</span></p>
                <p><span className="text-blue-500">SIZE:</span> <span className="text-blue-300 font-mono">{selectedNode.size}</span></p>
                <p><span className="text-blue-500">ID:</span> <span className="text-blue-300 font-mono text-xs">{selectedNode.id}</span></p>
              </div>
              <button 
                onClick={() => setSelectedNode(null)}
                className="mt-2 text-xs text-blue-500 hover:text-blue-300 font-mono"
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