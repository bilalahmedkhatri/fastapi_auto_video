"use client";

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { toast } from 'react-hot-toast';

// VoiceoverListItem component for individual voiceover display in list format
const VoiceoverListItem = ({ voiceover, onPlay, onPause, isPlaying, onDelete, onDownload }) => {
  const [showContent, setShowContent] = useState(false);
  const [popupPosition, setPopupPosition] = useState('below');
  const contentRef = useRef(null);
  const buttonRef = useRef(null);
  
  // Close content popup when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (contentRef.current && !contentRef.current.contains(event.target)) {
        setShowContent(false);
      }
    };

    if (showContent) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showContent]);
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200">
      <div className="grid grid-cols-12 gap-4 p-4 items-center">
        {/* Play Button */}
        <div className="col-span-1">
          <button
            onClick={isPlaying ? onPause : onPlay}
            disabled={!(voiceover.audio_file_url || voiceover.audio_url)}
            className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200 shadow-sm hover:shadow-md ${
              (voiceover.audio_file_url || voiceover.audio_url)
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700'
                : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }`}
          >
            {isPlaying ? (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            )}
          </button>
        </div>

        {/* Voice Name & Status */}
        <div className="col-span-3">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-gray-900 dark:text-white truncate">
              {voiceover.voice_name || 'Generated Voice'}
            </h3>
            <div className={`w-2 h-2 rounded-full ${
              voiceover.status === 'completed' ? 'bg-green-400' :
              voiceover.status === 'processing' ? 'bg-yellow-400 animate-pulse' :
              'bg-gray-400'
            }`}></div>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            ID: {voiceover.voice_id || 'N/A'}
          </div>
        </div>

        {/* Voice Type */}
        <div className="col-span-1.5">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {voiceover.voice_type || 'AI'}
          </span>
        </div>

        {/* Duration */}
        <div className="col-span-1 text-center">
          <span className="text-sm font-mono text-gray-600 dark:text-gray-300">
            {formatDuration(voiceover.duration)}
          </span>
        </div>

        {/* File Size */}
        <div className="col-span-1 text-center">
          <span className="text-sm text-gray-600 dark:text-gray-300">
            {formatFileSize(voiceover.file_size)}
          </span>
        </div>

        {/* Created Date */}
        <div className="col-span-2">
          <span className="text-sm text-gray-600 dark:text-gray-300">
            {formatDate(voiceover.created_at)}
          </span>
        </div>

        {/* Content Preview */}
        <div className="col-span-1.5">
          {voiceover.text_content && (
            <div className="relative">
              <button 
                ref={buttonRef}
                onClick={() => {
                  if (!showContent) {
                    // Calculate position before showing
                    const rect = buttonRef.current.getBoundingClientRect();
                    const viewportHeight = window.innerHeight;
                    const spaceBelow = viewportHeight - rect.bottom;
                    const spaceAbove = rect.top;
                    
                    // Need at least 350px for popup, prefer below if possible
                    const shouldShowAbove = spaceBelow < 350 && spaceAbove >= 350;
                    setPopupPosition(shouldShowAbove ? 'above' : 'below');
                  }
                  setShowContent(!showContent);
                }}
                className="flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-xs">Script</span>
              </button>
              {showContent && (
                <div 
                  ref={contentRef}
                  className={`fixed w-80 max-w-[90vw] p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-xl z-50`}
                  style={{
                    maxHeight: '300px',
                    overflowY: 'auto',
                    ...((() => {
                      if (!buttonRef.current) return {};
                      
                      const rect = buttonRef.current.getBoundingClientRect();
                      const viewportHeight = window.innerHeight;
                      const viewportWidth = window.innerWidth;
                      
                      // Calculate horizontal position (prefer right-aligned, but adjust if too close to edge)
                      let left = rect.right - 320; // 320px is popup width (w-80)
                      if (left < 10) left = rect.left; // If too far left, align with button left
                      if (left + 320 > viewportWidth - 10) left = viewportWidth - 330; // If too far right, adjust
                      
                      // Calculate vertical position
                      if (popupPosition === 'above') {
                        return {
                          left: `${Math.max(10, left)}px`,
                          bottom: `${viewportHeight - rect.top + 8}px`
                        };
                      } else {
                        return {
                          left: `${Math.max(10, left)}px`,
                          top: `${rect.bottom + 8}px`
                        };
                      }
                    })())
                  }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-xs font-medium text-gray-700 dark:text-gray-300">Content:</div>
                    <button
                      onClick={() => setShowContent(false)}
                      className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                      title="Close"
                    >
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed whitespace-pre-wrap">
                    {voiceover.text_content}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="col-span-1">
          <div className="flex items-center gap-1">
            <button
              onClick={() => onDownload(voiceover)}
              className="p-1.5 rounded-lg bg-gray-100 text-gray-600 hover:bg-blue-100 hover:text-blue-600 transition-colors"
              title="Download"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>
            
            <button
              onClick={() => onDelete(voiceover)}
              className="p-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
              title="Delete"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// VoiceoverFilters component for search and filtering
const VoiceoverFilters = ({ filters, onFiltersChange, totalCount }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 mb-6">
      <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center">
        {/* Search */}
        <div className="flex-1">
          <div className="relative">
            <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search voiceovers by name or content..."
              value={filters.search}
              onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Voice Filter */}
        <div className="min-w-48">
          <select
            value={filters.voice}
            onChange={(e) => onFiltersChange({ ...filters, voice: e.target.value })}
            className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Voice Types</option>
            <option value="Nicole">Nicole</option>
            <option value="David">David</option>
            <option value="Emma">Emma</option>
            <option value="Ryan">Ryan</option>
            <option value="AI">AI Generated</option>
          </select>
        </div>

        {/* Sort Options */}
        <div className="flex gap-2">
          <select
            value={filters.sortBy}
            onChange={(e) => onFiltersChange({ ...filters, sortBy: e.target.value })}
            className="px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="name">By Voice Name</option>
            <option value="duration">By Duration</option>
          </select>
        </div>

        {/* Results Count */}
        <div className="text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap">
          {totalCount} voiceover{totalCount !== 1 ? 's' : ''}
        </div>
      </div>
      
      {/* Clear Filters */}
      {(filters.search || filters.voice) && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <button
            onClick={() => onFiltersChange({ search: '', voice: '', sortBy: 'newest' })}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm font-medium"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
};

// Main Generated Voiceovers Page
export default function GeneratedVoiceoversPage() {
  const [voiceovers, setVoiceovers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    voice: '',
    sortBy: 'newest'
  });
  
  const audioRef = useRef(null);

  // Load voiceovers
  const loadVoiceovers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/voiceovers');
      
      if (!response.ok) {
        throw new Error('Failed to load voiceovers');
      }
      
      const data = await response.json();
      // Handle nested response format
      const voiceoversArray = data.voiceovers || data || [];
      
      console.log('Loaded voiceovers:', voiceoversArray.length);
      setVoiceovers(voiceoversArray);
      setError('');
    } catch (err) {
      console.error('Error loading voiceovers:', err);
      setError('Failed to load voiceovers. Please try again.');
      // Don't show toast error immediately, let user see the error state
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVoiceovers();
  }, []);

  // Filter and sort voiceovers
  const filteredVoiceovers = voiceovers
    .filter(vo => {
      const matchesSearch = !filters.search || 
        vo.voice_name?.toLowerCase().includes(filters.search.toLowerCase()) ||
        vo.text_content?.toLowerCase().includes(filters.search.toLowerCase());
      
      const matchesVoice = !filters.voice || vo.voice_name === filters.voice;
      
      return matchesSearch && matchesVoice;
    })
    .sort((a, b) => {
      switch (filters.sortBy) {
        case 'oldest':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'name':
          return (a.voice_name || '').localeCompare(b.voice_name || '');
        case 'duration':
          return (b.duration || 0) - (a.duration || 0);
        default: // newest
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });

  // Audio controls
  const playAudio = (voiceover) => {
    const audioUrl = voiceover.audio_file_url || voiceover.audio_url;
    
    if (!audioUrl) {
      toast.error('Audio file not available');
      return;
    }
    
    if (currentlyPlaying === voiceover.id) return;
    
    // Stop any currently playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    
    try {
      // Create new audio instance
      const fullAudioUrl = audioUrl.startsWith('http') ? audioUrl : audioUrl;
      audioRef.current = new Audio(fullAudioUrl);
      
      // Set up event listeners
      audioRef.current.onloadstart = () => {
        console.log('Loading audio:', voiceover.voice_name);
      };
      
      audioRef.current.oncanplay = () => {
        console.log('Audio ready to play:', voiceover.voice_name);
      };
      
      audioRef.current.onended = () => {
        setCurrentlyPlaying(null);
        console.log('Audio playback ended:', voiceover.voice_name);
      };
      
      audioRef.current.onerror = (err) => {
        console.error('Audio playback error:', err);
        toast.error(`Audio playback failed: ${err.target?.error?.message || 'Unknown error'}`);
        setCurrentlyPlaying(null);
      };
      
      // Start playback
      audioRef.current.play()
        .then(() => {
          setCurrentlyPlaying(voiceover.id);
          toast.success(`Playing "${voiceover.voice_name}"`);
          console.log('Playing voiceover:', voiceover.voice_name);
        })
        .catch(err => {
          console.error('Audio play() failed:', err);
          toast.error('Failed to play audio. Check if file exists and format is supported.');
          setCurrentlyPlaying(null);
        });
        
    } catch (err) {
      console.error('Audio initialization error:', err);
      toast.error('Failed to initialize audio player');
      setCurrentlyPlaying(null);
    }
  };

  const pauseAudio = () => {
    console.log('Pausing audio playback');
    if (audioRef.current) {
      audioRef.current.pause();
      setCurrentlyPlaying(null);
      toast.info('Audio paused');
    }
  };

  // Actions
  const handleDownload = async (voiceover) => {
    const audioUrl = voiceover.audio_file_url || voiceover.audio_url;
    
    if (!audioUrl) {
      toast.error('Audio file not available for download');
      return;
    }
    
    try {
      const link = document.createElement('a');
      const fullAudioUrl = audioUrl.startsWith('http') ? audioUrl : `/api/audio/${audioUrl}`;
      link.href = fullAudioUrl;
      link.download = `voiceover-${voiceover.voice_name || voiceover.title || 'audio'}-${voiceover.id}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success('Download started');
    } catch (err) {
      console.error('Download error:', err);
      toast.error('Download failed');
    }
  };

  const handleDelete = async (voiceover) => {
    if (!confirm('Are you sure you want to delete this voiceover?')) return;
    
    try {
      const response = await fetch(`/api/voiceovers/${voiceover.id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete voiceover');
      }
      
      setVoiceovers(prev => prev.filter(vo => vo.id !== voiceover.id));
      toast.success('Voiceover deleted successfully');
    } catch (err) {
      console.error('Delete error:', err);
      toast.error('Failed to delete voiceover');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5 pointer-events-none"></div>
      
      <div className="container mx-auto px-4 py-8">
        <div className="px-4 py-6 sm:px-0">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 dark:from-white dark:via-blue-200 dark:to-purple-200 bg-clip-text text-transparent mb-2">
                Generated Voiceovers
              </h1>
              <p className="text-gray-600 dark:text-gray-300">Manage and play your AI-generated voiceovers</p>
            </div>
            <div className="flex gap-3">
              <Link 
                href="/dashboard"
                className="inline-flex items-center px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Dashboard
              </Link>
              <Link 
                href="/voicerover"
                className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-colors shadow-sm"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create New Voiceover
              </Link>
            </div>
          </div>
        </div>

          {/* Filters */}
          <VoiceoverFilters 
            filters={filters}
            onFiltersChange={setFilters}
            totalCount={filteredVoiceovers.length}
          />

          {/* Content */}
          {loading ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
              {/* Table Header Skeleton */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 border-b border-gray-200 dark:border-gray-600">
                <div className="grid grid-cols-12 gap-4 p-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  <div className="col-span-1">Play</div>
                  <div className="col-span-3">Voice Name</div>
                  <div className="col-span-1.5">Type</div>
                  <div className="col-span-1 text-center">Duration</div>
                  <div className="col-span-1 text-center">Size</div>
                  <div className="col-span-2">Created</div>
                  <div className="col-span-1.5">Content</div>
                  <div className="col-span-1 text-center">Actions</div>
                </div>
              </div>

              {/* Row Skeletons */}
              <div className="divide-y divide-gray-100 dark:divide-gray-700">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 animate-pulse">
                    <div className="grid grid-cols-12 gap-4 p-4 items-center">
                      {/* Play Button Skeleton */}
                      <div className="col-span-1">
                        <div className="w-10 h-10 bg-gray-200 dark:bg-gray-600 rounded-full"></div>
                      </div>

                      {/* Voice Name & Status Skeleton */}
                      <div className="col-span-3">
                        <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-1/2"></div>
                      </div>

                      {/* Voice Type Skeleton */}
                      <div className="col-span-1.5">
                        <div className="h-6 bg-gray-200 dark:bg-gray-600 rounded-full w-12"></div>
                      </div>

                      {/* Duration Skeleton */}
                      <div className="col-span-1 text-center">
                        <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-8 mx-auto"></div>
                      </div>

                      {/* File Size Skeleton */}
                      <div className="col-span-1 text-center">
                        <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-10 mx-auto"></div>
                      </div>

                      {/* Created Date Skeleton */}
                      <div className="col-span-2">
                        <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-24"></div>
                      </div>

                      {/* Content Preview Skeleton */}
                      <div className="col-span-1.5">
                        <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-12"></div>
                      </div>

                      {/* Actions Skeleton */}
                      <div className="col-span-1">
                        <div className="flex items-center gap-1 justify-center">
                          <div className="w-7 h-7 bg-gray-200 dark:bg-gray-600 rounded-lg"></div>
                          <div className="w-7 h-7 bg-gray-200 dark:bg-gray-600 rounded-lg"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 mx-auto bg-red-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Voiceovers</h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <button
                onClick={loadVoiceovers}
                className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : filteredVoiceovers.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Voiceovers Found</h3>
              <p className="text-gray-600 mb-4">
                {filters.search || filters.voice ? 'Try adjusting your filters' : 'Start by generating your first voiceover'}
              </p>
              <Link
                href="/voicerover"
                className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Generate Voiceover
              </Link>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
              {/* Table Header */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 border-b border-gray-200 dark:border-gray-600">
                <div className="grid grid-cols-12 gap-4 p-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                  <div className="col-span-1">Play</div>
                  <div className="col-span-3">Voice Name</div>
                  <div className="col-span-1.5">Type</div>
                  <div className="col-span-1 text-center">Duration</div>
                  <div className="col-span-1 text-center">Size</div>
                  <div className="col-span-2">Created</div>
                  <div className="col-span-1.5">Content</div>
                  <div className="col-span-1 text-center">Actions</div>
                </div>
              </div>

              {/* Voiceovers List */}
              <div className="divide-y divide-gray-100 dark:divide-gray-700">
                {filteredVoiceovers.map((voiceover) => (
                  <VoiceoverListItem
                    key={voiceover.id}
                    voiceover={voiceover}
                    onPlay={() => playAudio(voiceover)}
                    onPause={pauseAudio}
                    isPlaying={currentlyPlaying === voiceover.id}
                    onDelete={() => handleDelete(voiceover)}
                    onDownload={() => handleDownload(voiceover)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}