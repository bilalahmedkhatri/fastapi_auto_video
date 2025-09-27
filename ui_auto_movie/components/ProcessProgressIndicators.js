/**
 * Real-time Process Progress Indicators
 * 
 * This component displays progress indicators for the video generation process,
 * including step progress, overall completion, and real-time updates.
 */

import React from 'react';
import { CheckCircle, Clock, AlertCircle, Loader2, Pause, Play } from 'lucide-react';

const PROCESS_STEPS = [
  {
    key: 'input_processing',
    label: 'Processing Input',
    description: 'Analyzing your prompt and requirements',
    icon: '📝'
  },
  {
    key: 'script_generation',
    label: 'Generating Scripts',
    description: 'Creating video scripts based on your input',
    icon: '📋'
  },
  {
    key: 'voiceover_generation',
    label: 'Creating Voiceover',
    description: 'Generating audio narration for your video',
    icon: '🎙️'
  },
  {
    key: 'social_media_content',
    label: 'Social Media Content',
    description: 'Creating platform-specific content variations',
    icon: '📱'
  },
  {
    key: 'media_collection',
    label: 'Collecting Media',
    description: 'Gathering images, videos, and other assets',
    icon: '🎬'
  },
  {
    key: 'effects_processing',
    label: 'Processing Effects',
    description: 'Applying visual effects and transitions',
    icon: '✨'
  },
  {
    key: 'final_assembly',
    label: 'Final Assembly',
    description: 'Combining all elements into final video',
    icon: '🎯'
  }
];

/**
 * Individual step progress indicator
 */
