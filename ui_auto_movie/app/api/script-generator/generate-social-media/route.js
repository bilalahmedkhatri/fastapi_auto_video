import { NextResponse } from 'next/server';

const FASTAPI_BASE = 'http://localhost:8000/script-generator';

export async function POST(request) {
  try {
    const body = await request.json();
    const response = await fetch(`${FASTAPI_BASE}/generate-social-media`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error proxying social media request to FastAPI:', error);
    return NextResponse.json({ 
      success: false,
      error: 'Failed to connect to backend',
      message: 'Could not generate social media content. Please try again.'
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ message: 'Social Media Content Generator API Proxy' });
}
