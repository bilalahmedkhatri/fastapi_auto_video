import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import jwt from 'jsonwebtoken';
import { prisma } from '@/lib/prisma';

export async function PUT(request) {
  try {
    // Get the token from cookies
    const cookieStore = await cookies();
    const token = cookieStore.get('token');
    
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    // Verify the token
    const decoded = jwt.verify(token.value, process.env.JWT_SECRET || 'secret');
    
    // Get the user ID from the token
    const userId = decoded.id;
    
    // Parse the request body
    const data = await request.json();
    
    // Fields that can be updated by the user
    const allowedFields = [
      'name',
      'avatar',
      'bio',
      'phone',
      'preferredLanguage',
      'notificationEnabled',
      'theme',
      'company',
      'jobTitle',
      'website',
      'twitter',
      'instagram',
      'youtube',
      'tiktok',
      'storagePreference',
      'downloadFormat',
    ];
    
    // Filter out fields that are not allowed to be updated
    const updateData = Object.keys(data)
      .filter(key => allowedFields.includes(key))
      .reduce((obj, key) => {
        obj[key] = data[key];
        return obj;
      }, {});
    
    // Update the user in the database
    const updatedUser = await prisma.user.update({
      where: { id: userId },
      data: updateData,
      select: {
        id: true,
        name: true,
        email: true,
        avatar: true,
        bio: true,
        phone: true,
        preferredLanguage: true,
        notificationEnabled: true,
        theme: true,
        company: true,
        jobTitle: true,
        website: true,
        twitter: true,
        instagram: true,
        youtube: true,
        tiktok: true,
        apiKey: true,
        storagePreference: true,
        downloadFormat: true,
        maxGenerationsPerMonth: true,
        createdAt: true,
        updatedAt: true,
      }
    });
    
    return NextResponse.json({
      message: 'Profile updated successfully',
      user: updatedUser
    });
  } catch (error) {
    console.error('Profile update error:', error);
    return NextResponse.json({ error: 'Failed to update profile' }, { status: 500 });
  }
}
