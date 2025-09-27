import { NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';
import { prisma } from '../../../../lib/prisma';

export async function GET(request) {
  try {
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'No token provided' }, { status: 401 });
    }

    const token = authHeader.substring(7);
    
    try {
      // Verify JWT token
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secret');
      
      // Get user data from database
      const user = await prisma.user.findUnique({
        where: { id: decoded.id },
        select: { id: true, name: true, email: true } // Don't include password
      });

      if (!user) {
        return NextResponse.json({ error: 'User not found' }, { status: 401 });
      }

      return NextResponse.json({
        user: {
          id: user.id,
          name: user.name,
          email: user.email
        }
      });
      
    } catch (jwtError) {
      console.error('JWT verification failed:', jwtError);
      return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
    }
    
  } catch (error) {
    console.error('Auth verification error:', error);
    return NextResponse.json({ error: 'Auth verification failed' }, { status: 500 });
  }
}
