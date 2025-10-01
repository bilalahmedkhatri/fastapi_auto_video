// Custom hooks for script management
import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'react-hot-toast';
import { useAuth } from '@/contexts/AuthContext';
import { fetchScripts } from '../utils/api';
import { useVideoWebSocket } from '@/ws_realtime/useVideoWebSocket';

// Hook for managing script data with filters, search, and pagination
export const useScripts = (initialFilters = {}) => {
  console.log('useScripts hook called with initialFilters:', initialFilters);
  const { user, isAuthenticated, isLoading } = useAuth();
  console.log('useScripts - user:', user, 'isAuthenticated:', isAuthenticated, 'isLoading:', isLoading);
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  
  // Filter states
  const [currentPage, setCurrentPage] = useState(initialFilters.currentPage || 1);
  const [sortBy, setSortBy] = useState(initialFilters.sortBy || 'recent');
  const [filterBy, setFilterBy] = useState(initialFilters.filterBy || 'all');
  const [searchQuery, setSearchQuery] = useState(initialFilters.searchQuery || '');

  // Fetch scripts with current filters
  const loadScripts = useCallback(async () => {
    console.log('loadScripts function called');
    setLoading(true);
    setError(null);
    
    try {
      console.log('Loading scripts with user:', user); // Debug log
      
      const result = await fetchScripts({
        currentPage,
        sortBy,
        filterBy,
        searchQuery,
        userId: user?.id || null // Pass authenticated user ID for proper mapping
      });
      
      console.log('Scripts loaded:', result); // Debug log
      
      setScripts(result.scripts);
      setTotalPages(result.totalPages);
      setTotalItems(result.totalItems);
      
      console.log('Scripts set in state:', result.scripts);
      console.log('Number of scripts in state:', result.scripts?.length);
      
    } catch (err) {
      console.error('Error in loadScripts:', err);
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  }, [currentPage, sortBy, filterBy, searchQuery, user?.id]);

  // Load scripts when filters change or user changes
  useEffect(() => {
    console.log('useEffect triggered - isAuthenticated:', isAuthenticated, 'isLoading:', isLoading);
    
    // Load scripts when authentication loading is complete
    if (!isLoading) {
      console.log('Authentication loading complete, loading scripts...');
      loadScripts();
    } else {
      console.log('Authentication still loading, waiting...');
    }
  }, [loadScripts, isLoading]);

  // WebSocket for real-time video process updates
  useVideoWebSocket(user?.id || 'demo_user', (processData) => {
    console.log('🔄 Received video process update:', processData);
    setScripts(prevScripts => 
      prevScripts.map(script => 
        script.user_id === user?.id 
          ? { ...script, video_process: processData }
          : script
      )
    );
  });

  // Reset to first page when filters change (except pagination)
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1);
    }
  }, [sortBy, filterBy, searchQuery]);

  // Filter update functions
  const updateSort = useCallback((newSortBy) => {
    setSortBy(newSortBy);
  }, []);

  const updateFilter = useCallback((newFilterBy) => {
    setFilterBy(newFilterBy);
  }, []);

  const updateSearch = useCallback((newSearchQuery) => {
    setSearchQuery(newSearchQuery);
  }, []);

  const updatePage = useCallback((newPage) => {
    setCurrentPage(newPage);
  }, []);

  // Clear all filters
  const clearFilters = useCallback(() => {
    setSortBy('recent');
    setFilterBy('all');
    setSearchQuery('');
    setCurrentPage(1);
  }, []);

  // Refresh scripts
  const refresh = useCallback(() => {
    loadScripts();
  }, [loadScripts]);

  return {
    // Data
    scripts,
    loading,
    error,
    totalPages,
    totalItems,
    
    // Current filter states
    currentPage,
    sortBy,
    filterBy,
    searchQuery,
    
    // Filter update functions
    updateSort,
    updateFilter,
    updateSearch,
    updatePage,
    clearFilters,
    refresh
  };
};

// Hook for managing view mode state
export const useViewMode = (initialMode = 'grid') => {
  const [viewMode, setViewMode] = useState(initialMode);
  
  // Save to localStorage
  useEffect(() => {
    localStorage.setItem('script-view-mode', viewMode);
  }, [viewMode]);
  
  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('script-view-mode');
    if (saved && ['grid', 'list', 'kanban'].includes(saved)) {
      setViewMode(saved);
    }
  }, []);

  return [viewMode, setViewMode];
};

// Hook for managing bulk selection
export const useBulkSelection = (scripts = []) => {
  const [selectedScripts, setSelectedScripts] = useState(new Set());
  
  const selectScript = useCallback((scriptId) => {
    setSelectedScripts(prev => {
      const newSelection = new Set(prev);
      if (newSelection.has(scriptId)) {
        newSelection.delete(scriptId);
      } else {
        newSelection.add(scriptId);
      }
      return newSelection;
    });
  }, []);
  
  const selectAll = useCallback(() => {
    setSelectedScripts(new Set(scripts.map(script => script.id)));
  }, [scripts]);
  
  const deselectAll = useCallback(() => {
    setSelectedScripts(new Set());
  }, []);
  
  const toggleSelectAll = useCallback(() => {
    if (selectedScripts.size === scripts.length) {
      deselectAll();
    } else {
      selectAll();
    }
  }, [selectedScripts.size, scripts.length, selectAll, deselectAll]);
  
  const isSelected = useCallback((scriptId) => {
    return selectedScripts.has(scriptId);
  }, [selectedScripts]);
  
  const isAllSelected = selectedScripts.size === scripts.length && scripts.length > 0;
  const isPartiallySelected = selectedScripts.size > 0 && selectedScripts.size < scripts.length;
  
  return {
    selectedScripts: Array.from(selectedScripts),
    selectedCount: selectedScripts.size,
    selectScript,
    selectAll,
    deselectAll,
    toggleSelectAll,
    isSelected,
    isAllSelected,
    isPartiallySelected
  };
};

// Hook for managing script actions
export const useScriptActions = () => {
  const [actionLoading, setActionLoading] = useState(false);
  
  const performAction = useCallback(async (action, scriptIds, options = {}) => {
    setActionLoading(true);
    
    try {
      // Handle different types of actions
      switch (action) {
        case 'delete':
          // TODO: Implement bulk delete
          console.log('Deleting scripts:', scriptIds);
          toast.success(`Deleted ${scriptIds.length} script(s)`);
          break;
          
        case 'update_status':
          // TODO: Implement bulk status update
          console.log('Updating status for scripts:', scriptIds, 'to:', options.status);
          toast.success(`Updated ${scriptIds.length} script(s)`);
          break;
          
        case 'export':
          // TODO: Implement export
          console.log('Exporting scripts:', scriptIds, 'format:', options.format);
          toast.success('Scripts exported successfully');
          break;
          
        default:
          throw new Error('Unknown action');
      }
      
      return true;
    } catch (error) {
      console.error('Error performing action:', error);
      toast.error(error.message || 'Failed to perform action');
      return false;
    } finally {
      setActionLoading(false);
    }
  }, []);
  
  return {
    actionLoading,
    performAction
  };
};
