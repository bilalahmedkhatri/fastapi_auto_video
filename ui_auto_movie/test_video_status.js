// Test script to verify the video status integration
const testUserId = '97541aed-574c-4206-bcd4-b41a752a24d5';

console.log('Testing video status integration...');

// Test the Next.js API route
fetch(`http://localhost:3000/api/scripts?user_id=${testUserId}&page=1&limit=12`)
  .then(response => {
    console.log('Next.js API Response Status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Next.js API Response:', JSON.stringify(data, null, 2));
    
    // Test direct FastAPI call
    return fetch(`http://localhost:8000/api/scripts/?user_id=demo_user&page=1&limit=12`);
  })
  .then(response => {
    console.log('FastAPI Direct Response Status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('FastAPI Direct Response:', JSON.stringify(data, null, 2));
  })
  .catch(error => {
    console.error('Test failed:', error);
  });