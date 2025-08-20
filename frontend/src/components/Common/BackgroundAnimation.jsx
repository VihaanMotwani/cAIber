import React, { useRef, useEffect } from 'react'
import * as THREE from 'three'

const BackgroundAnimation = () => {
  const mountRef = useRef(null)

  useEffect(() => {
    const mount = mountRef.current
    const width = mount.clientWidth
    const height = mount.clientHeight

    // Scene setup
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
    
    renderer.setSize(width, height)
    renderer.setPixelRatio(window.devicePixelRatio)
    mount.appendChild(renderer.domElement)

    // Create particles
    const particlesGeometry = new THREE.BufferGeometry()
    const particleCount = 1000
    const positions = new Float32Array(particleCount * 3)
    const colors = new Float32Array(particleCount * 3)

    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 50
      positions[i + 1] = (Math.random() - 0.5) * 50
      positions[i + 2] = (Math.random() - 0.5) * 50

      // Cyber colors
      const colorChoice = Math.random()
      if (colorChoice < 0.33) {
        colors[i] = 0 // Cyan
        colors[i + 1] = 1
        colors[i + 2] = 1
      } else if (colorChoice < 0.66) {
        colors[i] = 0.72 // Purple
        colors[i + 1] = 0.16
        colors[i + 2] = 0.87
      } else {
        colors[i] = 0 // Green
        colors[i + 1] = 1
        colors[i + 2] = 0.53
      }
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

    const particlesMaterial = new THREE.PointsMaterial({
      size: 0.05,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending
    })

    const particles = new THREE.Points(particlesGeometry, particlesMaterial)
    scene.add(particles)

    // Create connecting lines
    const linesGeometry = new THREE.BufferGeometry()
    const linePositions = new Float32Array(200 * 3)
    const lineColors = new Float32Array(200 * 3)

    for (let i = 0; i < 200 * 3; i += 3) {
      linePositions[i] = (Math.random() - 0.5) * 30
      linePositions[i + 1] = (Math.random() - 0.5) * 30
      linePositions[i + 2] = (Math.random() - 0.5) * 30
      
      lineColors[i] = 0
      lineColors[i + 1] = 1
      lineColors[i + 2] = 1
    }

    linesGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3))
    linesGeometry.setAttribute('color', new THREE.BufferAttribute(lineColors, 3))

    const linesMaterial = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.2,
      blending: THREE.AdditiveBlending
    })

    const lines = new THREE.LineSegments(linesGeometry, linesMaterial)
    scene.add(lines)

    camera.position.z = 20

    // Animation
    const animate = () => {
      requestAnimationFrame(animate)
      
      particles.rotation.x += 0.0005
      particles.rotation.y += 0.001
      lines.rotation.x -= 0.0003
      lines.rotation.y -= 0.0007

      renderer.render(scene, camera)
    }

    animate()

    // Handle resize
    const handleResize = () => {
      const width = mount.clientWidth
      const height = mount.clientHeight
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      mount.removeChild(renderer.domElement)
      renderer.dispose()
    }
  }, [])

  return (
    <div 
      ref={mountRef} 
      className="fixed inset-0 z-0 opacity-30"
      style={{ pointerEvents: 'none' }}
    />
  )
}

export default BackgroundAnimation