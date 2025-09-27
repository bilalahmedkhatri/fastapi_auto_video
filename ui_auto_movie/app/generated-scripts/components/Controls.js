// Controls Component for filters, search, and view mode
import React from 'react';
import { VIEW_MODES, SORT_OPTIONS, FILTER_OPTIONS } from '../config/constants';

const Controls = ({
  searchQuery,
  onSearchChange,
  filterBy,
  onFilterChange,
  sortBy,
  onSortChange,
  viewMode,
  onViewModeChange,
  onNewScript,
  totalItems
}) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <input
              type="text"
              placeholder="Search scripts..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-400">🔍</span>
            </div>
            {searchQuery && (
              <button
                onClick={() => onSearchChange('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Filters and Controls */}
        <div className="flex items-center gap-4">
          {/* Results Count */}
          {totalItems > 0 && (
            <div className="text-sm text-gray-600 dark:text-gray-400 hidden sm:block">
              {totalItems} script{totalItems !== 1 ? 's' : ''}
            </div>
          )}

          {/* Filter */}
          <select
            value={filterBy}
            onChange={(e) => onFilterChange(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 transition-colors"
          >
            <option value={FILTER_OPTIONS.ALL}>All Status</option>
            <option value={FILTER_OPTIONS.DRAFT}>Draft</option>
            <option value={FILTER_OPTIONS.SCRIPT_READY}>Script Ready</option>
            <option value={FILTER_OPTIONS.SOCIAL_MEDIA_READY}>Social Media Ready</option>
            <option value={FILTER_OPTIONS.VIDEO_READY}>Video Complete</option>
          </select>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 transition-colors"
          >
            <option value={SORT_OPTIONS.RECENT}>Most Recent</option>
            <option value={SORT_OPTIONS.TITLE}>Title A-Z</option>
            <option value={SORT_OPTIONS.STATUS}>Status</option>
            <option value={SORT_OPTIONS.DURATION}>Duration</option>
          </select>

          {/* View Mode Selector */}
          <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => onViewModeChange(VIEW_MODES.GRID)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                viewMode === VIEW_MODES.GRID
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
              title="Grid View"
            >
              🔲 Grid
            </button>
            <button
              onClick={() => onViewModeChange(VIEW_MODES.LIST)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                viewMode === VIEW_MODES.LIST
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
              title="List View"
            >
              📋 List
            </button>
            <button
              onClick={() => onViewModeChange(VIEW_MODES.KANBAN)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                viewMode === VIEW_MODES.KANBAN
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
              title="Kanban View"
            >
              📊 Kanban
            </button>
          </div>

          {/* New Script Button */}
          <button
            onClick={onNewScript}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <span>➕</span>
            <span className="hidden sm:inline">New Script</span>
          </button>
        </div>
      </div>

      {/* Active Filters Display */}
      {(searchQuery || filterBy !== FILTER_OPTIONS.ALL || sortBy !== SORT_OPTIONS.RECENT) && (
        <div className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <span className="text-sm text-gray-600 dark:text-gray-400">Active filters:</span>
          
          {searchQuery && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
              Search: "{searchQuery}"
              <button
                onClick={() => onSearchChange('')}
                className="ml-2 hover:text-blue-600 dark:hover:text-blue-200"
              >
                ✕
              </button>
            </span>
          )}
          
          {filterBy !== FILTER_OPTIONS.ALL && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
              Status: {filterBy.replace('_', ' ')}
              <button
                onClick={() => onFilterChange(FILTER_OPTIONS.ALL)}
                className="ml-2 hover:text-green-600 dark:hover:text-green-200"
              >
                ✕
              </button>
            </span>
          )}
          
          {sortBy !== SORT_OPTIONS.RECENT && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300">
              Sort: {sortBy}
              <button
                onClick={() => onSortChange(SORT_OPTIONS.RECENT)}
                className="ml-2 hover:text-purple-600 dark:hover:text-purple-200"
              >
                ✕
              </button>
            </span>
          )}
          
          <button
            onClick={() => {
              onSearchChange('');
              onFilterChange(FILTER_OPTIONS.ALL);
              onSortChange(SORT_OPTIONS.RECENT);
            }}
            className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
};

export default Controls;
