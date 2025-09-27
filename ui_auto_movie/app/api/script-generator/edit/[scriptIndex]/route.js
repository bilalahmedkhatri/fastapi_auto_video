import { NextResponse } from 'next/server';

const FASTAPI_BASE = 'http://localhost:8000/script-generator';

export async function POST(request, { params }) {
  try {
    const body = await request.json();
    const scriptIndex = params.scriptIndex;
    
    const response = await fetch(`${FASTAPI_BASE}/edit/${scriptIndex}`, {
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
