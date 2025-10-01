// Add this to browser console on the Generated Scripts page to monitor WebSocket behavior

console.log('🧪 WebSocket Monitor Started');
console.log('📋 Instructions:');
console.log('1. Switch tabs and watch for disconnect messages');
console.log('2. Return to this tab and watch for reconnect messages');
console.log('3. Monitor should show proper cleanup behavior');

let wsEventCount = {
  connections: 0,
  disconnections: 0,
  visibilityChanges: 0
};

// Monitor WebSocket creation
const originalWebSocket = window.WebSocket;
window.WebSocket = function(...args) {
  wsEventCount.connections++;
  console.log(`🔗 WebSocket Connection #${wsEventCount.connections}: ${args[0]}`);
  
  const ws = new originalWebSocket(...args);
  
  // Monitor close events
  const originalClose = ws.close;
  ws.close = function() {
    wsEventCount.disconnections++;
    console.log(`🔌 WebSocket Disconnection #${wsEventCount.disconnections}`);
    return originalClose.call(this);
  };
  
  return ws;
};

// Monitor visibility changes
document.addEventListener('visibilitychange', () => {
  wsEventCount.visibilityChanges++;
  const status = document.hidden ? 'HIDDEN 🙈' : 'VISIBLE 👁️';
  console.log(`📱 Visibility Change #${wsEventCount.visibilityChanges}: Page is ${status}`);
});

// Summary function
window.showWebSocketSummary = () => {
  console.log('📊 WebSocket Monitor Summary:');
  console.log(`- Total Connections: ${wsEventCount.connections}`);
  console.log(`- Total Disconnections: ${wsEventCount.disconnections}`);
  console.log(`- Visibility Changes: ${wsEventCount.visibilityChanges}`);
  
  if (wsEventCount.disconnections >= wsEventCount.connections - 1) {
    console.log('✅ SUCCESS: WebSocket properly cleaning up on tab changes');
  } else if (wsEventCount.connections === 0) {
    console.log('ℹ️ INFO: No WebSocket connections detected yet');
  } else {
    console.log('⚠️ WARNING: Some connections may not be cleaning up properly');
  }
};

console.log('✅ Monitor active. Run showWebSocketSummary() anytime to see results.');

// Auto-summary after 30 seconds
setTimeout(() => {
  console.log('\n⏰ Auto Summary (30 seconds):');
  window.showWebSocketSummary();
}, 30000);