"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Badge } from './ui/badge';
import { Play, Pause, RotateCcw, CheckCircle, Volume2, Settings, AlertCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { getVoiceovers } from '@/lib/voiceovers';
import LocalStorageManager from '@/lib/localStorageManager';

const VoiceSelectionStep = ({ scriptData, onNext, onBack, userId }) => {
  // Initialize LocalStorageManager for voiceover workflow tracking
  const voiceoverWorkflowManager = useRef(new LocalStorageManager('voiceoverWorkflow')).current;
  const [previousVoiceovers, setPreviousVoiceovers] = useState([]);
  const [selectedPreviousVoiceover, setSelectedPreviousVoiceover] = useState(null);
  
  // Fetch previous voiceovers from backend and localStorage
  useEffect(() => {
    const fetchPreviousVoiceovers = async () => {
      // First, try to load from localStorage
      const localVoiceovers = voiceoverWorkflowManager.getAll();
      console.log('📦 Loading voiceovers from localStorage:', localVoiceovers);
      
      // Filter and format localStorage voiceovers for display
      const formattedLocalVoiceovers = localVoiceovers
        .filter(vo => vo && vo.status === 'completed' && vo.audioUrl)
        .map(vo => ({
          id: vo.id,
          voice_name: vo.voiceName || vo.voice_name || 'Unknown Voice',
          voice_id: vo.voiceId || vo.voice_id,
          created_at: vo.completedAt || vo.created_at || new Date().toISOString(),
          speed: vo.speed || 1.0,
          pitch: vo.pitch || 1.0,
          volume: vo.volume || 0.8,
          audio_url: vo.audioUrl || vo.audio_url,
          generation_time: vo.generationTime || vo.generation_time,
          user_id: vo.userId || vo.user_id,
          script_id: vo.scriptId || vo.script_id
        }));
      
      // Set localStorage voiceovers first (for immediate display)
      if (formattedLocalVoiceovers.length > 0) {
        setPreviousVoiceovers(formattedLocalVoiceovers);
        console.log('✅ Loaded', formattedLocalVoiceovers.length, 'voiceovers from localStorage');
      }
      
      // Then try to fetch from backend API (optional enhancement)
      try {
        if (userId && scriptData?.id) {
          const data = await getVoiceovers({ 
            userId: userId, 
            scriptId: scriptData.id 
          });
          
          if (data && Array.isArray(data.voiceovers) && data.voiceovers.length > 0) {
            // Merge backend data with localStorage data (avoid duplicates)
            const backendIds = new Set(data.voiceovers.map(vo => vo.id));
            const uniqueLocalVoiceovers = formattedLocalVoiceovers.filter(vo => !backendIds.has(vo.id));
            const mergedVoiceovers = [...data.voiceovers, ...uniqueLocalVoiceovers];
            
            setPreviousVoiceovers(mergedVoiceovers);
            console.log('✅ Merged backend and localStorage voiceovers:', mergedVoiceovers.length, 'total');
          }
        }
      } catch (error) {
        console.warn('⚠️ Failed to fetch from backend API, using localStorage only:', error.message);
        // Keep using localStorage data, don't clear it
      }
    };
    
    fetchPreviousVoiceovers();
  }, [userId, scriptData?.id]);

  // Log localStorage workflow data on component mount and when it changes
  useEffect(() => {
    const workflowData = voiceoverWorkflowManager.getAll();
    console.log('📦 Voiceover Workflow LocalStorage Data:', workflowData);
    console.log('📊 Total voiceover records in localStorage:', workflowData.length);
  }, [voiceoverWorkflowManager]);

  // Debug logging for scriptData
  console.log('VoiceSelectionStep - Received scriptData:', scriptData);
  console.log('VoiceSelectionStep - scriptData type:', typeof scriptData);
  if (scriptData) {
    console.log('VoiceSelectionStep - scriptData keys:', Object.keys(scriptData));
    console.log('VoiceSelectionStep - Has voiceover_script:', !!scriptData.voiceover_script);
    console.log('VoiceSelectionStep - voiceover_script length:', scriptData.voiceover_script?.length || 0);
    console.log('VoiceSelectionStep - scriptData sample:', {
      id: scriptData.id,
      title: scriptData.title,
      hasVoiceoverScript: !!scriptData.voiceover_script,
      voiceoverScriptPreview: scriptData.voiceover_script?.substring(0, 100) + '...'
    });
  } else {
    console.log('VoiceSelectionStep - scriptData is null/undefined');
  }

  // Helper function to get script content with fallbacks
  const getScriptContent = () => {
    if (!scriptData) return 'No script data available';
    
    return scriptData.voiceover_script || 
           scriptData.script || 
           scriptData.content || 
           'Script content not available';
  };

  // Helper function to check if script content is available
  const hasScriptContent = () => {
    if (!scriptData) return false;
    
    return !!(scriptData.voiceover_script || 
              scriptData.script || 
              scriptData.content);
  };

  // State management
  const [voices, setVoices] = useState([]);
  const [filteredVoices, setFilteredVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [filters, setFilters] = useState({
    gender: '',
    accent: '',
    style: ''
  });
  const [audioSettings, setAudioSettings] = useState({
    speed: [1.0],
    pitch: [1.0], 
    volume: [0.8],
    background_music: false,
    background_music_volume: [0.3]
  });
  
  // Audio and generation states
  const [playingVoice, setPlayingVoice] = useState(null);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [generatedAudio, setGeneratedAudio] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioError, setAudioError] = useState(null);

  // Refs
  const audioRef = useRef(null);
  const { toast } = useToast();

  // Load available voices with improved error handling
  useEffect(() => {
    const loadVoices = async () => {
      try {
        const queryParams = new URLSearchParams();
        if (filters.gender) queryParams.append('gender', filters.gender);
        if (filters.accent) queryParams.append('accent', filters.accent);
        if (filters.style) queryParams.append('style', filters.style);
        
        const response = await fetch(`http://localhost:8000/api/voice/voices?${queryParams}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.voices && Array.isArray(data.voices)) {
          setVoices(data.voices);
          setFilteredVoices(data.voices);
          
          // Auto-select first voice if none selected
          if (!selectedVoice && data.voices.length > 0) {
            setSelectedVoice(data.voices[0]);
          }
        } else {
          throw new Error('Invalid response format from voices API');
        }
      } catch (error) {
        console.error('Failed to load voices:', error.message);
        toast({
          title: "Error",
          description: `Failed to load available voices: ${error.message}`,
          variant: "destructive"
        });
      }
    };

    loadVoices();
  }, [filters]);

  // Auto-select first voice when voices are loaded
  useEffect(() => {
    if (!selectedVoice && voices.length > 0) {
      setSelectedVoice(voices[0]);
    }
  }, [voices, selectedVoice]);

  // Enhanced audio playbook with proper error handling and CORS support
  const playVoiceSample = async (voice) => {
    try {
      // Stop any currently playing audio
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        setCurrentAudio(null);
        setPlayingVoice(null);
      }

      if (!voice.sample_url) {
        toast({
          title: "No Sample Available",
          description: "This voice doesn't have a preview sample",
          variant: "destructive"
        });
        return;
      }

      setPlayingVoice(voice.voice_id);
      setAudioError(null);
      
      // Create audio element with improved error handling
      const audio = new Audio();
      
      // Set up event listeners before setting src
      audio.addEventListener('loadstart', () => {
        console.log('Loading started for:', voice.sample_url);
      });
      
      audio.addEventListener('canplay', () => {
        console.log('Audio can start playing');
      });
      
      audio.addEventListener('error', (e) => {
        console.error('Audio playback failed:', e.target.error?.message || 'Unknown audio error');
        setAudioError(e.target.error);
        setPlayingVoice(null);
        toast({
          title: "Playback Error",
          description: `Failed to play voice sample: ${e.target.error?.message || 'Audio format not supported'}`,
          variant: "destructive"
        });
      });

      audio.addEventListener('ended', () => {
        setPlayingVoice(null);
        setCurrentAudio(null);
      });

      // Set audio properties for better compatibility
      audio.crossOrigin = 'anonymous';
      audio.preload = 'metadata';
      
      // Set the source
      const audioUrl = `http://localhost:8000${voice.sample_url}`;
      console.log('Attempting to play:', audioUrl);
      audio.src = audioUrl;
      
      setCurrentAudio(audio);
      
      // Play with user gesture handling
      try {
        await audio.play();
      } catch (playError) {
        console.error('Play error:', playError);
        if (playError.name === 'NotAllowedError') {
          toast({
            title: "Playback Blocked",
            description: "Browser blocked audio playback. Please interact with the page first.",
            variant: "destructive"
          });
        } else {
          throw playError;
        }
      }
    } catch (error) {
      console.error('Error in playVoiceSample:', error);
      setPlayingVoice(null);
      setAudioError(error);
      
      let errorMessage = "Failed to play voice sample";
      if (error.message.includes('CORS')) {
        errorMessage = "Audio blocked by CORS policy";
      } else if (error.message.includes('404')) {
        errorMessage = "Audio file not found";
      } else if (error.message.includes('network')) {
        errorMessage = "Network error loading audio";
      }
      
      toast({
        title: "Playback Error",
        description: errorMessage,
        variant: "destructive"
      });
    }
  };

  // Stop audio playback
  const stopAudio = () => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
      setPlayingVoice(null);
    }
  };

  // Generate voiceover with progress tracking
  const generateVoiceover = async () => {
    if (!selectedVoice || !scriptData) {
      toast({
        title: "Missing Requirements",
        description: "Please select a voice and ensure script data is available",
        variant: "destructive"
      });
      return;
    }

    if (!hasScriptContent()) {
      toast({
        title: "No Script Content",
        description: "No script content available for voiceover generation. Please ensure the script is properly loaded.",
        variant: "destructive"
      });
      console.error('Script content missing. Available scriptData:', scriptData);
      return;
    }

    console.log('Script data for voiceover:', scriptData);
    console.log('Selected voice:', selectedVoice);
    console.log('Audio settings:', audioSettings);

    setIsGenerating(true);
    setGenerationProgress(0);
    
    try {
      // Convert audioSettings arrays to scalar values for the API
      const apiAudioSettings = {
        speed: Array.isArray(audioSettings.speed) ? audioSettings.speed[0] : audioSettings.speed,
        pitch: Array.isArray(audioSettings.pitch) ? audioSettings.pitch[0] : audioSettings.pitch,
        volume: Array.isArray(audioSettings.volume) ? audioSettings.volume[0] : audioSettings.volume,
        tone: "neutral" // Default tone
      };

      const requestBody = {
        text: getScriptContent(),
        voice_id: selectedVoice.voice_id,
        audio_settings: apiAudioSettings,
        background_music: {
          enabled: audioSettings.background_music || false,
          music_type: "upbeat",
          volume: Array.isArray(audioSettings.background_music_volume) 
            ? audioSettings.background_music_volume[0] 
            : audioSettings.background_music_volume || 0.3,
          fade_in: 2.0,
          fade_out: 2.0
        },
        user_id: userId,
        script_id: scriptData.id || scriptData.script_id || `script_${Date.now()}`
      };

      console.log('Starting voiceover generation...');

      // Test server connectivity (try both localhost and 127.0.0.1)
      let serverUrl = 'http://localhost:8000';
      
      try {
        await fetch('http://localhost:8000/docs', { method: 'GET' });
      } catch (healthError) {
        try {
          await fetch('http://127.0.0.1:8000/docs', { method: 'GET' });
          serverUrl = 'http://127.0.0.1:8000';
        } catch (secondHealthError) {
          throw new Error('FastAPI server is not running. Please start the server and try again.');
        }
      }

      // Now try the voice generation endpoint
      let response;
      try {
        console.log('🔄 Sending voice generation request to:', `${serverUrl}/api/voice/generate`);
        console.log('📦 Request body:', JSON.stringify(requestBody, null, 2));
        
        response = await fetch(`${serverUrl}/api/voice/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });
        console.log('Voice generation response status:', response.status);
        console.log('Voice generation response ok:', response.ok);
      } catch (networkError) {
        console.error('Network connection failed:', networkError);
        throw new Error(`Unable to connect to voice generation endpoint: ${networkError.message}`);
      }

      if (!response.ok) {
        console.error(`❌ Voice generation failed with status: ${response.status}`);
        let errorMessage;
        try {
          const errorData = await response.json();
          console.error('📋 Error response data:', errorData);
          errorMessage = errorData.detail || errorData.message || `Server error (${response.status})`;
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
          errorMessage = `Server error (${response.status}): ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Voice generation result:', result);
      console.log('Available fields in response:', Object.keys(result));
      
      // Check for various possible audio URL fields
      const audioUrl = result.audio_url || result.audio_path || result.file_url || result.url;
      
      if (audioUrl) {
        // Ensure the result has the audio_url field that our components expect
        const generatedAudioData = {
          ...result,
          audio_url: audioUrl
        };
        
        setGeneratedAudio(generatedAudioData);
        
        // Add the newly generated voiceover to the previous voiceovers list
        const voiceoverId = result.id || result.voiceover_id || `vo_${Date.now()}`;
        const newVoiceoverEntry = {
          id: voiceoverId,
          voice_name: selectedVoice.name || selectedVoice.voice_id,
          voice_id: selectedVoice.voice_id,
          created_at: new Date().toISOString(),
          speed: apiAudioSettings.speed,
          pitch: apiAudioSettings.pitch,
          volume: apiAudioSettings.volume,
          audio_url: audioUrl,
          generation_time: result.generation_time,
          user_id: userId,
          script_id: scriptData.id || scriptData.script_id
        };
        
        // Store in localStorage for persistence
        try {
          await voiceoverWorkflowManager.create({
            id: voiceoverId,
            voiceName: newVoiceoverEntry.voice_name,
            voiceId: newVoiceoverEntry.voice_id,
            completedAt: newVoiceoverEntry.created_at,
            speed: newVoiceoverEntry.speed,
            pitch: newVoiceoverEntry.pitch,
            volume: newVoiceoverEntry.volume,
            audioUrl: newVoiceoverEntry.audio_url,
            generationTime: newVoiceoverEntry.generation_time,
            userId: newVoiceoverEntry.user_id,
            scriptId: newVoiceoverEntry.script_id,
            status: 'completed',
            step: 'voiceover_generated'
          });
          console.log('💾 Saved voiceover to localStorage with ID:', voiceoverId);
        } catch (storageError) {
          console.warn('⚠️ Failed to save to localStorage:', storageError.message);
          // Continue anyway, just log the error
        }
        
        // Add to the beginning of the list (most recent first)
        setPreviousVoiceovers(prev => [newVoiceoverEntry, ...prev]);
        
        console.log('✅ Added new voiceover to Previous Voiceovers list:', newVoiceoverEntry);
        
        toast({
          title: "Success",
          description: `Audio generated in ${result.generation_time?.toFixed(2)}s`,
          variant: "success"
        });
      
      } else {
        console.error('No audio URL found in response. Available fields:', Object.keys(result));
        console.error('Full response:', result);
        throw new Error('No audio URL in response. Check server logs for details.');
      }
    } catch (error) {
      // Comprehensive error message extraction with strict string conversion
      let errorMessage = "Failed to generate voiceover";
      
      try {
        // Extract meaningful error message
        if (typeof error === 'string') {
          errorMessage = error;
        } else if (error instanceof Error && error.message) {
          errorMessage = String(error.message);
        } else if (error && typeof error === 'object') {
          // Check each property and ensure it's a string
          const possibleMessages = [
            error.detail,
            error.message, 
            error.error,
            error.description,
            error.response?.data?.detail,
            error.response?.data?.message
          ];
          
          // Find the first string message
          for (const msg of possibleMessages) {
            if (msg && typeof msg === 'string' && msg.trim()) {
              errorMessage = msg.trim();
              break;
            } else if (msg && typeof msg !== 'string') {
              // Try to convert to string safely
              try {
                const stringMsg = String(msg);
                if (stringMsg && stringMsg !== '[object Object]' && stringMsg !== 'undefined') {
                  errorMessage = stringMsg;
                  break;
                }
              } catch (e) {
                // Continue to next property
                continue;
              }
            }
          }
        }
      } catch (extractionError) {
        errorMessage = "Error processing failed - unable to extract error details";
      }
      
      // Final safety check - ensure we have a valid string
      const finalMessage = (errorMessage && typeof errorMessage === 'string') ? 
        errorMessage : 'An unexpected error occurred during voiceover generation';
      
      console.error('Voiceover generation failed:', finalMessage);
      console.error('Original error object:', error);
      
      toast({
        title: "Generation Error", 
        description: finalMessage,
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
      setGenerationProgress(0);
    }
  };

  // Play generated audio
  const playGeneratedAudio = () => {
    if (!generatedAudio || !audioRef.current) return;

    try {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        console.log('Playing generated audio from URL:', generatedAudio.audio_url);
        // audioRef.current.src = `http://localhost:8000${generatedAudio.audio_url}`;
        audioRef.current.src = generatedAudio.audio_url;
        audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Error playing generated audio:', error);
      toast({
        title: "Playback Error",
        description: "Failed to play generated audio",
        variant: "destructive"
      });
    }
  };

  // Reset audio generation
  const resetGeneration = () => {
    setGeneratedAudio(null);
    setIsPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
    }
  };

  // Handle next step
  const handleNext = async () => {
    if (!generatedAudio) {
      toast({
        title: "No Audio Generated",
        description: "Please generate the voiceover before proceeding",
        variant: "destructive"
      });
      return;
    }

    // Ensure script_data has all necessary fields for next step
    const enhancedScriptData = {
      ...scriptData,
      voiceover_script: getScriptContent(),
      title: scriptData?.title || 'Generated Script',
      description: scriptData?.description || '',
      tags: scriptData?.tags || [],
      duration_estimate: scriptData?.duration_estimate || 'Unknown',
      word_count: scriptData?.word_count || getScriptContent().split(' ').length,
      script_type: scriptData?.script_type || 'unknown',
      category: scriptData?.category || 'General',
      language: scriptData?.language || 'English',
      id: scriptData?.id || `script_${Date.now()}`
    };

    const data = {
      voice: selectedVoice,
      audio_settings: audioSettings,
      generated_audio: generatedAudio,
      script_data: enhancedScriptData
    };

    // Update localStorage to mark voiceover step as completed
    try {
      // Extract voiceover ID from the generatedAudio object (which came from backend response)
      const voiceoverId = generatedAudio.id || generatedAudio.voiceover_id || generatedAudio.generated_voiceover_id;
      
      console.log('🔑 Attempting to update voiceover with ID:', voiceoverId);
      console.log('📦 Generated audio object:', generatedAudio);
      
      if (!voiceoverId) {
        console.warn('⚠️ No voiceover ID found in generatedAudio object. Cannot update localStorage.');
        console.log('Available fields in generatedAudio:', Object.keys(generatedAudio));
      } else {
        // Try to update existing record, or create new one if it doesn't exist
        try {
          await voiceoverWorkflowManager.update(voiceoverId, {
            step: 'voiceover_completed',
            completedAt: new Date().toISOString(),
            proceedingToNextStep: true,
            status: 'completed'
          });
          console.log('✅ Updated voiceover workflow status to completed for ID:', voiceoverId);
        } catch (updateError) {
          console.warn('⚠️ Update failed, attempting to create new record:', updateError.message);
          // If update fails (record doesn't exist), create new record with the voiceover ID
          await voiceoverWorkflowManager.create({
            id: voiceoverId, // Use actual voiceover ID, not scriptData.id
            step: 'voiceover_completed',
            scriptId: scriptData.id || scriptData.script_id,
            userId: userId,
            audioUrl: generatedAudio.audio_url,
            completedAt: new Date().toISOString(),
            proceedingToNextStep: true,
            status: 'completed'
          });
          console.log('✅ Created voiceover workflow completion record with ID:', voiceoverId);
        }
      }
    } catch (storageError) {
      console.error('❌ Failed to update voiceover workflow in localStorage:', storageError);
      console.error('❌ Error details:', storageError.message);
      // Don't block the flow if localStorage fails
    }

    console.log('Passing enhanced data to next step:', data);
    onNext(data);
  };

  // Get unique filter options
  const getFilterOptions = (field) => {
    const options = [...new Set(voices.map(voice => voice[field]))];
    return options.filter(Boolean).sort();
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Step 3: Voice Selection & Voiceover
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Choose a voice and customize audio settings for your script
        </p>
      </div>

      {/* Script Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Script Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Title:</span>
              <span className="ml-2 text-gray-900 dark:text-gray-100">
                {scriptData?.title || 'Generated Script'}
              </span>
            </div>
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Script:</span>
              <p className="mt-1 text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                {getScriptContent()}
              </p>
              {/* Debug info for development */}
              {process.env.NODE_ENV === 'development' && !hasScriptContent() && (
                <div className="mt-2 p-2 bg-red-100 dark:bg-red-900 text-xs text-red-600 dark:text-red-400 rounded">
                  <strong>Debug:</strong> Script content missing. Available fields: {scriptData ? Object.keys(scriptData).join(', ') : 'No scriptData'}
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <Badge variant="secondary">{scriptData?.word_count} words</Badge>
              <Badge variant="outline">{scriptData?.language}</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Previous Voiceovers Table Section */}
      {previousVoiceovers.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Previous Voiceovers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <div className="mb-2 text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-blue-500 rounded-full"></span>
                Click on any row to select a voiceover (excluding audio player)
              </div>
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">
                <thead className="bg-gray-100 dark:bg-gray-800">
                  <tr>
                    <th className="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-200">Voice</th>
                    <th className="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-200">Date</th>
                    <th className="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-200">Speed</th>
                    <th className="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-200">Pitch</th>
                    <th className="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-200">Volume</th>
                    <th className="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-200">Audio</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-100 dark:divide-gray-800">
                  {previousVoiceovers.map(vo => (
                    <tr 
                      key={vo.id} 
                      className={`transition-all duration-200 cursor-pointer ${
                        selectedPreviousVoiceover?.id === vo.id 
                          ? 'bg-blue-100 dark:bg-blue-900/30 ring-2 ring-blue-500 dark:ring-blue-400' 
                          : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                      onClick={(e) => {
                        // Don't select if clicking on audio controls
                        if (e.target.closest('audio')) {
                          return;
                        }
                        
                        // Set as selected
                        setSelectedPreviousVoiceover(vo);
                        
                        // Immediately apply as generated audio
                        const voiceoverData = {
                          id: vo.id,
                          audio_url: vo.audio_url,
                          generation_time: vo.generation_time,
                          voice_id: vo.voice_id,
                          voice_name: vo.voice_name
                        };
                        
                        setGeneratedAudio(voiceoverData);
                        
                        toast({
                          title: "Voiceover Applied",
                          description: `Now using: ${vo.voice_name}`,
                          variant: "success"
                        });
                      }}
                    >
                      <td className="px-4 py-2">
                        <div className="flex items-center gap-2">
                          {selectedPreviousVoiceover?.id === vo.id && (
                            <CheckCircle className="h-5 w-5 text-blue-500 dark:text-blue-400 flex-shrink-0" />
                          )}
                          <span className="font-medium text-gray-900 dark:text-gray-100">{vo.voice_name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-2 text-gray-600 dark:text-gray-300">{new Date(vo.created_at).toLocaleString()}</td>
                      <td className="px-4 py-2 text-gray-600 dark:text-gray-300">{vo?.speed}</td>
                      <td className="px-4 py-2 text-gray-600 dark:text-gray-300">{vo?.pitch}</td>
                      <td className="px-4 py-2 text-gray-600 dark:text-gray-300">{vo?.volume}</td>
                      <td 
                        className="px-4 py-2"
                        onClick={(e) => e.stopPropagation()} // Prevent row selection when clicking audio
                      >
                        {/* Classic HTML5 audio player */}
                        <audio 
                          controls 
                          preload="metadata"
                          className="h-8"
                          style={{ maxWidth: '250px' }}
                        >
                          <source src={vo.audio_url} type="audio/mpeg" />
                          Your browser does not support the audio element.
                        </audio>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Voice Selection */}
        <div className="lg:col-span-2 space-y-4">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Voice Filters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                    Gender
                  </label>
                  <Select value={filters.gender} onValueChange={(value) => 
                    setFilters(prev => ({ ...prev, gender: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Any gender</SelectItem>
                      {getFilterOptions('gender').map(gender => (
                        <SelectItem key={gender} value={gender}>{gender}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                    Accent
                  </label>
                  <Select value={filters.accent} onValueChange={(value) => 
                    setFilters(prev => ({ ...prev, accent: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any accent" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Any accent</SelectItem>
                      {getFilterOptions('accent').map(accent => (
                        <SelectItem key={accent} value={accent}>
                          {accent.replace('_', ' ')}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                    Style
                  </label>
                  <Select value={filters.style} onValueChange={(value) => 
                    setFilters(prev => ({ ...prev, style: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any style" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Any style</SelectItem>
                      {getFilterOptions('style').map(style => (
                        <SelectItem key={style} value={style}>{style}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Voice Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredVoices.map((voice) => (
              <Card 
                key={voice.voice_id} 
                className={`cursor-pointer transition-all duration-300 hover:shadow-md ${
                  selectedVoice?.voice_id === voice.voice_id 
                    ? 'ring-2 ring-blue-500 dark:ring-blue-400 shadow-lg' 
                    : ''
                } ${
                  playingVoice === voice.voice_id 
                    ? 'ring-2 ring-green-400 dark:ring-green-500 shadow-xl transform scale-[1.02]' 
                    : ''
                }`}
                onClick={() => setSelectedVoice(voice)}
              >
                <CardContent className={`p-4 transition-all duration-300 ${
                  playingVoice === voice.voice_id 
                    ? 'bg-gradient-to-br from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20' 
                    : ''
                }`}>
                  {/* Voice Avatar/Image Area with Play Animation */}
                  <div className="relative mb-3">
                    <div className={`
                      w-20 h-20 mx-auto mb-3 rounded-full flex items-center justify-center transition-all duration-500
                      ${playingVoice === voice.voice_id 
                        ? 'bg-gradient-to-br from-blue-400 to-green-500 shadow-xl' 
                        : 'bg-gray-200 dark:bg-gray-700'
                      }
                    `}>
                      {playingVoice === voice.voice_id ? (
                        <div className="flex items-center justify-center relative">
                          {/* Pulsing outer ring */}
                          <div className="absolute w-24 h-24 rounded-full bg-blue-400 opacity-30 animate-ping"></div>
                          <div className="absolute w-20 h-20 rounded-full bg-blue-500 opacity-50 animate-pulse"></div>
                          
                          {/* Audio waveform animation */}
                          <div className="flex space-x-1 z-10">
                            <div className="w-1 bg-white rounded-full animate-pulse" 
                                 style={{
                                   height: '8px',
                                   animationDuration: '0.8s',
                                   animationDelay: '0ms'
                                 }}></div>
                            <div className="w-1 bg-white rounded-full animate-pulse" 
                                 style={{
                                   height: '16px',
                                   animationDuration: '0.9s',
                                   animationDelay: '0.1s'
                                 }}></div>
                            <div className="w-1 bg-white rounded-full animate-pulse" 
                                 style={{
                                   height: '12px',
                                   animationDuration: '0.7s',
                                   animationDelay: '0.2s'
                                 }}></div>
                            <div className="w-1 bg-white rounded-full animate-pulse" 
                                 style={{
                                   height: '20px',
                                   animationDuration: '1.1s',
                                   animationDelay: '0.3s'
                                 }}></div>
                            <div className="w-1 bg-white rounded-full animate-pulse" 
                                 style={{
                                   height: '8px',
                                   animationDuration: '0.8s',
                                   animationDelay: '0.4s'
                                 }}></div>
                            <div className="w-1 bg-white rounded-full animate-pulse" 
                                 style={{
                                   height: '14px',
                                   animationDuration: '1.0s',
                                   animationDelay: '0.5s'
                                 }}></div>
                            <div className="w-1 bg-white rounded-full animate-pulse" 
                                 style={{
                                   height: '10px',
                                   animationDuration: '0.9s',
                                   animationDelay: '0.6s'
                                 }}></div>
                          </div>
                        </div>
                      ) : (
                        <Volume2 className={`h-8 w-8 ${
                          voice.gender === 'male' 
                            ? 'text-blue-600 dark:text-blue-400' 
                            : 'text-pink-600 dark:text-pink-400'
                        }`} />
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                      {voice.name}
                    </h3>
                    {selectedVoice?.voice_id === voice.voice_id && (
                      <CheckCircle className="h-5 w-5 text-blue-500 dark:text-blue-400" />
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {voice.description}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex gap-2">
                      <Badge variant="outline" className="text-xs">
                        {voice.gender}
                      </Badge>
                      <Badge variant="secondary" className="text-xs">
                        {voice.style}
                      </Badge>
                    </div>
                    
                    {voice.sample_url ? (
                      <Button
                        variant={playingVoice === voice.voice_id ? "default" : "outline"}
                        size="sm"
                        className={`transition-all duration-300 ${
                          playingVoice === voice.voice_id 
                            ? 'bg-blue-500 hover:bg-blue-600 text-white shadow-lg animate-pulse' 
                            : ''
                        }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (playingVoice === voice.voice_id) {
                            stopAudio();
                          } else {
                            playVoiceSample(voice);
                          }
                        }}
                        disabled={!voice.sample_url}
                      >
                        {playingVoice === voice.voice_id ? (
                          <Pause className="h-4 w-4" />
                        ) : (
                          <Play className="h-4 w-4" />
                        )}
                        <span className="ml-1 text-xs">
                          {playingVoice === voice.voice_id ? 'Playing...' : 'Preview'}
                        </span>
                      </Button>
                    ) : (
                      <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                        <AlertCircle className="h-4 w-4 mr-1" />
                        No sample
                      </div>
                    )}
                  </div>
                  
                  {audioError && playingVoice === voice.voice_id && (
                    <div className="mt-2 text-xs text-red-600 dark:text-red-400">
                      Playback error - file may be missing
                    </div>
                  )}
                  
                  {playingVoice === voice.voice_id && !audioError && (
                    <div className="mt-2 text-xs text-green-600 dark:text-green-400 font-medium animate-pulse">
                      🎵 Playing audio sample...
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Audio Settings and Generation */}
        <div className="space-y-4">
          {/* Audio Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Volume2 className="h-5 w-5" />
                Audio Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                  Speed: {audioSettings.speed[0].toFixed(1)}x
                </label>
                <Slider
                  value={audioSettings.speed}
                  onValueChange={(value) => setAudioSettings(prev => ({ ...prev, speed: value }))}
                  min={0.5}
                  max={2.0}
                  step={0.1}
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                  Pitch: {audioSettings.pitch[0].toFixed(1)}x
                </label>
                <Slider
                  value={audioSettings.pitch}
                  onValueChange={(value) => setAudioSettings(prev => ({ ...prev, pitch: value }))}
                  min={0.5}
                  max={2.0}
                  step={0.1}
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                  Volume: {Math.round(audioSettings.volume[0] * 100)}%
                </label>
                <Slider
                  value={audioSettings.volume}
                  onValueChange={(value) => setAudioSettings(prev => ({ ...prev, volume: value }))}
                  min={0}
                  max={1}
                  step={0.1}
                />
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="background-music"
                  checked={audioSettings.background_music}
                  onChange={(e) => setAudioSettings(prev => ({ 
                    ...prev, 
                    background_music: e.target.checked 
                  }))}
                  className="w-4 h-4 text-blue-600 dark:text-blue-500"
                />
                <label htmlFor="background-music" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Add Background Music
                </label>
              </div>

              {audioSettings.background_music && (
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                    Music Volume: {Math.round(audioSettings.background_music_volume[0] * 100)}%
                  </label>
                  <Slider
                    value={audioSettings.background_music_volume}
                    onValueChange={(value) => setAudioSettings(prev => ({ 
                      ...prev, 
                      background_music_volume: value 
                    }))}
                    min={0}
                    max={0.5}
                    step={0.05}
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Generation - Enhanced Visibility */}
          <Card className="border-2 border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
              <CardTitle className="text-xl font-bold flex items-center gap-2">
                🎵 Generate Voiceover
                {selectedVoice && (
                  <Badge variant="secondary" className="bg-white/20 text-white">
                    {selectedVoice.name}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 p-6">
              {!generatedAudio ? (
                <div className="space-y-3">
                  <div className="text-center p-4 bg-blue-100 dark:bg-blue-900/30 rounded-lg border border-blue-300 dark:border-blue-600">
                    <p className="text-blue-800 dark:text-blue-200 font-medium mb-2">
                      🚀 Ready to generate your voiceover!
                    </p>
                    <p className="text-sm text-blue-600 dark:text-blue-300">
                      {selectedVoice ? `Using ${selectedVoice.name} voice` : 'Please select a voice first'}
                    </p>
                  </div>
                  <Button
                    onClick={generateVoiceover}
                    disabled={!selectedVoice || isGenerating}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-4 text-lg"
                    size="lg"
                  >
                    {isGenerating ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        Generating Voiceover...
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        🎵 Generate Voiceover
                      </div>
                    )}
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <Button
                    onClick={playGeneratedAudio}
                    variant="outline"
                    className="w-full"
                  >
                    {isPlaying ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                    {isPlaying ? 'Pause' : 'Play'} Generated Audio
                  </Button>
                  
                  <Button
                    onClick={resetGeneration}
                    variant="ghost"
                    size="sm"
                    className="w-full"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Generate New
                  </Button>
                </div>
              )}

              {isGenerating && generationProgress > 0 && (
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${generationProgress}%` }}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-6">
        <Button variant="outline" onClick={onBack}>
          Back to Script
        </Button>
        <Button 
          onClick={() => {
            if (generatedAudio) {
              console.log('🚀 Generate Social Media button clicked');
              console.log('📦 Generated audio data:', generatedAudio);
              console.log('📋 Script data:', scriptData);
              
              // Prepare complete voiceover data for parent component
              const voiceoverCompleteData = {
                // Generated audio data
                generated_audio: {
                  audio_url: generatedAudio.audio_url,
                  generation_time: generatedAudio.generation_time,
                  duration: generatedAudio.duration,
                  file_size: generatedAudio.file_size
                },
                // Voice information
                voice: {
                  voice_id: selectedVoice.voice_id,
                  name: selectedVoice.name,
                  gender: selectedVoice.gender,
                  accent: selectedVoice.accent,
                  style: selectedVoice.style
                },
                // Audio settings used
                audio_settings: {
                  speed: Array.isArray(audioSettings.speed) ? audioSettings.speed[0] : audioSettings.speed,
                  pitch: Array.isArray(audioSettings.pitch) ? audioSettings.pitch[0] : audioSettings.pitch,
                  volume: Array.isArray(audioSettings.volume) ? audioSettings.volume[0] : audioSettings.volume,
                  background_music: audioSettings.background_music,
                  background_music_volume: Array.isArray(audioSettings.background_music_volume) 
                    ? audioSettings.background_music_volume[0] 
                    : audioSettings.background_music_volume
                },
                // Script data for context
                script_data: {
                  ...scriptData,
                  voiceover_script: getScriptContent(),
                  title: scriptData?.title || 'Generated Script',
                  description: scriptData?.description || '',
                  tags: scriptData?.tags || [],
                  duration_estimate: scriptData?.duration_estimate || 'Unknown',
                  word_count: scriptData?.word_count || getScriptContent().split(' ').length,
                  script_type: scriptData?.script_type || 'unknown',
                  category: scriptData?.category || 'General',
                  language: scriptData?.language || 'English',
                  id: scriptData?.id || `script_${Date.now()}`
                },
                // Metadata
                user_id: userId,
                created_at: new Date().toISOString(),
                success: true
              };
              
              console.log('✅ Calling onNext with complete voiceover data');
              
              // Call onNext callback to pass data to parent (page.js)
              onNext(voiceoverCompleteData);
              
              toast({
                title: "Success! 🎉",
                description: "Proceeding to social media generation...",
              });
            } else {
              toast({
                title: "No Audio Generated",
                description: "Please generate a voiceover first",
                variant: "destructive"
              });
            }
          }} 
          disabled={!generatedAudio}
          className="bg-gradient-to-r from-pink-500 to-red-600 hover:from-pink-600 hover:to-red-700"
        >
          📱 Generate Social Media
        </Button>
      </div>

      {/* Hidden audio element for generated audio playback */}
      <audio
        ref={audioRef}
        onEnded={() => setIsPlaying(false)}
        onError={(e) => {
          console.error('Generated audio error:', e);
          setIsPlaying(false);
          toast({
            title: "Playback Error",
            description: "Failed to play generated audio",
            variant: "destructive"
          });
        }}
      />
    </div>
  );
};

export default VoiceSelectionStep;
