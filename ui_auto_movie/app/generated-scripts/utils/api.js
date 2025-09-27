import { toast } from 'react-hot-toast';
import { PAGINATION_CONFIG } from '../config/constants';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3000';

// Fetch scripts from database with filters, search, and pagination
export const fetchScripts = async (filters = {}) => {
  const {
    currentPage = 1,
    sortBy = 'recent',
    filterBy = 'all',
    searchQuery = '',
    itemsPerPage = PAGINATION_CONFIG.ITEMS_PER_PAGE,
    userId = null
  } = filters;

  try {
    // Build query parameters
    const params = new URLSearchParams({
      page: currentPage.toString(),
      sort: sortBy,
      filter: filterBy,
      search: searchQuery,
      limit: itemsPerPage.toString()
    });

    // Add user_id if provided
    if (userId) {
      params.append('user_id', userId);
    }

    // Debug logging
    console.log('API URL:', `${API_BASE_URL}/api/scripts?${params}`);

    // Call Next.js API route which proxies to FastAPI
    const response = await fetch(`${API_BASE_URL}/api/scripts?${params}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Transform the data to match the expected format
    return {
      scripts: data.scripts.map(script => ({
        id: script.id,
        title: script.title,
        description: script.description,
        content: script.voiceover_script,
        category: script.category,
        language: script.language,
        script_type: script.script_type,
        tags: Array.isArray(script.tags) ? script.tags : [],
        duration_estimate: script.duration_estimate,
        word_count: script.word_count,
        status: script.status || 'completed',
        created_at: script.created_at,
        updated_at: script.updated_at,
        user_prompt: script.user_prompt,
        ai_model_used: script.ai_model_used,
        generation_duration_ms: script.generation_duration_ms,
        video_process: script.video_process  // Include video process status
      })),
      totalPages: data.total_pages,
      totalItems: data.total_items,
      currentPage: data.current_page
    };
  } catch (error) {
    console.error('Error fetching scripts from database:', error);
    toast.error('Failed to fetch scripts from database');
    throw error;
  }
};

// Update script status
export const updateScriptStatus = async (scriptId, newStatus) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/scripts`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scriptId, status: newStatus })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    toast.success('Script status updated successfully');
    return data;
  } catch (error) {
    console.error('Error updating script status:', error);
    toast.error('Failed to update script status');
    throw error;
  }
};

// Delete script
export const deleteScript = async (scriptId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/scripts?id=${scriptId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    toast.success('Script deleted successfully');
    return data;
  } catch (error) {
    console.error('Error deleting script:', error);
    toast.error('Failed to delete script');
    throw error;
  }
};

// Get script by ID
export const getScriptById = async (scriptId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/scripts/${scriptId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Script not found');
      }
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    
    const script = await response.json();
    
    // Transform the data to match the expected format
    return {
      id: script.id,
      title: script.title,
      description: script.description,
      content: script.voiceover_script,
      category: script.category,
      language: script.language,
      script_type: script.script_type,
      tags: Array.isArray(script.tags) ? script.tags : [],
      duration_estimate: script.duration_estimate,
      word_count: script.word_count,
      status: script.status || 'completed',
      created_at: script.created_at,
      updated_at: script.updated_at,
      user_prompt: script.user_prompt,
      ai_model_used: script.ai_model_used,
      generation_duration_ms: script.generation_duration_ms
    };
  } catch (error) {
    console.error('Error fetching script:', error);
    toast.error('Failed to fetch script');
    throw error;
  }
};
