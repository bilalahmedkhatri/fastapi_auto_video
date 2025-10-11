'use client';

import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import {
  InputForm,
  LoadingState,
  ScriptsGrid,
  ScriptEditor,
  ScriptMerger,
  SocialMediaContent
} from '@/components/ScriptGenerator';
import VoiceSelectionStep from '../voicerover/components/VoiceSelectionStep';
import MediaManager from '@/components/MediaManager';
import VideoEffectsEditor from '@/components/VideoEffectsEditor';
import VideoGenerationStep from '@/components/VideoGenerationStep';
import VideoPreviewStep from '@/components/VideoPreviewStep';
import { useVideoBuilderStore, useStepNavigation, useVideoProcess as useVideoProcessStore, STEPS } from '@/stores/useVideoBuilderStore';
import ResumeProjectDialog from '@/components/ResumeProjectDialog';
import EnhancedProgressIndicator from '@/components/EnhancedProgressIndicator';
import VideoBuilderNavigation from '@/components/VideoBuilderNavigation';
import { saveProcessState, clearProcessState } from '@/utils/processStateManager';
import LocalStorageManager from '@/lib/localStorageManager';

// Backend Integration Components
import useVideoProcess from '@/hooks/useVideoProcess';
import ProcessProgressIndicators, { CompactProcessIndicator } from '@/components/ProcessProgressIndicators';
import ProcessControlPanel, { CompactControlPanel } from '@/components/ProcessControlPanel';
import { checkApiHealth } from '@/utils/videoProcessApi';

