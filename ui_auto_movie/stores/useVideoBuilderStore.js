import React from 'react'
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

// Step definitions
export const STEPS = {
  INPUT: 'input',
  LOADING: 'loading', 
  SCRIPTS: 'scripts',
  EDITING: 'editing',
  MERGING: 'merging',
  VOICEOVER: 'voiceover',
  SOCIAL_MEDIA: 'social-media',
  MEDIA: 'media',
  VIDEO_EFFECTS: 'video-effects',
  VIDEO_GENERATION: 'video-generation',
  VIDEO_PREVIEW: 'video-preview'
}

// Step flow configuration
export const STEP_FLOW = {
  [STEPS.INPUT]: { next: STEPS.LOADING, prev: null },
  [STEPS.LOADING]: { next: STEPS.SCRIPTS, prev: STEPS.INPUT },
  [STEPS.SCRIPTS]: { next: STEPS.VOICEOVER, prev: STEPS.INPUT },
  [STEPS.EDITING]: { next: STEPS.SCRIPTS, prev: STEPS.SCRIPTS },
  [STEPS.MERGING]: { next: STEPS.SCRIPTS, prev: STEPS.SCRIPTS },
  [STEPS.VOICEOVER]: { next: STEPS.SOCIAL_MEDIA, prev: STEPS.SCRIPTS },
  [STEPS.SOCIAL_MEDIA]: { next: STEPS.MEDIA, prev: STEPS.VOICEOVER },
  [STEPS.MEDIA]: { next: STEPS.VIDEO_EFFECTS, prev: STEPS.SOCIAL_MEDIA },
  [STEPS.VIDEO_EFFECTS]: { next: STEPS.VIDEO_GENERATION, prev: STEPS.MEDIA },
  [STEPS.VIDEO_GENERATION]: { next: STEPS.VIDEO_PREVIEW, prev: STEPS.VIDEO_EFFECTS },
  [STEPS.VIDEO_PREVIEW]: { next: null, prev: STEPS.VIDEO_GENERATION }
}

// Initial state
const initialState = {
  // Project metadata
  projectId: null,
  currentStep: STEPS.INPUT,
  lastSaved: null,
  
  // Backend Process Integration
  processId: null,
  processState: 'idle', // idle, starting, running, paused, completed, failed, cancelled
  processStep: null,
  processProgress: 0,
  processError: null,
  processStartedAt: null,
  isBackendProcess: false, // Flag to indicate if using backend process system
  
  // Form data
  formData: {
    userPrompt: '',
    category: 'General',
    language: 'English',
    scriptTypes: ['short', 'medium', 'long'],
    duration: 'medium',
    priority: 'normal'
  },
  
  // Scripts data
  scripts: [],
  selectedScriptIndex: -1,
  editInstructions: '',
  editedScriptContent: '',
  editMode: 'instructions',
  mergeInstructions: '',
  selectedForMerge: [],
  
  // Generation state
  loading: false,
  generationStartTime: null,
  generationDuration: null,
  loadingElapsed: 0,
  
  // Voiceover data
  voiceoverData: null,
  selectedScriptForVoiceover: null,
  selectedVoice: null,
  audioSettings: {
    speed: [1.0],
    pitch: [1.0], 
    volume: [0.8],
    background_music: false,
    background_music_volume: [0.3]
  },
  
  // Social media data
  socialMediaContent: null,
  selectedPlatforms: ['youtube', 'instagram', 'tiktok', 'linkedin', 'twitter', 'facebook'],
  
  // Media data
  selectedMedia: [],
  uploadedFiles: [],
  searchResults: [],
  generatedMedia: [],
  
  // Video effects configuration
  videoEffectsConfig: null,
  
  // Video generation state
  videoGenerationTaskId: null,
  videoGenerationProgress: 0,
  videoGenerationStatus: 'idle',
  videoGenerationError: null,
  generatedVideoUrl: null,
  generatedVideoData: null,
  
  // Progress tracking
  stepProgress: {
    [STEPS.INPUT]: 'not-started',
    [STEPS.SCRIPTS]: 'not-started',
    [STEPS.VOICEOVER]: 'not-started',
    [STEPS.SOCIAL_MEDIA]: 'not-started',
    [STEPS.MEDIA]: 'not-started',
    [STEPS.VIDEO_EFFECTS]: 'not-started',
    [STEPS.VIDEO_GENERATION]: 'not-started',
    [STEPS.VIDEO_PREVIEW]: 'not-started'
  }
}

