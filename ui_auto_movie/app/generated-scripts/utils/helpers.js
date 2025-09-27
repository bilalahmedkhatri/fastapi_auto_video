// Utility functions for script management
import { toast } from 'react-hot-toast';

// Handle script actions (navigation to different tools)
export const handleScriptAction = async (scriptId, action, router) => {
  try {
    switch (action) {
      case 'generate_social_media':
        // Navigate to social media generation
        router.push(`/video-builder?script=${scriptId}&step=social-media`);
        break;
      case 'generate_voiceover':
        // Navigate to voiceover generation
        router.push(`/voiceover-generator?script=${scriptId}`);
        break;
      case 'generate_video':
        // Navigate to video generation
        router.push(`/video-creator?script=${scriptId}`);
        break;
      case 'edit_script':
        // Navigate to script editing page
        router.push(`/generated-scripts/${scriptId}`);
        break;
      case 'view_details':
        // Navigate to script details
        router.push(`/generated-scripts/${scriptId}`);
        break;
      default:
        toast.error('Unknown action');
        return false;
    }
    return true;
  } catch (error) {
    console.error('Error performing action:', error);
    toast.error('Failed to perform action');
    return false;
  }
};

// Get next recommended action for a script
export const getNextAction = (script) => {
  if (!script.social_media_generated) {
    return { 
      action: 'generate_social_media', 
      label: '📱 Generate Social Media', 
      color: 'bg-pink-500 hover:bg-pink-600' 
    };
  }
  if (!script.voiceover_generated) {
    return { 
      action: 'generate_voiceover', 
      label: '🎤 Generate Voiceover', 
      color: 'bg-purple-500 hover:bg-purple-600' 
    };
  }
  if (!script.video_generated) {
    return { 
      action: 'generate_video', 
      label: '🎬 Create Video', 
      color: 'bg-green-500 hover:bg-green-600' 
    };
  }
  return { 
    action: 'edit_script', 
    label: '✏️ Edit Script', 
    color: 'bg-gray-500 hover:bg-gray-600' 
  };
};

// Calculate script completion percentage
export const calculateCompletionPercentage = (script) => {
  let completed = 1; // Script itself is complete
  let total = 4; // Script + 3 additional stages
  
  if (script.social_media_generated) completed++;
  if (script.voiceover_generated) completed++;
  if (script.video_generated) completed++;
  
  return Math.round((completed / total) * 100);
};

// Format duration estimate
export const formatDuration = (duration) => {
  if (!duration) return 'Unknown';
  return duration.replace('-', ' - ') + ' min';
};

// Format file size
export const formatFileSize = (bytes) => {
  if (!bytes) return '0 KB';
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

// Get script type icon
export const getScriptTypeIcon = (type) => {
  const icons = {
    'short': '⚡',
    'medium': '📖',
    'long': '📚',
    'educational': '🎓',
    'storytelling': '📜',
    'promotional': '📢',
    'tutorial': '🔧',
    'documentary': '🎬'
  };
  return icons[type] || '📝';
};

// Get priority level based on script age and status
export const getPriorityLevel = (script) => {
  const now = new Date();
  const created = new Date(script.created_at);
  const daysDiff = Math.floor((now - created) / (1000 * 60 * 60 * 24));
  
  if (script.status === 'draft' && daysDiff > 7) {
    return { level: 'high', label: 'High Priority', color: 'text-red-600' };
  }
  if (script.status === 'script_ready' && daysDiff > 3) {
    return { level: 'medium', label: 'Medium Priority', color: 'text-yellow-600' };
  }
  return { level: 'normal', label: 'Normal', color: 'text-gray-600' };
};

// Validate script data
export const validateScript = (script) => {
  const errors = [];
  
  if (!script.title || script.title.trim().length === 0) {
    errors.push('Title is required');
  }
  
  if (!script.description || script.description.trim().length === 0) {
    errors.push('Description is required');
  }
  
  if (!script.script_type) {
    errors.push('Script type is required');
  }
  
  if (script.word_count < 50) {
    errors.push('Script must be at least 50 words');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Export script data
export const exportScriptData = (scripts, format = 'json') => {
  try {
    let data;
    let filename;
    let mimeType;
    
    switch (format) {
      case 'csv':
        data = convertToCSV(scripts);
        filename = 'scripts-export.csv';
        mimeType = 'text/csv';
        break;
      case 'json':
      default:
        data = JSON.stringify(scripts, null, 2);
        filename = 'scripts-export.json';
        mimeType = 'application/json';
        break;
    }
    
    const blob = new Blob([data], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    toast.success(`Scripts exported as ${format.toUpperCase()}`);
    return true;
  } catch (error) {
    console.error('Error exporting scripts:', error);
    toast.error('Failed to export scripts');
    return false;
  }
};

// Convert scripts to CSV format
const convertToCSV = (scripts) => {
  const headers = [
    'ID', 'Title', 'Description', 'Type', 'Status', 'Duration', 
    'Word Count', 'Created Date', 'Social Media', 'Voiceover', 'Video'
  ];
  
  const rows = scripts.map(script => [
    script.id,
    `"${script.title.replace(/"/g, '""')}"`,
    `"${script.description.replace(/"/g, '""')}"`,
    script.script_type,
    script.status,
    script.duration_estimate,
    script.word_count,
    new Date(script.created_at).toLocaleDateString(),
    script.social_media_generated ? 'Yes' : 'No',
    script.voiceover_generated ? 'Yes' : 'No',
    script.video_generated ? 'Yes' : 'No'
  ]);
  
  return [headers, ...rows].map(row => row.join(',')).join('\n');
};
