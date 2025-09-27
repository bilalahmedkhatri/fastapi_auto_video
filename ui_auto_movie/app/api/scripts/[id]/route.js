import { NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';

// GET /api/scripts/[id] - Get script by ID
export async function GET(request, { params }) {
  try {
    const { id } = await params;

    if (!id) {
      return NextResponse.json(
        { error: 'Script ID is required' },
        { status: 400 }
      );
    }

    // Call FastAPI backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/scripts/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Script not found' },
          { status: 404 }
        );
      }
      throw new Error(`FastAPI error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching script:', error);
    return NextResponse.json(
      { error: 'Failed to fetch script', message: error.message },
      { status: 500 }
    );
  }
}

// PUT /api/scripts/[id] - Update script
export async function PUT(request, { params }) {
  try {
    const { id } = await params;

    if (!id) {
      return NextResponse.json(
        { error: 'Script ID is required' },
        { status: 400 }
      );
    }

    const body = await request.json();

    // Call FastAPI backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/scripts/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Script not found' },
          { status: 404 }
        );
      }
      throw new Error(`FastAPI error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error updating script:', error);
    return NextResponse.json(
      { error: 'Failed to update script', message: error.message },
      { status: 500 }
    );
  }
}
