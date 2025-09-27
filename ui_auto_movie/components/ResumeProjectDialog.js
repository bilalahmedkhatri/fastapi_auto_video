'use client'

import React from 'react'
import { AlertCircle, Play, Trash2, Clock } from 'lucide-react'

const ResumeProjectDialog = ({ isOpen, onResume, onStartNew, onClose, projectSummary }) => {
  if (!isOpen) return null

  const formatLastSaved = (dateString) => {
    if (!dateString) return 'Unknown'
    
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minutes ago`
    if (diffHours < 24) return `${diffHours} hours ago`
    if (diffDays === 1) return 'Yesterday'
    return `${diffDays} days ago`
  }

  const getStepDisplayName = (step) => {
    const stepNames = {
      'input': 'Script Input',
      'loading': 'Generating Scripts',
      'scripts': 'Script Selection', 
      'editing': 'Script Editing',
      'merging': 'Script Merging',
      'voiceover': 'Voiceover Generation',
      'social-media': 'Social Media Content'
    }
    return stepNames[step] || step
  }

  const getProgressIcon = (status) => {
    switch(status) {
      case 'completed': return '✅'
      case 'in-progress': return '🔄'
      default: return '⚪'
    }
  }

  const getCompletionPercentage = () => {
    if (!projectSummary?.progress) return 0
    
    const totalSteps = Object.keys(projectSummary.progress).length
    const completedSteps = Object.values(projectSummary.progress).filter(status => status === 'completed').length
    
    return Math.round((completedSteps / totalSteps) * 100)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <AlertCircle className="h-6 w-6" />
            <h2 className="text-xl font-bold">Resume Your Project?</h2>
          </div>
          <p className="text-blue-100 text-sm">
            We found an incomplete video project. Would you like to continue where you left off?
          </p>
        </div>

        {/* Project Summary */}
        <div className="p-6 space-y-4">
          {/* Project Info */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Project ID:</span>
              <span className="text-sm text-gray-800 dark:text-gray-200 font-mono">
                {projectSummary?.projectId?.slice(-8) || 'Unknown'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Last Saved:</span>
              <span className="text-sm text-gray-800 dark:text-gray-200 flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formatLastSaved(projectSummary?.lastSaved)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Current Step:</span>
              <span className="text-sm text-blue-600 dark:text-blue-400 font-semibold">
                {getStepDisplayName(projectSummary?.currentStep)}
              </span>
            </div>
          </div>

          {/* Progress Indicator */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Progress</span>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {getCompletionPercentage()}% Complete
              </span>
            </div>
            
            <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getCompletionPercentage()}%` }}
              />
            </div>

            {/* Step Status */}
            <div className="grid grid-cols-2 gap-2 mt-3">
              {projectSummary?.progress && Object.entries(projectSummary.progress).map(([step, status]) => (
                <div key={step} className="flex items-center gap-2 text-xs">
                  <span>{getProgressIcon(status)}</span>
                  <span className="text-gray-600 dark:text-gray-400 truncate">
                    {getStepDisplayName(step)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Content Preview */}
          {projectSummary?.prompt && (
            <div className="space-y-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Video Topic:</span>
              <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-3 rounded italic">
                "{projectSummary.prompt.length > 100 
                  ? projectSummary.prompt.substring(0, 100) + '...' 
                  : projectSummary.prompt}"
              </p>
            </div>
          )}

          {/* Quick Stats */}
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>📝 Scripts: {projectSummary?.hasScripts ? '✓' : '✗'}</span>
            <span>🎵 Voice: {projectSummary?.hasVoiceover ? '✓' : '✗'}</span>
            <span>📱 Social: {projectSummary?.hasSocialMedia ? '✓' : '✗'}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="px-6 pb-6 flex gap-3">
          <button
            onClick={onResume}
            className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
          >
            <Play className="h-4 w-4" />
            Resume Project
          </button>
          
          <button
            onClick={onStartNew}
            className="flex-1 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-800 dark:text-gray-200 font-semibold py-3 px-4 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
          >
            <Trash2 className="h-4 w-4" />
            Start New
          </button>
        </div>

        {/* Close option */}
        <div className="px-6 pb-4">
          <button
            onClick={onClose}
            className="w-full text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
          >
            Close (I'll decide later)
          </button>
        </div>
      </div>
    </div>
  )
}

export default ResumeProjectDialog