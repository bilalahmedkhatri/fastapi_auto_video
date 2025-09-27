'use client';

import React, { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { BackgroundJobsIndicator, requestNotificationPermission } from '../hooks/useBackgroundVideoMonitor';

/**
 * App Layout with Background Video Monitoring
 */
const AppLayout = ({ children }) => {
  useEffect(() => {
    // Request notification permission on app load
    requestNotificationPermission();
  }, []);

  return (
    <>
      {children}
      
      {/* Background Jobs Indicator */}
      <BackgroundJobsIndicator />
      
      {/* Toast Notifications */}
      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
          },
          error: {
            duration: 5000,
          },
        }}
      />
    </>
  );
};

export default AppLayout;