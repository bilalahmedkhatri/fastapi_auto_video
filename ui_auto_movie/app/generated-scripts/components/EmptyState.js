// Empty State Component
import React from 'react';

const EmptyState = ({ 
  hasFilters, 
  searchQuery, 
  filterBy, 
  onNewScript, 
  onClearFilters 
}) => {
  if (hasFilters) {
    return (
      <div className="text-center py-16">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          No scripts found
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto">
          No scripts match your current filters. Try adjusting your search terms or filters to find what you're looking for.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={onClearFilters}
            className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors"
          >
            Clear All Filters
          </button>
          <button
            onClick={onNewScript}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
          >
            Create New Script
          </button>
        </div>
        
        {/* Filter Summary */}
        <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
          <p>Current filters:</p>
          <div className="flex flex-wrap justify-center gap-2 mt-2">
            {searchQuery && (
              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-300 rounded">
                Search: "{searchQuery}"
              </span>
            )}
            {filterBy !== 'all' && (
              <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 rounded">
                Status: {filterBy.replace('_', ' ')}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="text-center py-16">
      <div className="text-6xl mb-6">📝</div>
      <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
        Welcome to Script Management
      </h3>
      <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-lg mx-auto">
        You haven't created any video scripts yet. Get started by creating your first AI-generated script for your video content.
      </p>
      
      {/* Getting Started Steps */}
      <div className="max-w-2xl mx-auto mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-3xl mb-3">🤖</div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">AI Script Generation</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Use our AI to generate engaging video scripts based on your topics and preferences.
            </p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-3xl mb-3">📱</div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Social Media Optimization</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Automatically optimize your scripts for different social media platforms.
            </p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="text-3xl mb-3">🎬</div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Complete Production</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Generate voiceovers and create videos directly from your scripts.
            </p>
          </div>
        </div>
      </div>
      
      <button
        onClick={onNewScript}
        className="px-8 py-4 bg-blue-500 hover:bg-blue-600 text-white text-lg rounded-lg font-medium transition-colors inline-flex items-center gap-3"
      >
        <span>🚀</span>
        Create Your First Script
      </button>
      
      {/* Quick Tips */}
      <div className="mt-12 max-w-md mx-auto">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-4">💡 Quick Tips</h4>
        <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
          <li>• Start with a clear topic or theme for your video</li>
          <li>• Consider your target audience when generating scripts</li>
          <li>• Use different script types for various content formats</li>
          <li>• Track your progress from script to final video</li>
        </ul>
      </div>
    </div>
  );
};

export default EmptyState;