const ScriptGeneratorPage = () => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();
  
  // Zustand store state
  const store = useVideoBuilderStore(); 
  const navigation = useStepNavigation();
  const processStore = useVideoProcessStore();
  
  // Backend process integration
  const videoProcess = useVideoProcess(user?.id, {
    onProcessComplete: (processData) => {
      toast.success('Video generation completed successfully!');
      store.updateProcessState({ status: 'completed', ...processData });
      
      // Handle final results if available
      if (processData.results) {
        store.handleProcessResults('final_assembly', processData.results);
      }
    },
    onProcessError: (error) => {
      toast.error(`Process failed: ${error.message}`);
      store.setProcessError(error);
    },
    onStepChange: (step, stepData) => {
      store.updateProcessState({
        currentStep: step,
        ...stepData
      });
      
      // Handle step-specific results
      if (stepData.results) {
        store.handleProcessResults(step, stepData.results);
      }
    }
  });
  
  // Local state for UI
  const [showResumeDialog, setShowResumeDialog] = useState(false);
  const [loadingElapsed, setLoadingElapsed] = useState(0);
  
  // Use consistent userId: prefer authenticated user.id, fallback to localStorage-persisted ID
  const [userId, setUserId] = useState(() => {
    if (typeof window === 'undefined') return 'user_temp';
    
    // Get or create a persistent session ID from localStorage
    const storageKey = 'video_builder_session_id';
    let sessionId = localStorage.getItem(storageKey);
    
    if (!sessionId) {
      sessionId = `user_${Date.now()}`;
      localStorage.setItem(storageKey, sessionId);
    }
    
    return sessionId;
  });
  
  // Update userId when user authenticates
  useEffect(() => {
    if (user?.id && userId !== user.id) {
      setUserId(user.id);
      // Update the stored session ID to use the authenticated user ID
      if (typeof window !== 'undefined') {
        localStorage.setItem('video_builder_session_id', user.id);
      }
    }
  }, [user?.id]);
  
  // Cleanup old workflow entries - keep only current user's workflow
  useEffect(() => {
    if (userId && typeof window !== 'undefined') {
      try {
        const allWorkflows = workflowManager.getAll();
        const currentWorkflowId = `workflow_${userId}`;
        
        // Remove all workflows except the current user's workflow
        const cleanedWorkflows = allWorkflows.filter(workflow => 
          workflow && workflow.id === currentWorkflowId
        );
        
        // Only update if we actually removed something
        if (cleanedWorkflows.length !== allWorkflows.length) {
          localStorage.setItem('videoBuilderWorkflow', JSON.stringify(cleanedWorkflows));
          console.log(`🧹 Cleaned up old workflows. Kept ${cleanedWorkflows.length} of ${allWorkflows.length} entries`);
        }
      } catch (error) {
        console.error('Error cleaning up old workflows:', error);
      }
    }
  }, [userId]); // Run when userId changes or on mount
  
  const [isGeneratingSocialMedia, setIsGeneratingSocialMedia] = useState(false);
  const [useBackendProcess, setUseBackendProcess] = useState(false);
  const [backendAvailable, setBackendAvailable] = useState(false);
  const [workflowManager] = useState(() => new LocalStorageManager('videoBuilderWorkflow'));

  const API_BASE = '/api/script-generator';

  // Backend process functions
  const startBackendProcess = async () => {
    if (!user?.id) {
      toast.error('User authentication required for backend process');
      return;
    }

    try {
      store.setLoading(true);
      store.setCurrentStep(STEPS.LOADING);
      
      // Prepare process data
      const processData = store.updateFormDataForBackend(
        store.formData,
        user.id,
        `session_${Date.now()}`
      );

      console.log('Starting backend video process with data:', processData);
      
      // Start the backend process
      const response = await videoProcess.startProcess(processData);
      
      toast.success('Video generation process started successfully!');
      
      // Update UI to show process is running
      store.setCurrentStep(STEPS.LOADING);
      
    } catch (error) {
      console.error('Failed to start backend process:', error);
      toast.error(`Failed to start process: ${error.message}`);
      store.setLoading(false);
    }
  };

  const pauseBackendProcess = async (reason) => {
    try {
      await videoProcess.pauseProcess(reason);
    } catch (error) {
      console.error('Failed to pause process:', error);
      throw error;
    }
  };

  const resumeBackendProcess = async () => {
    try {
      await videoProcess.resumeProcess();
    } catch (error) {
      console.error('Failed to resume process:', error);
      throw error;
    }
  };

  const cancelBackendProcess = async (reason) => {
    try {
      await videoProcess.cancelProcess();
      store.clearProcessState();
      store.setCurrentStep(STEPS.INPUT);
    } catch (error) {
      console.error('Failed to cancel process:', error);
      throw error;
    }
  };

  const retryBackendProcess = async (reason) => {
    try {
      await videoProcess.retryStep(null, reason);
    } catch (error) {
      console.error('Failed to retry process:', error);
      throw error;
    }
  };

  // Script type configurations
  const scriptTypeConfigs = {
    short: { name: 'Short', description: '30-45 seconds, quick & punchy', icon: '⚡' },
    medium: { name: 'Medium', description: '1-2 minutes, balanced info', icon: '📊' },
    long: { name: 'Long', description: '3-5 minutes, in-depth', icon: '📚' },
    educational: { name: 'Educational', description: '2-4 minutes, teaching style', icon: '🎓' },
    storytelling: { name: 'Storytelling', description: '2-3 minutes, narrative', icon: '📖' },
    entertaining: { name: 'Entertaining', description: '1-2 minutes, fun & engaging', icon: '🎪' }
  };

  // Loading elapsed timer effect
  useEffect(() => {
    let timer;
    if (store.currentStep === STEPS.LOADING) {
      setLoadingElapsed(0);
      timer = setInterval(() => {
        setLoadingElapsed(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [store.currentStep]);

  // Check backend availability
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const isAvailable = await checkApiHealth();
        setBackendAvailable(isAvailable);
        if (isAvailable) {
          console.log('Backend video process API is available');
        } else {
          console.log('Backend video process API is not available, falling back to legacy mode');
        }
      } catch (error) {
        console.error('Error checking backend availability:', error);
        setBackendAvailable(false);
      }
    };

    checkBackend();
  }, []);

  // Sync video process updates with store
  useEffect(() => {
    if (videoProcess.currentProcess && videoProcess.currentProcess.id !== processStore.processId) {
      store.setProcessId(videoProcess.currentProcess.id);
    }
    
    if (videoProcess.processState && videoProcess.processState !== processStore.processState) {
      store.updateProcessState({
        status: videoProcess.processState,
        currentStep: videoProcess.currentStep,
        progress: videoProcess.progress,
        error: videoProcess.error
      });
    }
  }, [
    videoProcess.currentProcess?.id, 
    videoProcess.processState, 
    videoProcess.currentStep, 
    videoProcess.progress, 
    videoProcess.error?.message,
    processStore.processId,
    processStore.processState
  ]);

  // Auto-clear localStorage after 150 seconds
  useEffect(() => {
    const clearLocalStorageTimer = setTimeout(() => {
      try {
        // Clear specific localStorage items
        localStorage.removeItem('generatedVoiceoverData');
        localStorage.removeItem('videoBuilderState');
        localStorage.removeItem('projectData');
        
        // Log the cleanup for debugging
        console.log('📅 Auto-cleanup: localStorage cleared after 4 minutes');
        
        // Show a toast notification
        toast('Session data automatically cleared after 4 minutes', {
          duration: 4000,
          icon: 'ℹ️',
        });
      } catch (error) {
        console.error('Error clearing localStorage:', error);
      }
    }, 240 * 1000); // 240 seconds (4 minutes)

    // Cleanup timer on component unmount
    return () => {
      clearTimeout(clearLocalStorageTimer);
    };
  }, []);

  // Auto-generate social media content when reaching social-media step
  // DISABLED for now to prevent infinite loops - will be manual generation only
  // useEffect(() => {
  //   if (store.currentStep === 'social-media' && !store.socialMediaContent && !store.loading) {
  //     console.log('Auto-generating social media content for step transition...');
  //     generateSocialMediaContent();
  //   }
  // }, [store.currentStep]);

  // Project initialization and resume logic
  useEffect(() => {
    if (typeof window !== 'undefined' && user?.id) {
      const urlParams = new URLSearchParams(window.location.search);
      const resume = urlParams.get('resume');
      const step = urlParams.get('step');
      const scriptId = urlParams.get('scriptId');
      const fresh = urlParams.get('fresh');
      
      // Handle fresh start (from "New Script" button)
      if (fresh === 'true') {
        console.log('🆕 Starting fresh process - clearing all states');
        
        // Force reset the Zustand store
        store.resetToInitialState();
        
        // Create completely new project
        store.createNewProject(user.id);
        
        // Ensure we start at INPUT step
        store.setCurrentStep(STEPS.INPUT);
        
        // Clean up URL parameters
        window.history.replaceState({}, document.title, window.location.pathname);
        
        toast.success('Starting fresh video creation process!', { duration: 2000 });
        return; // Exit early - skip all other logic
      }
      
      // Handle resume from generated-scripts page
      if (resume === 'true' && step && scriptId) {
        // Load process state from storage
        import('@/utils/processStateManager').then(({ getProcessState, WORKFLOW_STEPS }) => {
          const processState = getProcessState(scriptId);
          
          if (processState && processState.scriptData) {
            // Restore state with script data
            const script = processState.scriptData;
            
            // Update store with script data
            store.setScripts([script]);
            store.setSelectedScript(0);
            
            // Navigate to appropriate step based on process state
            switch (step) {
              case 'platform_selection':
                store.setCurrentStep(STEPS.SCRIPTS);
                break;
              case 'social_media_generation':
                store.setCurrentStep(STEPS.SOCIAL_MEDIA);
                break;
              case 'voiceover_generation':
                store.setCurrentStep(STEPS.VOICEOVER);
                break;
              case 'media_selection':
                store.setCurrentStep(STEPS.MEDIA);
                break;
              case 'video_building':
                store.setCurrentStep(STEPS.VIDEO_EFFECTS);
                break;
              default:
                store.setCurrentStep(STEPS.SCRIPTS);
            }
            
            toast.success(`Resuming from ${WORKFLOW_STEPS[step.toUpperCase()]?.name || 'previous step'}`, {
              duration: 3000
            });
          } else {
            // Fallback to script selection if no process state
            store.setCurrentStep(STEPS.SCRIPTS);
            toast('Starting fresh process', { 
              duration: 3000,
              icon: 'ℹ️'
            });
          }
          
          // Clean up URL parameters
          window.history.replaceState({}, document.title, window.location.pathname);
        });
        
        return; // Exit early for resume flow
      }
      
      // Check if there's an existing project (normal flow)
      const existingProject = store.getProjectSummary();
      
      if (existingProject.projectId && !step && !resume) {
        // Show resume dialog if there's an existing project
        setShowResumeDialog(true);
      } else if (!existingProject.projectId && !resume) {
        // Create new project if none exists
        store.createNewProject(user.id);
      }
      
      // Handle URL step parameter (for backward compatibility)
      if (step === 'social-media') {
        const voiceoverData = localStorage.getItem('generatedVoiceoverData');
        if (voiceoverData) {
          try {
            const parsedData = JSON.parse(voiceoverData);
            console.log('Loading voiceover data for social media:', parsedData);
            console.log('Script data structure:', parsedData.script_data);
            console.log('Script data keys:', Object.keys(parsedData.script_data || {}));
            console.log('Has voiceover_script:', !!parsedData.script_data?.voiceover_script);
            
            // Ensure script_data has all required fields for ScriptsGrid
            const scriptDataWithFallbacks = {
              ...parsedData.script_data,
              // Fallback fields in case they're missing
              voiceover_script: parsedData.script_data?.voiceover_script || 
                               parsedData.script_data?.script || 
                               parsedData.script_data?.content || 
                               'Script content not available',
              title: parsedData.script_data?.title || 'Generated Script',
              description: parsedData.script_data?.description || '',
              tags: parsedData.script_data?.tags || [],
              duration_estimate: parsedData.script_data?.duration_estimate || 'Unknown',
              word_count: parsedData.script_data?.word_count || 0,
              script_type: parsedData.script_data?.script_type || 'unknown',
              category: parsedData.script_data?.category || 'General',
              language: parsedData.script_data?.language || 'English'
            };
            
            console.log('Enhanced script data:', scriptDataWithFallbacks);
            
            // Update store with enhanced voiceover data
            store.setScripts([scriptDataWithFallbacks]);
            store.setSelectedScript(0);
            store.setVoiceoverData(parsedData);
            store.setCurrentStep(STEPS.SOCIAL_MEDIA);
            
            localStorage.removeItem('generatedVoiceoverData');
            
            setTimeout(() => {
              generateSocialMediaContent(0);
            }, 100);
            
          } catch (error) {
            console.error('Error parsing voiceover data:', error);
            store.setCurrentStep(STEPS.INPUT);
          }
        }
        
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, [user?.id, store]);

  // Track workflow progress in localStorage
  useEffect(() => {
    if (store.currentStep && userId) {
      const stepData = {};
      
      // Collect step-specific data
      if (store.currentStep === STEPS.SCRIPTS && store.scripts.length > 0 && store.selectedScriptIndex >= 0) {
        stepData.scriptId = store.scripts[store.selectedScriptIndex]?.id;
      } else if (store.currentStep === STEPS.VOICEOVER && store.voiceoverData) {
        stepData.audioSettings = store.voiceoverData.audio_settings;
        stepData.audioUrl = store.voiceoverData.generated_audio?.audio_url;
        stepData.voiceId = store.voiceoverData.voice?.voice_id;
        stepData.voiceName = store.voiceoverData.voice?.name;
        stepData.generatedAt = new Date().toISOString();
        stepData.generationTime = store.voiceoverData.generated_audio?.generation_time;
      } else if (store.currentStep === STEPS.SOCIAL_MEDIA && store.socialMediaContent) {
        stepData.platforms = Object.keys(store.socialMediaContent || {});
      } else if (store.currentStep === STEPS.MEDIA && store.selectedMedia) {
        stepData.mediaCount = store.selectedMedia?.length || 0;
      } else if (store.currentStep === STEPS.VIDEO_EFFECTS && store.videoEffectsConfig) {
        stepData.effectsConfigured = true;
      } else if (store.currentStep === STEPS.VIDEO_GENERATION && store.generatedVideoData) {
        stepData.videoUrl = store.generatedVideoData?.videoUrl;
      }
      
      try {
        workflowManager.updateVideoBuilderWorkflow(userId, store.currentStep, stepData);
      } catch (error) {
        console.error('Failed to update workflow in localStorage:', error);
      }
    }
  }, [store.currentStep, userId, store.scripts, store.selectedScriptIndex, store.voiceoverData, store.socialMediaContent, store.selectedMedia, store.videoEffectsConfig, store.generatedVideoData]);

  // Protect the route
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      toast.error('Please login to access the Script Generator');
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Don't render anything if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  // Handle form input changes
  // const handleInputChange = (e) => {
  //   const { name, value } = e.target;
  //   setFormData(prev => ({
  //     ...prev,
  //     [name]: value
  //   }));
  // };

  // Resume dialog handlers
  const handleResumeProject = () => {
    setShowResumeDialog(false);
    toast.success('Resumed your video project!');
  };

  const handleStartNewProject = () => {
    store.deleteProject();
    store.createNewProject(user.id);
    setShowResumeDialog(false);
    toast.success('Started a new video project!');
  };

  const handleCloseResumeDialog = () => {
    setShowResumeDialog(false);
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    store.updateFormData({ [name]: value });
  };

  // Handle script type selection
  const toggleScriptType = (type) => {
    const currentTypes = store.formData.scriptTypes;
    const newTypes = currentTypes.includes(type)
      ? currentTypes.filter(t => t !== type)
      : [...currentTypes, type];
    store.updateFormData({ scriptTypes: newTypes });
  };

  // Generate scripts with backend process option
  const generateScripts = async () => {
    if (!store.formData.userPrompt.trim()) {
      toast.error('Please enter a video topic/prompt');
      return;
    }

    if (store.formData.scriptTypes.length === 0) {
      toast.error('Please select at least one script type');
      return;
    }

    // Use backend process if available and enabled
    if (useBackendProcess && backendAvailable) {
      return await startBackendProcess();
    }

    // Legacy script generation
    store.setLoading(true);
    store.setCurrentStep(STEPS.LOADING);
    store.markStepInProgress(STEPS.SCRIPTS);
    const generationStartTime = Date.now();

    try {
      console.log('Generating scripts with data:', API_BASE)
      const response = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_prompt: store.formData.userPrompt,
          script_types: store.formData.scriptTypes,
          voiceover_language: store.formData.language,
          category: store.formData.category,
          user_id: userId
        })
      });

      console.log("check response: ", response)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        store.setScripts(data.scripts);
        store.setCurrentStep(STEPS.SCRIPTS);
        store.setGenerationDuration(Date.now() - generationStartTime);
        
        // Save process state for each generated script
        data.scripts.forEach(async (script, index) => {
          if (script.id) {
            // Save to process state manager for backward compatibility
            saveProcessState(script.id, {
              currentStep: 'script_selection',
              scriptData: script,
              formData: store.formData,
              generatedAt: new Date().toISOString()
            });
            
            console.log(`✅ Script ${script.id} saved to process state: script_selection`);
          }
        });
        
        toast.success(`Generated ${data.scripts.length} script variations!`);
      } else {
        toast.error(data.message || 'Failed to generate scripts');
        store.setCurrentStep(STEPS.INPUT);
      }
    } catch (error) {
      console.error('Error generating scripts:', error);
      if (error.message.includes('fetch')) {
        toast.error('Error connecting to server. Please check your internet connection and try again.');
      } else if (error.message.includes('HTTP error')) {
        toast.error(`Server error (${error.message}). Please try again later.`);
      } else {
        toast.error('An unexpected error occurred. Please try again.');
      }
      store.setCurrentStep(STEPS.INPUT);
    } finally {
      store.setLoading(false);
    }
  };

  // Regenerate scripts
  const regenerateScripts = async () => {
    store.setLoading(true);
    store.setCurrentStep(STEPS.LOADING);
    const generationStartTime = Date.now();

    try {
      const response = await fetch(`${API_BASE}/regenerate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_prompt: store.formData.userPrompt,
          script_types: store.formData.scriptTypes,
          voiceover_language: store.formData.language,
          category: store.formData.category,
          user_id: userId
        })
      });

      const data = await response.json();

      if (data.success) {
        store.setScripts(data.scripts);
        store.setCurrentStep(STEPS.SCRIPTS);
        store.setGenerationDuration(Date.now() - generationStartTime);
        toast.success(`Regenerated ${data.scripts.length} script variations!`);
      } else {
        toast.error(data.message || 'Failed to regenerate scripts');
      }
    } catch (error) {
      console.error('Error regenerating scripts:', error);
      toast.error('Error connecting to server. Please try again.');
    } finally {
      store.setLoading(false);
    }
  };

  // Save directly edited script
  const saveDirectEdit = async () => {
    if (store.selectedScriptIndex === -1) {
      toast.error('No script selected');
      return;
    }

    if (!store.editedScriptContent.trim()) {
      toast.error('Script content cannot be empty');
      return;
    }

    try {
      const updatedScripts = [...store.scripts];
      updatedScripts[store.selectedScriptIndex] = {
        ...updatedScripts[store.selectedScriptIndex],
        voiceover_script: store.editedScriptContent,
        word_count: store.editedScriptContent.split(' ').length
      };
      
      store.setScripts(updatedScripts);
      store.setEditedScriptContent('');
      store.setCurrentStep(STEPS.SCRIPTS);
      toast.success('Script updated successfully!');
    } catch (error) {
      console.error('Error updating script:', error);
      toast.error('Error updating script. Please try again.');
    }
  };

  // Edit script
  const editScript = async () => {
    if (store.selectedScriptIndex === -1) {
      toast.error('Please select a script to edit first');
      return;
    }

    if (!store.editInstructions.trim()) {
      toast.error('Please enter edit instructions');
      return;
    }

    store.setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/edit/${store.selectedScriptIndex}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          script_index: store.selectedScriptIndex,
          edit_instructions: store.editInstructions,
          user_id: userId
        })
      });

      const editedScript = await response.json();

      if (response.ok) {
        const updatedScripts = [...store.scripts];
        updatedScripts[store.selectedScriptIndex] = editedScript;
        store.setScripts(updatedScripts);
        store.setEditInstructions('');
        store.setCurrentStep(STEPS.SCRIPTS);
        toast.success('Script edited successfully!');
      } else {
        toast.error('Failed to edit script');
      }
    } catch (error) {
      console.error('Error editing script:', error);
      toast.error('Error connecting to server. Please try again.');
    } finally {
      store.setLoading(false);
    }
  };

  // Merge scripts
  const mergeScripts = async () => {
    if (store.selectedForMerge.length < 2) {
      toast.error('Please select at least 2 scripts to merge');
      return;
    }

    store.setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/merge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          script_indices: store.selectedForMerge,
          merge_instructions: store.mergeInstructions,
          user_id: userId
        })
      });

      const mergedScript = await response.json();

      if (response.ok) {
        store.setScripts([...store.scripts, mergedScript]);
        store.setSelectedForMerge([]);
        store.setMergeInstructions('');
        store.setCurrentStep(STEPS.SCRIPTS);
        toast.success('Scripts merged successfully!');
      } else {
        toast.error('Failed to merge scripts');
      }
    } catch (error) {
      console.error('Error merging scripts:', error);
      toast.error('Error connecting to server. Please try again.');
    } finally {
      store.setLoading(false);
    }
  };

  // Generate social media content
  const generateSocialMediaContent = async (scriptIndex = null, selectedPlatforms = null) => {
    // Prevent multiple simultaneous requests
    if (isGeneratingSocialMedia || store.loading) {
      console.log('Social media generation already in progress, skipping...');
      return;
    }

    // Determine which script to use
    let indexToUse = scriptIndex;
    
    // If no scriptIndex provided, try to find the script from selectedScriptForVoiceover
    if (indexToUse === null) {
      if (store.selectedScriptForVoiceover) {
        // Find the index of selectedScriptForVoiceover in the scripts array
        indexToUse = store.scripts.findIndex(script => 
          script.id === store.selectedScriptForVoiceover.id || 
          script.title === store.selectedScriptForVoiceover.title
        );
        console.log('📍 Found script index from selectedScriptForVoiceover:', indexToUse);
      } else {
        // Fallback to selectedScriptIndex
        indexToUse = store.selectedScriptIndex;
        console.log('📍 Using selectedScriptIndex:', indexToUse);
      }
    }
    
    // Use provided platforms or fallback to default platforms
    const platformsToUse = selectedPlatforms || store.selectedPlatforms || ['youtube', 'instagram', 'tiktok', 'linkedin', 'twitter', 'facebook'];
    
    console.log('🚀 generateSocialMediaContent called with:', { 
      scriptIndex, 
      indexToUse, 
      scripts: store.scripts.length, 
      currentStep: store.currentStep,
      userId,
      selectedScript: store.scripts[indexToUse],
      selectedScriptForVoiceover: store.selectedScriptForVoiceover,
      platforms: platformsToUse
    });
    
    if (indexToUse === -1 || !store.scripts[indexToUse]) {
      console.error('❌ No valid script found at index:', indexToUse);
      console.error('❌ Store state:', {
        selectedScriptIndex: store.selectedScriptIndex,
        selectedScriptForVoiceover: store.selectedScriptForVoiceover,
        scriptsCount: store.scripts.length
      });
      toast.error('Please select a script first');
      return;
    }

    console.log('Generating social media content for script:', store.scripts[indexToUse]?.title);
    setIsGeneratingSocialMedia(true);
    store.setLoading(true);

    try {
      console.log('Sending social media generation request:', {
        script_index: indexToUse,
        user_id: userId,
        platforms: platformsToUse,
        script_data: store.scripts[indexToUse]
      });

      const response = await fetch(`${API_BASE}/generate-social-media`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          script_index: indexToUse,
          user_id: userId,
          platforms: platformsToUse,
          // Include script data to avoid session dependency
          script_data: {
            title: store.scripts[indexToUse].title,
            description: store.scripts[indexToUse].description,
            voiceover_script: store.scripts[indexToUse].voiceover_script,
            script_type: store.scripts[indexToUse].script_type,
            category: store.scripts[indexToUse].category,
            language: store.scripts[indexToUse].language,
            tags: store.scripts[indexToUse].tags || []
          }
        })
      });

      console.log('Social media response status:', response.status);
      console.log('Social media response ok:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Social media API error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      console.log('Social media API response data:', data);

      if (data.success) {
        console.log('✅ Social media generation successful, updating store...');
        console.log('📦 Social media data received:', data);
        
        store.setSocialMediaContent(data);
        console.log('✅ Store updated with social media content');
        
        store.setCurrentStep(STEPS.SOCIAL_MEDIA);
        console.log('✅ Current step set to:', STEPS.SOCIAL_MEDIA);
        console.log('📊 Current store state:', {
          currentStep: store.currentStep,
          hasSocialMediaContent: !!store.socialMediaContent,
          loading: store.loading
        });
        
        // Update process state - mark social media as complete
        const currentScript = store.scripts[indexToUse];
        if (currentScript?.id) {
          const updatedScript = {
            ...currentScript,
            social_media_generated: true,
            social_media_content: data
          };
          
          // Save updated script state with social media data
          saveProcessState(currentScript.id, {
            currentStep: 'voiceover_generation',
            scriptData: updatedScript,
            socialMediaData: data,
            lastUpdated: new Date().toISOString()
          });
          
          console.log(`✅ Workflow updated for script ${currentScript.id}: social_media_complete`);
        }
        
        toast.success('Social media content generated successfully!');
      } else {
        console.error('Social media generation failed:', data.message);
        toast.error(data.message || 'Failed to generate social media content');
      }
    } catch (error) {
      console.error('Error generating social media content:', error);
      if (error.message.includes('fetch')) {
        toast.error('Network error: Unable to connect to the server. Please check if the server is running.');
      } else if (error.message.includes('HTTP error')) {
        toast.error(`Server error: ${error.message}`);
      } else {
        toast.error(`Unexpected error: ${error.message}`);
      }
    } finally {
      store.setLoading(false);
      setIsGeneratingSocialMedia(false);
    }
  };

  // Start voiceover generation
  const startVoiceoverGeneration = (scriptIndex = null) => {
    const indexToUse = scriptIndex !== null ? scriptIndex : store.selectedScriptIndex;
    
    if (indexToUse === -1 || !store.scripts[indexToUse]) {
      toast.error('Please select a script first');
      return;
    }

    const scriptToUse = store.scripts[indexToUse];
    console.log('🎯 Starting voiceover generation for script:', scriptToUse?.title);
    console.log('📋 Full script data:', scriptToUse);
    console.log('📊 Store state before setting:', {
      selectedScriptIndex: indexToUse,
      totalScripts: store.scripts.length,
      currentSelectedScript: store.selectedScriptForVoiceover
    });
    
    // Mark scripts step as completed before moving to voiceover
    try {
      workflowManager.markStepCompleted(userId, 'scripts', {
        scriptId: scriptToUse?.id
      });
    } catch (error) {
      console.error('Failed to mark scripts step as completed:', error);
    }
    
    // Set the selected script
    store.setSelectedScriptForVoiceover(scriptToUse);
    
    console.log('✅ Called setSelectedScriptForVoiceover with:', scriptToUse?.title);
    console.log('📊 Store state after setting:', {
      selectedScriptForVoiceover: store.selectedScriptForVoiceover
    });
    
    // Move to voiceover step
    store.setCurrentStep(STEPS.VOICEOVER);
  };

  // Handle voiceover completion
  const handleVoiceoverComplete = (data) => {
    try {
      console.log('Voiceover generation completed:', data);
      
      // Check if data contains an error
      if (data && data.error) {
        const errorMessage = typeof data.error === 'string' 
          ? data.error 
          : data.error.message || JSON.stringify(data.error) || 'Voiceover generation failed';
        toast.error(`Voiceover generation failed: ${errorMessage}`);
        return;
      }
      
      // Check if data is valid
      if (!data || !data.generated_audio) {
        toast.error('Voiceover generation failed: No audio data received');
        return;
      }
      
      store.setVoiceoverData(data);
      toast.success('Voiceover generated successfully! Proceeding to social media generation...');
      
      // Mark voiceover step as completed in workflow
      try {
        workflowManager.markStepCompleted(userId, 'voiceover', {
          audioSettings: data.audio_settings,
          audioUrl: data.generated_audio?.audio_url,
          voiceId: data.voice?.voice_id,
          voiceName: data.voice?.name,
          generationTime: data.generated_audio?.generation_time
        });
      } catch (error) {
        console.error('Failed to mark voiceover step as completed:', error);
      }
      
      // Update process state - mark voiceover as complete
      const currentScript = store.selectedScriptForVoiceover;
      if (currentScript?.id) {
        const updatedScript = {
          ...currentScript,
          voiceover_generated: true,
          voiceover_data: data
        };
        
        saveProcessState(currentScript.id, {
          currentStep: 'media_selection',
          scriptData: updatedScript,
          voiceoverData: data,
          lastUpdated: new Date().toISOString()
        });
      }
      
      // Store the voiceover data for future use
      localStorage.setItem('generatedVoiceoverData', JSON.stringify({
        ...data,
        script_data: store.selectedScriptForVoiceover,
        timestamp: Date.now()
      }));
      
      // Automatically proceed to social media generation
      setTimeout(() => {
        generateSocialMediaContent();
      }, 100);
    } catch (error) {
      console.error('Error in handleVoiceoverComplete:', error);
      const errorMessage = error.message || 'An unexpected error occurred during voiceover completion';
      toast.error(`Voiceover completion failed: ${errorMessage}`);
    }
  };

  // Handle voiceover back navigation
  const handleVoiceoverBack = () => {
    store.setCurrentStep(STEPS.SCRIPTS);
    store.setSelectedScriptForVoiceover(null);
  };

  // Select script for video creation
  const selectScriptForVideo = async () => {
    if (store.selectedScriptIndex === -1) {
      toast.error('Please select a script for video creation');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/select/${store.selectedScriptIndex}?user_id=${userId}`, {
        method: 'POST'
      });

      const data = await response.json();

      if (data.success) {
        toast.success(`Selected script: "${data.ai_data.title}". Redirecting to video creation...`);
        // Here you would typically redirect to video creation page or trigger video generation
        console.log('Script data for video creation:', data.ai_data);
        
        // Simulate redirect to video creation
        setTimeout(() => {
          window.location.href = '/create-video';
        }, 100);
      } else {
        toast.error('Failed to select script for video creation');
      }
    } catch (error) {
      console.error('Error selecting script:', error);
      toast.error('Error connecting to server. Please try again.');
    }
  };

  // Main render
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-purple-900 py-8 px-4 transition-colors duration-200">
      
      {/* Backend Process Status */}
      {processStore.isBackendProcess && processStore.processId && (
        <div className="max-w-6xl mx-auto mb-6">
          <ProcessProgressIndicators
            processState={videoProcess.processState}
            currentStep={videoProcess.currentStep}
            progress={videoProcess.progress}
            message={videoProcess.error?.message || ''}
            startedAt={processStore.processStartedAt}
            duration={processStore.getProcessDuration()}
          />
        </div>
      )}

      {/* Backend Process Controls */}
      {processStore.isBackendProcess && processStore.processId && (
        <div className="max-w-6xl mx-auto mb-6">
          <ProcessControlPanel
            processState={videoProcess.processState}
            processId={videoProcess.currentProcess?.id}
            canControl={videoProcess.canControl}
            onPause={pauseBackendProcess}
            onResume={resumeBackendProcess}
            onCancel={cancelBackendProcess}
            onRetry={retryBackendProcess}
            processError={videoProcess.error}
            isLoading={videoProcess.isLoading}
          />
        </div>
      )}

      {/* Progress Indicator */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4 text-center">
            🎬 Video Creation Workflow
          </h2>
          <div className="flex justify-between items-center">
            {[
              { step: 'input', label: 'Script Input', icon: '✏️' },
              { step: 'loading', label: 'Generating', icon: '⏳' },
              { step: 'scripts', label: 'Script Selection', icon: '📋' },
              { step: 'voiceover', label: 'Voiceover', icon: '🎵' },
              { step: 'social-media', label: 'Social Media', icon: '📱' },
              { step: 'media', label: 'Media Manager', icon: '🎬' }
            ].map((item, index) => (
              <div key={item.step} className="flex flex-col items-center">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center text-xl mb-2 transition-all ${
                  store.currentStep === item.step 
                    ? (item.step === 'social-media' && store.socialMediaContent ? 'bg-green-500 text-white' : 
                       item.step === 'media' && store.selectedMedia.length > 0 ? 'bg-green-500 text-white' :
                       'bg-blue-500 text-white ring-4 ring-blue-200 dark:ring-blue-800')
                    : ['input', 'loading', 'scripts', 'editing', 'merging', 'voiceover', 'social-media', 'media'].indexOf(store.currentStep) > index ||
                      (item.step === 'scripts' && store.scripts.length > 0) ||
                      (item.step === 'voiceover' && store.voiceoverData) ||
                      (item.step === 'social-media' && store.socialMediaContent) ||
                      (item.step === 'media' && store.selectedMedia.length > 0)
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 dark:bg-gray-600 text-gray-500 dark:text-gray-400'
                }`}>
                  {store.currentStep === item.step && item.step === 'social-media' && store.socialMediaContent ? '✅' :
                   store.currentStep === item.step && item.step === 'media' && store.selectedMedia.length > 0 ? '✅' :
                   store.currentStep === item.step ? '🔄' : 
                   ['input', 'loading', 'scripts', 'editing', 'merging', 'voiceover', 'social-media', 'media'].indexOf(store.currentStep) > index ||
                   (item.step === 'scripts' && store.scripts.length > 0) ||
                   (item.step === 'voiceover' && store.voiceoverData) ||
                   (item.step === 'social-media' && store.socialMediaContent) ||
                   (item.step === 'media' && store.selectedMedia.length > 0) ? '✅' : item.icon}
                </div>
                <span className={`text-sm font-medium ${
                  store.currentStep === item.step ? 'text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400'
                }`}>
                  {item.label}
                </span>
                {index < 5 && (
                  <div className={`w-full h-1 mt-2 rounded ${
                    ['input', 'loading', 'scripts', 'editing', 'merging', 'voiceover', 'social-media', 'media'].indexOf(store.currentStep) > index ||
                    (index === 2 && store.scripts.length > 0) ||
                    (index === 3 && store.voiceoverData) ||
                    (index === 4 && store.socialMediaContent) ||
                    (index === 5 && store.selectedMedia.length > 0)
                      ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-600'
                  }`} style={{ marginLeft: '50px', width: '100px' }} />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {store.currentStep === 'input' && (
        <div>
          {/* Backend Process Option */}
          {backendAvailable && (
            <div className="max-w-4xl mx-auto mb-6">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                      🚀 Enhanced Backend Processing
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Use our advanced backend system for complete video generation with real-time progress tracking
                    </p>
                  </div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={useBackendProcess}
                      onChange={(e) => setUseBackendProcess(e.target.checked)}
                      className="sr-only"
                    />
                    <div className={`
                      relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                      ${useBackendProcess ? 'bg-blue-600' : 'bg-gray-200'}
                    `}>
                      <span className={`
                        inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                        ${useBackendProcess ? 'translate-x-6' : 'translate-x-1'}
                      `} />
                    </div>
                    <span className="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                      {useBackendProcess ? 'Enabled' : 'Disabled'}
                    </span>
                  </label>
                </div>
                
                {useBackendProcess && (
                  <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-start gap-3">
                      <div className="text-blue-600 dark:text-blue-400">ℹ️</div>
                      <div className="text-sm text-blue-800 dark:text-blue-200">
                        <strong>Backend Process Features:</strong>
                        <ul className="mt-2 space-y-1 list-disc list-inside">
                          <li>Complete video generation from prompt to final video</li>
                          <li>Real-time progress tracking with WebSocket updates</li>
                          <li>Pause, resume, and cancel capabilities</li>
                          <li>Automatic retry on failures</li>
                          <li>Steps: Scripts → Voiceover → Social Media → Media → Effects → Final Assembly</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          <InputForm
            formData={store.formData}
            scriptTypeConfigs={scriptTypeConfigs}
            onInputChange={handleInputChange}
            onToggleScriptType={toggleScriptType}
            onGenerateScripts={generateScripts}
            loading={store.loading || videoProcess.isLoading}
            backendProcessEnabled={useBackendProcess}
            backendAvailable={backendAvailable}
          />
        </div>
      )}
      {store.currentStep === 'loading' && (
        <div>
          {/* Show backend process progress if using backend */}
          {processStore.isBackendProcess && processStore.processId ? (
            <div className="max-w-4xl mx-auto">
              <CompactProcessIndicator
                processState={videoProcess.processState}
                currentStep={videoProcess.currentStep}
                progress={videoProcess.progress}
                message={videoProcess.error?.message || 'Processing your video...'}
                className="mb-6"
              />
              
              {/* Compact controls */}
              <div className="text-center">
                <CompactControlPanel
                  processState={videoProcess.processState}
                  processId={videoProcess.currentProcess?.id}
                  canControl={videoProcess.canControl}
                  onPause={pauseBackendProcess}
                  onResume={resumeBackendProcess}
                  onCancel={cancelBackendProcess}
                  className="justify-center"
                />
              </div>
            </div>
          ) : (
            <LoadingState loadingElapsed={loadingElapsed} />
          )}
        </div>
      )}
      
      {store.currentStep === 'scripts' && (
        <ScriptsGrid
          scripts={store.scripts}
          selectedScriptIndex={store.selectedScriptIndex}
          generationDuration={store.generationDuration}
          loading={store.loading}
          onSelectScript={store.setSelectedScript}
          onDirectEdit={(index, content) => {
            store.setSelectedScript(index);
            store.setEditedScriptContent(content);
            store.setEditMode('direct');
            store.setCurrentStep('editing');
          }}
          onAIEdit={(index) => {
            store.setSelectedScript(index); 
            store.setEditMode('instructions');
            store.setCurrentStep('editing');
          }}
          onSocialMedia={(index, selectedPlatforms) => generateSocialMediaContent(index, selectedPlatforms)}
          onRegenerateScripts={regenerateScripts}
          onEditSelected={() => store.setCurrentStep('editing')}
          onMergeScripts={() => store.setCurrentStep('merging')}
          onGenerateSocialMedia={() => generateSocialMediaContent()}
          onGenerateVoiceover={(index) => startVoiceoverGeneration(index)}
          onSelectScriptForVideo={selectScriptForVideo}
          onBackToInput={() => store.setCurrentStep('input')}
        />
      )}
      
      {store.currentStep === 'editing' && (
        <ScriptEditor
          selectedScript={store.scripts[store.selectedScriptIndex]}
          selectedScriptIndex={store.selectedScriptIndex}
          editMode={store.editMode}
          editedScriptContent={store.editedScriptContent}
          editInstructions={store.editInstructions}
          loading={store.loading}
          onEditModeChange={(mode) => {
            store.setEditMode(mode);
            if (mode === 'direct') {
              store.setEditedScriptContent(store.scripts[store.selectedScriptIndex]?.voiceover_script || '');
            }
          }}
          onEditedContentChange={store.setEditedScriptContent}
          onEditInstructionsChange={store.setEditInstructions}
          onSaveDirectEdit={saveDirectEdit}
          onApplyAIEdit={editScript}
          onCancel={() => {
            store.setCurrentStep('scripts');
            store.setEditInstructions('');
            store.setEditedScriptContent('');
            store.setEditMode('instructions');
          }}
        />
      )}
      
      {store.currentStep === 'merging' && (
        <ScriptMerger
          scripts={store.scripts}
          selectedForMerge={store.selectedForMerge}
          mergeInstructions={store.mergeInstructions}
          loading={store.loading}
          onToggleScriptSelection={(index) => {
            if (store.selectedForMerge.includes(index)) {
              store.setSelectedForMerge(store.selectedForMerge.filter(i => i !== index));
            } else {
              store.setSelectedForMerge([...store.selectedForMerge, index]);
            }
          }}
          onMergeInstructionsChange={store.setMergeInstructions}
          onMergeScripts={mergeScripts}
          onCancel={() => {
            store.setCurrentStep('scripts');
            store.setSelectedForMerge([]);
            store.setMergeInstructions('');
          }}
        />
      )}
      
      {store.currentStep === 'voiceover' && (
        <VoiceSelectionStep
          scriptData={store.selectedScriptForVoiceover}
          onNext={handleVoiceoverComplete}
          onBack={handleVoiceoverBack}
          userId={userId}
        />
      )}
      
      {store.currentStep === 'social-media' && (
        <>
          {console.log('Social media step - socialMediaContent:', store.socialMediaContent)}
          {console.log('Current store state:', { currentStep: store.currentStep, hasContent: !!store.socialMediaContent, loading: store.loading })}
          {store.loading ? (
            <div className="max-w-4xl mx-auto text-center p-8">
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-600 rounded-xl p-6">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <h3 className="text-xl font-semibold text-blue-800 dark:text-blue-300 mb-2">
                  🚀 Generating Social Media Content...
                </h3>
                <p className="text-blue-700 dark:text-blue-400">
                  Creating optimized content for all platforms
                </p>
              </div>
            </div>
          ) : !store.socialMediaContent ? (
            <div className="max-w-4xl mx-auto text-center p-8">
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-600 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-yellow-800 dark:text-yellow-300 mb-3">
                  📱 No Social Media Content Available
                </h3>
                <p className="text-yellow-700 dark:text-yellow-400 mb-4">
                  Social media content hasn't been generated yet. Let's generate it now!
                </p>
                <button
                  onClick={() => generateSocialMediaContent()}
                  className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-all"
                >
                  🚀 Generate Social Media Content
                </button>
              </div>
            </div>
          ) : (
            <SocialMediaContent
              socialMediaContent={store.socialMediaContent}
              loading={store.loading}
              onRegenerateSocialMedia={() => generateSocialMediaContent()}
              onBackToScripts={() => store.setCurrentStep('scripts')}
              onNext={() => {
                try {
                  workflowManager.markStepCompleted(userId, 'social-media', {
                    platforms: Object.keys(store.socialMediaContent || {})
                  });
                } catch (error) {
                  console.error('Failed to mark social-media step as completed:', error);
                }
                store.setCurrentStep(STEPS.MEDIA);
              }}
            />
          )}
        </>
      )}

      {store.currentStep === 'media' && (
        <MediaManager
          socialMediaContent={store.socialMediaContent}
          scriptData={store.selectedScriptForVoiceover}
          onNext={(selectedMedia) => {
            try {
              workflowManager.markStepCompleted(userId, 'media', {
                mediaCount: selectedMedia.length
              });
            } catch (error) {
              console.error('Failed to mark media step as completed:', error);
            }
            store.setSelectedMedia(selectedMedia);
            store.setCurrentStep(STEPS.VIDEO_EFFECTS);
            toast.success(`Selected ${selectedMedia.length} media items! Configuring video effects...`);
          }}
          onBack={() => store.setCurrentStep(STEPS.SOCIAL_MEDIA)}
        />
      )}

      {store.currentStep === 'video-effects' && (
        <VideoEffectsEditor
          selectedMedia={store.selectedMedia}
          scriptData={store.selectedScriptForVoiceover}
          socialMediaContent={store.socialMediaContent}
          onNext={(videoEffects) => {
            try {
              workflowManager.markStepCompleted(userId, 'video-effects', {
                effectsConfigured: true
              });
            } catch (error) {
              console.error('Failed to mark video-effects step as completed:', error);
            }
            store.setVideoEffectsConfig(videoEffects);
            store.setCurrentStep(STEPS.VIDEO_GENERATION);
            toast.success('Video effects configured! Starting video generation...');
          }}
          onBack={() => store.setCurrentStep(STEPS.MEDIA)}
        />
      )}

      {store.currentStep === 'video-generation' && (
        <VideoGenerationStep
          scriptData={store.selectedScriptForVoiceover}
          voiceoverData={store.voiceoverData}
          socialMediaContent={store.socialMediaContent}
          selectedMedia={store.selectedMedia}
          videoEffectsConfig={store.videoEffectsConfig}
          onComplete={(generatedVideo) => {
            try {
              workflowManager.markStepCompleted(userId, 'video-generation', {
                videoUrl: generatedVideo?.videoUrl,
                duration: generatedVideo?.duration
              });
            } catch (error) {
              console.error('Failed to mark video-generation step as completed:', error);
            }
            store.setGeneratedVideo(generatedVideo);
            store.setCurrentStep(STEPS.VIDEO_PREVIEW);
            toast.success('Video generation completed!');
          }}
          onBack={() => store.setCurrentStep(STEPS.MEDIA)}
          onError={(error) => {
            console.error('Video generation error:', error);
            toast.error(`Video generation failed: ${error.message}`);
          }}
        />
      )}

      {store.currentStep === 'video-preview' && (
        <VideoPreviewStep
          generatedVideo={store.generatedVideoData}
          onRegenerate={() => {
            // Instead of immediately regenerating, send user back to MEDIA step
            // so they can adjust media/effects before rebuilding.
            store.clearVideoGeneration();
            // Preserve previously selected media/effects in store; just move step back.
            store.setCurrentStep(STEPS.MEDIA);
            toast('Adjust your media or effects, then proceed to regenerate.', {
              icon: '🛠️'
            });
          }}
          onDownload={(videoData) => {
            toast.success('Video download initiated!');
          }}
          onNewVideo={() => {
            store.resetToInitialState();
            store.setCurrentStep(STEPS.INPUT);
            toast.success('Starting new video creation!');
          }}
          onBack={() => store.setCurrentStep(STEPS.MEDIA)}
        />
      )}
    </div>
  );
};

export default ScriptGeneratorPage;