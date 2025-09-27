// View Components for different display modes
import React from 'react';
// NEW: Import hooks for real-time updates (commented for future implementation)
// import { useState, useEffect, useRef } from 'react';
import ScriptCard from '../components/ScriptCard';
import ScriptListItem from '../components/ScriptListItem';
import KanbanCard from '../components/KanbanCard';
import { statusConfig } from '../config/constants';

// NEW: Real-time generation updates hook (commented for future implementation)
// const useRealTimeGenerationUpdates = (scripts) => {
//   const [liveScripts, setLiveScripts] = useState(scripts);
//   const wsRef = useRef(null);
//   
//   useEffect(() => {
//     // WebSocket connection for live updates
//     // wsRef.current = new WebSocket('ws://localhost:8000/ws/generation-updates');
//     
//     // wsRef.current.onmessage = (event) => {
//     //   const update = JSON.parse(event.data);
//     //   if (update.type === 'generation_progress') {
//     //     setLiveScripts(prev => prev.map(script => 
//     //       script.id === update.script_id 
//     //         ? { ...script, generation_progress: update.progress, status: update.status }
//     //         : script
//     //     ));
//     //   }
//     // };
//     
//     // Polling fallback for updates every 2 seconds
//     // const pollInterval = setInterval(async () => {
//     //   try {
//     //     const response = await fetch('/api/script-generator/generation-status');
//     //     const updates = await response.json();
//     //     setLiveScripts(prev => prev.map(script => {
//     //       const update = updates.find(u => u.script_id === script.id);
//     //       return update ? { ...script, ...update } : script;
//     //     }));
//     //   } catch (error) {
//     //     console.error('Failed to poll generation updates:', error);
//     //   }
//     // }, 2000);
//     
//     // return () => {
//     //   if (wsRef.current) wsRef.current.close();
//     //   clearInterval(pollInterval);
//     // };
//   }, []);
//   
//   return liveScripts;
// };

// NEW: Generation analytics calculator (commented for future implementation)
// const calculateGenerationAnalytics = (scripts) => {
//   const totalScripts = scripts.length;
//   const completedScripts = scripts.filter(s => s.status !== 'generating' && s.status !== 'draft').length;
//   const averageProcessingTime = scripts.reduce((sum, s) => sum + (s.processing_duration || 0), 0) / totalScripts;
//   const averageQuality = scripts.reduce((sum, s) => sum + (s.quality_score || 0), 0) / totalScripts;
//   const totalCost = scripts.reduce((sum, s) => sum + (s.generation_cost || 0), 0);
//   const successRate = (completedScripts / totalScripts) * 100;
//   
//   return {
//     totalScripts,
//     completedScripts,
//     averageProcessingTime: averageProcessingTime.toFixed(2),
//     averageQuality: averageQuality.toFixed(1),
//     totalCost: totalCost.toFixed(3),
//     successRate: successRate.toFixed(1)
//   };
// };

