import { NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';

// Simple mapping function for user IDs
function mapPrismaUserToFastAPI(prismaUserId) {
  // For now, use a simple mapping - you can make this more sophisticated later
  const userMapping = {
    // Add mappings for testing
    'test-uuid-123': 'demo_user',
    'test-uuid-456': 'test_user_123',
    // Add your actual Prisma user UUIDs here as you discover them
    // Format: 'prisma-uuid': 'fastapi-user-id'
  };
  
  // If no mapping found, default to 'demo_user' for testing
  return userMapping[prismaUserId] || 'demo_user';
}

// GET /api/scripts - Fetch scripts with filters and pagination
export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const currentPage = searchParams.get('page') || '1';
    const sortBy = searchParams.get('sort') || 'recent';
    const filterBy = searchParams.get('filter') || 'all';
    const searchQuery = searchParams.get('search') || '';
    const itemsPerPage = searchParams.get('limit') || '10';
    const frontendUserId = searchParams.get('user_id') || '';

    // Map frontend user ID to FastAPI user ID
    const fastApiUserId = frontendUserId ? mapPrismaUserToFastAPI(frontendUserId) : 'demo_user';

    // Build query parameters for FastAPI
    const params = new URLSearchParams({
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      filter_by: filterBy,
      search: searchQuery,
    });

    // Always pass a user_id to FastAPI (mapped or default)
    params.append('user_id', fastApiUserId);

    // Call FastAPI backend (note the trailing slash)
    const response = await fetch(`${FASTAPI_BASE_URL}/api/scripts/?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`FastAPI error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching scripts:', error);
    return NextResponse.json(
      { error: 'Failed to fetch scripts', message: error.message },
      { status: 500 }
    );
  }
}

// DELETE /api/scripts?id=script_id - Delete a script
export async function DELETE(request) {
  try {
    const { searchParams } = new URL(request.url);
    const scriptId = searchParams.get('id');

    if (!scriptId) {
      return NextResponse.json(
        { error: 'Script ID is required' },
        { status: 400 }
      );
    }

    // Call FastAPI backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/scripts/${scriptId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`FastAPI error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error deleting script:', error);
    return NextResponse.json(
      { error: 'Failed to delete script', message: error.message },
      { status: 500 }
    );
  }
}

// PUT /api/scripts - Update script status
export async function PUT(request) {
  try {
    const body = await request.json();
    const { scriptId, status } = body;

    if (!scriptId) {
      return NextResponse.json(
        { error: 'Script ID is required' },
        { status: 400 }
      );
    }

    // Call FastAPI backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/scripts/${scriptId}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });

    if (!response.ok) {
      throw new Error(`FastAPI error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error updating script status:', error);
    return NextResponse.json(
      { error: 'Failed to update script status', message: error.message },
      { status: 500 }
    );
  }
}
