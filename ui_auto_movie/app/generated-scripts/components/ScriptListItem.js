// Script List Item Component for List View
import React from 'react';
import { useRouter } from 'next/navigation';
import { 
  getNextActionConfig, 
  getProcessCompletion, 
  navigateToStep,
  determineCurrentStep 
} from '@/utils/processStateManager';

const ScriptListItem = ({ script, onAction }) => {
  const router = useRouter();
  
  const statusInfo = {
    draft: { label: 'Draft', color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300', icon: '📝' },
    script_ready: { label: 'Script Ready', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300', icon: '✅' },
    social_media_ready: { label: 'Social Media Ready', color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300', icon: '🚀' },
    video_ready: { label: 'Video Complete', color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300', icon: '🎉' }
  };

  const status = statusInfo[script.status] || statusInfo.draft;
  const nextActionConfig = getNextActionConfig(script);
  const currentStep = determineCurrentStep(script);
  const completionPercentage = getProcessCompletion(script);

  // Handle continue process action
  const handleContinueProcess = () => {
    navigateToStep(router, script);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-all duration-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-4 mb-2">
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {script.title}
            </h3>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color} flex items-center`}>
              <span className="mr-1">{status.icon}</span>
              {status.label}
            </span>
          </div>
          
          <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
            {script.description}
          </p>
          
          <div className="flex items-center gap-6 text-sm text-gray-500 dark:text-gray-400">
            <span>🎭 {script.script_type}</span>
            <span>⏱️ {script.duration_estimate}</span>
            <span>📝 {script.word_count} words</span>
            <span>📅 {new Date(script.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4 ml-4">
          {/* Enhanced Progress Section */}
          <div className="flex flex-col items-end">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {currentStep.icon} {currentStep.name}
              </span>
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                {completionPercentage}%
              </span>
            </div>
            
            {/* Progress Bar */}
            <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-1 mb-1">
              <div 
                className="bg-gradient-to-r from-blue-500 to-green-500 h-1 rounded-full transition-all duration-300"
                style={{ width: `${completionPercentage}%` }}
              />
            </div>
            
            {/* Step Indicators */}
            <div className="flex gap-1">
              <div className={`w-2 h-2 rounded-full ${script.voiceover_script ? 'bg-blue-500' : 'bg-gray-300'}`} title="Script Ready" />
              <div className={`w-2 h-2 rounded-full ${script.social_media_generated ? 'bg-green-500' : 'bg-gray-300'}`} title="Social Media" />
              <div className={`w-2 h-2 rounded-full ${script.voiceover_generated ? 'bg-purple-500' : 'bg-gray-300'}`} title="Voiceover" />
              <div className={`w-2 h-2 rounded-full ${script.video_generated ? 'bg-orange-500' : 'bg-gray-300'}`} title="Video Complete" />
            </div>
          </div>
          
          {/* Smart Actions */}
          <div className="flex gap-2">
            {nextActionConfig.action === 'continue_process' ? (
              <button
                onClick={handleContinueProcess}
                className={`px-3 py-1 ${nextActionConfig.color} text-white text-sm rounded transition-colors`}
              >
                {nextActionConfig.label}
              </button>
            ) : (
              <button
                onClick={() => onAction(script.id, nextActionConfig.action)}
                className={`px-3 py-1 ${nextActionConfig.color} text-white text-sm rounded transition-colors`}
              >
                {nextActionConfig.label}
              </button>
            )}
            <button
              onClick={() => onAction(script.id, 'edit_script')}
              className="px-3 py-1 bg-gray-500 hover:bg-gray-600 text-white text-sm rounded transition-colors"
            >
              ✏️
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScriptListItem;
