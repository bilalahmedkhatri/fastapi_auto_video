import { prisma } from '../../../../lib/prisma';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

export async function POST(request) {
  try {
    const { email, password } = await request.json();
    if (!email || !password) {
      return new Response(JSON.stringify({ message: 'Email and password are required' }), { status: 400 });
    }
    
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      return new Response(JSON.stringify({ message: 'Invalid email or password' }), { status: 401 });
    }
    
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) {
      return new Response(JSON.stringify({ message: 'Invalid email or password' }), { status: 401 });
    }
    
    // Generate JWT token
    const token = jwt.sign(
      { id: user.id, email: user.email },
      process.env.JWT_SECRET || 'secret',
      { expiresIn: '7d' } // Token expires in 7 days
    );
    
    // Set the JWT token in a cookie
    return new Response(
      JSON.stringify({ 
        message: 'Login successful',
        token: token, // Include token in response for localStorage
        user: { 
          id: user.id, 
          name: user.name, 
          email: user.email 
        } 
      }), 
      {
        status: 200,
        headers: { 
          'Set-Cookie': `token=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=604800` // 7 days in seconds
        }
      }
    );
  } catch (err) {
    console.error('Login error:', err);
    return new Response(JSON.stringify({ message: 'Server error' }), { status: 500 });
  }
}
// Removed duplicate POST definition
