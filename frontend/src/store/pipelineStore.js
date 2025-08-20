import { create } from 'zustand'
import { api } from '../api/apiClient'
import toast from 'react-hot-toast'

export const usePipelineStore = create((set, get) => ({
  // State
  status: 'idle', // idle, running, completed, error
  currentStage: null,
  stageProgress: {
    stage1: { status: 'pending', data: null },
    stage2: { status: 'pending', data: null },
    stage3: { status: 'pending', data: null },
    stage4: { status: 'pending', data: null },
  },
  results: {
    pirs: null,
    keywords: null,
    threatLandscape: null,
    riskAssessments: null,
    executiveSummary: null,
    threatModel: null,
  },
  startTime: null,
  endTime: null,
  error: null,

  // Actions
  resetPipeline: () => set({
    status: 'idle',
    currentStage: null,
    stageProgress: {
      stage1: { status: 'pending', data: null },
      stage2: { status: 'pending', data: null },
      stage3: { status: 'pending', data: null },
      stage4: { status: 'pending', data: null },
    },
    results: {
      pirs: null,
      keywords: null,
      threatLandscape: null,
      riskAssessments: null,
      executiveSummary: null,
      threatModel: null,
    },
    startTime: null,
    endTime: null,
    error: null,
  }),

  updateStageProgress: (stage, status, data = null) => set((state) => ({
    stageProgress: {
      ...state.stageProgress,
      [stage]: { status, data },
    },
  })),

  runFullPipeline: async () => {
    const startTime = Date.now()
    set({ 
      status: 'running', 
      currentStage: 'stage1',
      startTime,
      error: null 
    })

    try {
      toast.loading('Initializing threat analysis pipeline...', { id: 'pipeline' })
      
      // Stage 1: Generate PIRs
      set({ currentStage: 'stage1' })
      get().updateStageProgress('stage1', 'running')
      toast.loading('Stage 1: Generating Priority Intelligence Requirements...', { id: 'pipeline' })
      
      const pirsResponse = await api.generatePIRs()
      const pirs = pirsResponse.pirs
      get().updateStageProgress('stage1', 'completed', pirs)
      
      // Extract keywords from PIRs (mock for now)
      const keywords = {
        technologies: ['kubernetes', 'azure', 'docker', 'aws'],
        threats: ['ransomware', 'phishing', 'supply-chain'],
        geographies: ['europe', 'us-east', 'asia-pacific'],
        compliance: ['gdpr', 'hipaa', 'pci-dss']
      }
      
      set((state) => ({
        results: { ...state.results, pirs, keywords }
      }))

      // Stage 2: Collect Threats
      set({ currentStage: 'stage2' })
      get().updateStageProgress('stage2', 'running')
      toast.loading('Stage 2: Collecting threat intelligence from multiple sources...', { id: 'pipeline' })
      
      const threatsResponse = await api.collectThreats(keywords)
      const threatLandscape = threatsResponse.landscape
      get().updateStageProgress('stage2', 'completed', threatLandscape)
      
      set((state) => ({
        results: { ...state.results, threatLandscape }
      }))

      // Stage 3: Correlate Threats
      set({ currentStage: 'stage3' })
      get().updateStageProgress('stage3', 'running')
      toast.loading('Stage 3: Correlating threats with organizational context...', { id: 'pipeline' })
      
      const correlationResponse = await api.correlateThreats(threatLandscape)
      const riskAssessments = correlationResponse.assessments
      get().updateStageProgress('stage3', 'completed', riskAssessments)
      
      // Stage 4: Threat Modeling (mock for now)
      set({ currentStage: 'stage4' })
      get().updateStageProgress('stage4', 'running')
      toast.loading('Stage 4: Generating comprehensive threat model...', { id: 'pipeline' })
      
      // Simulate threat modeling
      await new Promise(resolve => setTimeout(resolve, 2000))
      const threatModel = {
        attack_paths: [
          {
            path_description: "Supply chain attack via compromised dependency",
            steps: [
              {
                step: 1,
                action: "Attacker compromises popular npm package",
                mitre_attack: "Initial Access (T1195): Supply Chain Compromise",
                stride_classification: "Tampering",
                justification: "Malicious code injection into trusted component"
              },
              {
                step: 2,
                action: "Malicious package deployed to production",
                mitre_attack: "Execution (T1059): Command and Scripting Interpreter",
                stride_classification: "Elevation of Privilege",
                justification: "Code executes with application privileges"
              }
            ]
          }
        ]
      }
      
      get().updateStageProgress('stage4', 'completed', threatModel)
      
      const endTime = Date.now()
      set({
        status: 'completed',
        currentStage: null,
        endTime,
        results: {
          ...get().results,
          riskAssessments,
          threatModel,
          executiveSummary: "Analysis complete: Identified critical threats requiring immediate attention."
        }
      })
      
      toast.success(`Pipeline completed in ${((endTime - startTime) / 1000).toFixed(1)} seconds`, { id: 'pipeline' })
      
    } catch (error) {
      console.error('Pipeline error:', error)
      set({ 
        status: 'error', 
        error: error.message,
        currentStage: null,
        endTime: Date.now()
      })
      toast.error('Pipeline failed: ' + error.message, { id: 'pipeline' })
    }
  },

  runStage: async (stage) => {
    set({ status: 'running', currentStage: stage })
    
    try {
      switch(stage) {
        case 'stage1':
          const pirsResponse = await api.generatePIRs()
          get().updateStageProgress('stage1', 'completed', pirsResponse.pirs)
          set((state) => ({
            results: { ...state.results, pirs: pirsResponse.pirs }
          }))
          toast.success('PIRs generated successfully')
          break
          
        case 'stage2':
          // Need keywords from stage 1
          if (!get().results.keywords) {
            throw new Error('Keywords required from Stage 1')
          }
          const threatsResponse = await api.collectThreats(get().results.keywords)
          get().updateStageProgress('stage2', 'completed', threatsResponse.landscape)
          set((state) => ({
            results: { ...state.results, threatLandscape: threatsResponse.landscape }
          }))
          toast.success('Threats collected successfully')
          break
          
        case 'stage3':
          // Need threat landscape from stage 2
          if (!get().results.threatLandscape) {
            throw new Error('Threat landscape required from Stage 2')
          }
          const correlationResponse = await api.correlateThreats(get().results.threatLandscape)
          get().updateStageProgress('stage3', 'completed', correlationResponse.assessments)
          set((state) => ({
            results: { ...state.results, riskAssessments: correlationResponse.assessments }
          }))
          toast.success('Risk correlation completed')
          break
          
        default:
          throw new Error('Invalid stage')
      }
      
      set({ status: 'idle', currentStage: null })
      
    } catch (error) {
      console.error('Stage error:', error)
      set({ status: 'error', error: error.message, currentStage: null })
      toast.error('Stage failed: ' + error.message)
    }
  }
}))

export default usePipelineStore