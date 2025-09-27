'use client'

import React from 'react'
import { ArrowLeft, ArrowRight, RotateCcw, Save, AlertTriangle } from 'lucide-react'
import { useVideoBuilderStore, useStepNavigation, STEPS } from '@/stores/useVideoBuilderStore'

const VideoBuilderNavigation = ({ 
  onBack, 
  onNext, 
  onRegenerate, 
  nextLabel = "Continue",
  backLabel = "Back",
  regenerateLabel = "Regenerate",
  showRegenerate = false,
  disabled = false,
  loading = false,
  customActions = null
}) => {
  const { canGoBack, canGoNext, currentStep } = useStepNavigation()
  const hasUnsavedChanges = useVideoBuilderStore(state => state.hasUnsavedChanges())
  const autoSave = useVideoBuilderStore(state => state.autoSave)
  const lastSaved = useVideoBuilderStore(state => state.lastSaved)

  const handleBack = () => {
    if (hasUnsavedChanges) {
      autoSave()
    }
    if (onBack) {
      onBack()
    }
  }

  const handleNext = () => {
    if (hasUnsavedChanges) {
      autoSave()  
    }
    if (onNext) {
      onNext()
    }
  }

  const getStepDisplayName = (step) => {
    const stepNames = {
      [STEPS.INPUT]: 'Script Input',
      [STEPS.LOADING]: 'Generating',
      [STEPS.SCRIPTS]: 'Script Selection',
      [STEPS.EDITING]: 'Editing',
      [STEPS.MERGING]: 'Merging',
      [STEPS.VOICEOVER]: 'Voiceover',
      [STEPS.SOCIAL_MEDIA]: 'Social Media',
      [STEPS.MEDIA]: 'Media Selection',
      [STEPS.VIDEO_EFFECTS]: 'Video Effects'
    }
    return stepNames[step] || step
  }

  const formatLastSaved = () => {
    if (!lastSaved) return null
    
    const date = new Date(lastSaved)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffMins < 1) return 'Saved just now'
    if (diffMins < 60) return `Saved ${diffMins}m ago`
    return `Saved ${Math.floor(diffMins / 60)}h ago`
  }

  return (
    <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
      {/* Save Status */}
      {lastSaved && (
        <div className="flex items-center justify-center mb-4">
          <div className={`flex items-center gap-2 text-xs px-3 py-1 rounded-full ${
            hasUnsavedChanges 
              ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
              : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
          }`}>
            {hasUnsavedChanges ? (
              <>
                <AlertTriangle className="h-3 w-3" />
                <span>Unsaved changes</span>
              </>
            ) : (
              <>
                <Save className="h-3 w-3" />
                <span>{formatLastSaved()}</span>
              </>
            )}
          </div>
        </div>
      )}

      {/* Navigation Controls */}
      <div className="flex items-center justify-between">
        {/* Back Button */}
        <div className="flex-1">
          {canGoBack && (
            <button
              onClick={handleBack}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowLeft className="h-4 w-4" />
              <span className="font-medium">{backLabel}</span>
            </button>
          )}
        </div>

        {/* Center Actions */}
        <div className="flex items-center gap-3">
          {/* Current Step Indicator */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
            <span className="text-sm text-gray-600 dark:text-gray-400">Current:</span>
            <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              {getStepDisplayName(currentStep)}
            </span>
          </div>

          {/* Regenerate Button */}
          {showRegenerate && (
            <button
              onClick={onRegenerate}
              disabled={loading || disabled}
              className="flex items-center gap-2 px-4 py-2 text-amber-600 hover:text-amber-700 dark:text-amber-400 dark:hover:text-amber-300 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed border border-amber-200 dark:border-amber-800"
            >
              <RotateCcw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span className="font-medium">{regenerateLabel}</span>
            </button>
          )}

          {/* Custom Actions */}
          {customActions}
        </div>

        {/* Next Button */}
        <div className="flex-1 flex justify-end">
          {canGoNext && (
            <button
              onClick={handleNext}
              disabled={loading || disabled}
              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{nextLabel}</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Step Progress Bar */}
      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-2">
          <span>Workflow Progress</span>
          <span>Step {Object.values(STEPS).indexOf(currentStep) + 1} of {Object.keys(STEPS).length}</span>
        </div>
        
        <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-1">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-1 rounded-full transition-all duration-300"
            style={{ 
              width: `${((Object.values(STEPS).indexOf(currentStep) + 1) / Object.keys(STEPS).length) * 100}%` 
            }}
          />
        </div>
      </div>
    </div>
  )
}

export default VideoBuilderNavigation