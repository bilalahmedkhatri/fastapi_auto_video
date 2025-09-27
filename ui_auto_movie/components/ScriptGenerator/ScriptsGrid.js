'use client';

import React, { useState, useEffect, useRef } from 'react';

const ScriptsGrid = ({ 
    scripts, 
    selectedScriptIndex, 
    generationDuration,
    loading,
    onSelectScript,
    onDirectEdit,
    onAIEdit,
    onSocialMedia,
    onRegenerateScripts,
    onEditSelected,
    onMergeScripts,
    onGenerateSocialMedia,
    onGenerateVoiceover,
    onSelectScriptForVideo,
    onBackToInput
}) => {
    // Platform selection state for each script
    const [scriptPlatforms, setScriptPlatforms] = useState({});
    
    // Debug logging
    console.log('ScriptsGrid - scripts: 111', scripts);
    console.log('ScriptsGrid - scripts length:', scripts?.length);
    if (scripts?.length > 0) {
        console.log('ScriptsGrid - first script keys:', Object.keys(scripts[0]));
        console.log('ScriptsGrid - first script voiceover_script exists:', !!scripts[0].voiceover_script);
        console.log('ScriptsGrid - first script sample:', {
            id: scripts[0].id,
            title: scripts[0].title,
            hasVoiceoverScript: !!scripts[0].voiceover_script,
            voiceoverScriptLength: scripts[0].voiceover_script?.length || 0
        });
    }
    // Available platforms
    const availablePlatforms = [
        { id: 'youtube', name: 'YouTube', icon: '🎥', color: 'text-red-600' },
        { id: 'instagram', name: 'Instagram', icon: '📷', color: 'text-pink-600' },
        { id: 'tiktok', name: 'TikTok', icon: '🎵', color: 'text-black' },
        { id: 'linkedin', name: 'LinkedIn', icon: '💼', color: 'text-blue-700' },
        { id: 'twitter', name: 'Twitter/X', icon: '🐦', color: 'text-blue-500' },
        { id: 'facebook', name: 'Facebook', icon: '👥', color: 'text-blue-600' }
    ];
    
    // Handle platform selection changes
    const handlePlatformChange = (scriptIndex, selectedPlatforms) => {
        setScriptPlatforms(prev => ({
            ...prev,
            [scriptIndex]: selectedPlatforms
        }));
    };
    
    // Get selected platforms for a script (default to YouTube and Instagram)
    const getSelectedPlatforms = (scriptIndex) => {
        return scriptPlatforms[scriptIndex] || ['youtube', 'instagram'];
    };
    
    // Platform Dropdown Component
    const PlatformDropdown = ({ scriptIndex, onPlatformChange }) => {
        const [isOpen, setIsOpen] = useState(false);
        const dropdownRef = useRef(null);
        const selectedPlatforms = getSelectedPlatforms(scriptIndex);
        
        // Close dropdown when clicking outside
        useEffect(() => {
            const handleClickOutside = (event) => {
                if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                    setIsOpen(false);
                }
            };
            
            if (isOpen) {
                document.addEventListener('mousedown', handleClickOutside);
            }
            
            return () => {
                document.removeEventListener('mousedown', handleClickOutside);
            };
        }, [isOpen]);
        
        const togglePlatform = (platformId) => {
            const newSelection = selectedPlatforms.includes(platformId)
                ? selectedPlatforms.filter(p => p !== platformId)
                : [...selectedPlatforms, platformId];
            
            // Ensure at least one platform is selected
            if (newSelection.length > 0) {
                onPlatformChange(newSelection);
            }
        };
        
        const selectAll = () => {
            onPlatformChange(availablePlatforms.map(p => p.id));
        };
        
        const clearAll = () => {
            onPlatformChange(['youtube']); // Keep at least YouTube
        };
        
        return (
            <div className="relative" ref={dropdownRef} onClick={(e) => e.stopPropagation()}>
                {/* Dropdown Button */}
                <button
                    type="button"
                    onClick={(e) => {
                        e.stopPropagation();
                        setIsOpen(!isOpen);
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-left text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <span className="text-gray-700 dark:text-gray-300">
                        {selectedPlatforms.length === 0 ? 'Choose platforms...' : 
                         selectedPlatforms.length === 1 ? '1 platform selected' :
                         `${selectedPlatforms.length} platforms selected`}
                    </span>
                    <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>
                
                {/* Selected Platform Tags */}
                {selectedPlatforms.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                        {selectedPlatforms.map(platformId => {
                            const platform = availablePlatforms.find(p => p.id === platformId);
                            return platform ? (
                                <span key={platformId} className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                                    <span className="mr-1">{platform.icon}</span>
                                    {platform.name}
                                </span>
                            ) : null;
                        })}
                    </div>
                )}
                
                {/* Dropdown Menu */}
                {isOpen && (
                    <div className="absolute z-10 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
                        {/* Quick Actions */}
                        <div className="p-2 border-b border-gray-200 dark:border-gray-700">
                            <div className="flex gap-2">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        selectAll();
                                    }}
                                    className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                                >
                                    Select All
                                </button>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        clearAll();
                                    }}
                                    className="text-xs px-2 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
                                >
                                    Clear All
                                </button>
                            </div>
                        </div>
                        
                        {/* Platform Options */}
                        <div className="max-h-48 overflow-y-auto">
                            {availablePlatforms.map(platform => (
                                <label
                                    key={platform.id}
                                    className="flex items-center px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <input
                                        type="checkbox"
                                        checked={selectedPlatforms.includes(platform.id)}
                                        onChange={(e) => {
                                            e.stopPropagation();
                                            togglePlatform(platform.id);
                                        }}
                                        className="mr-3 w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                                    />
                                    <span className="mr-2 text-lg">{platform.icon}</span>
                                    <span className={`text-sm font-medium ${platform.color}`}>
                                        {platform.name}
                                    </span>
                                    {selectedPlatforms.includes(platform.id) && (
                                        <span className="ml-auto text-green-500">✓</span>
                                    )}
                                </label>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        );
    };
    
    return (
        <div className="max-w-6xl mx-auto">
            <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-4">
                    📋 Generated Script Options
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                    Select a script to use for video generation, or edit/merge scripts below
                </p>
                {generationDuration && (
                    <p className="text-sm text-blue-600 dark:text-blue-400 mt-2">
                        ⏱️ Generated in {(generationDuration / 1000).toFixed(1)} seconds
                    </p>
                )}
            </div>

            {/* Scripts Grid */}
            <div className={`grid grid-cols-1 ${scripts.length >= 2 ? 'lg:grid-cols-2' : 'lg:grid-cols-1'} gap-6 mb-8`}>
                {scripts.map((script, index) => (
                    <div
                        key={index}
                        onClick={() => onSelectScript(selectedScriptIndex === index ? -1 : index)}
                        className={`p-6 border-2 rounded-xl cursor-pointer transition-all ${
                            selectedScriptIndex === index
                                ? 'border-green-500 bg-green-50 dark:bg-green-900/20 transform scale-105'
                                : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400 hover:shadow-lg bg-white dark:bg-gray-800'
                        }`}
                    >
                        <div className="flex items-center justify-between mb-4">
                            <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-semibold uppercase">
                                {script.script_type}
                            </span>
                            {selectedScriptIndex === index && (
                                <span className="text-green-500 text-2xl">✓</span>
                            )}
                        </div>
                        
                        <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-3">
                            {script.title}
                        </h3>
                        
                        <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
                            <span>⏱️ {script.duration_estimate}</span>
                            <span>📝 {script.word_count} words</span>
                            <span>🏷️ {script.tags?.slice(0, 3).join(', ')}</span>
                        </div>
                        
                        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg border-l-4 border-blue-500 mb-4">
                            <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">Full Script:</h4>
                            <div className="max-h-96 overflow-y-auto">
                                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                                    {script.voiceover_script || script.script || script.content || 'No script content available'}
                                </p>
                                {/* Debug info */}
                                {process.env.NODE_ENV === 'development' && (
                                    <div className="mt-2 p-2 bg-yellow-100 dark:bg-yellow-900 text-xs text-gray-600 dark:text-gray-400 rounded">
                                        <strong>Debug:</strong> voiceover_script: {script.voiceover_script ? '✓' : '✗'} | 
                                        script: {script.script ? '✓' : '✗'} | 
                                        content: {script.content ? '✓' : '✗'} | 
                                        Keys: {Object.keys(script).join(', ')}
                                    </div>
                                )}
                            </div>
                        </div>
                        
                        {/* Platform Selection Dropdown */}
                        <div 
                            className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                📱 Select Platforms for Social Media:
                            </label>
                            <PlatformDropdown 
                                scriptIndex={index}
                                onPlatformChange={(platforms) => handlePlatformChange(index, platforms)}
                            />
                        </div>
                        
                        {/* Quick Edit Button */}
                        <div className="mt-4 flex gap-2 flex-wrap">
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDirectEdit(index, script.voiceover_script);
                                }}
                                className="bg-yellow-500 text-white px-3 py-1 rounded-lg hover:bg-yellow-600 transition-all text-xs"
                            >
                                ✏️ Direct Edit
                            </button>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onAIEdit(index);
                                }}
                                className="bg-blue-500 text-white px-3 py-1 rounded-lg hover:bg-blue-600 transition-all text-xs"
                            >
                                🤖 AI Edit
                            </button>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    const selectedPlatforms = getSelectedPlatforms(index);
                                    if (selectedPlatforms.length === 0) {
                                        alert('Please select at least one platform first!');
                                        return;
                                    }
                                    onSocialMedia(index, selectedPlatforms);
                                }}
                                disabled={loading}
                                className="bg-pink-500 text-white px-3 py-1 rounded-lg hover:bg-pink-600 transition-all text-xs disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? '⏳' : '📱'} Social Media
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="text-center space-x-4 mb-8">
                <button
                    onClick={onRegenerateScripts}
                    disabled={loading}
                    className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? '⏳ Regenerating...' : '🔄 Regenerate Scripts'}
                </button>
                <button
                    onClick={onGenerateSocialMedia}
                    disabled={selectedScriptIndex === -1 || loading}
                    className="bg-gradient-to-r from-pink-500 to-red-600 text-white px-6 py-2 rounded-lg hover:from-pink-600 hover:to-red-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? '⏳ Generating...' : '📱 Social Media'}
                </button>
                <button
                    onClick={() => onGenerateVoiceover && onGenerateVoiceover()}
                    disabled={selectedScriptIndex === -1 || loading}
                    className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-6 py-2 rounded-lg hover:from-purple-600 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    🗣️ Generate Voiceover
                </button>
            </div>

            {/* Back to Input Button */}
            <div className="text-center">
                <button
                    onClick={onBackToInput}
                    className="text-blue-500 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 underline"
                >
                    ← Back to Input Form
                </button>
            </div>
        </div>
    );
};

export default ScriptsGrid;