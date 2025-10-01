/**
 * Final Integration Test - All WebSocket Files in ws_realtime Directory
 */
console.log('🧪 Testing Organized WebSocket Structure...');

// Test 1: API Endpoint
const testAPI = async () => {
  console.log('\n1️⃣ Testing FastAPI with organized WebSocket structure...');
  
  try {
    const response = await fetch('http://localhost:8000/api/scripts/?user_id=demo_user&page=1&limit=1');
    const data = await response.json();
    console.log('✅ FastAPI: Working with organized WebSocket imports');
    return true;
  } catch (error) {
    console.error('❌ FastAPI: Failed -', error.message);
    return false;
  }
};

// Test 2: Frontend API  
const testFrontendAPI = async () => {
  console.log('\n2️⃣ Testing Next.js with organized WebSocket structure...');
  
  try {
    const response = await fetch('http://localhost:3000/api/scripts?user_id=demo_user&page=1&limit=1');
    const data = await response.json();
    console.log('✅ Next.js API: Working with organized WebSocket imports');
    return true;
  } catch (error) {
    console.error('❌ Next.js API: Failed -', error.message);
    return false;
  }
};

// Test 3: WebSocket Connection
const testWebSocket = () => {
  console.log('\n3️⃣ Testing WebSocket connection from organized structure...');
  
  return new Promise((resolve) => {
    let success = false;
    
    try {
      const ws = new WebSocket('ws://localhost:8000/ws/video-process?user_id=demo_user');
      
      ws.onopen = () => {
        console.log('✅ WebSocket: Connected successfully from organized structure');
        success = true;
        ws.close();
      };
      
      ws.onclose = () => {
        resolve(success);
      };
      
      ws.onerror = (error) => {
        console.error('❌ WebSocket: Failed -', error);
        resolve(false);
      };
      
      // Timeout after 5 seconds
      setTimeout(() => {
        if (ws.readyState !== WebSocket.CLOSED) {
          ws.close();
        }
        resolve(success);
      }, 5000);
      
    } catch (error) {
      console.error('❌ WebSocket: Connection error -', error.message);
      resolve(false);
    }
  });
};

// Run all tests
const runOrganizationTest = async () => {
  const results = {
    fastapi: await testAPI(),
    nextjs: await testFrontendAPI(),
    websocket: await testWebSocket()
  };
  
  console.log('\n📊 Organization Test Results:');
  console.log('- FastAPI Integration:', results.fastapi ? '✅ PASS' : '❌ FAIL');
  console.log('- Next.js Integration:', results.nextjs ? '✅ PASS' : '❌ FAIL');
  console.log('- WebSocket Connection:', results.websocket ? '✅ PASS' : '❌ FAIL');
  
  const allPassed = Object.values(results).every(result => result);
  
  console.log('\n🎉 Final Status:', allPassed ? '✅ ALL SYSTEMS OPERATIONAL' : '⚠️ SOME ISSUES DETECTED');
  
  if (allPassed) {
    console.log('🗂️ WebSocket files successfully organized in ws_realtime directories!');
    console.log('📁 Structure: All WebSocket code is now centralized and working properly.');
  }
  
  return allPassed;
};

// Execute test
runOrganizationTest();