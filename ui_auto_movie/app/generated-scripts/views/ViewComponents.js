// View Components for different display modes
import React from 'react';
// NEW: Import hooks for real-time updates (commented for future implementation)
// import { useState, useEffect, useRef } from 'react';
import ScriptCard from '../components/ScriptCard';
import ScriptListItem from '../components/ScriptListItem';
import KanbanCard from '../components/KanbanCard';
import { statusConfig } from '../config/constants';

export const GridView = ({ scripts, onAction, filters = {}, sortBy = 'generation_time' }) => {
  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 gap-6">
        {scripts.map((script) => (
          <ScriptCard 
            key={script.id} 
            script={script} 
          />
        ))}
      </div>
    </div>
  );
};

// List View Component  
export const ListView = ({ scripts, onAction, filters = {}, sortBy = 'generation_time' }) => {
  return (
    <div className="space-y-4">
      {scripts.map((script) => (
        <ScriptListItem 
          key={script.id} 
          script={script} 
          onAction={onAction}
        />
      ))}
    </div>
  );
};

// Kanban View Component
export const KanbanView = ({ scripts, onAction, filters = {}, sortBy = 'generation_time' }) => {

  const kanbanColumns = {
    draft: scripts.filter(s => s.status === 'draft'),
    script_ready: scripts.filter(s => s.status === 'script_ready'),
    social_media_ready: scripts.filter(s => s.status === 'social_media_ready'),
    video_ready: scripts.filter(s => s.status === 'video_ready')
  };

  return (
    <div className="flex gap-6 overflow-x-auto pb-6">
      {Object.entries(kanbanColumns).map(([status, statusScripts]) => (
        <div key={status} className="flex-shrink-0 w-80">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center">
                <span className="mr-2">{statusConfig[status]?.icon}</span>
                {statusConfig[status]?.label}
                <span className="ml-2 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs px-2 py-1 rounded-full">
                  {statusScripts.length}
                </span>
              </h3>
              
            </div>
            <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
              {statusScripts.map((script) => (
                <KanbanCard 
                  key={script.id} 
                  script={script} 
                  onAction={onAction}
                />
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// NEW: Export utility functions for generation data management (commented for future implementation)
// export { useRealTimeGenerationUpdates, calculateGenerationAnalytics };

// NEW: Generation data filtering utilities (commented for future implementation)
// export const GenerationFilters = {
//   AI_MODELS: ['GPT-4-turbo', 'GPT-4', 'GPT-3.5-turbo', 'Claude-3', 'Llama-2'],
//   GENERATION_METHODS: ['ai_generated', 'user_edited', 'merged', 'regenerated'],
//   QUALITY_RANGES: [
//     { label: 'Excellent (90-100)', min: 90, max: 100 },
//     { label: 'Good (70-89)', min: 70, max: 89 },
//     { label: 'Fair (50-69)', min: 50, max: 69 },
//     { label: 'Poor (0-49)', min: 0, max: 49 }
//   ],
//   SORT_OPTIONS: [
//     { value: 'generation_time', label: 'Generation Time' },
//     { value: 'quality_score', label: 'Quality Score' },
//     { value: 'processing_duration', label: 'Processing Speed' },
//     { value: 'generation_cost', label: 'Generation Cost' },
//     { value: 'alphabetical', label: 'Alphabetical' }
//   ]
// };
