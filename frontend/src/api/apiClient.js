// apiClient.js
import axios from 'axios'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail || 'An error occurred'
    toast.error(message)
    return Promise.reject(err)
  }
)

export const api = {
  // Start an upload session
  startSession: async () => {
    const res = await apiClient.post('/documents/start')
    return res.data // { session_id }
  },

  // Upload ONE file (session_id required)
  uploadDocument: async (file, sessionId) => {
    const fd = new FormData()
    fd.append('file', file)
    // Let the browser set multipart boundary; don't set Content-Type manually
    const res = await axios.post(
      `${API_URL}/upload?session_id=${encodeURIComponent(sessionId)}`,
      fd
    )
    return res.data
  },

  // Upload MANY files (session_id required)
  uploadDocuments: async (files, sessionId) => {
    const fd = new FormData()
    files.forEach((f) => fd.append('files', f))
    const res = await axios.post(
      `${API_URL}/upload-batch?session_id=${encodeURIComponent(sessionId)}`,
      fd
    )
    return res.data
  },

  // Stage 1 now POSTs with session_id
  generatePIRs: async (sessionId, clearExisting = false) => {
    const res = await apiClient.post('/generate-pirs', {
      session_id: sessionId,
      clear_existing: clearExisting,
    })
    return res.data
  },

  // Stage 2–4 unchanged
  collectThreats: async (pirKeywords) => {
    const res = await apiClient.post('/collect-threats', pirKeywords)
    return res.data
  },
  correlateThreats: async (threatLandscape) => {
    const res = await apiClient.post('/correlate-threats', threatLandscape)
    return res.data
  },
  collectAndCorrelate: async (pirKeywords) => {
    const res = await apiClient.post('/collect-and-correlate', pirKeywords)
    return res.data
  },
  runFullPipeline: async () => {
    const res = await apiClient.post('/run-complete-pipeline')
    return res.data
  },
  threatModel: async (intelligenceData) => {
    const res = await apiClient.post('/threat-model', intelligenceData)
    return res.data
  },
}

export default apiClient