// Grid View Component
export const GridView = ({ scripts, onAction, filters = {}, sortBy = 'generation_time' }) => {
  // NEW: Enhanced script data with generation metadata (commented for future implementation)
  // const enhancedScripts = scripts.map(script => ({
  //   ...script,
  //   // Mock generation data - will be replaced with real API data
  //   generation_time: script.generation_time || new Date().toISOString(),
  //   ai_model_used: script.ai_model_used || 'GPT-4-turbo',
  //   processing_duration: script.processing_duration || Math.random() * 5 + 2, // 2-7 seconds
  //   quality_score: script.quality_score || Math.floor(Math.random() * 30 + 70), // 70-100
  //   generation_method: script.generation_method || 'ai_generated',
  //   prompt_used: script.prompt_used || 'AI-generated content',
  //   token_usage: script.token_usage || { input: 150, output: 300 },
  //   generation_cost: script.generation_cost || 0.02
  // }));

  // NEW: Filter and sort scripts based on generation data (commented for future implementation)
  // const filteredAndSortedScripts = enhancedScripts
  //   .filter(script => {
  //     if (filters.aiModel && script.ai_model_used !== filters.aiModel) return false;
  //     if (filters.qualityMin && script.quality_score < filters.qualityMin) return false;
  //     if (filters.qualityMax && script.quality_score > filters.qualityMax) return false;
  //     if (filters.dateFrom && new Date(script.generation_time) < new Date(filters.dateFrom)) return false;
  //     if (filters.dateTo && new Date(script.generation_time) > new Date(filters.dateTo)) return false;
  //     if (filters.generationMethod && script.generation_method !== filters.generationMethod) return false;
  //     return true;
  //   })
  //   .sort((a, b) => {
  //     switch (sortBy) {
  //       case 'generation_time':
  //         return new Date(b.generation_time) - new Date(a.generation_time);
  //       case 'quality_score':
  //         return (b.quality_score || 0) - (a.quality_score || 0);
  //       case 'processing_duration':
  //         return (a.processing_duration || 0) - (b.processing_duration || 0);
  //       case 'generation_cost':
  //         return (a.generation_cost || 0) - (b.generation_cost || 0);
  //       case 'alphabetical':
  //         return a.title.localeCompare(b.title);
  //       default:
  //         return 0;
  //     }
  //   });
  
  // NEW: Calculate and display generation analytics (commented for future implementation)
  // const analytics = calculateGenerationAnalytics(scripts);
  
  return (
    <div>
      {/* NEW: Generation Analytics Dashboard (commented for future implementation) */}
      {/* <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
        <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-3">📊 Generation Analytics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 text-sm">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{analytics.totalScripts}</div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Total Scripts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">{analytics.successRate}%</div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{analytics.averageQuality}</div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Avg Quality</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">{analytics.averageProcessingTime}s</div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Avg Time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">${analytics.totalCost}</div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Total Cost</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600 dark:text-gray-400">{analytics.completedScripts}</div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Completed</div>
          </div>
        </div>
      </div> */}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 gap-6">
        {scripts.map((script) => (
          <ScriptCard 
            key={script.id} 
            script={script} 
            onAction={onAction}
            // NEW: Pass generation metadata to ScriptCard (commented for future)
            // showGenerationData={true}
            // generationMetadata={{
            //   model: script.ai_model_used,
            //   processingTime: script.processing_duration,
            //   quality: script.quality_score,
            //   cost: script.generation_cost
            // }}
          />
        ))}
      </div>
    </div>
  );
};

// List View Component  
export const ListView = ({ scripts, onAction, filters = {}, sortBy = 'generation_time' }) => {
  // NEW: Enhanced scripts with generation data (commented for future implementation)
  // const scriptsWithGenerationData = scripts.map(script => ({
  //   ...script,
  //   // Generation timeline data
  //   generation_timeline: script.generation_timeline || [
  //     { step: 'prompt_received', timestamp: new Date(Date.now() - 10000).toISOString(), status: 'completed' },
  //     { step: 'ai_processing', timestamp: new Date(Date.now() - 8000).toISOString(), status: 'completed' },
  //     { step: 'post_processing', timestamp: new Date(Date.now() - 3000).toISOString(), status: 'completed' },
  //     { step: 'quality_check', timestamp: new Date().toISOString(), status: 'completed' }
  //   ],
  //   // Generation parameters used
  //   generation_params: script.generation_params || {
  //     temperature: 0.7,
  //     max_tokens: 1000,
  //     model_version: 'gpt-4-turbo',
  //     creativity_level: 'balanced'
  //   },
  //   // Performance metrics
  //   performance_metrics: script.performance_metrics || {
  //     response_time: Math.random() * 3 + 1,
  //     token_efficiency: Math.random() * 0.3 + 0.7,
  //     quality_rating: Math.random() * 0.3 + 0.7
  //   }
  // }));

  return (
    <div className="space-y-4">
      {/* NEW: Enhanced List Header with Generation Columns (commented for future) */}
      {/* <div className="hidden lg:grid lg:grid-cols-12 gap-4 px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300">
        <div className="col-span-3">Script Details</div>
        <div className="col-span-2">Generation Info</div>
        <div className="col-span-2">Performance</div>
        <div className="col-span-2">AI Model</div>
        <div className="col-span-2">Timeline</div>
        <div className="col-span-1">Actions</div>
      </div> */}
      
      {scripts.map((script) => (
        <ScriptListItem 
          key={script.id} 
          script={script} 
          onAction={onAction}
          // NEW: Pass generation metadata to ScriptListItem (commented for future)
          // showGenerationColumns={true}
          // generationData={{
          //   timeline: script.generation_timeline,
          //   parameters: script.generation_params,
          //   metrics: script.performance_metrics
          // }}
        />
      ))}
    </div>
  );
};

