export async function POST() {
  // Clear the user cookie
  return new Response(JSON.stringify({ message: 'Logged out' }), {
    status: 200,
    headers: { 'Set-Cookie': 'user=; Path=/; HttpOnly; Max-Age=0; SameSite=Lax' }
  });
}
