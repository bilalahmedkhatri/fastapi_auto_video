'use client';

import React from 'react';

const ScriptMerger = ({
  scripts,
  selectedForMerge,
  mergeInstructions,
  loading,
  onToggleScriptSelection,
  onMergeInstructionsChange,
  onMergeScripts,
  onCancel
}) => {
  return (
    <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-6 text-center">
        🔀 Merge Scripts
      </h2>
      
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Select Scripts to Merge:
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {scripts.map((script, index) => (
            <div
              key={index}
              onClick={() => onToggleScriptSelection(index)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                selectedForMerge.includes(index)
                  ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/30'
                  : 'border-gray-200 dark:border-gray-600 hover:border-purple-300 dark:hover:border-purple-400 bg-white dark:bg-gray-700'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded text-sm text-gray-800 dark:text-gray-200">
                  {script.script_type}
                </span>
                {selectedForMerge.includes(index) && (
                  <span className="text-purple-500">✓</span>
                )}
              </div>
              <h4 className="font-semibold truncate text-gray-900 dark:text-gray-100">{script.title}</h4>
            </div>
          ))}
        </div>
      </div>
      
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Merge Instructions (Optional)
        </label>
        <textarea
          value={mergeInstructions}
          onChange={(e) => onMergeInstructionsChange(e.target.value)}
          placeholder="e.g., 'Combine the introduction from script 1 with the conclusion from script 2', 'Create a balanced version'..."
          className="w-full p-4 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none min-h-[100px] bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
        />
      </div>
      
      <div className="text-center space-x-4">
        <button
          onClick={onMergeScripts}
          disabled={loading || selectedForMerge.length < 2}
          className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Merging...' : 'Merge Scripts'}
        </button>
        <button
          onClick={onCancel}
          className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-all"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

export default ScriptMerger;