export const useVideoBuilderStore = create(
  persist(
    (set, get) => ({
      ...initialState,

      // Project management
      createNewProject: (userId) => {
        const projectId = `project_${userId}_${Date.now()}`
        set({
          ...initialState,
          projectId,
          lastSaved: new Date().toISOString()
        })
        return projectId
      },

      loadProject: (projectData) => {
        set({
          ...projectData,
          lastSaved: new Date().toISOString()
        })
      },

      deleteProject: () => {
        set(initialState)
        localStorage.removeItem('video-builder-storage')
      },

      // Complete reset to initial state (for fresh start)
      resetToInitialState: () => {
        set(initialState)
        localStorage.removeItem('video-builder-storage')
      },

      // Step navigation
      setCurrentStep: (step) => {
        const state = get()
        set({
          currentStep: step,
          lastSaved: new Date().toISOString()
        })
      },

      goToNextStep: () => {
        const { currentStep } = get()
        const nextStep = STEP_FLOW[currentStep]?.next
        if (nextStep) {
          get().setCurrentStep(nextStep)
        }
      },

      goToPreviousStep: () => {
        const { currentStep } = get()
        const prevStep = STEP_FLOW[currentStep]?.prev
        if (prevStep) {
          get().setCurrentStep(prevStep)
        }
      },

      // Progress tracking
      updateStepProgress: (step, status) => {
        const state = get()
        set({
          stepProgress: {
            ...state.stepProgress,
            [step]: status
          },
          lastSaved: new Date().toISOString()
        })
      },

      markStepCompleted: (step) => {
        get().updateStepProgress(step, 'completed')
      },

      markStepInProgress: (step) => {
        get().updateStepProgress(step, 'in-progress')
      },

      // Form data management
      updateFormData: (newFormData) => {
        const state = get()
        set({
          formData: { ...state.formData, ...newFormData },
          lastSaved: new Date().toISOString()
        })
      },

      // Scripts management
      setScripts: (scripts) => {
        set({
          scripts,
          lastSaved: new Date().toISOString()
        })
        get().markStepCompleted(STEPS.SCRIPTS)
      },

      setSelectedScript: (index) => {
        set({
          selectedScriptIndex: index,
          lastSaved: new Date().toISOString()
        })
      },

      updateScript: (index, updatedScript) => {
        const state = get()
        const newScripts = [...state.scripts]
        newScripts[index] = updatedScript
        set({
          scripts: newScripts,
          lastSaved: new Date().toISOString()
        })
      },

      // Loading state management
      setLoading: (loading) => {
        set({ 
          loading,
          generationStartTime: loading ? Date.now() : null
        })
      },

      setGenerationDuration: (duration) => {
        set({ generationDuration: duration })
      },

      // Voiceover management
      setVoiceoverData: (data) => {
        set({
          voiceoverData: data,
          lastSaved: new Date().toISOString()
        })
        get().markStepCompleted(STEPS.VOICEOVER)
      },

      setSelectedScriptForVoiceover: (script) => {
        set({
          selectedScriptForVoiceover: script,
          lastSaved: new Date().toISOString()
        })
      },

      setSelectedVoice: (voice) => {
        set({
          selectedVoice: voice,
          lastSaved: new Date().toISOString()
        })
      },

      updateAudioSettings: (settings) => {
        const state = get()
        set({
          audioSettings: { ...state.audioSettings, ...settings },
          lastSaved: new Date().toISOString()
        })
      },

      // Social media management
      setSocialMediaContent: (content) => {
        set({
          socialMediaContent: content,
          lastSaved: new Date().toISOString()
        })
        get().markStepCompleted(STEPS.SOCIAL_MEDIA)
      },

      updateSelectedPlatforms: (platforms) => {
        set({
          selectedPlatforms: platforms,
          lastSaved: new Date().toISOString()
        })
      },

      // Media management
      setSelectedMedia: (media) => {
        set({
          selectedMedia: media,
          lastSaved: new Date().toISOString()
        })
        get().markStepCompleted(STEPS.MEDIA)
      },

      addUploadedFile: (file) => {
        const state = get()
        set({
          uploadedFiles: [...state.uploadedFiles, file],
          lastSaved: new Date().toISOString()
        })
      },

      setUploadedFiles: (files) => {
        set({
          uploadedFiles: files,
          lastSaved: new Date().toISOString()
        })
      },

      setSearchResults: (results) => {
        set({
          searchResults: results,
          lastSaved: new Date().toISOString()
        })
      },

      addGeneratedMedia: (media) => {
        const state = get()
        set({
          generatedMedia: [...state.generatedMedia, ...media],
          lastSaved: new Date().toISOString()
        })
      },

      setGeneratedMedia: (media) => {
        set({
          generatedMedia: media,
          lastSaved: new Date().toISOString()
        })
      },

      clearMediaData: () => {
        set({
          selectedMedia: [],
          uploadedFiles: [],
          searchResults: [],
          generatedMedia: [],
          lastSaved: new Date().toISOString()
        })
      },

      // Video generation management
      setVideoGenerationTaskId: (taskId) => {
        set({
          videoGenerationTaskId: taskId,
          videoGenerationStatus: 'started',
          lastSaved: new Date().toISOString()
        })
        get().markStepInProgress(STEPS.VIDEO_GENERATION)
      },

      updateVideoGenerationProgress: (progress, status, error = null) => {
        set({
          videoGenerationProgress: progress,
          videoGenerationStatus: status,
          videoGenerationError: error,
          lastSaved: new Date().toISOString()
        })
      },

      setGeneratedVideo: (videoData) => {
        set({
          generatedVideoUrl: videoData.url || videoData.output_url,
          generatedVideoData: videoData,
          videoGenerationStatus: 'completed',
          videoGenerationProgress: 100,
          lastSaved: new Date().toISOString()
        })
        get().markStepCompleted(STEPS.VIDEO_GENERATION)
      },

      setGeneratedVideo: (videoData) => {
        set({
          generatedVideoUrl: videoData.url || videoData.output_url,
          generatedVideoData: videoData,
          videoGenerationStatus: 'completed',
          videoGenerationProgress: 100,
          lastSaved: new Date().toISOString()
        })
        get().markStepCompleted(STEPS.VIDEO_GENERATION)
      },

      clearVideoGeneration: () => {
        set({
          videoGenerationTaskId: null,
          videoGenerationProgress: 0,
          videoGenerationStatus: 'idle',
          videoGenerationError: null,
          generatedVideoUrl: null,
          generatedVideoData: null,
          lastSaved: new Date().toISOString()
        })
      },

      // Video effects configuration
      setVideoEffectsConfig: (config) => {
        set({
          videoEffectsConfig: config,
          lastSaved: new Date().toISOString()
        })
      },

      // Editing state management
      setEditMode: (mode) => {
        set({ editMode: mode })
      },

      setEditInstructions: (instructions) => {
        set({ editInstructions: instructions })
      },

      setEditedScriptContent: (content) => {
        set({ editedScriptContent: content })
      },

      // Merge state management
      setSelectedForMerge: (indices) => {
        set({ selectedForMerge: indices })
      },

      setMergeInstructions: (instructions) => {
        set({ mergeInstructions: instructions })
      },

      // Utility functions
      canGoBack: () => {
        const { currentStep } = get()
        return STEP_FLOW[currentStep]?.prev !== null
      },

      canGoNext: () => {
        const { currentStep } = get()
        return STEP_FLOW[currentStep]?.next !== null
      },

      hasUnsavedChanges: () => {
        const { lastSaved } = get()
        if (!lastSaved) return true
        const timeDiff = Date.now() - new Date(lastSaved).getTime()
        return timeDiff > 5000 // Consider changes unsaved if more than 5 seconds since last save
      },

      getProjectSummary: () => {
        const state = get()
        return {
          projectId: state.projectId,
          currentStep: state.currentStep,
          lastSaved: state.lastSaved,
          progress: state.stepProgress,
          hasScripts: state.scripts.length > 0,
          hasVoiceover: !!state.voiceoverData,
          hasSocialMedia: !!state.socialMediaContent,
          prompt: state.formData.userPrompt
        }
      },

      // Auto-save functionality
      autoSave: () => {
        set({ lastSaved: new Date().toISOString() })
      },

      // Reset functions for regeneration
      resetScripts: () => {
        set({
          scripts: [],
          selectedScriptIndex: -1,
          stepProgress: {
            ...get().stepProgress,
            [STEPS.SCRIPTS]: 'not-started',
            [STEPS.VOICEOVER]: 'not-started',
            [STEPS.SOCIAL_MEDIA]: 'not-started'
          }
        })
      },

      resetVoiceover: () => {
        set({
          voiceoverData: null,
          selectedScriptForVoiceover: null,
          stepProgress: {
            ...get().stepProgress,
            [STEPS.VOICEOVER]: 'not-started',
            [STEPS.SOCIAL_MEDIA]: 'not-started'
          }
        })
      },

      resetSocialMedia: () => {
        set({
          socialMediaContent: null,
          stepProgress: {
            ...get().stepProgress,
            [STEPS.SOCIAL_MEDIA]: 'not-started'
          }
        })
      },

      // Backend Process Management
      setProcessId: (id) => {
        set({
          processId: id,
          isBackendProcess: true,
          processStartedAt: new Date().toISOString(),
          lastSaved: new Date().toISOString()
        })
      },

      updateProcessState: (processData) => {
        set({
          processState: processData.status || get().processState,
          processStep: processData.currentStep || processData.current_step || get().processStep,
          processProgress: processData.progress || get().processProgress,
          processError: processData.error || null,
          lastSaved: new Date().toISOString()
        })

        // Update UI step based on process step
        const state = get()
        if (processData.currentStep || processData.current_step) {
          const stepMapping = {
            'input_processing': STEPS.LOADING,
            'script_generation': STEPS.SCRIPTS,
            'voiceover_generation': STEPS.VOICEOVER,
            'social_media_content': STEPS.SOCIAL_MEDIA,
            'media_collection': STEPS.MEDIA,
            'effects_processing': STEPS.VIDEO_EFFECTS,
            'final_assembly': STEPS.VIDEO_EFFECTS
          }
          
          const uiStep = stepMapping[processData.currentStep || processData.current_step]
          if (uiStep && state.currentStep !== uiStep) {
            get().setCurrentStep(uiStep)
          }
        }
      },

      setProcessError: (error) => {
        set({
          processError: error,
          processState: 'failed',
          lastSaved: new Date().toISOString()
        })
      },

      clearProcessState: () => {
        set({
          processId: null,
          processState: 'idle',
          processStep: null,
          processProgress: 0,
          processError: null,
          processStartedAt: null,
          isBackendProcess: false,
          lastSaved: new Date().toISOString()
        })
      },

      // Enhanced form data for backend integration
      updateFormDataForBackend: (formData, userId, sessionId = null) => {
        const state = get()
        const backendFormData = {
          ...state.formData,
          ...formData,
          userId: userId,
          sessionId: sessionId,
          additional_settings: {
            script_types: formData.scriptTypes || state.formData.scriptTypes,
            voice_settings: state.audioSettings,
            social_platforms: state.selectedPlatforms,
            duration: formData.duration || state.formData.duration,
            priority: formData.priority || state.formData.priority,
            ...(formData.additional_settings || {})
          }
        }
        
        set({
          formData: backendFormData,
          lastSaved: new Date().toISOString()
        })
        
        return backendFormData
      },

      // Process result handlers
      handleProcessResults: (step, results) => {
        const state = get()
        
        switch(step) {
          case 'script_generation':
            if (results.scripts) {
              get().setScripts(results.scripts)
            }
            break
            
          case 'voiceover_generation':
            if (results.voiceover_data) {
              get().setVoiceoverData(results.voiceover_data)
            }
            break
            
          case 'social_media_content':
            if (results.social_media_content) {
              get().setSocialMediaContent(results.social_media_content)
            }
            break
            
          case 'media_collection':
            if (results.media_items) {
              get().setGeneratedMedia(results.media_items)
            }
            break
            
          case 'effects_processing':
          case 'final_assembly':
            if (results.video_config) {
              get().setVideoEffectsConfig(results.video_config)
            }
            break
        }
      },

      // Process control methods
      canControlProcess: (action) => {
        const { processState, isBackendProcess } = get()
        if (!isBackendProcess) return false
        
        switch (action) {
          case 'pause':
            return processState === 'running'
          case 'resume':
            return processState === 'paused'
          case 'cancel':
            return ['running', 'paused', 'starting'].includes(processState)
          case 'retry':
            return processState === 'failed'
          default:
            return false
        }
      },

      getProcessDuration: () => {
        const { processStartedAt } = get()
        if (!processStartedAt) return 0
        return Date.now() - new Date(processStartedAt).getTime()
      },

      // Enhanced project summary with process info
      getProcessSummary: () => {
        const state = get()
        return {
          ...state.getProjectSummary(),
          processInfo: {
            id: state.processId,
            state: state.processState,
            step: state.processStep,
            progress: state.processProgress,
            error: state.processError,
            isBackendProcess: state.isBackendProcess,
            duration: state.getProcessDuration(),
            startedAt: state.processStartedAt
          }
        }
      }
    }),
    {
      name: 'video-builder-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => {
        // Helper function to remove large data from media items
        const sanitizeMediaItems = (items) => {
          if (!items || !Array.isArray(items)) return items;
          return items.map(item => ({
            ...item,
            url: item.url ? (item.url.length > 1000 ? '[base64-data-removed]' : item.url) : item.url,
            file: undefined // Remove file object
          }));
        };

        return {
          // Only persist essential data, exclude loading states and large data
          projectId: state.projectId,
          currentStep: state.currentStep,
          lastSaved: state.lastSaved,
          formData: state.formData,
          scripts: state.scripts,
          selectedScriptIndex: state.selectedScriptIndex,
          voiceoverData: state.voiceoverData,
          selectedVoice: state.selectedVoice,
          audioSettings: state.audioSettings,
          socialMediaContent: state.socialMediaContent,
          selectedPlatforms: state.selectedPlatforms,
          // Sanitize media arrays to remove large base64 data
          selectedMedia: sanitizeMediaItems(state.selectedMedia),
          uploadedFiles: sanitizeMediaItems(state.uploadedFiles),
          searchResults: sanitizeMediaItems(state.searchResults),
          generatedMedia: sanitizeMediaItems(state.generatedMedia),
          videoEffectsConfig: state.videoEffectsConfig,
          stepProgress: state.stepProgress,
          generationDuration: state.generationDuration,
          // Backend process state
          processId: state.processId,
          processState: state.processState,
          processStep: state.processStep,
          processProgress: state.processProgress,
          processStartedAt: state.processStartedAt,
          isBackendProcess: state.isBackendProcess
        };
      }
    }
  )
)

