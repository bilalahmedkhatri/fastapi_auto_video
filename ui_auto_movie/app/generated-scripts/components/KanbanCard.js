// Kanban Card Component
import React from 'react';
import { useRouter } from 'next/navigation';
import { 
  getNextActionConfig, 
  getProcessCompletion, 
  navigateToStep 
} from '@/utils/processStateManager';

const KanbanCard = ({ script, onAction }) => {
  const router = useRouter();
  const nextActionConfig = getNextActionConfig(script);
  const completionPercentage = getProcessCompletion(script);

  // Handle continue process action
  const handleContinueProcess = () => {
    navigateToStep(router, script);
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600 hover:shadow-sm transition-all cursor-pointer">
      <h4 className="font-medium text-gray-900 dark:text-white text-sm mb-2 line-clamp-2">
        {script.title}
      </h4>
      
      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-2">
        <span>{script.script_type}</span>
        <span>{completionPercentage}%</span>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-1 mb-2">
        <div 
          className="bg-gradient-to-r from-blue-500 to-green-500 h-1 rounded-full transition-all duration-300"
          style={{ width: `${completionPercentage}%` }}
        />
      </div>
      
      <div className="flex gap-1 mb-3">
        <div className={`w-2 h-2 rounded-full ${script.voiceover_script ? 'bg-blue-500' : 'bg-gray-300'}`} title="Script Ready" />
        <div className={`w-2 h-2 rounded-full ${script.social_media_generated ? 'bg-green-500' : 'bg-gray-300'}`} title="Social Media" />
        <div className={`w-2 h-2 rounded-full ${script.voiceover_generated ? 'bg-purple-500' : 'bg-gray-300'}`} title="Voiceover" />
        <div className={`w-2 h-2 rounded-full ${script.video_generated ? 'bg-orange-500' : 'bg-gray-300'}`} title="Video Complete" />
      </div>
      
      {nextActionConfig.action === 'continue_process' ? (
        <button
          onClick={handleContinueProcess}
          className={`w-full px-2 py-1 ${nextActionConfig.color} text-white text-xs rounded transition-colors`}
        >
          {nextActionConfig.label}
        </button>
      ) : (
        <button
          onClick={() => onAction(script.id, nextActionConfig.action)}
          className={`w-full px-2 py-1 ${nextActionConfig.color} text-white text-xs rounded transition-colors`}
        >
          {nextActionConfig.label}
        </button>
      )}
    </div>
  );
};

export default KanbanCard;
