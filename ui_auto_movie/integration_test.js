/**
 * Final Integration Test
 */
console.log('🚀 Starting Final Integration Test...');

// Test 1: API Endpoint
console.log('\n📡 Testing API endpoint...');
fetch('http://localhost:8000/api/scripts/?user_id=demo_user&page=1&limit=1')
  .then(response => response.json())
  .then(data => {
    console.log('✅ API Test: SUCCESS');
    console.log('📊 Response:', data);
  })
  .catch(error => {
    console.error('❌ API Test: FAILED', error);
  });

// Test 2: WebSocket Connection
console.log('\n🔗 Testing WebSocket connection...');
const ws = new WebSocket('ws://localhost:8000/ws/video-process?user_id=demo_user');

ws.onopen = () => {
  console.log('✅ WebSocket Test: SUCCESS - Connection established');
  
  // Send test message
  ws.send(JSON.stringify({
    type: 'test',
    message: 'Integration test message'
  }));
};

ws.onmessage = (event) => {
  console.log('📩 WebSocket Message:', event.data);
};

ws.onerror = (error) => {
  console.error('❌ WebSocket Test: FAILED', error);
};

ws.onclose = () => {
  console.log('🔌 WebSocket connection closed');
};

// Test 3: Frontend Integration
console.log('\n🌐 Testing Frontend integration...');
fetch('http://localhost:3000/api/scripts?user_id=demo_user&page=1&limit=1')
  .then(response => response.json())
  .then(data => {
    console.log('✅ Frontend Test: SUCCESS');
    console.log('📊 Frontend Response:', data);
  })
  .catch(error => {
    console.error('❌ Frontend Test: FAILED', error);
  });

// Clean up after 5 seconds
setTimeout(() => {
  ws.close();
  console.log('\n🎉 Integration Test Complete!');
}, 5000);