// Utility hook for step navigation
export const useStepNavigation = () => {
  const store = useVideoBuilderStore()
  
  return {
    currentStep: store.currentStep,
    canGoBack: store.canGoBack(),
    canGoNext: store.canGoNext(),
    goBack: store.goToPreviousStep,
    goNext: store.goToNextStep,
    setStep: store.setCurrentStep,
    stepProgress: store.stepProgress
  }
}

// Hook for auto-save functionality
export const useAutoSave = (interval = 30000) => {
  const autoSave = useVideoBuilderStore(state => state.autoSave)
  
  React.useEffect(() => {
    const timer = setInterval(() => {
      autoSave()
    }, interval)
    
    return () => clearInterval(timer)
  }, [interval]) // Remove autoSave from dependencies to prevent infinite loop
}

// Hook for backend process integration
export const useVideoProcess = () => {
  const store = useVideoBuilderStore()
  
  return {
    // Process state
    processId: store.processId,
    processState: store.processState,
    processStep: store.processStep,
    processProgress: store.processProgress,
    processError: store.processError,
    isBackendProcess: store.isBackendProcess,
    processStartedAt: store.processStartedAt,
    
    // Actions
    setProcessId: store.setProcessId,
    updateProcessState: store.updateProcessState,
    setProcessError: store.setProcessError,
    clearProcessState: store.clearProcessState,
    handleProcessResults: store.handleProcessResults,
    updateFormDataForBackend: store.updateFormDataForBackend,
    
    // Utilities
    canControlProcess: store.canControlProcess,
    getProcessDuration: store.getProcessDuration,
    getProcessSummary: store.getProcessSummary,
    
    // Computed state
    isActive: ['starting', 'running', 'paused'].includes(store.processState),
    isCompleted: store.processState === 'completed',
    isFailed: store.processState === 'failed',
    isPaused: store.processState === 'paused',
    hasError: Boolean(store.processError)
  }
}