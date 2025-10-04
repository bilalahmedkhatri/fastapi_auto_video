'use client';

import React, { useState, useRef } from 'react';
import { toast } from 'react-hot-toast';
import { useVideoBuilderStore } from '@/stores/useVideoBuilderStore';
import { useMediaProcessing } from '@/hooks/useMediaProcessing';

const MediaManager = ({ 
  onNext, 
  onBack, 
  socialMediaContent,
  scriptData 
}) => {
  const store = useVideoBuilderStore();
  const [activeTab, setActiveTab] = useState('upload');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [showSequenceDialog, setShowSequenceDialog] = useState(false);
  const [selectedMediaForSequence, setSelectedMediaForSequence] = useState(null);
  const [sequenceNumber, setSequenceNumber] = useState('');
  const [searchTags, setSearchTags] = useState([]);
  const [searchKeywords, setSearchKeywords] = useState([]);
  const [customTag, setCustomTag] = useState('');
  const [customKeyword, setCustomKeyword] = useState('');
  const [isSequenceMode, setIsSequenceMode] = useState(false);
  
  // Use store state
  const uploadedFiles = store.uploadedFiles;
  const searchResults = store.searchResults;
  const selectedMedia = store.selectedMedia;
  const generatedMedia = store.generatedMedia;
  
  // Backend processing integration
  const {
    isUploading,
    isProcessing,
    processingTasks,
    processingProgress,
    uploadFiles,
    cancelTask,
    getProcessingStats
  } = useMediaProcessing();
  
  const fileInputRef = useRef(null);
  const videoInputRef = useRef(null);

  // Initialize search tags and keywords from social media content
  React.useEffect(() => {
    if (socialMediaContent && socialMediaContent.platform_descriptions) {
      const allTags = [];
      const allKeywords = [];
      
      socialMediaContent.platform_descriptions.forEach(platform => {
        if (platform.hashtags) {
          allTags.push(...platform.hashtags.map(tag => tag.replace('#', '')));
        }
        if (platform.seo_keywords) {
          allKeywords.push(...platform.seo_keywords);
        }
      });
      
      // Remove duplicates and set initial tags/keywords
      setSearchTags([...new Set(allTags)].slice(0, 10));
      setSearchKeywords([...new Set(allKeywords)].slice(0, 8));
    }
  }, [socialMediaContent]);

  // Handle file upload with backend integration
  const handleFileUpload = async (event, type) => {
    const files = Array.from(event.target.files);
    
    // Validate files before uploading
    const validFiles = [];
    for (const file of files) {
      if (type === 'image' && !file.type.startsWith('image/')) {
        toast.error(`${file.name} is not a valid image file`);
        continue;
      }
      if (type === 'video' && !file.type.startsWith('video/')) {
        toast.error(`${file.name} is not a valid video file`);
        continue;
      }
      validFiles.push(file);
    }
    
    if (validFiles.length === 0) {
      return;
    }

    try {
      // Upload files to backend with auto-processing
      await uploadFiles(validFiles, {
        userId: 'user123', // Replace with actual user ID
        autoProcess: true,
        onProgress: (status) => {
          // Update processing progress in store
          store.updateMediaProcessingProgress(status.task_id, status);
        },
        onComplete: (result, uploadResponse) => {
          // Process the results and update store
          if (result && result.results) {
            Object.entries(result.results).forEach(([mediaId, analysis]) => {
              // Find corresponding uploaded file info
              const fileInfo = uploadResponse.files.find(f => f.id === mediaId);
              
              if (fileInfo && analysis) {
                // Create enhanced media item with analysis
                const mediaItem = {
                  id: `${Date.now()}-${Math.random()}-${mediaId}`, // Unique frontend ID
                  backendId: mediaId, // Backend media ID
                  name: fileInfo.filename || analysis.file_info?.filename || 'Unknown',
                  type: analysis.file_info?.extension?.startsWith('.') ? 
                    (analysis.file_info.extension.match(/\.(jpg|jpeg|png|bmp|tiff|webp)$/i) ? 'image' : 'video') : type,
                  size: analysis.file_info?.size_bytes || fileInfo.size_bytes || 0,
                  url: null, // Will be set from file reader
                  file: null, // Original file reference
                  source: 'upload',
                  sequenceNumber: null,
                  
                  // Backend analysis results
                  analysisResult: analysis,
                  backendProcessed: !analysis.errors || analysis.errors.length === 0,
                  uploadedToBackend: true,
                  backendFileInfo: fileInfo,
                  
                  // Quality information for UI
                  qualityScore: analysis.quality_metrics?.quality_score || null,
                  recommendations: analysis.processing_recommendations || {},
                  technicalSpecs: analysis.technical_specs || {},
                  contentAnalysis: analysis.content_analysis || {},
                  
                  // Processing status
                  processingStatus: analysis.errors?.length > 0 ? 'error' : 'completed',
                  processingErrors: analysis.errors || [],
                  processingWarnings: analysis.warnings || []
                };
                
                // Read file for preview URL (fallback for display)
                const originalFile = validFiles.find(f => f.name === (fileInfo.filename || fileInfo.original_filename));
                if (originalFile) {
                  const reader = new FileReader();
                  reader.onload = (e) => {
                    mediaItem.url = e.target.result;
                    mediaItem.file = originalFile;
                    
                    // Add to store with analysis
                    store.addUploadedFileWithAnalysis(mediaItem, analysis);
                    
                    // Store analysis results separately
                    store.setMediaAnalysisResult(mediaItem.id, analysis);
                  };
                  reader.readAsDataURL(originalFile);
                } else {
                  // Add to store without preview URL
                  store.addUploadedFileWithAnalysis(mediaItem, analysis);
                  store.setMediaAnalysisResult(mediaItem.id, analysis);
                }
              }
            });
          } else {
            // Fallback: add files without analysis (processing may have failed)
            validFiles.forEach((file, index) => {
              const reader = new FileReader();
              reader.onload = (e) => {
                const mediaItem = {
                  id: Date.now() + Math.random() + index,
                  name: file.name,
                  type: type,
                  size: file.size,
                  url: e.target.result,
                  file: file,
                  source: 'upload',
                  sequenceNumber: null,
                  backendProcessed: false,
                  uploadedToBackend: true,
                  processingStatus: 'uploaded'
                };
                
                store.addUploadedFile(mediaItem);
              };
              reader.readAsDataURL(file);
            });
          }
          
          toast.success(`Successfully processed ${validFiles.length} file(s)!`);
        },
        onError: (error, uploadResponse) => {
          console.error('Upload/processing error:', error);
          
          // Still add files to UI even if processing failed
          if (uploadResponse && uploadResponse.files) {
            uploadResponse.files.forEach((fileInfo, index) => {
              const originalFile = validFiles[index];
              if (originalFile) {
                const reader = new FileReader();
                reader.onload = (e) => {
                  const mediaItem = {
                    id: Date.now() + Math.random() + index,
                    backendId: fileInfo.id,
                    name: fileInfo.filename || originalFile.name,
                    type: type,
                    size: fileInfo.size_bytes || originalFile.size,
                    url: e.target.result,
                    file: originalFile,
                    source: 'upload',
                    sequenceNumber: null,
                    backendProcessed: false,
                    uploadedToBackend: true,
                    processingStatus: 'error',
                    processingErrors: [error.message]
                  };
                  
                  store.addUploadedFile(mediaItem);
                };
                reader.readAsDataURL(originalFile);
              }
            });
          } else {
            // Complete fallback - add files as before
            validFiles.forEach((file, index) => {
              const reader = new FileReader();
              reader.onload = (e) => {
                const mediaItem = {
                  id: Date.now() + Math.random() + index,
                  name: file.name,
                  type: type,
                  size: file.size,
                  url: e.target.result,
                  file: file,
                  source: 'upload',
                  sequenceNumber: null,
                  backendProcessed: false,
                  uploadedToBackend: false,
                  processingStatus: 'local'
                };
                
                store.addUploadedFile(mediaItem);
              };
              reader.readAsDataURL(file);
            });
          }
        }
      });
      
    } catch (error) {
      console.error('File upload failed:', error);
      toast.error('Upload failed. Adding files locally...');
      
      // Fallback to local file handling
      validFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const mediaItem = {
            id: Date.now() + Math.random() + index,
            name: file.name,
            type: type,
            size: file.size,
            url: e.target.result,
            file: file,
            source: 'upload',
            sequenceNumber: null,
            backendProcessed: false,
            uploadedToBackend: false,
            processingStatus: 'local'
          };
          
          store.addUploadedFile(mediaItem);
        };
        reader.readAsDataURL(file);
      });
    }
  };

  // Handle sequence assignment
  const handleSequenceAssignment = (media) => {
    setSelectedMediaForSequence(media);
    setShowSequenceDialog(true);
    setSequenceNumber(media.sequenceNumber?.toString() || '');
  };

  const handleSequenceSubmit = () => {
    if (!sequenceNumber || isNaN(sequenceNumber) || sequenceNumber < 1) {
      toast.error('Please enter a valid page sequence number (1 or higher)');
      return;
    }
    
    if (selectedMediaForSequence) {
      // Update the media item with sequence number
      const updatedMedia = {
        ...selectedMediaForSequence,
        sequenceNumber: parseInt(sequenceNumber),
        pagePosition: parseInt(sequenceNumber)
      };
      
      // Update in the appropriate store array
      if (selectedMediaForSequence.source === 'upload') {
        const updatedFiles = (store.uploadedFiles || []).map(file => 
          file.id === selectedMediaForSequence.id ? updatedMedia : file
        );
        store.setUploadedFiles(updatedFiles);
      } else if (selectedMediaForSequence.source === 'ai-generated') {
        const updatedGenerated = (store.generatedMedia || []).map(item => 
          item.id === selectedMediaForSequence.id ? updatedMedia : item
        );
        store.setGeneratedMedia(updatedGenerated);
      } else {
        // Handle search results or any other source
        const updatedSearch = (store.searchResults || []).map(item => 
          item.id === selectedMediaForSequence.id ? updatedMedia : item
        );
        store.setSearchResults(updatedSearch);
      }
      
      toast.success(`Sequence #${sequenceNumber} assigned to ${selectedMediaForSequence.name}`);
    }
    
    // Always close dialog regardless of success/failure
    setShowSequenceDialog(false);
    setSelectedMediaForSequence(null);
    setSequenceNumber('');
  };

  const handleSequenceCancel = () => {
    setShowSequenceDialog(false);
    setSelectedMediaForSequence(null);
    setSequenceNumber('');
  };

  // Clear all sequences
  const clearAllSequences = () => {
    // Clear sequences from uploaded files
    const clearedUploaded = store.uploadedFiles.map(file => ({
      ...file,
      sequenceNumber: null,
      pagePosition: null
    }));
    store.setUploadedFiles(clearedUploaded);

    // Clear sequences from search results  
    const clearedSearch = store.searchResults.map(item => ({
      ...item,
      sequenceNumber: null,
      pagePosition: null
    }));
    store.setSearchResults(clearedSearch);

    // Clear sequences from generated media
    const clearedGenerated = store.generatedMedia.map(item => ({
      ...item,
      sequenceNumber: null,
      pagePosition: null
    }));
    store.setGeneratedMedia(clearedGenerated);

    toast.success('All sequence assignments cleared');
  };

  // Auto-assign sequences to selected media
  const autoAssignSequences = () => {
    if (selectedMedia.length === 0) {
      toast.error('No media items selected');
      return;
    }

    let sequenceCounter = 1;
    
    // Update uploaded files
    const updatedUploaded = store.uploadedFiles.map(file => {
      if (selectedMedia.find(item => item.id === file.id)) {
        return {
          ...file,
          sequenceNumber: sequenceCounter++,
          pagePosition: sequenceCounter - 1
        };
      }
      return file;
    });
    store.setUploadedFiles(updatedUploaded);

    // Update search results
    const updatedSearch = store.searchResults.map(item => {
      if (selectedMedia.find(selected => selected.id === item.id)) {
        return {
          ...item,
          sequenceNumber: sequenceCounter++,
          pagePosition: sequenceCounter - 1
        };
      }
      return item;
    });
    store.setSearchResults(updatedSearch);

    // Update generated media
    const updatedGenerated = store.generatedMedia.map(item => {
      if (selectedMedia.find(selected => selected.id === item.id)) {
        return {
          ...item,
          sequenceNumber: sequenceCounter++,
          pagePosition: sequenceCounter - 1
        };
      }
      return item;
    });
    store.setGeneratedMedia(updatedGenerated);

    toast.success(`Auto-assigned sequence numbers 1-${selectedMedia.length} to selected media`);
  };

  // Handle tags and keywords management
  const addCustomTag = () => {
    if (customTag.trim() && !searchTags.includes(customTag.trim())) {
      setSearchTags([...searchTags, customTag.trim()]);
      setCustomTag('');
      toast.success(`Added tag: ${customTag.trim()}`);
    }
  };

  const removeTag = (tagToRemove) => {
    setSearchTags(searchTags.filter(tag => tag !== tagToRemove));
    toast(`Removed tag: ${tagToRemove}`, {
      icon: 'ℹ️'
    });
  };

  const addCustomKeyword = () => {
    if (customKeyword.trim() && !searchKeywords.includes(customKeyword.trim())) {
      setSearchKeywords([...searchKeywords, customKeyword.trim()]);
      setCustomKeyword('');
      toast.success(`Added keyword: ${customKeyword.trim()}`);
    }
  };

  const removeKeyword = (keywordToRemove) => {
    setSearchKeywords(searchKeywords.filter(keyword => keyword !== keywordToRemove));
    toast(`Removed keyword: ${keywordToRemove}`, {
      icon: 'ℹ️'
    });
  };

  // Handle media search
  const handleSearch = async () => {
    if (!searchQuery.trim() && searchTags.length === 0 && searchKeywords.length === 0) {
      toast.error('Please enter a search query or select tags/keywords');
      return;
    }

    setIsSearching(true);
    
    try {
      // Call backend API for internet media search
      const response = await fetch('http://localhost:8000/api/media/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery.trim(),
          platforms: ['pexels', 'google'], // Search both Pexels and Google
          media_type: 'both', // Search for both images and videos
          tags: searchTags,
          keywords: searchKeywords,
          per_page: 15,
          orientation: null // No orientation filter for now
        })
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.status === 'no_results') {
        toast(`No results found for "${data.query}"`, {
          icon: 'ℹ️'
        });
        store.setSearchResults([]);
      } else {
        // Add tags and keywords to results
        const enrichedResults = data.results.map(result => ({
          ...result,
          tags: searchTags.length > 0 ? searchTags : ['stock'],
          keywords: searchKeywords.length > 0 ? searchKeywords : []
        }));
        
        store.setSearchResults(enrichedResults);
        
        // Show success message with platform info
        const platformsUsed = data.platforms_searched.join(', ');
        toast.success(`Found ${data.total_results} results from ${platformsUsed}`);
        
        // Show any platform errors as warnings
        if (data.errors && Object.keys(data.errors).length > 0) {
          const errorMessages = Object.entries(data.errors)
            .map(([platform, error]) => `${platform}: ${error}`)
            .join('; ');
          toast(`Platform issues: ${errorMessages}`, {
            icon: '⚠️'
          });
        }
      }
      
      setIsSearching(false);
    } catch (error) {
      console.error('Media search error:', error);
      setIsSearching(false);
      toast.error(`Search failed: ${error.message}`);
      
      // Fallback to empty results
      store.setSearchResults([]);
    }
  };

  // Handle AI generation
  const handleAIGeneration = async () => {
    if (!aiPrompt.trim()) {
      toast.error('Please enter an AI generation prompt');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await fetch('http://localhost:8000/api/media/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: aiPrompt.trim(),
          platforms: ['pexels'],
          media_type: 'both',
          tags: searchTags,
          keywords: searchKeywords,
          per_page: 10
        })
      });

      if (!response.ok) {
        throw new Error(`AI generation failed: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.status === 'no_results') {
        toast(`No media found for "${aiPrompt}"`, {
          icon: 'ℹ️'
        });
      } else {
        const generatedMedia = data.results.map(result => ({
          ...result,
          source: 'ai-generated',
          prompt: aiPrompt,
          tags: ['ai', 'generated', ...(result.tags || [])],
        }));
        
        store.addGeneratedMedia(generatedMedia);
        toast.success(`Generated ${generatedMedia.length} AI media items`);
      }
      
      setAiPrompt('');
      setIsGenerating(false);
    } catch (error) {
      console.error('AI generation error:', error);
      setIsGenerating(false);
      toast.error(`AI generation failed: ${error.message}`);
    }
  };

  // Toggle media selection
  const toggleMediaSelection = (media) => {
    const currentSelected = store.selectedMedia;
    const isSelected = currentSelected.find(item => item.id === media.id);
    if (isSelected) {
      store.setSelectedMedia(currentSelected.filter(item => item.id !== media.id));
    } else {
      store.setSelectedMedia([...currentSelected, media]);
    }
  };

  // Get all media items
  const getAllMedia = () => {
    return [
      ...uploadedFiles,
      ...searchResults,
      ...generatedMedia
    ];
  };

  // Handle next step
  const handleNext = () => {
    if (selectedMedia.length === 0) {
      toast.error('Please select at least one media item to continue');
      return;
    }
    
    try {
      // Store full media data in sessionStorage as backup
      sessionStorage.setItem('selectedMediaFull', JSON.stringify(selectedMedia));
      
      // Update store with current selected media
      store.setSelectedMedia(selectedMedia);
      
      toast.success(`Selected ${selectedMedia.length} media items for video effects`);
    } catch (error) {
      console.warn('Failed to store media in localStorage, using session storage only:', error);
      // Store only in sessionStorage if localStorage fails
      sessionStorage.setItem('selectedMediaFull', JSON.stringify(selectedMedia));
      
      // Store minimal data in store
      const minimalMedia = selectedMedia.map(item => ({
        id: item.id,
        name: item.name,
        type: item.type,
        source: item.source,
        sequenceNumber: item.sequenceNumber,
        pagePosition: item.pagePosition
      }));
      store.setSelectedMedia(minimalMedia);
      
      toast.success(`Selected ${selectedMedia.length} media items for video effects`);
    }
    onNext(selectedMedia);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          🎬 Media Manager
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-2">
          Upload, search, or generate images and videos for your project
        </p>
        <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <span>Script: <strong>{scriptData?.title || 'Untitled'}</strong></span>
          <span>•</span>
          <span>Selected: <strong className="text-blue-600 dark:text-blue-400">{selectedMedia.length}</strong> items</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-1 inline-flex">
          {[
            { id: 'upload', label: 'Upload', icon: '📁' },
            { id: 'search', label: 'Search', icon: '🔍' },
            { id: 'ai-generate', label: 'AI Generate', icon: '🤖' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-2 rounded-md font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-200'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="mb-8">
        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Image Upload */}
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center hover:border-blue-400 dark:hover:border-blue-500 transition-colors">
                <div className="space-y-4">
                  <div className="text-4xl">🖼️</div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                    Upload Images
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    JPG, PNG, GIF up to 10MB each<br/>
                    <span className="text-xs">Assign sequence later in gallery</span>
                  </p>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-all"
                  >
                    Choose Images
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => handleFileUpload(e, 'image')}
                  />
                </div>
              </div>

              {/* Video Upload */}
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center hover:border-purple-400 dark:hover:border-purple-500 transition-colors">
                <div className="space-y-4">
                  <div className="text-4xl">🎥</div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                    Upload Videos
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    MP4, AVI, MOV up to 100MB each<br/>
                    <span className="text-xs">Assign sequence later in gallery</span>
                  </p>
                  <button
                    onClick={() => videoInputRef.current?.click()}
                    className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 transition-all"
                  >
                    Choose Videos
                  </button>
                  <input
                    ref={videoInputRef}
                    type="file"
                    multiple
                    accept="video/*"
                    className="hidden"
                    onChange={(e) => handleFileUpload(e, 'video')}
                  />
                </div>
              </div>
            </div>

            {/* Processing Status Display */}
            {(isUploading || isProcessing || processingTasks.size > 0) && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-3 flex items-center gap-2">
                  {isUploading ? '📤 Uploading Files...' : isProcessing ? '⚙️ Processing Media...' : '📊 Processing Status'}
                </h4>
                
                {/* Overall Stats */}
                {processingTasks.size > 0 && (
                  <div className="mb-4">
                    {(() => {
                      const stats = getProcessingStats();
                      return (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div className="bg-white dark:bg-gray-800 rounded p-2 text-center">
                            <div className="font-bold text-blue-600 dark:text-blue-400">{stats.total}</div>
                            <div className="text-gray-600 dark:text-gray-400">Total</div>
                          </div>
                          <div className="bg-white dark:bg-gray-800 rounded p-2 text-center">
                            <div className="font-bold text-yellow-600 dark:text-yellow-400">{stats.processing}</div>
                            <div className="text-gray-600 dark:text-gray-400">Processing</div>
                          </div>
                          <div className="bg-white dark:bg-gray-800 rounded p-2 text-center">
                            <div className="font-bold text-green-600 dark:text-green-400">{stats.completed}</div>
                            <div className="text-gray-600 dark:text-gray-400">Completed</div>
                          </div>
                          <div className="bg-white dark:bg-gray-800 rounded p-2 text-center">
                            <div className="font-bold text-red-600 dark:text-red-400">{stats.failed}</div>
                            <div className="text-gray-600 dark:text-gray-400">Failed</div>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                )}

                {/* Individual Task Progress */}
                <div className="space-y-2">
                  {Array.from(processingTasks.entries()).map(([taskId, task]) => {
                    const progress = processingProgress.get(taskId);
                    return (
                      <div key={taskId} className="bg-white dark:bg-gray-800 rounded p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Task: {task.id.slice(0, 8)}...
                          </span>
                          <div className="flex items-center gap-2">
                            <span className={`text-xs px-2 py-1 rounded ${
                              task.status === 'SUCCESS' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                              task.status === 'FAILURE' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                              ['STARTED', 'PROCESSING'].includes(task.status) ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                              'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                            }`}>
                              {task.status}
                            </span>
                            {['STARTED', 'PROCESSING'].includes(task.status) && (
                              <button
                                onClick={() => cancelTask(taskId)}
                                className="text-xs text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
                              >
                                Cancel
                              </button>
                            )}
                          </div>
                        </div>
                        
                        {progress && (
                          <div>
                            {/* Progress Bar */}
                            {progress.progress !== undefined && (
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
                                <div 
                                  className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${Math.min(100, Math.max(0, progress.progress || 0))}%` }}
                                ></div>
                              </div>
                            )}
                            
                            {/* Status Message */}
                            {progress.status && (
                              <div className="text-xs text-gray-600 dark:text-gray-400">
                                {progress.status}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Loading Spinner for Upload */}
                {isUploading && (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Uploading files...</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="space-y-6">
            <div className="max-w-4xl mx-auto">
              {/* Search Input */}
              <div className="flex gap-4 mb-6">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for stock images and videos..."
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <button
                  onClick={handleSearch}
                  disabled={isSearching}
                  className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSearching ? (
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Searching...
                    </div>
                  ) : (
                    '🔍 Search'
                  )}
                </button>
              </div>

              {/* Tags Management */}
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600 mb-4">
                <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                  🏷️ Search Tags {searchTags.length > 0 && `(${searchTags.length})`}
                </h4>
                
                <div className="flex flex-wrap gap-2 mb-3">
                  {searchTags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                    >
                      #{tag}
                      <button
                        onClick={() => removeTag(tag)}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={customTag}
                    onChange={(e) => setCustomTag(e.target.value)}
                    placeholder="Add custom tag..."
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-sm"
                    onKeyPress={(e) => e.key === 'Enter' && addCustomTag()}
                  />
                  <button
                    onClick={addCustomTag}
                    className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-all text-sm"
                  >
                    Add Tag
                  </button>
                </div>
              </div>

              {/* Keywords Management */}
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600 mb-4">
                <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                  🔑 SEO Keywords {searchKeywords.length > 0 && `(${searchKeywords.length})`}
                </h4>
                
                <div className="flex flex-wrap gap-2 mb-3">
                  {searchKeywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-sm"
                    >
                      {keyword}
                      <button
                        onClick={() => removeKeyword(keyword)}
                        className="text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-200"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={customKeyword}
                    onChange={(e) => setCustomKeyword(e.target.value)}
                    placeholder="Add custom keyword..."
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white text-sm"
                    onKeyPress={(e) => e.key === 'Enter' && addCustomKeyword()}
                  />
                  <button
                    onClick={addCustomKeyword}
                    className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-all text-sm"
                  >
                    Add Keyword
                  </button>
                </div>
              </div>
              
              <div className="text-sm text-gray-600 dark:text-gray-400 text-center">
                <p>🌐 Search across Unsplash, Pexels, Pixabay, and Shutterstock</p>
                <p className="mt-1">💡 Tags and keywords are automatically generated from your social media content</p>
              </div>
            </div>
          </div>
        )}

        {/* AI Generate Tab */}
        {activeTab === 'ai-generate' && (
          <div className="space-y-6">
            <div className="max-w-2xl mx-auto">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    AI Generation Prompt
                  </label>
                  <textarea
                    value={aiPrompt}
                    onChange={(e) => setAiPrompt(e.target.value)}
                    placeholder="Describe the image or video you want to generate..."
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white resize-none"
                  />
                </div>
                
                <button
                  onClick={handleAIGeneration}
                  disabled={isGenerating}
                  className="w-full bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isGenerating ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Generating AI Media...
                    </div>
                  ) : (
                    '🤖 Generate with AI'
                  )}
                </button>
              </div>
              
              <div className="mt-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-600">
                <h4 className="font-semibold text-purple-800 dark:text-purple-300 mb-2">💡 AI Generation Tips:</h4>
                <ul className="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                  <li>• Be specific about style, colors, and composition</li>
                  <li>• Include context from your script for better results</li>
                  <li>• Mention if you want realistic or artistic style</li>
                  <li>• For videos, describe the action or movement</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Media Gallery */}
      {getAllMedia().length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
              📋 Media Library ({getAllMedia().length} items)
            </h3>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setIsSequenceMode(!isSequenceMode)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isSequenceMode 
                    ? 'bg-purple-500 text-white' 
                    : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500'
                }`}
              >
                {isSequenceMode ? '📝 Sequencing Mode' : '🔢 Assign Sequences'}
              </button>
              
              {selectedMedia.length > 0 && (
                <button
                  onClick={autoAssignSequences}
                  className="px-4 py-2 rounded-lg text-sm font-medium bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50 transition-all"
                >
                  ⚡ Auto-Assign to Selected ({selectedMedia.length})
                </button>
              )}
              
              {getAllMedia().some(media => media.sequenceNumber) && (
                <button
                  onClick={clearAllSequences}
                  className="px-4 py-2 rounded-lg text-sm font-medium bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/50 transition-all"
                >
                  🗑️ Clear All Sequences
                </button>
              )}
            </div>
          </div>
          
          {isSequenceMode && (
            <div className="mb-4 p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-600 rounded-lg">
              <p className="text-purple-800 dark:text-purple-300 text-sm">
                💡 <strong>Sequence Mode Active:</strong> Click on any media item to assign a page sequence number (1, 2, 3...) for video ordering.
              </p>
            </div>
          )}
          


          <div className="grid grid-cols-4 gap-6">
            {getAllMedia().map((media) => (
              <div
                key={media.id}
                className={`relative group cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                  selectedMedia.find(item => item.id === media.id)
                    ? 'border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800'
                    : isSequenceMode
                    ? 'border-purple-300 dark:border-purple-600 hover:border-purple-400 dark:hover:border-purple-500'
                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                }`}
                onClick={() => isSequenceMode ? handleSequenceAssignment(media) : toggleMediaSelection(media)}
              >
                <div className="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center relative">
                  {media.type === 'image' ? (
                    <img
                      src={media.url}
                      alt={media.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gray-200 dark:bg-gray-600">
                      <div className="text-center">
                        <div className="text-2xl mb-1">🎥</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Video</div>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Sequence Number Badge */}
                {media.sequenceNumber ? (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="bg-purple-500 text-white text-4xl font-bold w-16 h-16 rounded-full flex items-center justify-center shadow-lg border-4 border-white">
                      {media.sequenceNumber}
                    </div>
                  </div>
                ) : isSequenceMode && (
                  <div className="absolute top-2 left-2 bg-gray-500 bg-opacity-80 text-white text-xs font-bold px-2 py-1 rounded-full">
                    📝 Click
                  </div>
                )}

                {/* Sequence Mode Overlay */}
                {isSequenceMode && !media.sequenceNumber && (
                  <div className="absolute inset-0 bg-purple-500 bg-opacity-20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="bg-purple-500 text-white rounded-lg px-3 py-2 text-sm font-medium">
                      Click to Set #
                    </div>
                  </div>
                )}

                {/* Backend Processing Status */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                  <div className="text-white text-xs">
                    <div className="font-medium truncate" title={media.name}>
                      {media.name}
                    </div>
                    
                    {/* Processing Status Indicators */}
                    <div className="flex items-center gap-1 mt-1">
                      {media.backendProcessed ? (
                        <div className="flex items-center gap-1">
                          <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                          <span className="text-xs">Analyzed</span>
                          {media.qualityScore && (
                            <span className="text-xs bg-green-500/30 px-1 rounded">
                              Q{Math.round(media.qualityScore)}
                            </span>
                          )}
                        </div>
                      ) : media.uploadedToBackend ? (
                        <div className="flex items-center gap-1">
                          <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                          <span className="text-xs">Uploaded</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1">
                          <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                          <span className="text-xs">Local</span>
                        </div>
                      )}
                      
                      {/* Error Indicator */}
                      {media.processingErrors && media.processingErrors.length > 0 && (
                        <span className="w-2 h-2 bg-red-400 rounded-full" title="Processing errors"></span>
                      )}
                    </div>

                    {/* Quality Indicators */}
                    {media.analysisResult && (
                      <div className="flex items-center gap-1 mt-1 text-xs opacity-80">
                        {media.contentAnalysis?.faces_detected > 0 && (
                          <span title="Faces detected">👤</span>
                        )}
                        {media.contentAnalysis?.objects_detected?.length > 0 && (
                          <span title="Objects detected">🎯</span>
                        )}
                        {media.technicalSpecs?.width && media.technicalSpecs?.height && (
                          <span title="Resolution">
                            {media.technicalSpecs.width}x{media.technicalSpecs.height}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Size Info */}
                    {media.size && (
                      <div className="text-xs opacity-60 mt-1">
                        {(media.size / 1024 / 1024).toFixed(1)}MB
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Media Type Icon - Small Corner Badge */}
                <div className="absolute top-2 right-2 w-6 h-6 bg-black bg-opacity-60 text-white rounded-full flex items-center justify-center text-xs">
                  {media.type === 'image' ? '🖼️' : '🎥'}
                </div>

                {/* Processing Recommendations Badge */}
                {media.recommendations?.suggested_effects?.length > 0 && (
                  <div className="absolute top-2 left-2 w-6 h-6 bg-purple-500 bg-opacity-80 text-white rounded-full flex items-center justify-center text-xs" 
                       title={`Recommendations: ${media.recommendations.suggested_effects.join(', ')}`}>
                    ✨
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="text-center space-x-4">
        <button
          onClick={onBack}
          className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-all"
        >
          ← Back to Social Media
        </button>
        <button
          onClick={handleNext}
          disabled={selectedMedia.length === 0}
          className="bg-gradient-to-r from-green-500 to-blue-600 text-white px-6 py-2 rounded-lg hover:from-green-600 hover:to-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue to Video Effects ({selectedMedia.length} selected)
        </button>
      </div>

      {/* Sequence Dialog Modal */}
      {showSequenceDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
              📄 Set Page Sequence
            </h3>
            
            {selectedMediaForSequence && (
              <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-16 h-16 bg-gray-200 dark:bg-gray-600 rounded-lg flex items-center justify-center overflow-hidden">
                    {selectedMediaForSequence.type === 'image' ? (
                      <img src={selectedMediaForSequence.url} alt={selectedMediaForSequence.name} className="w-full h-full object-cover" />
                    ) : (
                      <div className="text-2xl">🎥</div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-800 dark:text-gray-200 truncate max-w-xs" title={selectedMediaForSequence.name}>
                      {selectedMediaForSequence.name}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {selectedMediaForSequence.type} • {selectedMediaForSequence.source}
                      {selectedMediaForSequence.size && (
                        <span> • {(selectedMediaForSequence.size / 1024 / 1024).toFixed(2)} MB</span>
                      )}
                    </div>
                    {selectedMediaForSequence.sequenceNumber && (
                      <div className="text-xs text-purple-600 dark:text-purple-400 mt-1">
                        Current sequence: #{selectedMediaForSequence.sequenceNumber}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Page Sequence Number
              </label>
              <input
                type="number"
                min="1"
                value={sequenceNumber}
                onChange={(e) => setSequenceNumber(e.target.value)}
                placeholder="Enter page number (1, 2, 3...)"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                autoFocus
              />
              <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                💡 This determines the order of this media in your video sequence
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleSequenceCancel}
                className="flex-1 bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleSequenceSubmit}
                className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-all"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaManager;