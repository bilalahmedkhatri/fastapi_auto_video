import { NextResponse } from 'next/server';

const FASTAPI_BASE = 'http://localhost:8000/script-generator';

export async function POST(request) {
  try {
    const body = await request.json();
    console.log('Received request to /generate');
    const response = await fetch(`${FASTAPI_BASE}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error proxying to FastAPI:', error);
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ message: 'Script Generator API Proxy' });
}
