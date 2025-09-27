'use client';

import React from 'react';

const InputForm = ({ 
  formData, 
  scriptTypeConfigs, 
  onInputChange, 
  onToggleScriptType, 
  onGenerateScripts, 
  loading 
}) => {
  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          🎬 Multi-Script Video Generator
        </h1>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          Generate multiple video script variations and select the perfect one
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 max-w-4xl mx-auto">
        {/* Prompt Input */}
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            📝 Video Topic/Prompt
          </label>
          <textarea
            name="userPrompt"
            value={formData.userPrompt}
            onChange={onInputChange}
            placeholder="e.g., 'AI in Education', 'The Future of Electric Cars', 'Climate Change Solutions'..."
            className="w-full p-4 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none resize-vertical min-h-[100px] bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            required
          />
        </div>

        {/* Script Types Selection */}
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            🎭 Script Types (Select one or more)
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(scriptTypeConfigs).map(([type, config]) => (
              <div
                key={type}
                onClick={() => onToggleScriptType(type)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  formData.scriptTypes.includes(type)
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                    : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400 bg-white dark:bg-gray-700'
                }`}
              >
                <div className="text-2xl mb-2">{config.icon}</div>
                <h4 className="font-semibold text-gray-900 dark:text-gray-100">{config.name}</h4>
                <p className="text-sm opacity-75 text-gray-600 dark:text-gray-400">{config.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Category and Language */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              🏷️ Category
            </label>
            <input
              type="text"
              name="category"
              value={formData.category}
              onChange={onInputChange}
              placeholder="e.g., Technology, Education, Entertainment"
              className="w-full p-3 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              🌍 Language
            </label>
            <select
              name="language"
              value={formData.language}
              onChange={onInputChange}
              className="w-full p-3 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option value="English">English</option>
              <option value="Spanish">Spanish</option>
              <option value="French">French</option>
              <option value="German">German</option>
              <option value="Italian">Italian</option>
            </select>
          </div>
        </div>

        {/* Generate Button */}
        <div className="text-center">
          <button
            onClick={onGenerateScripts}
            disabled={loading}
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Generate Scripts'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default InputForm;