// Kanban View Component
export const KanbanView = ({ scripts, onAction, filters = {}, sortBy = 'generation_time' }) => {
  // NEW: Enhanced Kanban with generation tracking (commented for future implementation)
  // const scriptsWithGenerationStatus = scripts.map(script => ({
  //   ...script,
  //   generation_queue_position: script.generation_queue_position || null,
  //   estimated_completion: script.estimated_completion || null,
  //   generation_progress: script.generation_progress || (script.status === 'generating' ? Math.random() * 100 : 100)
  // }));

  const kanbanColumns = {
    // NEW: Add generating column for scripts in progress (commented for future)
    // generating: scriptsWithGenerationStatus.filter(s => s.status === 'generating'),
    draft: scripts.filter(s => s.status === 'draft'),
    script_ready: scripts.filter(s => s.status === 'script_ready'),
    social_media_ready: scripts.filter(s => s.status === 'social_media_ready'),
    video_ready: scripts.filter(s => s.status === 'video_ready')
  };

  // NEW: Calculate performance metrics per column (commented for future)
  // const columnMetrics = Object.entries(kanbanColumns).reduce((acc, [status, statusScripts]) => {
  //   const totalProcessingTime = statusScripts.reduce((sum, script) => sum + (script.processing_duration || 0), 0);
  //   const avgProcessingTime = statusScripts.length > 0 ? totalProcessingTime / statusScripts.length : 0;
  //   const avgQuality = statusScripts.reduce((sum, script) => sum + (script.quality_score || 0), 0) / statusScripts.length;
  //   
  //   acc[status] = {
  //     count: statusScripts.length,
  //     avgProcessingTime: avgProcessingTime.toFixed(1),
  //     avgQuality: avgQuality.toFixed(1),
  //     totalCost: statusScripts.reduce((sum, script) => sum + (script.generation_cost || 0), 0)
  //   };
  //   return acc;
  // }, {});

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
              
              {/* NEW: Performance metrics per column (commented for future implementation) */}
              {/* {columnMetrics[status] && (
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 space-y-1">
                  <div className="flex justify-between">
                    <span>Avg Processing:</span>
                    <span>{columnMetrics[status].avgProcessingTime}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Avg Quality:</span>
                    <span>{columnMetrics[status].avgQuality}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Cost:</span>
                    <span>${columnMetrics[status].totalCost.toFixed(3)}</span>
                  </div>
                </div>
              )} */}
            </div>
            <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
              {statusScripts.map((script) => (
                <KanbanCard 
                  key={script.id} 
                  script={script} 
                  onAction={onAction}
                  // NEW: Pass generation tracking data to KanbanCard (commented for future)
                  // showGenerationProgress={status === 'generating'}
                  // queuePosition={script.generation_queue_position}
                  // estimatedCompletion={script.estimated_completion}
                  // generationProgress={script.generation_progress}
                />
              ))}
              
              {/* NEW: Real-time generation queue display (commented for future implementation) */}
              {/* {status === 'generating' && (
                <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
                  <div className="text-xs text-blue-700 dark:text-blue-300 font-medium mb-2">
                    🔄 Generation Queue
                  </div>
                  <div className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
                    <div>Active: {statusScripts.filter(s => s.generation_progress > 0).length}</div>
                    <div>Queued: {statusScripts.filter(s => s.generation_progress === 0).length}</div>
                    <div>Est. Time: {Math.max(...statusScripts.map(s => s.estimated_completion || 0))}s</div>
                  </div>
                </div>
              )} */}
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
