import { prisma } from '../../../../lib/prisma';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

export async function POST(request) {
  try {
    const { name, email, password } = await request.json();
    if (!name || !email || !password) {
      return new Response(JSON.stringify({ message: 'All fields are required' }), { status: 400 });
    }
    const existing = await prisma.user.findUnique({ where: { email } });
    if (existing) {
      return new Response(JSON.stringify({ message: 'Email already in use' }), { status: 409 });
    }
    const hashed = await bcrypt.hash(password, 10);
    const user = await prisma.user.create({ data: { name, email, password: hashed } });
    
    // Generate JWT token
    const token = jwt.sign(
      { id: user.id, email: user.email },
      process.env.JWT_SECRET || 'secret',
      { expiresIn: '7d' } // Token expires in 7 days
    );
    
    // Set the JWT token in a cookie
    return new Response(
      JSON.stringify({ 
        message: 'Signup successful', 
        user: { 
          id: user.id, 
          name: user.name, 
          email: user.email 
        } 
      }), 
      {
        status: 201,
        headers: { 
          'Set-Cookie': `token=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=604800` // 7 days in seconds
        }
      }
    );
  } catch (err) {
    console.error('Signup error:', err);
    return new Response(JSON.stringify({ message: 'Server error' }), { status: 500 });
  }
}
