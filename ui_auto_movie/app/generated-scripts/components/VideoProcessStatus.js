'use client';

import React from 'react';
import { CheckCircle, Clock, AlertCircle, Play, Pause } from 'lucide-react';

const VideoProcessStatus = ({ videoProcess }) => {
  if (!videoProcess) {
    return null;
  }

  const getStepIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in-progress':
        return <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'not-started':
        return <div className="w-5 h-5 border-2 border-gray-300 rounded-full" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStepColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'in-progress':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'not-started':
        return 'bg-gray-100 text-gray-600 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  const getStepDisplayName = (stepName) => {
    const stepNames = {
      'input': 'Input & Preferences',
      'loading': 'AI Script Generation',
      'scripts': 'Script Selection',
      'editing': 'Script Editing',
      'voiceover': 'Voice Generation',
      'social-media': 'Social Media Content',
      'media': 'Media Selection',
      'video-effects': 'Video Effects'
    };
    return stepNames[stepName] || stepName;
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const completedSteps = videoProcess.steps?.filter(step => step.status === 'completed').length || 0;
  const totalSteps = videoProcess.steps?.length || 8;
  const progressPercentage = Math.round((completedSteps / totalSteps) * 100);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
            <Play className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Video Generation in Progress
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Current Step: {getStepDisplayName(videoProcess.current_step)}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {progressPercentage}%
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {completedSteps} of {totalSteps} steps
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-3">
        {videoProcess.steps?.map((step, index) => (
          <div 
            key={step.step_name} 
            className={`flex items-center justify-between p-3 rounded-lg border ${getStepColor(step.status)}`}
          >
            <div className="flex items-center space-x-3">
              {getStepIcon(step.status)}
              <div>
                <div className="font-medium">
                  {step.step_order}. {getStepDisplayName(step.step_name)}
                </div>
                {step.status === 'in-progress' && (
                  <div className="text-xs text-blue-600 dark:text-blue-400">
                    Processing...
                  </div>
                )}
                {step.status === 'completed' && step.duration_seconds && (
                  <div className="text-xs text-green-600 dark:text-green-400">
                    Completed in {formatDuration(step.duration_seconds)}
                  </div>
                )}
                {step.status === 'failed' && (
                  <div className="text-xs text-red-600 dark:text-red-400">
                    Step failed - retrying...
                  </div>
                )}
              </div>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 capitalize">
              {step.status.replace('-', ' ')}
            </div>
          </div>
        ))}
      </div>

      {/* Estimated Completion */}
      {videoProcess.estimated_completion && (
        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            <Clock className="w-4 h-4 inline mr-2" />
            Estimated completion: {new Date(videoProcess.estimated_completion).toLocaleTimeString()}
          </div>
        </div>
      )}

      {/* Status Badge */}
      <div className="mt-4 flex justify-between items-center">
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          videoProcess.status === 'active' 
            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
            : videoProcess.status === 'completed'
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {videoProcess.status.toUpperCase()}
        </div>
        {videoProcess.process_id && (
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Process ID: #{videoProcess.process_id}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoProcessStatus;