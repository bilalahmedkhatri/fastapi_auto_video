/**
 * Test WebSocket Cleanup Behavior
 */
console.log('🧪 Testing WebSocket Tab Change Behavior...');

let connectionCount = 0;
let disconnectionCount = 0;

// Monitor WebSocket connections
const originalWebSocket = window.WebSocket;
window.WebSocket = function(...args) {
  connectionCount++;
  console.log(`🔗 WebSocket Connection #${connectionCount}:`, args[0]);
  
  const ws = new originalWebSocket(...args);
  
  const originalClose = ws.close;
  ws.close = function(...closeArgs) {
    disconnectionCount++;
    console.log(`🔌 WebSocket Disconnection #${disconnectionCount}`);
    return originalClose.apply(this, closeArgs);
  };
  
  return ws;
};

// Test visibility change
console.log('\n📱 Testing Page Visibility Changes...');
console.log('1. Open DevTools Console');
console.log('2. Switch to another tab');
console.log('3. Come back to this tab');
console.log('4. Check connection/disconnection counts');

// Monitor visibility changes
let visibilityChangeCount = 0;
document.addEventListener('visibilitychange', () => {
  visibilityChangeCount++;
  const status = document.hidden ? 'HIDDEN' : 'VISIBLE';
  console.log(`👁️ Visibility Change #${visibilityChangeCount}: Page is now ${status}`);
});

// Summary after 30 seconds
setTimeout(() => {
  console.log('\n📊 Test Summary:');
  console.log(`- Total Connections: ${connectionCount}`);
  console.log(`- Total Disconnections: ${disconnectionCount}`);
  console.log(`- Visibility Changes: ${visibilityChangeCount}`);
  
  if (disconnectionCount >= connectionCount - 1) {
    console.log('✅ SUCCESS: WebSocket properly disconnects on tab changes');
  } else {
    console.log('⚠️ WARNING: Some WebSocket connections may not be closing properly');
  }
  
  // Restore original WebSocket
  window.WebSocket = originalWebSocket;
}, 30000);