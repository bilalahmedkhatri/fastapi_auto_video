'use client';

import React from 'react';
import LoadingSpinner from '@/components/LoadingSpinner';

const LoadingState = ({ loadingElapsed }) => {
  console.log('Loading elapsed time:', loadingElapsed);
  const getLoadingMessage = () => {
    if (loadingElapsed > 150) return 'We are sorry for the wait, please bear with us while we finish up.';
    if (loadingElapsed > 90) return 'Almost there! AI is crafting your scripts.';
    if (loadingElapsed > 40) return 'Still working! This can take a few moments.';
    if (loadingElapsed > 1) return 'Generating your script options...';
    return 'AI is working hard to generate your scripts.';
  };

  return (
    <LoadingSpinner 
      size="large" 
      message={getLoadingMessage()} 
    />
  );
};

export default LoadingState;