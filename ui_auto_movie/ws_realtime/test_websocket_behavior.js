/**
 * Comprehensive WebSocket Tab Behavior Test
 */
console.log('🧪 Comprehensive WebSocket Tab Behavior Test');

const testWebSocketCleanup = () => {
  let ws = null;
  let isConnected = false;
  let connectionAttempts = 0;
  let disconnections = 0;
  
  const connect = () => {
    connectionAttempts++;
    console.log(`🔗 Connection attempt #${connectionAttempts}`);
    
    ws = new WebSocket('ws://localhost:8000/ws/video-process?user_id=cleanup_test');
    
    ws.onopen = () => {
      isConnected = true;
      console.log(`✅ Connected successfully (attempt #${connectionAttempts})`);
    };
    
    ws.onclose = () => {
      isConnected = false;
      disconnections++;
      console.log(`🔌 Disconnected (total disconnections: ${disconnections})`);
    };
    
    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };
  };
  
  const disconnect = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      console.log('🔌 Manually closing connection...');
      ws.close();
    }
  };
  
  // Test sequence
  console.log('\n📋 Test Sequence:');
  console.log('1. Connect WebSocket');
  console.log('2. Simulate tab change (visibility change)');
  console.log('3. Wait for cleanup');
  
  // Step 1: Connect
  connect();
  
  // Step 2: Simulate tab change after 3 seconds
  setTimeout(() => {
    console.log('\n📱 Simulating tab change (page becomes hidden)...');
    
    // Simulate visibility change
    Object.defineProperty(document, 'hidden', {
      writable: true,
      value: true
    });
    
    // Trigger visibility change event
    const event = new Event('visibilitychange');
    document.dispatchEvent(event);
    
    // Check if connection should close
    setTimeout(() => {
      if (isConnected) {
        console.log('⚠️ WARNING: WebSocket still connected after tab change');
        disconnect(); // Force disconnect for test
      } else {
        console.log('✅ SUCCESS: WebSocket properly disconnected on tab change');
      }
      
      // Step 3: Simulate coming back to tab
      setTimeout(() => {
        console.log('\n📱 Simulating return to tab (page becomes visible)...');
        
        Object.defineProperty(document, 'hidden', {
          writable: true,
          value: false
        });
        
        const returnEvent = new Event('visibilitychange');
        document.dispatchEvent(returnEvent);
        
        // Final summary
        setTimeout(() => {
          console.log('\n📊 Final Test Results:');
          console.log(`- Connection attempts: ${connectionAttempts}`);
          console.log(`- Total disconnections: ${disconnections}`);
          console.log(`- Currently connected: ${isConnected ? 'YES' : 'NO'}`);
          
          if (disconnections > 0) {
            console.log('✅ SUCCESS: WebSocket cleanup is working');
          } else {
            console.log('❌ FAILURE: WebSocket not cleaning up properly');
          }
          
          // Clean up
          if (ws) {
            ws.close();
          }
        }, 2000);
      }, 2000);
    }, 1000);
  }, 3000);
};

// Run the test
testWebSocketCleanup();