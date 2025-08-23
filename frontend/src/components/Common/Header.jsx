import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Shield, Activity, Target, Home, Network } from 'lucide-react'
import clsx from 'clsx'

const Header = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/organizational-dna', label: 'Organizational DNA', icon: Network },
    { path: '/analysis', label: 'Analysis', icon: Activity },
    { path: '/threat-modeling', label: 'Threat Model', icon: Target },
  ]

  return (
    <header className="bg-black/90 backdrop-blur-md border-b border-purple-500/40 sticky top-0 z-40" style={{boxShadow: '0 0 30px rgba(147, 51, 234, 0.3)'}}>
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-purple-400" />
            <div>
              <h1 className="text-xl font-semibold text-gradient">
                cAIber
              </h1>
              <p className="text-xs font-medium text-purple-300">AI-Powered Cyber Defense Platform</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-1">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={clsx(
                  "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  location.pathname === path
                    ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg"
                    : "text-purple-300 hover:text-purple-100 hover:bg-purple-500/10"
                )}
                style={location.pathname === path ? {boxShadow: '0 0 20px rgba(147, 51, 234, 0.5)'} : {}}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            ))}
          </nav>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2 px-3 py-1 bg-purple-500/15 rounded-full border border-purple-400">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-purple-300">ONLINE</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header