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
      <div className="min-h-screen bg-slate-950 text-slate-200">
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
              background: '#1e293b',
              color: '#e2e8f0',
              border: '1px solid #475569',
              borderRadius: '8px',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#1e293b',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#1e293b',
              },
            },
          }}
        />
      </div>
    </Router>
  )
}

export default App