// Script Card Component for Grid View
import React from 'react';
import { useRouter } from 'next/navigation';
import { useTheme } from '@/components/ThemeProvider';
import { 
  getNextActionConfig, 
  getProcessCompletion, 
  navigateToStep,
  determineCurrentStep 
} from '@/utils/processStateManager';

const ScriptCard = ({ script, onAction }) => {
  const { theme } = useTheme();
  const router = useRouter();
  
  const statusInfo = {
    draft: { label: 'Draft', color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300', icon: '📝' },
    script_ready: { label: 'Script Ready', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300', icon: '✅' },
    social_media_pending: { label: 'Social Media Pending', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300', icon: '📱' },
    social_media_ready: { label: 'Social Media Ready', color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300', icon: '🚀' },
    voiceover_pending: { label: 'Voiceover Pending', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300', icon: '🎤' },
    voiceover_ready: { label: 'Voiceover Ready', color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300', icon: '🔊' },
    video_pending: { label: 'Video Pending', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300', icon: '🎬' },
    video_ready: { label: 'Video Complete', color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300', icon: '🎉' }
  };

  // Get smart action configuration based on process state
  const nextActionConfig = getNextActionConfig(script);
  const currentStep = determineCurrentStep(script);
  const completionPercentage = getProcessCompletion(script);
  const status = statusInfo[script.status] || statusInfo.draft;

  // Handle continue process action
  const handleContinueProcess = () => {
    navigateToStep(router, script);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all duration-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-gray-900 dark:text-white text-lg leading-tight">
            {script.title}
          </h3>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color} flex items-center`}>
            <span className="mr-1">{status.icon}</span>
            {status.label}
          </span>
        </div>
        <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-2">
          {script.description}
        </p>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
          <span className="flex items-center">
            <span className="mr-1">🎭</span>
            {script.script_type}
          </span>
          <span className="flex items-center">
            <span className="mr-1">⏱️</span>
            {script.duration_estimate}
          </span>
          <span className="flex items-center">
            <span className="mr-1">📝</span>
            {script.word_count} words
          </span>
        </div>

        {/* Enhanced Progress Indicators */}
        <div className="mb-4">
          {/* Progress Bar */}
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {currentStep.icon} {currentStep.name}
            </span>
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
              {completionPercentage}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
          
          {/* Step Indicators */}
          <div className="flex gap-2 mt-3">
            <div className={`w-3 h-3 rounded-full ${script.voiceover_script ? 'bg-blue-500' : 'bg-gray-300'}`} title="Script Ready" />
            <div className={`w-3 h-3 rounded-full ${script.social_media_generated ? 'bg-green-500' : 'bg-gray-300'}`} title="Social Media" />
            <div className={`w-3 h-3 rounded-full ${script.voiceover_generated ? 'bg-purple-500' : 'bg-gray-300'}`} title="Voiceover" />
            <div className={`w-3 h-3 rounded-full ${script.video_generated ? 'bg-orange-500' : 'bg-gray-300'}`} title="Video Complete" />
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-4">
          {script.tags.map((tag, index) => (
            <span key={index} className="px-2 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded">
              {tag}
            </span>
          ))}
        </div>

        {/* Smart Actions */}
        <div className="flex gap-2">
          {nextActionConfig.action === 'continue_process' ? (
            <button
              onClick={handleContinueProcess}
              className={`flex-1 px-3 py-2 ${nextActionConfig.color} text-white text-sm rounded-lg font-medium transition-colors`}
            >
              {nextActionConfig.label}
            </button>
          ) : (
            <button
              onClick={() => onAction(script.id, nextActionConfig.action)}
              className={`flex-1 px-3 py-2 ${nextActionConfig.color} text-white text-sm rounded-lg font-medium transition-colors`}
            >
              {nextActionConfig.label}
            </button>
          )}
          <button
            onClick={() => onAction(script.id, 'edit_script')}
            className="px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            title="Edit Script"
          >
            ✏️
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700/50 rounded-b-lg">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Created {new Date(script.created_at).toLocaleDateString()}
        </p>
      </div>
    </div>
  );
};

export default ScriptCard;
