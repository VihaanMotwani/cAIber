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
    <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-primary-500" />
            <div>
              <h1 className="text-xl font-semibold text-gradient">
                cAIber
              </h1>
              <p className="text-xs text-slate-500">Threat Intelligence Platform</p>
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
                    ? "bg-primary-600 text-white shadow-lg shadow-primary-600/25"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                )}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            ))}
          </nav>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2 px-3 py-1 bg-teal-900/30 rounded-full border border-teal-700/50">
              <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-teal-400">ONLINE</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header