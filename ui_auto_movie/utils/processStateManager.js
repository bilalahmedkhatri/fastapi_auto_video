// Process State Management for Video Builder Workflow
import { STEPS } from '@/stores/useVideoBuilderStore';

// Workflow step definitions with routing information
export const WORKFLOW_STEPS = {
  TOPIC_INPUT: {
    id: 'topic_input',
    name: 'Topic Input',
    route: '/video-builder',
    icon: '📝',
    description: 'Enter topic and preferences'
  },
  SCRIPT_GENERATION: {
    id: 'script_generation',
    name: 'Script Generation',
    route: '/video-builder',
    icon: '⚡',
    description: 'AI generates script options'
  },
  SCRIPT_SELECTION: {
    id: 'script_selection',
    name: 'Script Selection',
    route: '/video-builder',
    icon: '📋',
    description: 'Choose and edit scripts'
  },
  PLATFORM_SELECTION: {
    id: 'platform_selection',
    name: 'Platform Selection',
    route: '/video-builder',
    icon: '📱',
    description: 'Select social media platforms'
  },
  SOCIAL_MEDIA_GENERATION: {
    id: 'social_media_generation',
    name: 'Social Media Content',
    route: '/video-builder',
    icon: '🚀',
    description: 'Generate platform-specific content'
  },
  VOICEOVER_GENERATION: {
    id: 'voiceover_generation',
    name: 'Voiceover Generation',
    route: '/video-builder',
    icon: '🎤',
    description: 'Generate voice narration'
  },
  MEDIA_SELECTION: {
    id: 'media_selection',
    name: 'Media Selection',
    route: '/video-builder',
    icon: '🖼️',
    description: 'Choose images and videos'
  },
  VIDEO_BUILDING: {
    id: 'video_building',
    name: 'Video Building',
    route: '/video-builder',
    icon: '🎬',
    description: 'Create final video'
  },
  COMPLETED: {
    id: 'completed',
    name: 'Completed',
    route: '/generated-scripts',
    icon: '✅',
    description: 'Process completed'
  }
};

// Process state storage key
const PROCESS_STATE_KEY = 'video_builder_process_states';

// Get process state for a script/project
export const getProcessState = (scriptId) => {
  if (typeof window === 'undefined') return null;
  
  try {
    const states = JSON.parse(localStorage.getItem(PROCESS_STATE_KEY) || '{}');
    return states[scriptId] || null;
  } catch (error) {
    console.error('Error getting process state:', error);
    return null;
  }
};

// Save process state for a script/project
export const saveProcessState = (scriptId, state) => {
  if (typeof window === 'undefined') return;
  
  try {
    const states = JSON.parse(localStorage.getItem(PROCESS_STATE_KEY) || '{}');
    states[scriptId] = {
      ...state,
      lastUpdated: new Date().toISOString(),
      scriptId
    };
    localStorage.setItem(PROCESS_STATE_KEY, JSON.stringify(states));
  } catch (error) {
    console.error('Error saving process state:', error);
  }
};

// Clear process state for a script/project
export const clearProcessState = (scriptId) => {
  if (typeof window === 'undefined') return;
  
  try {
    const states = JSON.parse(localStorage.getItem(PROCESS_STATE_KEY) || '{}');
    delete states[scriptId];
    localStorage.setItem(PROCESS_STATE_KEY, JSON.stringify(states));
  } catch (error) {
    console.error('Error clearing process state:', error);
  }
};

// Clear all process states (for fresh start)
export const clearAllProcessStates = () => {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.removeItem(PROCESS_STATE_KEY);
  } catch (error) {
    console.error('Error clearing all process states:', error);
  }
};

