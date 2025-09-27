'use client';

import React from 'react';

const ScriptEditor = ({
  selectedScript,
  selectedScriptIndex,
  editMode,
  editedScriptContent,
  editInstructions,
  loading,
  onEditModeChange,
  onEditedContentChange,
  onEditInstructionsChange,
  onSaveDirectEdit,
  onApplyAIEdit,
  onCancel
}) => {
  if (selectedScriptIndex === -1 || !selectedScript) {
    return (
      <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-6 text-center">
          ✏️ Edit Script
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-400">
          Please select a script to edit first.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-6 text-center">
        ✏️ Edit Script
      </h2>
      
      <div className="mb-6">
        {/* Script Info */}
        <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
          <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">
            Editing: {selectedScript.title}
          </h3>
          <p className="text-blue-700 dark:text-blue-400 text-sm">
            Type: {selectedScript.script_type} • 
            Duration: {selectedScript.duration_estimate} • 
            Words: {selectedScript.word_count}
          </p>
        </div>
        
        {/* Edit Mode Selector */}
        <div className="mb-4">
          <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => onEditModeChange('direct')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                editMode === 'direct'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              ✏️ Direct Edit
            </button>
            <button
              onClick={() => onEditModeChange('instructions')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                editMode === 'instructions'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              🤖 AI Edit
            </button>
          </div>
        </div>
        
        {editMode === 'direct' ? (
          /* Direct Edit Mode */
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Edit Script Content Directly:
            </label>
            <textarea
              value={editedScriptContent}
              onChange={(e) => onEditedContentChange(e.target.value)}
              placeholder="Edit your script content here..."
              className="w-full p-4 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none min-h-[300px] font-mono text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            />
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              ✏️ Edit the script content directly. Changes will be saved immediately when you click Save.
            </p>
          </div>
        ) : (
          /* AI Edit Mode */
          <>
            {/* Current Script Content */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Current Script Content:
              </label>
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg border dark:border-gray-600 max-h-60 overflow-y-auto">
                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {selectedScript.voiceover_script}
                </p>
              </div>
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Edit Instructions
              </label>
              <textarea
                value={editInstructions}
                onChange={(e) => onEditInstructionsChange(e.target.value)}
                placeholder="e.g., 'Make it more casual and friendly', 'Add more technical details', 'Shorten the introduction', 'Change the tone to be more professional'..."
                className="w-full p-4 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none min-h-[120px] bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                💡 Tip: Be specific about what you want to change. The AI will modify the script according to your instructions.
              </p>
            </div>
          </>
        )}
      </div>
      
      <div className="text-center space-x-4">
        {editMode === 'direct' ? (
          <button
            onClick={onSaveDirectEdit}
            disabled={!editedScriptContent.trim()}
            className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            💾 Save Changes
          </button>
        ) : (
          <button
            onClick={onApplyAIEdit}
            disabled={loading || !editInstructions.trim()}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Editing...' : '🤖 Apply AI Edit'}
          </button>
        )}
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

export default ScriptEditor;