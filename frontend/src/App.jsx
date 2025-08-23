import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import ThreatModeling from './pages/ThreatModeling'
import OrganizationalDNA from './pages/OrganizationalDNA'
import Header from './components/Common/Header'

function App() {
  return (
    <Router>
      <div className="min-h-screen text-slate-200">
        <Header />
        
        <main className="container mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/threat-modeling" element={<ThreatModeling />} />
            <Route path="/organizational-dna" element={<OrganizationalDNA />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <Toaster
          position="bottom-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'rgba(15, 4, 32, 0.95)',
              color: '#e2e8f0',
              border: '1px solid rgba(147, 51, 234, 0.5)',
              borderRadius: '12px',
              backdropFilter: 'blur(20px)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.6), 0 0 16px rgba(147, 51, 234, 0.2)',
            },
            success: {
              iconTheme: {
                primary: '#60a5fa',
                secondary: 'rgba(15, 4, 32, 0.95)',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: 'rgba(15, 4, 32, 0.95)',
              },
            },
          }}
        />
      </div>
    </Router>
  )
}

export default App