// Determine current step based on script data and generation flags
export const determineCurrentStep = (script) => {
  if (!script) return WORKFLOW_STEPS.TOPIC_INPUT;

  // Check completion flags to determine current step
  if (script.video_generated) {
    return WORKFLOW_STEPS.COMPLETED;
  }
  
  if (script.voiceover_generated && script.social_media_generated) {
    return WORKFLOW_STEPS.VIDEO_BUILDING;
  }
  
  if (script.voiceover_generated) {
    return WORKFLOW_STEPS.MEDIA_SELECTION;
  }
  
  if (script.social_media_generated) {
    return WORKFLOW_STEPS.VOICEOVER_GENERATION;
  }
  
  if (script.voiceover_script) {
    return WORKFLOW_STEPS.SOCIAL_MEDIA_GENERATION;
  }
  
  return WORKFLOW_STEPS.SCRIPT_SELECTION;
};

// Get next action button configuration based on current step
export const getNextActionConfig = (script) => {
  const currentStep = determineCurrentStep(script);
  
  switch (currentStep.id) {
    case 'script_selection':
      return {
        action: 'continue_process',
        label: '📱 Continue to Platforms',
        color: 'bg-blue-500 hover:bg-blue-600',
        step: WORKFLOW_STEPS.PLATFORM_SELECTION
      };
    
    case 'social_media_generation':
      return {
        action: 'continue_process',
        label: '🎤 Continue to Voiceover',
        color: 'bg-purple-500 hover:bg-purple-600',
        step: WORKFLOW_STEPS.VOICEOVER_GENERATION
      };
    
    case 'voiceover_generation':
      return {
        action: 'continue_process',
        label: '🖼️ Continue to Media',
        color: 'bg-green-500 hover:bg-green-600',
        step: WORKFLOW_STEPS.MEDIA_SELECTION
      };
    
    case 'media_selection':
      return {
        action: 'continue_process',
        label: '🎬 Build Video',
        color: 'bg-red-500 hover:bg-red-600',
        step: WORKFLOW_STEPS.VIDEO_BUILDING
      };
    
    case 'completed':
      return {
        action: 'view_project',
        label: '👁️ View Project',
        color: 'bg-gray-500 hover:bg-gray-600',
        step: WORKFLOW_STEPS.COMPLETED
      };
    
    default:
      return {
        action: 'continue_process',
        label: '▶️ Continue Process',
        color: 'bg-indigo-500 hover:bg-indigo-600',
        step: currentStep
      };
  }
};

// Get process completion percentage
export const getProcessCompletion = (script) => {
  if (!script) return 0;
  
  let completed = 0;
  const totalSteps = 6; // Total workflow steps
  
  if (script.voiceover_script) completed += 1; // Script ready
  if (script.social_media_generated) completed += 1; // Social media ready
  if (script.voiceover_generated) completed += 1; // Voiceover ready
  if (script.media_selected) completed += 1; // Media selected (we'll need to add this field)
  if (script.video_generated) completed += 2; // Video complete (worth 2 points)
  
  return Math.round((completed / totalSteps) * 100);
};

// Navigate to appropriate step in video builder
export const navigateToStep = (router, script, targetStep = null) => {
  const currentStep = targetStep || determineCurrentStep(script);
  
  // Save process state before navigation
  if (script?.id) {
    saveProcessState(script.id, {
      currentStep: currentStep.id,
      scriptData: script,
      targetRoute: currentStep.route
    });
  }
  
  // Navigate with query parameters to indicate resume
  const queryParams = new URLSearchParams({
    resume: 'true',
    step: currentStep.id,
    scriptId: script?.id || 'new'
  });
  
  router.push(`${currentStep.route}?${queryParams.toString()}`);
};

// Start fresh process (clear all states)
export const startFreshProcess = (router) => {
  // Clear all stored states
  clearAllProcessStates();
  
  // Clear additional localStorage items that might persist
  if (typeof window !== 'undefined') {
    try {
      localStorage.removeItem('video-builder-storage');
      localStorage.removeItem('generatedVoiceoverData');
      localStorage.removeItem('videoBuilderState');
      localStorage.removeItem('projectData');
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }
  
  // Navigate to fresh video builder with fresh start flag
  router.push('/video-builder?fresh=true');
};