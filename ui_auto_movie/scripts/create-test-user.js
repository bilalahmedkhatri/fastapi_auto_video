const bcrypt = require('bcryptjs');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function createTestUser() {
  try {
    const hashedPassword = await bcrypt.hash('password123', 10);
    const user = await prisma.user.upsert({
      where: { email: 'test@example.com' },
      update: {
        password: hashedPassword // Update password if user exists
      },
      create: {
        name: 'Test User',
        email: 'test@example.com',
        password: hashedPassword
      }
    });
    
    console.log('✅ Test user created/updated successfully:');
    console.log('📧 Email: test@example.com');
    console.log('🔒 Password: password123');
    console.log('👤 User ID:', user.id);
    
    await prisma.$disconnect();
    process.exit(0);
  } catch (error) {
    console.error('❌ Error creating test user:', error);
    await prisma.$disconnect();
    process.exit(1);
  }
}

createTestUser();
