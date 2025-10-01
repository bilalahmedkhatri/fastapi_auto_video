// Quick test to verify no infinite API calls
let callCount = 0;
let originalFetch = fetch;

// Monitor API calls
window.fetch = function(...args) {
  if (args[0].includes('/api/scripts')) {
    callCount++;
    console.log(`🔍 API Call #${callCount}: ${args[0]}`);
    
    // Alert if too many calls
    if (callCount > 5) {
      console.error('⚠️ POSSIBLE INFINITE LOOP DETECTED! Too many API calls:', callCount);
    }
  }
  return originalFetch.apply(this, args);
};

console.log('🧪 Monitoring API calls for infinite loops...');
console.log('📊 Visit http://localhost:3000/generated-scripts to test');

// Reset counter after 30 seconds
setTimeout(() => {
  console.log(`✅ Test completed. Total API calls: ${callCount}`);
  if (callCount <= 3) {
    console.log('🎉 SUCCESS: No infinite loop detected!');
  } else {
    console.log('⚠️ WARNING: High number of API calls detected');
  }
  window.fetch = originalFetch;
}, 30000);