'use client';

import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { useVideoBuilderStore } from '@/stores/useVideoBuilderStore';

const VideoEffectsEditor = ({ 
  onNext, 
  onBack, 
  selectedMedia,
  scriptData 
}) => {
  const store = useVideoBuilderStore();
  
  // Get full media data from sessionStorage if available
  const [fullMediaData, setFullMediaData] = useState([]);
  
  React.useEffect(() => {
    try {
      const sessionMedia = sessionStorage.getItem('selectedMediaFull');
      if (sessionMedia) {
        const parsedMedia = JSON.parse(sessionMedia);
        setFullMediaData(parsedMedia);
      } else {
        // Fallback to passed selectedMedia or store data
        setFullMediaData(selectedMedia || store.selectedMedia || []);
      }
    } catch (error) {
      console.warn('Failed to retrieve media from sessionStorage:', error);
      setFullMediaData(selectedMedia || store.selectedMedia || []);
    }
  }, [selectedMedia, store.selectedMedia]);
  
  // Video Configuration State
  const [videoConfig, setVideoConfig] = useState({
    aspectRatio: 'youtube_short',
    imageDuration: 5,
    transitionDuration: 1,
    totalDuration: 0
  });

  // Visual Effects State
  const [visualEffects, setVisualEffects] = useState({
    kenBurns: {
      enabled: true,
      zoomRatio: 0.8,
      direction: 'zoom_in'
    },
    transitions: {
      type: 'crossfade',
      duration: 1.0,
      intensity: 0.5
    },
    colorGrading: {
      enabled: false,
      brightness: 0,
      contrast: 0,
      saturation: 0,
      warmth: 0
    },
    overlays: {
      faceOverlay: true,
      particles: false,
      vignette: false
    }
  });

  // Text Styling State
  const [textStyles, setTextStyles] = useState({
    enabled: true,
    position: 'top',
    fontSize: 100,
    fontFamily: 'Arial',
    baseColor: '#ffffff',
    highlightColor: '#ffe066',
    highlightTextColor: '#000000',
    borderColor: '#ffae00',
    borderWidth: 4,
    padding: 16,
    animation: 'word_highlight',
    maxWordsPerLine: 5
  });

  // Audio Settings State
  const [audioSettings, setAudioSettings] = useState({
    backgroundMusic: false,
    musicVolume: 0.3,
    voiceVolume: 1.0,
    audioEffects: 'none',
    synchronization: 'word_level'
  });

  const aspectRatios = {
    'youtube_short': { label: 'YouTube Shorts', size: '9:16', resolution: '1080×1920' },
    'youtube_standard': { label: 'YouTube Standard', size: '16:9', resolution: '1920×1080' },
    'instagram_story': { label: 'Instagram Story', size: '9:16', resolution: '1080×1920' },
    'instagram_feed': { label: 'Instagram Feed', size: '1:1', resolution: '1080×1080' },
    'facebook_story': { label: 'Facebook Story', size: '9:16', resolution: '1080×1920' },
    'facebook': { label: 'Facebook Video', size: '16:9', resolution: '1200×630' },
    'tiktok': { label: 'TikTok', size: '9:16', resolution: '1080×1920' },
    'linkedin': { label: 'LinkedIn', size: '16:9', resolution: '1920×1080' },
    'snapshot': { label: 'Snapchat', size: '9:16', resolution: '1080×1920' }
  };

  const transitionTypes = {
    'crossfade': { label: 'Cross Fade', icon: '🌟', description: 'Smooth blending transition' },
    'slide': { label: 'Slide', icon: '📱', description: 'Slide left/right transition' },
    'zoom': { label: 'Zoom', icon: '🔍', description: 'Zoom in/out transition' },
    'wipe': { label: 'Wipe', icon: '🧹', description: 'Directional wipe effect' },
    'dissolve': { label: 'Dissolve', icon: '💫', description: 'Particle dissolve effect' }
  };

  const colorFilters = {
    'none': { label: 'None', preview: 'bg-gray-200' },
    'vintage': { label: 'Vintage', preview: 'bg-yellow-200' },
    'dramatic': { label: 'Dramatic', preview: 'bg-red-200' },
    'cool': { label: 'Cool Blue', preview: 'bg-blue-200' },
    'warm': { label: 'Warm Sunset', preview: 'bg-orange-200' },
    'monochrome': { label: 'Monochrome', preview: 'bg-gray-400' }
  };

  // Calculate estimated video duration
  React.useEffect(() => {
    const imageCount = fullMediaData?.length || 0;
    const imageDuration = videoConfig.imageDuration;
    const transitionOverlap = videoConfig.transitionDuration;
    
    const totalDuration = imageCount > 0 
      ? (imageCount * imageDuration) - ((imageCount - 1) * transitionOverlap)
      : 0;
    
    setVideoConfig(prev => ({ ...prev, totalDuration }));
  }, [fullMediaData, videoConfig.imageDuration, videoConfig.transitionDuration]);

  // Handle configuration updates
  const updateVideoConfig = (field, value) => {
    setVideoConfig(prev => ({ ...prev, [field]: value }));
  };

  const updateVisualEffects = (category, field, value) => {
    setVisualEffects(prev => ({
      ...prev,
      [category]: { ...prev[category], [field]: value }
    }));
  };

  const updateTextStyles = (field, value) => {
    setTextStyles(prev => ({ ...prev, [field]: value }));
  };

  const updateAudioSettings = (field, value) => {
    setAudioSettings(prev => ({ ...prev, [field]: value }));
  };

  // Preview effects
  const previewEffects = () => {
    toast('🎬 Effect preview coming soon!', {
      icon: 'ℹ️'
    });
  };

  // Reset to defaults
  const resetToDefaults = () => {
    setVideoConfig({
      aspectRatio: 'youtube_short',
      imageDuration: 5,
      transitionDuration: 1,
      totalDuration: 0
    });
    
    setVisualEffects({
      kenBurns: { enabled: true, zoomRatio: 0.8, direction: 'zoom_in' },
      transitions: { type: 'crossfade', duration: 1.0, intensity: 0.5 },
      colorGrading: { enabled: false, brightness: 0, contrast: 0, saturation: 0, warmth: 0 },
      overlays: { faceOverlay: true, particles: false, vignette: false }
    });
    
    toast.success('Reset to default settings');
  };

  // Handle next step
  const handleNext = () => {
    // Prepare complete effects configuration
    const effectsConfig = {
      videoConfig,
      visualEffects,
      textStyles,
      audioSettings,
      selectedMedia: fullMediaData || []
    };
    
    // Save all settings to store
    store.setVideoEffectsConfig(effectsConfig);
    
    // Log for debugging
    console.log('🎨 Video Effects Config being sent:', effectsConfig);
    
    toast.success('Video effects configured successfully!');
    
    // Pass configuration to parent component
    onNext(effectsConfig);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          🎨 Video Effects & Styling
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-2">
          Customize visual effects, transitions, and styling for your video
        </p>
        <div className="flex items-center justify-center gap-4 text-sm text-gray-500 dark:text-gray-400">
          <span>Media Items: <strong className="text-purple-600">{fullMediaData?.length || 0}</strong></span>
          <span>•</span>
          <span>Est. Duration: <strong className="text-green-600">{Math.round(videoConfig.totalDuration)}s</strong></span>
          <span>•</span>
          <span>Resolution: <strong>{aspectRatios[videoConfig.aspectRatio]?.resolution}</strong></span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Video Configuration */}
        <div className="space-y-6">
          
          {/* Video Format Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-600">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
              📐 Video Format
            </h3>
            
            <div className="space-y-4">
              {/* Aspect Ratio Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Platform & Aspect Ratio
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(aspectRatios).map(([key, ratio]) => (
                    <button
                      key={key}
                      onClick={() => updateVideoConfig('aspectRatio', key)}
                      className={`p-3 rounded-lg border text-left transition-all ${
                        videoConfig.aspectRatio === key
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
                          : 'border-gray-200 dark:border-gray-600 hover:border-purple-300'
                      }`}
                    >
                      <div className="font-medium text-sm">{ratio.label}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{ratio.size} • {ratio.resolution}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Duration Settings */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Image Duration (seconds)
                  </label>
                  <input
                    type="range"
                    min="2"
                    max="10"
                    step="0.5"
                    value={videoConfig.imageDuration}
                    onChange={(e) => updateVideoConfig('imageDuration', parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <div className="text-center text-sm text-gray-500 mt-1">{videoConfig.imageDuration}s</div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Transition Duration
                  </label>
                  <input
                    type="range"
                    min="0.2"
                    max="2"
                    step="0.1"
                    value={videoConfig.transitionDuration}
                    onChange={(e) => updateVideoConfig('transitionDuration', parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <div className="text-center text-sm text-gray-500 mt-1">{videoConfig.transitionDuration}s</div>
                </div>
              </div>
            </div>
          </div>

          {/* Visual Effects */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-600">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
              ✨ Visual Effects
            </h3>

            <div className="space-y-4">
              {/* Ken Burns Effect */}
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={visualEffects.kenBurns.enabled}
                      onChange={(e) => updateVisualEffects('kenBurns', 'enabled', e.target.checked)}
                      className="rounded"
                    />
                    <span className="font-medium">🔍 Ken Burns Effect</span>
                  </label>
                </div>
                
                {visualEffects.kenBurns.enabled && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">Zoom Intensity</label>
                      <input
                        type="range"
                        min="0.1"
                        max="1.5"
                        step="0.1"
                        value={visualEffects.kenBurns.zoomRatio}
                        onChange={(e) => updateVisualEffects('kenBurns', 'zoomRatio', parseFloat(e.target.value))}
                        className="w-full"
                      />
                      <div className="text-xs text-center text-gray-500 mt-1">{Math.round(visualEffects.kenBurns.zoomRatio * 100)}%</div>
                    </div>
                    
                    <div>
                      <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">Direction</label>
                      <select
                        value={visualEffects.kenBurns.direction}
                        onChange={(e) => updateVisualEffects('kenBurns', 'direction', e.target.value)}
                        className="w-full px-3 py-1 rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-600"
                      >
                        <option value="zoom_in">Zoom In</option>
                        <option value="zoom_out">Zoom Out</option>
                        <option value="pan_left">Pan Left</option>
                        <option value="pan_right">Pan Right</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>

              {/* Transitions */}
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <label className="block font-medium mb-3">🎬 Transitions</label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(transitionTypes).map(([key, transition]) => (
                    <button
                      key={key}
                      onClick={() => updateVisualEffects('transitions', 'type', key)}
                      className={`p-2 rounded border text-left transition-all ${
                        visualEffects.transitions.type === key
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-blue-300'
                      }`}
                    >
                      <div className="text-sm font-medium">{transition.icon} {transition.label}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{transition.description}</div>
                    </button>
                  ))}
                </div>
                {/* Slide direction selector, only show if slide is selected */}
                {visualEffects.transitions.type === 'slide' && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Slide Direction</label>
                    <select
                      value={visualEffects.transitions.slideDirection || 'left'}
                      onChange={e => updateVisualEffects('transitions', 'slideDirection', e.target.value)}
                      className="w-full px-3 py-2 rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-600"
                    >
                      <option value="left">Left</option>
                      <option value="right">Right</option>
                      <option value="up">Up</option>
                      <option value="down">Down</option>
                    </select>
                  </div>
                )}
              </div>

              {/* Overlays */}
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <label className="block font-medium mb-3">🎭 Overlays & Effects</label>
                <div className="space-y-2">
                  {[
                    { key: 'faceOverlay', label: '👤 Animated Character', description: 'Add character overlay' },
                    { key: 'particles', label: '✨ Particle Effects', description: 'Floating particles' },
                    { key: 'vignette', label: '🌑 Vignette Effect', description: 'Darkened edges' }
                  ].map((overlay) => (
                    <label key={overlay.key} className="flex items-center justify-between">
                      <div>
                        <span className="font-medium text-sm">{overlay.label}</span>
                        <div className="text-xs text-gray-500 dark:text-gray-400">{overlay.description}</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={visualEffects.overlays[overlay.key]}
                        onChange={(e) => updateVisualEffects('overlays', overlay.key, e.target.checked)}
                        className="rounded"
                      />
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Text & Audio */}
        <div className="space-y-6">
          
          {/* Text Styling */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                📝 Text Styling
              </h3>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={textStyles.enabled}
                  onChange={(e) => updateTextStyles('enabled', e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm">Enable Text</span>
              </label>
            </div>

            {textStyles.enabled && (
              <div className="space-y-4">
                {/* Font Settings */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Font Size</label>
                    <input
                      type="range"
                      min="50"
                      max="200"
                      step="10"
                      value={textStyles.fontSize}
                      onChange={(e) => updateTextStyles('fontSize', parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="text-center text-sm text-gray-500 mt-1">{textStyles.fontSize}px</div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Position</label>
                    <select
                      value={textStyles.position}
                      onChange={(e) => updateTextStyles('position', e.target.value)}
                      className="w-full px-3 py-2 rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-600"
                    >
                      <option value="top">Top</option>
                      <option value="center">Center</option>
                      <option value="bottom">Bottom</option>
                    </select>
                  </div>
                </div>

                {/* Color Settings */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Text Color</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="color"
                        value={textStyles.baseColor}
                        onChange={(e) => updateTextStyles('baseColor', e.target.value)}
                        className="w-8 h-8 rounded"
                      />
                      <input
                        type="text"
                        value={textStyles.baseColor}
                        onChange={(e) => updateTextStyles('baseColor', e.target.value)}
                        className="flex-1 px-2 py-1 text-sm rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-600"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Highlight Color</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="color"
                        value={textStyles.highlightColor}
                        onChange={(e) => updateTextStyles('highlightColor', e.target.value)}
                        className="w-8 h-8 rounded"
                      />
                      <input
                        type="text"
                        value={textStyles.highlightColor}
                        onChange={(e) => updateTextStyles('highlightColor', e.target.value)}
                        className="flex-1 px-2 py-1 text-sm rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-600"
                      />
                    </div>
                  </div>
                </div>

                {/* Animation Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Animation Style</label>
                  <select
                    value={textStyles.animation}
                    onChange={(e) => updateTextStyles('animation', e.target.value)}
                    className="w-full px-3 py-2 rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-600"
                  >
                    <option value="word_highlight">Word Highlight</option>
                    <option value="fade_in">Fade In</option>
                    <option value="slide_in">Slide In</option>
                    <option value="typewriter">Typewriter</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Color Grading */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                🎨 Color Grading
              </h3>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={visualEffects.colorGrading.enabled}
                  onChange={(e) => updateVisualEffects('colorGrading', 'enabled', e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm">Enable</span>
              </label>
            </div>

            {visualEffects.colorGrading.enabled && (
              <div className="space-y-4">
                {/* Filter Presets */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Presets</label>
                  <div className="grid grid-cols-3 gap-2">
                    {Object.entries(colorFilters).map(([key, filter]) => (
                      <button
                        key={key}
                        className={`p-2 rounded text-xs text-center border ${filter.preview} hover:scale-105 transition-transform`}
                      >
                        {filter.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Manual Controls */}
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { key: 'brightness', label: 'Brightness', min: -50, max: 50 },
                    { key: 'contrast', label: 'Contrast', min: -50, max: 50 },
                    { key: 'saturation', label: 'Saturation', min: -50, max: 50 },
                    { key: 'warmth', label: 'Warmth', min: -50, max: 50 }
                  ].map((control) => (
                    <div key={control.key}>
                      <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">{control.label}</label>
                      <input
                        type="range"
                        min={control.min}
                        max={control.max}
                        value={visualEffects.colorGrading[control.key]}
                        onChange={(e) => updateVisualEffects('colorGrading', control.key, parseInt(e.target.value))}
                        className="w-full"
                      />
                      <div className="text-xs text-center text-gray-500 mt-1">{visualEffects.colorGrading[control.key]}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Audio Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-600">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
              🎵 Audio Settings
            </h3>

            <div className="space-y-4">
              {/* Background Music */}
              <label className="flex items-center justify-between">
                <div>
                  <span className="font-medium">🎶 Background Music</span>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Add instrumental background</div>
                </div>
                <input
                  type="checkbox"
                  checked={audioSettings.backgroundMusic}
                  onChange={(e) => updateAudioSettings('backgroundMusic', e.target.checked)}
                  className="rounded"
                />
              </label>

              {/* Volume Controls */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Voice Volume</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={audioSettings.voiceVolume}
                    onChange={(e) => updateAudioSettings('voiceVolume', parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <div className="text-center text-sm text-gray-500 mt-1">{Math.round(audioSettings.voiceVolume * 100)}%</div>
                </div>
                
                {audioSettings.backgroundMusic && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Music Volume</label>
                    <input
                      type="range"
                      min="0"
                      max="0.5"
                      step="0.05"
                      value={audioSettings.musicVolume}
                      onChange={(e) => updateAudioSettings('musicVolume', parseFloat(e.target.value))}
                      className="w-full"
                    />
                    <div className="text-center text-sm text-gray-500 mt-1">{Math.round(audioSettings.musicVolume * 100)}%</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Preview & Actions */}
      <div className="mt-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={previewEffects}
            className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 transition-all"
          >
            👁️ Preview Effects
          </button>
          <button
            onClick={resetToDefaults}
            className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-all"
          >
            🔄 Reset Defaults
          </button>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-all"
          >
            ← Back to Media
          </button>
          <button
            onClick={handleNext}
            className="bg-gradient-to-r from-green-500 to-blue-600 text-white px-6 py-2 rounded-lg hover:from-green-600 hover:to-blue-700 transition-all"
          >
            Continue to Generation →
          </button>
        </div>
      </div>
    </div>
  );
};

export default VideoEffectsEditor;