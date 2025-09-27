'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ProcessingModal from '@/components/ProcessingModal';
import { useGlobalProcessing } from '@/hooks/useGlobalProcessing';

// Create a reusable form field component
const FormField = ({ label, id, type = "text", value, onChange, options = [], placeholder = "", description = "", min, max, step, className = "", required = false }) => {
  if (type === "select") {
    return (
      <div className={`mb-4 ${className}`}>
        <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <select
          id={id}
          name={id}
          value={value}
          onChange={onChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          required={required}
        >
          {options.map(option => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
        {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
      </div>
    );
  }
  
  if (type === "textarea") {
    return (
      <div className={`mb-4 ${className}`}>
        <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <textarea
          id={id}
          name={id}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          rows={4}
          required={required}
        ></textarea>
        {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
      </div>
    );
  }
  
  if (type === "checkbox") {
    return (
      <div className={`flex items-start mb-4 ${className}`}>
        <div className="flex items-center h-5">
          <input
            id={id}
            name={id}
            type="checkbox"
            checked={value}
            onChange={onChange}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
        </div>
        <div className="ml-3 text-sm">
          <label htmlFor={id} className="font-medium text-gray-700">{label}</label>
          {description && <p className="text-gray-500">{description}</p>}
        </div>
      </div>
    );
  }
  
  if (type === "radio-group") {
    return (
      <div className={`mb-4 ${className}`}>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <div className="flex flex-wrap gap-4">
          {options.map(option => (
            <div key={option.value} className="flex items-center">
              <input
                id={`${id}-${option.value}`}
                name={id}
                type="radio"
                value={option.value}
                checked={value === option.value}
                onChange={onChange}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
              />
              <label htmlFor={`${id}-${option.value}`} className="ml-2 text-sm text-gray-700">
                {option.label}
              </label>
            </div>
          ))}
        </div>
        {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
      </div>
    );
  }
  
  if (type === "checkbox-group") {
    return (
      <div className={`mb-4 ${className}`}>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {options.map(option => (
            <div key={option.value} className="flex items-center">
              <input
                id={`${id}-${option.value}`}
                name={`${id}-${option.value}`}
                type="checkbox"
                checked={value.includes(option.value)}
                onChange={() => {
                  const currentValues = [...value];
                  if (currentValues.includes(option.value)) {
                    onChange(currentValues.filter(v => v !== option.value));
                  } else {
                    onChange([...currentValues, option.value]);
                  }
                }}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor={`${id}-${option.value}`} className="ml-2 text-sm text-gray-700">
                {option.label}
              </label>
            </div>
          ))}
        </div>
        {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
      </div>
    );
  }
  
  if (type === "range") {
    return (
      <div className={`mb-4 ${className}`}>
        <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>} 
          <span className="ml-2 text-indigo-600 font-medium">{value}</span>
        </label>
        <input
          id={id}
          name={id}
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={onChange}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          required={required}
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{min}</span>
          <span>{max}</span>
        </div>
        {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
      </div>
    );
  }
  
  // Default is text input
  return (
    <div className={`mb-4 ${className}`}>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        id={id}
        name={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        min={min}
        max={max}
        step={step}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        required={required}
      />
      {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
    </div>
  );
};

export default function CreateVideo() {
  const router = useRouter();
  const { startProcessing } = useGlobalProcessing();
  
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');
  
  // Progress modal state
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [currentVideoId, setCurrentVideoId] = useState(null);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  
  // Check if user is authenticated
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/auth/me', {
          credentials: 'include' // Include cookies for authentication
        });
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // Redirect to login if not authenticated
          router.push('/login');
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        router.push('/login');
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, [router]);
  
  const [formData, setFormData] = useState({
    // Basic settings
    // These can be auto-generated from the prompt if not provided
    title: '',
    description: '',
    prompt: '',
    
    // Video preferences
    resolution: '1080p',
    duration: 30,
    style: 'cinematic',
    aspectRatio: '16:9',
    
    // Advanced settings
    fps: 24,
    quality: 'high',
    useAI: true,
    includeAudio: true,
    musicType: 'ambient',
    customAudio: '',
    
    // Visual effects
    colorGrading: 'natural',
    visualEffects: [],
    transitionEffects: 'smooth',
    
    // Generation options
    generateType: 'full',
    model: 'standard',
    priority: 'normal',
    saveAsDraft: false
  });
  
  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.href = '/login';
    } catch (err) {
      alert('Logout failed');
    }
  };
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  // Handle multi-select checkboxes
  const handleMultiSelectChange = (name, values) => {
    setFormData(prev => ({
      ...prev,
      [name]: values
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Prepare data for FastAPI backend
      const videoData = {
        // Convert frontend field names to backend field names (snake_case)
        title: formData.title || (formData.prompt ? formData.prompt.substring(0, 30) + (formData.prompt.length > 30 ? '...' : '') : 'Untitled Video'),
        description: formData.description || formData.prompt || '',
        prompt: formData.prompt || '',
        duration: parseInt(formData.duration) || 30,
        resolution: formData.resolution || '720p',
        format: formData.format || 'mp4',
        content_type: formData.contentType || 'general',
        style: formData.style || 'cinematic',
        audio_type: formData.audioType || 'voiceover',
        aspect_ratio: formData.aspectRatio || '16:9',
        fps: parseInt(formData.fps) || 24,
        quality: formData.quality || 'high',
        use_ai: formData.useAi !== undefined ? formData.useAi : true,
        include_audio: formData.includeAudio !== undefined ? formData.includeAudio : true,
        music_type: formData.musicType || 'ambient',
        custom_audio: formData.customAudio || null,
        color_grading: formData.colorGrading || 'natural',
        visual_effects: Array.isArray(formData.visualEffects) ? formData.visualEffects : [],
        transition_effects: formData.transitionEffects || 'smooth',
        target_audience: formData.targetAudience || '',
        script: formData.script || '',
        media_urls: Array.isArray(formData.mediaUrls) ? formData.mediaUrls : [],
        background_music: formData.backgroundMusic || '',
        text_overlay_style: formData.textOverlayStyle || 'minimal',
        transitions: formData.transitions || 'fade',
        generate_type: formData.generateType || 'full',
        model: formData.model || 'standard',
        priority: formData.priority || 'normal',
        thumbnail: formData.thumbnail || '',
        user_id: user?.id || 'anonymous_user', // Use authenticated user ID
      };
      
      // Send data to FastAPI backend
      const response = await fetch('http://localhost:8000/api/videos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(videoData),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage;
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || 'Failed to create video';
        } catch {
          errorMessage = errorText || 'Failed to create video';
        }
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      
      // Register processing job globally and show progress modal with video and task IDs
      setCurrentVideoId(result.video_id);
      setCurrentTaskId(result.task_id);
      setShowProgressModal(true);
      
      // Also register in global processing hook for header indicator
      startProcessing(result.video_id, result.task_id);
      
    } catch (error) {
      console.error('Error submitting form:', error);
      alert(`Error creating video: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle closing progress modal and redirecting to dashboard
  const handleModalClose = () => {
    setShowProgressModal(false);
    setCurrentVideoId(null);
    setCurrentTaskId(null);
    router.push('/dashboard');
  };
  
  const tabs = [
    { id: 'basic', label: 'Basic Settings' },
    { id: 'video', label: 'Video Preferences' },
    { id: 'advanced', label: 'Advanced Options' },
    { id: 'effects', label: 'Visual Effects' },
  ];

  // Show loading state or redirect if not authenticated
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }
  
  // If no user after loading (should have redirected, but just in case)
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Video</h2>
          
          {/* Tabs */}
          <div className="mb-6 border-b border-gray-200">
            <div className="flex overflow-x-auto pb-1">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 font-medium text-sm mr-4 ${
                    activeTab === tab.id
                      ? 'text-indigo-600 border-b-2 border-indigo-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
          
          <div className="bg-white shadow rounded-lg p-6">
            <form onSubmit={handleSubmit}>
              {/* Basic Settings */}
              {activeTab === 'basic' && (
                <div>
                  <FormField
                    label="Prompt"
                    id="prompt"
                    type="textarea"
                    value={formData.prompt}
                    onChange={handleChange}
                    placeholder="Describe what you want the AI to generate in detail..."
                    description="Title and description will be automatically generated from your prompt if not provided below."
                    required={true}
                  />
                  
                  <FormField
                    label="Title (Optional)"
                    id="title"
                    type="text"
                    value={formData.title}
                    onChange={handleChange}
                    placeholder="Video title (will be auto-generated from prompt if left empty)"
                  />
                  
                  <FormField
                    label="Description (Optional)"
                    id="description"
                    type="textarea"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="Video description (will be auto-generated from prompt if left empty)"
                  />
                </div>
              )}
              
              {/* Video Preferences */}
              {activeTab === 'video' && (
                <div>
                  <FormField
                    label="Resolution"
                    id="resolution"
                    type="select"
                    value={formData.resolution}
                    onChange={handleChange}
                    options={[
                      { value: '720p', label: '720p (HD)' },
                      { value: '1080p', label: '1080p (Full HD)' },
                      { value: '1440p', label: '1440p (2K)' },
                      { value: '4K', label: '4K (Ultra HD)' }
                    ]}
                    description="Higher resolutions may take longer to generate."
                  />
                  
                  <FormField
                    label="Duration (seconds)"
                    id="duration"
                    type="number"
                    value={formData.duration}
                    onChange={handleChange}
                    min="5"
                    max="120"
                    description="Videos can be between 5-120 seconds."
                  />
                  
                  <FormField
                    label="Style"
                    id="style"
                    type="select"
                    value={formData.style}
                    onChange={handleChange}
                    options={[
                      { value: 'cinematic', label: 'Cinematic' },
                      { value: 'documentary', label: 'Documentary' },
                      { value: 'animation', label: 'Animation' },
                      { value: 'vintage', label: 'Vintage' },
                      { value: 'futuristic', label: 'Futuristic' },
                      { value: 'vlog', label: 'Vlog/Personal' },
                      { value: 'corporate', label: 'Corporate/Professional' }
                    ]}
                    description="Visual style affects the overall look and feel of your video."
                  />
                  
                  <FormField
                    label="Aspect Ratio"
                    id="aspectRatio"
                    type="select"
                    value={formData.aspectRatio}
                    onChange={handleChange}
                    options={[
                      { value: '16:9', label: '16:9 (Landscape - YouTube, TV)' },
                      { value: '9:16', label: '9:16 (Portrait - Instagram, TikTok)' },
                      { value: '1:1', label: '1:1 (Square - Instagram)' },
                      { value: '4:3', label: '4:3 (Traditional)' },
                      { value: '21:9', label: '21:9 (Ultrawide - Cinematic)' }
                    ]}
                  />
                </div>
              )}
              
              {/* Advanced Settings */}
              {activeTab === 'advanced' && (
                <div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      label="Frames Per Second (FPS)"
                      id="fps"
                      type="select"
                      value={formData.fps}
                      onChange={handleChange}
                      options={[
                        { value: '24', label: '24 FPS (Cinematic)' },
                        { value: '30', label: '30 FPS (Standard)' },
                        { value: '60', label: '60 FPS (Smooth)' }
                      ]}
                      className="col-span-1"
                    />
                    
                    <FormField
                      label="Quality"
                      id="quality"
                      type="select"
                      value={formData.quality}
                      onChange={handleChange}
                      options={[
                        { value: 'draft', label: 'Draft (Fast)' },
                        { value: 'standard', label: 'Standard' },
                        { value: 'high', label: 'High' },
                        { value: 'ultra', label: 'Ultra (Slow)' }
                      ]}
                      description="Higher quality takes longer to generate."
                      className="col-span-1"
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      label="Include Audio"
                      id="includeAudio"
                      type="checkbox"
                      value={formData.includeAudio}
                      onChange={handleChange}
                      description="Generate or add audio to your video."
                      className="col-span-1"
                    />
                    
                    <FormField
                      label="Use AI Enhancement"
                      id="useAI"
                      type="checkbox"
                      value={formData.useAI}
                      onChange={handleChange}
                      description="Improve quality with AI post-processing."
                      className="col-span-1"
                    />
                  </div>
                  
                  {formData.includeAudio && (
                    <>
                      <FormField
                        label="Music Type"
                        id="musicType"
                        type="select"
                        value={formData.musicType}
                        onChange={handleChange}
                        options={[
                          { value: 'none', label: 'No Music' },
                          { value: 'ambient', label: 'Ambient/Background' },
                          { value: 'upbeat', label: 'Upbeat/Energetic' },
                          { value: 'emotional', label: 'Emotional/Dramatic' },
                          { value: 'cinematic', label: 'Cinematic Score' },
                          { value: 'electronic', label: 'Electronic' },
                          { value: 'acoustic', label: 'Acoustic' },
                          { value: 'custom', label: 'Custom Audio Upload' }
                        ]}
                      />
                      
                      {formData.musicType === 'custom' && (
                        <FormField
                          label="Custom Audio URL"
                          id="customAudio"
                          type="text"
                          value={formData.customAudio}
                          onChange={handleChange}
                          placeholder="Link to your audio file"
                        />
                      )}
                    </>
                  )}
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <FormField
                      label="Generation Model"
                      id="model"
                      type="select"
                      value={formData.model}
                      onChange={handleChange}
                      options={[
                        { value: 'standard', label: 'Standard' },
                        { value: 'creative', label: 'Creative' },
                        { value: 'realistic', label: 'Ultra-Realistic' },
                        { value: 'stylized', label: 'Stylized' }
                      ]}
                      className="col-span-1"
                    />
                    
                    <FormField
                      label="Generation Priority"
                      id="priority"
                      type="select"
                      value={formData.priority}
                      onChange={handleChange}
                      options={[
                        { value: 'low', label: 'Low' },
                        { value: 'normal', label: 'Normal' },
                        { value: 'high', label: 'High (Premium)' }
                      ]}
                      className="col-span-1"
                    />
                  </div>
                  
                  <FormField
                    label="Save As Draft"
                    id="saveAsDraft"
                    type="checkbox"
                    value={formData.saveAsDraft}
                    onChange={handleChange}
                    description="Save settings without generating the video yet."
                    className="mt-4"
                  />
                </div>
              )}
              
              {/* Visual Effects */}
              {activeTab === 'effects' && (
                <div>
                  <FormField
                    label="Color Grading"
                    id="colorGrading"
                    type="select"
                    value={formData.colorGrading}
                    onChange={handleChange}
                    options={[
                      { value: 'natural', label: 'Natural' },
                      { value: 'warm', label: 'Warm' },
                      { value: 'cool', label: 'Cool' },
                      { value: 'vibrant', label: 'Vibrant' },
                      { value: 'muted', label: 'Muted' },
                      { value: 'highContrast', label: 'High Contrast' },
                      { value: 'vintage', label: 'Vintage' },
                      { value: 'blackAndWhite', label: 'Black & White' }
                    ]}
                  />
                  
                  <FormField
                    label="Visual Effects"
                    id="visualEffects"
                    type="checkbox-group"
                    value={formData.visualEffects}
                    onChange={(values) => handleMultiSelectChange('visualEffects', values)}
                    options={[
                      { value: 'blur', label: 'Blur/Focus Effects' },
                      { value: 'particles', label: 'Particle Effects' },
                      { value: 'lightLeaks', label: 'Light Leaks' },
                      { value: 'grain', label: 'Film Grain' },
                      { value: 'glitch', label: 'Glitch' },
                      { value: 'slowMotion', label: 'Slow Motion' },
                      { value: 'timelapse', label: 'Timelapse' },
                      { value: 'zoom', label: 'Zoom Effects' },
                      { value: 'overlay', label: 'Text Overlays' }
                    ]}
                  />
                  
                  <FormField
                    label="Transitions"
                    id="transitionEffects"
                    type="select"
                    value={formData.transitionEffects}
                    onChange={handleChange}
                    options={[
                      { value: 'none', label: 'None/Cut' },
                      { value: 'smooth', label: 'Smooth Fade' },
                      { value: 'whip', label: 'Whip Pan' },
                      { value: 'dissolve', label: 'Dissolve' },
                      { value: 'zoom', label: 'Zoom Transition' },
                      { value: 'wipe', label: 'Wipe' },
                      { value: 'glitch', label: 'Glitch Transition' }
                    ]}
                  />
                </div>
              )}
              
              <div className="mt-8 flex justify-between">
                <button
                  type="button"
                  onClick={() => router.push('/dashboard')}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
                >
                  Cancel
                </button>
                
                <div className="flex space-x-3">
                  {activeTab !== 'basic' && (
                    <button
                      type="button"
                      onClick={() => {
                        const currentIndex = tabs.findIndex(tab => tab.id === activeTab);
                        setActiveTab(tabs[currentIndex - 1].id);
                      }}
                      className="px-4 py-2 text-sm font-medium text-indigo-700 bg-white border border-indigo-300 rounded-md shadow-sm hover:bg-indigo-50"
                    >
                      Previous
                    </button>
                  )}
                  
                  {activeTab !== 'effects' ? (
                    <button
                      type="button"
                      onClick={() => {
                        const currentIndex = tabs.findIndex(tab => tab.id === activeTab);
                        setActiveTab(tabs[currentIndex + 1].id);
                      }}
                      className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md shadow-sm hover:bg-indigo-700"
                    >
                      Next
                    </button>
                  ) : (
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md shadow-sm hover:bg-indigo-700 disabled:bg-indigo-400"
                    >
                      {isSubmitting ? 'Creating...' : formData.saveAsDraft ? 'Save Draft' : 'Create Video'}
                    </button>
                  )}
                </div>
              </div>
            </form>
          </div>
        </div>
      </main>
      
      {/* Processing Modal */}
      <ProcessingModal
        isVisible={showProgressModal}
        videoId={currentVideoId}
        taskId={currentTaskId}
        onClose={handleModalClose}
      />
    </div>
  );
}
