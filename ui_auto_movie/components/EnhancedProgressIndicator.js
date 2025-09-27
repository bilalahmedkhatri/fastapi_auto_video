'use client'

import React from 'react'
import { Check, Clock, Play, Pause, AlertCircle } from 'lucide-react'
import { useVideoBuilderStore, STEPS } from '@/stores/useVideoBuilderStore'

const EnhancedProgressIndicator = ({ allowStepNavigation = false }) => {
  const currentStep = useVideoBuilderStore(state => state.currentStep)
  const stepProgress = useVideoBuilderStore(state => state.stepProgress)
  const setCurrentStep = useVideoBuilderStore(state => state.setCurrentStep)
  const lastSaved = useVideoBuilderStore(state => state.lastSaved)
  const loading = useVideoBuilderStore(state => state.loading)

  const stepConfig = [
    { 
      step: STEPS.INPUT, 
      label: 'Script Input', 
      icon: '✏️',
      description: 'Enter your video topic and preferences'
    },
    { 
      step: STEPS.LOADING, 
      label: 'Generating', 
      icon: '⏳',
      description: 'AI is creating your scripts'
    },
    { 
      step: STEPS.SCRIPTS, 
      label: 'Script Selection', 
      icon: '📋',
      description: 'Choose and edit your preferred script'
    },
    { 
      step: STEPS.VOICEOVER, 
      label: 'Voiceover', 
      icon: '🎵',
      description: 'Generate voice narration'
    },
    {
      step: STEPS.SOCIAL_MEDIA, 
      label: 'Social Media', 
      icon: '📱',
      description: 'Create promotional content'
    },
    {
      step: STEPS.MEDIA, 
      label: 'Media Selection', 
      icon: '🎬',
      description: 'Choose images and videos'
    },
    {
      step: STEPS.VIDEO_EFFECTS, 
      label: 'Video Effects', 
      icon: '🎨',
      description: 'Configure visual effects'
    }
  ]

  const getStepStatus = (step) => {
    if (step === currentStep && loading) return 'loading'
    if (step === currentStep) return 'current'
    return stepProgress[step] || 'not-started'
  }

  const getStepIcon = (step, status) => {
    const config = stepConfig.find(s => s.step === step)
    
    switch(status) {
      case 'completed':
        return <Check className="h-5 w-5 text-white" />
      case 'current':
        return <Play className="h-5 w-5 text-white" />
      case 'loading':
        return <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
      case 'in-progress':
        return <Pause className="h-5 w-5 text-white" />
      default:
        return <span className="text-xl">{config?.icon}</span>
    }
  }

  const getStepColor = (status) => {
    switch(status) {
      case 'completed':
        return 'bg-green-500 ring-green-200'
      case 'current':
        return 'bg-blue-500 ring-blue-200'
      case 'loading':
        return 'bg-blue-500 ring-blue-200 animate-pulse'
      case 'in-progress':
        return 'bg-yellow-500 ring-yellow-200'
      default:
        return 'bg-gray-300 dark:bg-gray-600'
    }
  }

  const canNavigateToStep = (step) => {
    if (!allowStepNavigation) return false
    
    const stepIndex = stepConfig.findIndex(s => s.step === step)
    const currentIndex = stepConfig.findIndex(s => s.step === currentStep)
    
    // Can navigate to completed steps or adjacent steps
    return stepProgress[step] === 'completed' || 
           Math.abs(stepIndex - currentIndex) <= 1
  }

  const handleStepClick = (step) => {
    if (canNavigateToStep(step) && step !== currentStep) {
      setCurrentStep(step)
    }
  }

  const formatLastSaved = () => {
    if (!lastSaved) return null
    
    const date = new Date(lastSaved)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffMins < 1) return 'Auto-saved just now'
    if (diffMins < 60) return `Auto-saved ${diffMins}m ago`
    return `Auto-saved ${Math.floor(diffMins / 60)}h ago`
  }

  const getCompletionPercentage = () => {
    const completedSteps = Object.values(stepProgress).filter(status => status === 'completed').length
    return Math.round((completedSteps / Object.keys(stepProgress).length) * 100)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
              🎬 Video Creation Workflow
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {getCompletionPercentage()}% Complete
            </p>
          </div>
          
          {lastSaved && (
            <div className="text-right">
              <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                <Clock className="h-3 w-3" />
                {formatLastSaved()}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Progress Steps */}
      <div className="p-6">
        {/* Overall Progress Bar */}
        <div className="mb-6">
          <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${getCompletionPercentage()}%` }}
            />
          </div>
        </div>

        {/* Step Indicators */}
        <div className="relative">
          {/* Connection Lines */}
          <div className="absolute top-6 left-6 right-6 h-0.5 bg-gray-200 dark:bg-gray-600 -z-10">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
              style={{ 
                width: `${(stepConfig.findIndex(s => s.step === currentStep) / (stepConfig.length - 1)) * 100}%` 
              }}
            />
          </div>

          {/* Step Circles */}
          <div className="flex justify-between items-start">
            {stepConfig.map((config, index) => {
              const status = getStepStatus(config.step)
              const isClickable = canNavigateToStep(config.step)
              
              return (
                <div 
                  key={config.step} 
                  className="flex flex-col items-center flex-1"
                >
                  {/* Step Circle */}
                  <div 
                    className={`
                      relative w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 mb-3
                      ${getStepColor(status)}
                      ${status === 'current' ? 'ring-4 ring-blue-200 dark:ring-blue-800 scale-110' : ''}
                      ${isClickable ? 'cursor-pointer hover:scale-105' : 'cursor-default'}
                      ${status === 'loading' ? 'animate-pulse' : ''}
                    `}
                    onClick={() => handleStepClick(config.step)}
                    title={isClickable ? `Navigate to ${config.label}` : config.description}
                  >
                    {getStepIcon(config.step, status)}
                    
                    {/* Status Indicator */}
                    {status === 'in-progress' && (
                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
                        <AlertCircle className="h-2.5 w-2.5 text-yellow-800" />
                      </div>
                    )}
                  </div>

                  {/* Step Label */}
                  <div className="text-center max-w-20">
                    <h3 className={`text-sm font-medium mb-1 ${
                      status === 'current' 
                        ? 'text-blue-600 dark:text-blue-400' 
                        : 'text-gray-600 dark:text-gray-400'
                    }`}>
                      {config.label}
                    </h3>
                    
                    {/* Status Text */}
                    {status === 'current' && (
                      <div className="text-xs text-blue-500 dark:text-blue-400 font-medium animate-pulse">
                        {loading ? 'Processing...' : 'Active'}
                      </div>
                    )}
                    
                    {status === 'completed' && (
                      <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                        Completed
                      </div>
                    )}
                    
                    {status === 'in-progress' && (
                      <div className="text-xs text-yellow-600 dark:text-yellow-400 font-medium">
                        In Progress
                      </div>
                    )}
                  </div>

                  {/* Connection Line to Next Step */}
                  {index < stepConfig.length - 1 && (
                    <div className="hidden" /> // Placeholder for spacing
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Current Step Description */}
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="flex items-start gap-3">
            <div className="text-2xl">
              {stepConfig.find(s => s.step === currentStep)?.icon}
            </div>
            <div>
              <h4 className="font-semibold text-blue-800 dark:text-blue-200">
                Current: {stepConfig.find(s => s.step === currentStep)?.label}
              </h4>
              <p className="text-sm text-blue-600 dark:text-blue-300 mt-1">
                {stepConfig.find(s => s.step === currentStep)?.description}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EnhancedProgressIndicator