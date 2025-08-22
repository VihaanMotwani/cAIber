import axios from 'axios'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || 'An error occurred'
    toast.error(message)
    return Promise.reject(error)
  }
)

export const api = {
  // Stage 1: Generate PIRs
  generatePIRs: async () => {
    const response = await apiClient.get('/generate-pirs')
    return response.data
  },

  // Stage 2: Collect Threats
  collectThreats: async (pirKeywords) => {
    const response = await apiClient.post('/collect-threats', pirKeywords)
    return response.data
  },

  // Stage 3: Correlate Threats
  correlateThreats: async (threatLandscape) => {
    const response = await apiClient.post('/correlate-threats', threatLandscape)
    return response.data
  },

  // Combined: Collect and Correlate
  collectAndCorrelate: async (pirKeywords) => {
    const response = await apiClient.post('/collect-and-correlate', pirKeywords)
    return response.data
  },

  // Full Pipeline
  runFullPipeline: async () => {
    const response = await apiClient.post('/run-complete-pipeline')
    return response.data
  },

  threatModel: async (intelligenceData) => {
    const response = await apiClient.post('/threat-model', intelligenceData)
    return response.data
  }
}

export default apiClient