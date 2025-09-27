import { NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';

// GET /api/scripts - Fetch scripts with filters and pagination
export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const currentPage = searchParams.get('page') || '1';
    const sortBy = searchParams.get('sort') || 'recent';
    const filterBy = searchParams.get('filter') || 'all';
    const searchQuery = searchParams.get('search') || '';
    const itemsPerPage = searchParams.get('limit') || '10';
    const userId = searchParams.get('user_id') || '';

    // Build query parameters for FastAPI
    const params = new URLSearchParams({
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      filter_by: filterBy,
      search: searchQuery,
    });

    if (userId) {
      params.append('user_id', userId);
    }

    // Call FastAPI backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/scripts?${params}`, {
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
