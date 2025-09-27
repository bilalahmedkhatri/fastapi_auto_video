// Status configuration for script statuses
export const statusConfig = {
  draft: { 
    label: 'Draft', 
    color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    icon: '📝'
  },
  script_ready: { 
    label: 'Script Ready', 
    color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    icon: '✅'
  },
  social_media_pending: { 
    label: 'Social Media Pending', 
    color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    icon: '📱'
  },
  social_media_ready: { 
    label: 'Social Media Ready', 
    color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    icon: '🚀'
  },
  voiceover_pending: { 
    label: 'Voiceover Pending', 
    color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    icon: '🎤'
  },
  voiceover_ready: { 
    label: 'Voiceover Ready', 
    color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
    icon: '🔊'
  },
  video_pending: { 
    label: 'Video Pending', 
    color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
    icon: '🎬'
  },
  video_ready: { 
    label: 'Video Complete', 
    color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300',
    icon: '🎉'
  }
};

// API configuration
export const API_CONFIG = {
  BASE_URL: '/api/script-generator',
  ENDPOINTS: {
    SCRIPTS: '/scripts',
    SCRIPT_BY_ID: '/scripts',
    UPDATE_STATUS: '/scripts/status'
  }
};

// Pagination configuration
export const PAGINATION_CONFIG = {
  ITEMS_PER_PAGE: 12,
  MAX_VISIBLE_PAGES: 5
};

// View modes
export const VIEW_MODES = {
  GRID: 'grid',
  LIST: 'list',
  KANBAN: 'kanban'
};

// Sort options
export const SORT_OPTIONS = {
  RECENT: 'recent',
  TITLE: 'title',
  STATUS: 'status',
  DURATION: 'duration'
};

// Filter options
export const FILTER_OPTIONS = {
  ALL: 'all',
  DRAFT: 'draft',
  SCRIPT_READY: 'script_ready',
  SOCIAL_MEDIA_READY: 'social_media_ready',
  VIDEO_READY: 'video_ready'
};