function StepIndicator({ step, isActive, isCompleted, isFailed, progress = 0, message = '' }) {
  const getStatusIcon = () => {
    if (isFailed) return <AlertCircle className="h-5 w-5 text-red-500" />;
    if (isCompleted) return <CheckCircle className="h-5 w-5 text-green-500" />;
    if (isActive) return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
    return <Clock className="h-5 w-5 text-gray-400" />;
  };

  const getStatusColor = () => {
    if (isFailed) return 'border-red-200 bg-red-50';
    if (isCompleted) return 'border-green-200 bg-green-50';
    if (isActive) return 'border-blue-200 bg-blue-50';
    return 'border-gray-200 bg-gray-50';
  };

  return (
    <div className={`p-4 rounded-lg border ${getStatusColor()}`}>
      <div className="flex items-center gap-3 mb-2">
        <span className="text-2xl">{step.icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <h3 className="font-semibold text-gray-900">{step.label}</h3>
          </div>
          <p className="text-sm text-gray-600 mt-1">{step.description}</p>
        </div>
      </div>
      
      {isActive && (
        <div className="mt-2">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          {message && (
            <p className="text-xs text-gray-500 mt-2">{message}</p>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Overall process progress bar
 */
function OverallProgress({ currentStep, totalSteps, overallProgress, processState }) {
  const getStateColor = () => {
    switch (processState) {
      case 'running': return 'bg-blue-500';
      case 'paused': return 'bg-yellow-500';
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      case 'cancelled': return 'bg-gray-500';
      default: return 'bg-gray-300';
    }
  };

  const getStateText = () => {
    switch (processState) {
      case 'starting': return 'Starting...';
      case 'running': return 'In Progress';
      case 'paused': return 'Paused';
      case 'completed': return 'Completed';
      case 'failed': return 'Failed';
      case 'cancelled': return 'Cancelled';
      default: return 'Idle';
    }
  };

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-semibold text-gray-900">Video Generation Progress</h2>
        <div className="flex items-center gap-2">
          {processState === 'paused' && <Pause className="h-4 w-4 text-yellow-600" />}
          {processState === 'running' && <Play className="h-4 w-4 text-blue-600" />}
          <span className="text-sm font-medium text-gray-600">
            {getStateText()} • {currentStep} of {totalSteps}
          </span>
        </div>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`h-3 rounded-full transition-all duration-500 ${getStateColor()}`}
          style={{ width: `${overallProgress}%` }}
        />
      </div>
      
      <div className="text-xs text-gray-500 mt-1">
        {Math.round(overallProgress)}% complete
      </div>
    </div>
  );
}

/**
 * Process timing information
 */
function ProcessTiming({ startedAt, duration, estimatedTimeRemaining = null }) {
  const formatDuration = (ms) => {
    if (!ms) return '0s';
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${remainingSeconds}s`;
  };

  const formatTime = (isoString) => {
    if (!isoString) return 'N/A';
    return new Date(isoString).toLocaleTimeString();
  };

  return (
    <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg text-sm">
      <div>
        <div className="text-gray-600">Started At</div>
        <div className="font-medium">{formatTime(startedAt)}</div>
      </div>
      <div>
        <div className="text-gray-600">Duration</div>
        <div className="font-medium">{formatDuration(duration)}</div>
      </div>
      <div>
        <div className="text-gray-600">Time Remaining</div>
        <div className="font-medium">
          {estimatedTimeRemaining ? formatDuration(estimatedTimeRemaining) : 'Calculating...'}
        </div>
      </div>
    </div>
  );
}

/**
 * Main progress indicators component
 */
function ProcessProgressIndicators({
  processState = 'idle',
  currentStep = null,
  progress = 0,
  message = '',
  startedAt = null,
  duration = 0,
  estimatedTimeRemaining = null,
  className = ''
}) {
  if (processState === 'idle') {
    return null; // Don't show anything when idle
  }

  // Calculate overall progress
  const currentStepIndex = PROCESS_STEPS.findIndex(step => step.key === currentStep);
  const stepProgress = currentStepIndex >= 0 ? currentStepIndex : 0;
  const overallProgress = ((stepProgress / PROCESS_STEPS.length) * 100) + 
                         ((progress / 100) * (100 / PROCESS_STEPS.length));

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <OverallProgress
        currentStep={stepProgress + 1}
        totalSteps={PROCESS_STEPS.length}
        overallProgress={overallProgress}
        processState={processState}
      />
      
      <div className="grid gap-3">
        {PROCESS_STEPS.map((step, index) => {
          const isActive = step.key === currentStep;
          const isCompleted = index < currentStepIndex || 
                            (index === currentStepIndex && processState === 'completed');
          const isFailed = isActive && processState === 'failed';
          const stepProgress = isActive ? progress : (isCompleted ? 100 : 0);
          
          return (
            <StepIndicator
              key={step.key}
              step={step}
              isActive={isActive}
              isCompleted={isCompleted}
              isFailed={isFailed}
              progress={stepProgress}
              message={isActive ? message : ''}
            />
          );
        })}
      </div>
      
      {(startedAt || duration > 0) && (
        <div className="mt-6">
          <ProcessTiming
            startedAt={startedAt}
            duration={duration}
            estimatedTimeRemaining={estimatedTimeRemaining}
          />
        </div>
      )}
    </div>
  );
}

/**
 * Compact version for smaller spaces
 */
export function CompactProcessIndicator({
  processState = 'idle',
  currentStep = null,
  progress = 0,
  message = '',
  className = ''
}) {
  if (processState === 'idle') return null;

  const currentStepData = PROCESS_STEPS.find(step => step.key === currentStep);
  const currentStepIndex = PROCESS_STEPS.findIndex(step => step.key === currentStep);
  const overallProgress = ((currentStepIndex / PROCESS_STEPS.length) * 100) + 
                         ((progress / 100) * (100 / PROCESS_STEPS.length));

  return (
    <div className={`bg-blue-50 border border-blue-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-center gap-3 mb-3">
        <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
        <div>
          <div className="font-medium text-blue-900">
            {currentStepData ? currentStepData.label : 'Processing...'}
          </div>
          <div className="text-sm text-blue-600">
            {message || (currentStepData ? currentStepData.description : 'Working on your video...')}
          </div>
        </div>
      </div>
      
      <div className="w-full bg-blue-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${overallProgress}%` }}
        />
      </div>
      
      <div className="text-xs text-blue-600 mt-1 text-right">
        {Math.round(overallProgress)}% complete
      </div>
    </div>
  );
}

export default ProcessProgressIndicators;