import { NextResponse } from 'next/server';

// FastAPI backend base URL
const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';

// Helper function to fetch from FastAPI
async function fetchFromFastAPI(endpoint, options = {}) {
  try {
    const response = await fetch(`${FASTAPI_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      throw new Error(`FastAPI request failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('FastAPI fetch error:', error);
    throw error;
  }
}

// Helper function to transform FastAPI data to match frontend expectations
function transformVoiceoverData(voiceover) {
  // Convert relative URLs to full FastAPI URLs
  const getFullAudioUrl = (url) => {
    if (!url) return null;
    if (url.startsWith('http')) return url; // Already full URL
    return `${FASTAPI_BASE_URL}${url}`; // Convert relative to full URL
  };

  return {
    id: voiceover.id,
    voice_name: voiceover.voice_name,
    voice_id: voiceover.voice_id,
    voice_type: voiceover.voice_id.includes('female') ? 'Female' : 
                voiceover.voice_id.includes('male') ? 'Male' : 
                voiceover.voice_name?.toLowerCase().includes('nicole') || voiceover.voice_name?.toLowerCase().includes('emma') ? 'Female' :
                voiceover.voice_name?.toLowerCase().includes('david') || voiceover.voice_name?.toLowerCase().includes('ryan') ? 'Male' : 'AI',
    duration: voiceover.duration_seconds || 0,
    file_size: voiceover.file_size || 0,
    created_at: voiceover.created_at,
    status: voiceover.status,
    text_content: voiceover.text_content,
    audio_url: getFullAudioUrl(voiceover.file_url),
    audio_file_url: getFullAudioUrl(voiceover.file_url),
    // Additional fields from FastAPI
    user_id: voiceover.user_id,
    script_id: voiceover.script_id,
    video_id: voiceover.video_id,
    speed: voiceover.speed,
    pitch: voiceover.pitch,
    volume: voiceover.volume,
    tone: voiceover.tone,
    filename: voiceover.filename,
    generation_duration_ms: voiceover.generation_duration_ms,
    ai_provider: voiceover.ai_provider,
    ai_model: voiceover.ai_model,
    error_message: voiceover.error_message,
    updated_at: voiceover.updated_at
  };
}
export async function GET(request) {
  try {
    // Extract query parameters
    const { searchParams } = new URL(request.url);
    const user_id = searchParams.get('user_id');
    const script_id = searchParams.get('script_id');
    const video_id = searchParams.get('video_id');
    const voice_id = searchParams.get('voice_id');
    const page = searchParams.get('page') || '1';
    const per_page = searchParams.get('per_page') || '50'; // Get more items by default

    // Build query string for FastAPI
    const queryParams = new URLSearchParams();
    if (user_id) queryParams.append('user_id', user_id);
    if (script_id) queryParams.append('script_id', script_id);
    if (video_id) queryParams.append('video_id', video_id);
    if (voice_id) queryParams.append('voice_id', voice_id);
    queryParams.append('page', page);
    queryParams.append('per_page', per_page);

    const endpoint = `/api/voiceovers/?${queryParams.toString()}`;
    
    // Fetch data from FastAPI backend
    const data = await fetchFromFastAPI(endpoint);
    
    // Transform data to match frontend expectations
    const transformedVoiceovers = data.voiceovers.map(transformVoiceoverData);

    return NextResponse.json({
      voiceovers: transformedVoiceovers,
      total: data.total || transformedVoiceovers.length,
      page: data.page || parseInt(page),
      per_page: data.per_page || parseInt(per_page),
      status: 'success'
    });
    
  } catch (error) {
    console.error('Error fetching voiceovers from FastAPI:', error);
    
    // Return empty result instead of error to avoid breaking the UI
    return NextResponse.json({
      voiceovers: [],
      total: 0,
      page: 1,
      per_page: 50,
      status: 'error',
      message: 'Failed to fetch voiceovers from backend'
    });
  }
}

export async function DELETE(request) {
  try {
    const url = new URL(request.url);
    const pathParts = url.pathname.split('/');
    const id = pathParts[pathParts.length - 1];
    
    if (!id || id === 'route.js') {
      return NextResponse.json(
        { error: 'Voiceover ID is required' },
        { status: 400 }
      );
    }

    // Forward delete request to FastAPI backend
    await fetchFromFastAPI(`/api/voiceovers/${id}`, {
      method: 'DELETE'
    });

    return NextResponse.json({
      success: true,
      message: 'Voiceover deleted successfully'
    });
    
  } catch (error) {
    console.error('Error deleting voiceover:', error);
    return NextResponse.json(
      { error: 'Failed to delete voiceover' },
      { status: 500 }
    );
  }
}