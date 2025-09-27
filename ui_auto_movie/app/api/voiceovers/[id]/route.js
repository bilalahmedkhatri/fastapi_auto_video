import { NextResponse } from 'next/server';

export async function DELETE(request, { params }) {
  try {
    const { id } = params;
    
    // Simulate deletion - in a real app, this would remove from database
    await new Promise(resolve => setTimeout(resolve, 200));
    
    return NextResponse.json({
      success: true,
      message: 'Voiceover deleted successfully',
      id: id
    });
  } catch (error) {
    console.error('Error deleting voiceover:', error);
    return NextResponse.json(
      { error: 'Failed to delete voiceover' },
      { status: 500 }
    );
  }
}