'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { useTheme } from '@/components/ThemeProvider';
import LoadingSpinner from '@/components/LoadingSpinner';

const ScriptEditPage = () => {
  const router = useRouter();
  const params = useParams();
  const { theme } = useTheme();
  const scriptId = params.id;

  const [script, setScript] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    voiceover_script: '',
    category: 'General',
    script_type: 'short',
    language: 'English',
    tags: []
  });

  // Load script data
  useEffect(() => {
    if (scriptId) {
      loadScript();
    }
  }, [scriptId]);

  const loadScript = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/scripts/${scriptId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load script');
      }
      
      const data = await response.json();
      setScript(data);
      
      // Populate form with existing data
      setFormData({
        title: data.title || '',
        description: data.description || '',
        voiceover_script: data.voiceover_script || '',
        category: data.category || 'General',
        script_type: data.script_type || 'short',
        language: data.language || 'English',
        tags: data.tags || []
      });
    } catch (error) {
      console.error('Error loading script:', error);
      toast.error('Failed to load script');
      router.push('/generated-scripts');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      const response = await fetch(`/api/scripts/${scriptId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to save script');
      }

      toast.success('Script updated successfully!');
      router.push('/generated-scripts');
    } catch (error) {
      console.error('Error saving script:', error);
      toast.error('Failed to save script');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleTagsChange = (newTags) => {
    const tagsArray = newTags.split(',').map(tag => tag.trim()).filter(tag => tag);
    setFormData(prev => ({
      ...prev,
      tags: tagsArray
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading script...</p>
        </div>
      </div>
    );
  }

  if (!script) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-gray-600 dark:text-gray-400">Script not found</p>
          <button 
            onClick={() => router.push('/generated-scripts')}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Back to Scripts
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                ✏️ Edit Script
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Modify your script content and settings
              </p>
            </div>
            <button
              onClick={() => router.push('/generated-scripts')}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              ← Back to Scripts
            </button>
          </div>
        </div>

        {/* Edit Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
            {/* Basic Info Section */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Basic Information
              </h3>
              
              {/* Title */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Title
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Enter script title"
                />
              </div>

              {/* Description */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Enter script description"
                />
              </div>

              {/* Settings Row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                {/* Category */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => handleInputChange('category', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="General">General</option>
                    <option value="Business">Business</option>
                    <option value="Education">Education</option>
                    <option value="Entertainment">Entertainment</option>
                    <option value="Technology">Technology</option>
                    <option value="Health">Health</option>
                    <option value="Travel">Travel</option>
                    <option value="Food">Food</option>
                  </select>
                </div>

                {/* Script Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Script Type
                  </label>
                  <select
                    value={formData.script_type}
                    onChange={(e) => handleInputChange('script_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="short">Short (30-60s)</option>
                    <option value="medium">Medium (1-3 min)</option>
                    <option value="long">Long (3+ min)</option>
                  </select>
                </div>

                {/* Language */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Language
                  </label>
                  <select
                    value={formData.language}
                    onChange={(e) => handleInputChange('language', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="English">English</option>
                    <option value="Spanish">Spanish</option>
                    <option value="French">French</option>
                    <option value="German">German</option>
                    <option value="Italian">Italian</option>
                    <option value="Portuguese">Portuguese</option>
                  </select>
                </div>
              </div>

              {/* Tags */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.tags.join(', ')}
                  onChange={(e) => handleTagsChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="tag1, tag2, tag3"
                />
              </div>
            </div>

            {/* Script Content Section */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Script Content
              </h3>
              
              {/* Voiceover Script */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Voiceover Script
                </label>
                <textarea
                  value={formData.voiceover_script}
                  onChange={(e) => handleInputChange('voiceover_script', e.target.value)}
                  rows={12}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white font-mono"
                  placeholder="Enter the voiceover script content"
                />
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Word count: {formData.voiceover_script.split(' ').filter(word => word.trim()).length}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-600">
              <button
                type="button"
                onClick={() => router.push('/generated-scripts')}
                className="px-6 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              >
                Cancel
              </button>
              
              <div className="flex items-center space-x-4">
                <button
                  type="button"
                  onClick={() => window.open(`/generated-scripts/${scriptId}/preview`, '_blank')}
                  className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  👁️ Preview
                </button>
                
                <button
                  type="submit"
                  disabled={saving}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Saving...
                    </>
                  ) : (
                    <>💾 Save Changes</>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Script Stats */}
        {script && (
          <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Script Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500 dark:text-gray-400">Created:</span>
                <div className="font-medium text-gray-900 dark:text-white">
                  {new Date(script.created_at).toLocaleDateString()}
                </div>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Updated:</span>
                <div className="font-medium text-gray-900 dark:text-white">
                  {new Date(script.updated_at).toLocaleDateString()}
                </div>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Status:</span>
                <div className="font-medium text-gray-900 dark:text-white">
                  {script.status}
                </div>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">AI Model:</span>
                <div className="font-medium text-gray-900 dark:text-white">
                  {script.ai_model_used || 'N/A'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScriptEditPage;
