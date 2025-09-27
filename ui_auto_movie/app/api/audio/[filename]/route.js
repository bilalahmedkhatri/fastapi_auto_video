import { NextResponse } from 'next/server';

export async function GET(request, { params }) {
  try {
    const { filename } = params;
    
    // In a real app, this would serve actual audio files
    // For demo purposes, we'll redirect to a placeholder or return info
    
    // Return information about the audio file
    return NextResponse.json({
      message: 'Audio file not found - this is a demo',
      filename: filename,
      note: 'In production, this would serve actual audio files'
    }, { status: 404 });
    
  } catch (error) {
    console.error('Error serving audio file:', error);
    return NextResponse.json(
      { error: 'Audio file not found' },
      { status: 404 }
    );
  }
}