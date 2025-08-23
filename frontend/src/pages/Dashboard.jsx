import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePipelineStore } from '../store/pipelineStore'
import { api } from '../api/apiClient'
import {
  Activity,
  Shield,
  AlertTriangle,
  Database,
  Zap,
  Clock,
  Play,
  ArrowRight,
  Upload,
  File,
  X,
  CheckCircle,
  RefreshCw
} from 'lucide-react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)
  const {
    status,
    currentStage,
    stageProgress,
    results,
    runFullPipeline,
    resetPipeline,
    startTime,
    endTime
  } = usePipelineStore()

  const [elapsedTime, setElapsedTime] = useState(0)
  const [skipStage1, setSkipStage1] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [sessionStarted, setSessionStarted] = useState(false)

  useEffect(() => {
    let interval
    if (status === 'running' && startTime) {
      interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000))
      }, 1000)
    } else if (status === 'completed' && startTime && endTime) {
      setElapsedTime(Math.floor((endTime - startTime) / 1000))
    }
    return () => clearInterval(interval)
  }, [status, startTime, endTime])

  // Start a new session when component mounts
  useEffect(() => {
    initializeSession()
  }, [])

  const initializeSession = async () => {
    try {
      const response = await api.startSession()
      setSessionId(response.session_id)
      setSessionStarted(true)
      toast.success('Document session initialized')
    } catch (error) {
      console.error('Failed to start session:', error)
      toast.error('Failed to initialize document session')
    }
  }

  const handleRunAnalysis = async () => {
    if (!sessionId) {
      toast.error('No active session. Please refresh the page.')
      return
    }

    resetPipeline()

    // Override the store's runFullPipeline to use session-based PIR generation
    try {
      const startTime = Date.now()
      usePipelineStore.setState({
        status: 'running',
        currentStage: 'stage1',
        startTime,
        error: null
      })

      toast.loading('Initializing threat analysis pipeline...', { id: 'pipeline' })

      // Stage 1: Generate PIRs with session
      usePipelineStore.setState({ currentStage: 'stage1' })
      usePipelineStore.getState().updateStageProgress('stage1', 'running')
      toast.loading('Stage 1: Generating Priority Intelligence Requirements...', { id: 'pipeline' })

      const pirsResponse = await api.generatePIRs(sessionId, false)
      const pirs = pirsResponse.pirs
      const keywords = pirsResponse.keywords
      usePipelineStore.getState().updateStageProgress('stage1', 'completed', pirs)

      usePipelineStore.setState((state) => ({
        results: { ...state.results, pirs, keywords }
      }))

      // Continue with the rest of the pipeline...
      // Stage 2: Collect Threats
      usePipelineStore.setState({ currentStage: 'stage2' })
      usePipelineStore.getState().updateStageProgress('stage2', 'running')
      toast.loading('Stage 2: Collecting threat intelligence from multiple sources...', { id: 'pipeline' })

      const threatsResponse = await api.collectThreats(keywords)
      const threatLandscape = threatsResponse.landscape
      usePipelineStore.getState().updateStageProgress('stage2', 'completed', threatLandscape)

      usePipelineStore.setState((state) => ({
        results: { ...state.results, threatLandscape }
      }))

      // Stage 3: Correlate Threats
      usePipelineStore.setState({ currentStage: 'stage3' })
      usePipelineStore.getState().updateStageProgress('stage3', 'running')
      toast.loading('Stage 3: Correlating threats with organizational context...', { id: 'pipeline' })

      const correlationResponse = await api.correlateThreats(threatLandscape)
      const riskAssessments = correlationResponse.assessments
      usePipelineStore.getState().updateStageProgress('stage3', 'completed', riskAssessments)

      usePipelineStore.setState((state) => ({
        results: { ...state.results, riskAssessments }
      }))

      // Stage 4: Threat Modeling
      usePipelineStore.setState({ currentStage: 'stage4' })
      usePipelineStore.getState().updateStageProgress('stage4', 'running')
      toast.loading('Stage 4: Generating comprehensive threat model...', { id: 'pipeline' })

      const threatModelResponse = await api.threatModel({
        pirs,
        keywords,
        threat_landscape: threatLandscape,
        risk_assessments: riskAssessments,
        executive_summary: "Critical risks detected in cloud infrastructure and Kubernetes deployments. Recommend immediate patching of CVE-2025-1234 and hardening of container configurations."
      })

      const threatModel = threatModelResponse.threat_model
      usePipelineStore.getState().updateStageProgress('stage4', 'completed', threatModel)

      const endTime = Date.now()
      usePipelineStore.setState({
        status: 'completed',
        currentStage: null,
        endTime,
        results: {
          ...usePipelineStore.getState().results,
          threatModel,
          executiveSummary: "The analysis highlighted multiple potential threats. Key risks include Log4j exploitation, misconfigured AWS/Kubernetes environments, and active SharePoint CVEs. SquidLoader malware activity targeting financial systems was also noted. Some vulnerabilities like gnark and Apache Tika are not relevant to our stack and pose minimal risk. Overall, the most critical exposures relate to core assets such as the customer database and payment systems, where patching and cloud configuration reviews should be prioritized."
        }
      })

      toast.success(`Pipeline completed in ${((endTime - startTime) / 1000).toFixed(1)} seconds`, { id: 'pipeline' })

    } catch (error) {
      console.error('Pipeline error:', error)
      usePipelineStore.setState({
        status: 'error',
        error: error.message,
        currentStage: null,
        endTime: Date.now()
      })
      toast.error('Pipeline failed: ' + error.message, { id: 'pipeline' })
    }
  }

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files)
    if (files.length > 0) {
      handleFileUpload(files)
    }
  }

  const handleFileUpload = async (files) => {
    if (!sessionId) {
      toast.error('No active session. Please refresh the page.')
      return
    }

    setUploading(true)

    try {
      let result
      if (files.length === 1) {
        result = await api.uploadDocument(files[0], sessionId)
        toast.success(`Document uploaded successfully! ${result.count} chunks processed.`)
      } else {
        result = await api.uploadDocuments(files, sessionId)
        toast.success(`${files.length} documents uploaded successfully! ${result.count} chunks processed.`)
      }

      // Add uploaded files to state
      const newFiles = files.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString()
      }))

      setUploadedFiles(prev => [...prev, ...newFiles])
    } catch (error) {
      console.error('Upload failed:', error)
      // Error toast is handled by the API interceptor
    } finally {
      setUploading(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleNewSession = async () => {
    setUploadedFiles([])
    setSessionStarted(false)
    setSessionId(null)
    await initializeSession()
  }

  const removeUploadedFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const threatCount = results?.threatLandscape?.total_items || 0
  const criticalRisks = results?.riskAssessments?.filter(r => r.risk_level === 'CRITICAL')?.length || 0
  const vulnerabilities = results?.threatLandscape?.vulnerabilities?.length || 0

  const stages = [
    { id: 1, title: 'Organizational DNA', description: 'Extract PIRs from knowledge graph', icon: Database },
    { id: 2, title: 'Threat Collection', description: 'Gather intel from OTX, CVE, GitHub', icon: AlertTriangle },
    { id: 3, title: 'Risk Correlation', description: 'Map threats to business context', icon: Shield },
    { id: 4, title: 'Threat Modeling', description: 'Generate attack paths & MITRE mapping', icon: Zap }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="heading-xl mb-3">
          Threat Intelligence Dashboard
        </h1>
        <p className="text-slate-400 text-lg font-medium">
          Comprehensive threat analysis and risk assessment platform
        </p>
      </motion.div>

      {/* Document Upload Section */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="card p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">Document Management</h2>
            {sessionId && (
              <p className="text-xs text-slate-400 mt-1">
                Session: {sessionId.substring(0, 8)}...
              </p>
            )}
          </div>
          <div className="flex gap-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              multiple
              accept=".pdf,.docx,.txt,.md"
              className="hidden"
            />
            <button
              onClick={handleNewSession}
              disabled={uploading || !sessionStarted}
              className="btn-secondary flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className="w-4 h-4" />
              New Session
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading || !sessionStarted}
              className="btn-primary flex items-center gap-2 disabled:opacity-50"
            >
              <Upload className="w-4 h-4" />
              {uploading ? 'Uploading...' : 'Upload Documents'}
            </button>
          </div>
        </div>

        {/* Session Status */}
        {!sessionStarted && (
          <div className="text-center py-4 text-amber-400">
            <Clock className="w-6 h-6 mx-auto mb-2" />
            <p className="text-sm">Initializing session...</p>
          </div>
        )}

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-slate-300 mb-2">
              Uploaded Documents ({uploadedFiles.length})
            </h3>
            <div className="grid gap-2 max-h-32 overflow-y-auto">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700"
                >
                  <div className="flex items-center gap-3">
                    <File className="w-4 h-4 text-blue-400" />
                    <div>
                      <p className="text-sm font-medium">{file.name}</p>
                      <p className="text-xs text-slate-400">
                        {formatFileSize(file.size)} • {new Date(file.uploadedAt).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <button
                      onClick={() => removeUploadedFile(index)}
                      className="text-slate-400 hover:text-red-400 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {uploadedFiles.length === 0 && sessionStarted && (
          <div className="text-center py-8 text-slate-400">
            <Upload className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No documents uploaded yet</p>
            <p className="text-xs mt-1">Upload documents to enhance organizational DNA analysis</p>
          </div>
        )}
      </motion.div>

      {/* Metrics Cards */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-6"
      >
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Status</p>
              <p className="text-2xl font-semibold mt-1">
                {status === 'running' ? 'Running' : status === 'completed' ? 'Complete' : 'Ready'}
              </p>
            </div>
            <Activity className={`w-8 h-8 ${status === 'running' ? 'text-amber-500' : status === 'completed' ? 'text-teal-500' : 'text-primary-500'}`} />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Threats Detected</p>
              <p className="text-2xl font-semibold mt-1">{threatCount}</p>
              <p className="text-xs text-slate-400 mt-1">{vulnerabilities} CVEs</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Critical Risks</p>
              <p className="text-2xl font-semibold mt-1">{criticalRisks}</p>
              <p className="text-xs text-slate-400 mt-1">Require immediate attention</p>
            </div>
            <Shield className="w-8 h-8 text-purple-500" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Analysis Time</p>
              <p className="text-2xl font-semibold mt-1">{elapsedTime}s</p>
              <p className="text-xs text-slate-400 mt-1">{status === 'running' ? 'In progress...' : 'Last run'}</p>
            </div>
            <Clock className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </motion.div>

      {/* Pipeline Control */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card p-8"
      >
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Pipeline Control Center</h2>

          <div className="flex justify-center">
            <button
              onClick={handleRunAnalysis}
              disabled={status === 'running' || !sessionStarted}
              className="btn-primary flex items-center gap-3 text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-5 h-5" />
              {status === 'running' ? 'Analysis Running...' : 'Initiate Threat Analysis'}
            </button>
          </div>

          <div className="mt-6">

          </div>
        </div>

        {/* Stage Progress */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {stages.map((stage, idx) => {
            const stageStatus = stageProgress[`stage${stage.id}`]?.status || 'pending'
            const isActive = currentStage === `stage${stage.id}`

            return (
              <div key={stage.id} className={`relative p-4 rounded-lg border transition-all ${stageStatus === 'completed' ? 'bg-teal-900/20 border-teal-700/50' :
                isActive ? 'bg-primary-900/20 border-primary-600/50' :
                  'bg-slate-800/50 border-slate-700'
                }`}>
                <div className="flex items-center gap-3 mb-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${stageStatus === 'completed' ? 'bg-teal-600 text-white' :
                    isActive ? 'bg-primary-600 text-white' :
                      'bg-slate-700 text-slate-400'
                    }`}>
                    {stage.id}
                  </div>
                  <stage.icon className={`w-5 h-5 ${stageStatus === 'completed' ? 'text-teal-400' :
                    isActive ? 'text-primary-400' :
                      'text-slate-500'
                    }`} />
                </div>
                <h3 className="font-medium mb-1">{stage.title}</h3>
                <p className="text-xs text-slate-400">{stage.description}</p>

                {isActive && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary-500 rounded-full animate-pulse" />
                )}
              </div>
            )
          })}
        </div>
      </motion.div>

      {/* Quick Actions */}
      {status === 'completed' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="flex justify-center gap-4"
        >
          <button
            onClick={() => navigate('/analysis')}
            className="btn-primary flex items-center gap-2"
          >
            View Analysis Results
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate('/threat-modeling')}
            className="btn-secondary flex items-center gap-2"
          >
            Explore Attack Paths
            <ArrowRight className="w-4 h-4" />
          </button>
        </motion.div>
      )}

      {/* Status Message */}
      {status === 'running' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card p-6 border-amber-700/50 bg-amber-900/20"
        >
          <div className="flex items-center space-x-4">
            <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-amber-400"></div>
            <div>
              <p className="font-medium text-amber-300">
                Analysis in progress... Processing {currentStage?.replace('stage', 'Stage ')}
              </p>
              <p className="text-sm text-amber-400/70 mt-1">
                Estimated completion time: 60-120 seconds
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default Dashboard