'use client';

import { useState, useEffect, useRef } from 'react';

// Custom styles for processing animation phases
const animationStyles = `
  @keyframes scaleUpCenter {
    0% { 
      transform: scale(1); 
    }
    100% { 
      transform: scale(5); 
    }
  }
  
  @keyframes moveToBottomLeft {
    0% { 
      transform: scale(5);
      left: calc(50% - 24px);
      top: calc(50% - 24px);
    }
    100% { 
      transform: scale(1);
      left: 1rem;
      top: calc(100vh - 1rem - 48px);
    }
  }
  
  .scale-up-center {
    animation: scaleUpCenter 1s cubic-bezier(0.68, -0.55, 0.27, 1.55) forwards;
  }
  
  .move-to-bottom-left {
    animation: moveToBottomLeft 2s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  }
  
  .spinner-fixed-center {
    position: fixed;
    left: calc(50% - 24px);
    top: calc(50% - 24px);
    width: 48px;
    height: 48px;
  }
  
  .spinner-fixed-transitioning {
    position: fixed;
    left: calc(50% - 24px);
    top: calc(50% - 24px);
    width: 48px;
    height: 48px;
  }
`;

// Progress Modal Component
export default function ProcessingModal({ isVisible, videoId, taskId, onClose }) {
  const [progress, setProgress] = useState({ current_step: 0, total_steps: 10, status: 'Initializing...' });
  const [finalResult, setFinalResult] = useState(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  
  // Animation phase states
  const [animationPhase, setAnimationPhase] = useState('notification'); // 'notification', 'centerScale', 'slideToCorner', 'complete'
  const [showSpinner, setShowSpinner] = useState(false);
  
  // Timer refs for cleanup
  const timersRef = useRef([]);

  useEffect(() => {
    if (!isVisible || !videoId) return;

    // Clear any existing timers
    timersRef.current.forEach(timer => clearTimeout(timer));
    timersRef.current = [];

    // Start animation sequence
    setAnimationPhase('notification');
    
    // Phase 1: Show notification for 5 seconds
    const notificationTimer = setTimeout(() => {
      setAnimationPhase('centerScale');
      setShowSpinner(true);
      
      // Phase 2: Scale up spinner for 1 second
      const scaleTimer = setTimeout(() => {
        setAnimationPhase('slideToCorner');
        
        // Phase 3: Slide to corner for 2 seconds
        const slideTimer = setTimeout(() => {
          setAnimationPhase('complete');
          // Call the existing transition callback
          if (typeof handleTransitionToFloating === 'function') {
            handleTransitionToFloating();
          }
        }, 2000);
        
        timersRef.current.push(slideTimer);
      }, 1000);
      
      timersRef.current.push(scaleTimer);
    }, 5000);
    
    timersRef.current.push(notificationTimer);

    const pollProgress = async () => {
      try {
        // First try Redis processing status
        const redisResponse = await fetch(`http://localhost:8000/api/redis/processing/${videoId}`);
        
        if (redisResponse.ok) {
          const redisData = await redisResponse.json();
          
          if (redisData.found && redisData.state) {
            const state = redisData.state;
            
            // Check if Redis shows completion
            if (state.stage === 'completed' || state.status.includes('Completed')) {
              // Video is completed according to Redis, now get final data from database
              const dbResponse = await fetch(`http://localhost:8000/api/videos/status/${videoId}`);
              if (dbResponse.ok) {
                const dbData = await dbResponse.json();
                setIsCompleted(true);
                setFinalResult({
                  output_url: dbData.output_url || state.output_url,
                  title: dbData.title || 'Generated Video'
                });
                return; // Stop polling
              }
            }
            
            // Update progress for ongoing processing
            setProgress({
              current_step: state.current_step || 0,
              total_steps: state.total_steps || 10,
              status: state.status || 'Processing...',
              stage: state.stage || 'unknown'
            });
          } else {
            // Fallback to database status
            const dbResponse = await fetch(`http://localhost:8000/api/videos/status/${videoId}`);
            if (dbResponse.ok) {
              const dbData = await dbResponse.json();
              
              if (dbData.status === 'completed') {
                setIsCompleted(true);
                setFinalResult({
                  output_url: dbData.output_url,
                  title: dbData.title
                });
                return; // Stop polling
              } else if (dbData.status === 'failed') {
                setProgress({
                  current_step: 0,
                  total_steps: 10,
                  status: 'Failed: ' + (dbData.error || 'Unknown error'),
                  stage: 'failed'
                });
                return;
              }
            }
          }
        }
      } catch (error) {
        console.error('Error polling progress:', error);
        setProgress(prev => ({ ...prev, status: 'Error checking progress...' }));
      }
    };

    // Start polling immediately
    pollProgress();
    
    // Continue polling every 2 seconds if not completed
    const interval = setInterval(() => {
      if (!isCompleted) {
        pollProgress();
      }
    }, 2000);

    return () => {
      clearInterval(interval);
      // Clean up all timers
      timersRef.current.forEach(timer => clearTimeout(timer));
      timersRef.current = [];
    };
  }, [isVisible, videoId, isCompleted]);

  if (!isVisible) return null;

  return (
    <>
      <style jsx>{animationStyles}</style>
      
      {/* Phase 1: Notification - Video processing started */}
      {animationPhase === 'notification' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Video Processing Started!</h3>
            <p className="text-gray-600">Your video is being created. This may take a few minutes...</p>
            <div className="text-xs text-gray-400 mt-4">
              <p>Video ID: {videoId}</p>
              <p>Task ID: {taskId}</p>
            </div>
          </div>
        </div>
      )}

      {/* Phase 2: Center Scale - Spinner scaling up */}
      {animationPhase === 'centerScale' && showSpinner && (
        <div className="fixed inset-0 bg-black bg-opacity-30 z-50">
          <div className="spinner-fixed-center scale-up-center" style={{ zIndex: 60 }}>
            <div className="w-full h-full rounded-full bg-indigo-600 flex items-center justify-center">
              <svg className="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 000 8v4a8 8 0 01-8-8z"></path>
              </svg>
            </div>
          </div>
        </div>
      )}

      {/* Phase 3: Slide to Corner - Moving to bottom-left */}
      {animationPhase === 'slideToCorner' && showSpinner && (
        <div className="fixed inset-0 bg-black bg-opacity-10 z-50 transition-opacity duration-1000">
          <div className="spinner-fixed-transitioning move-to-bottom-left" style={{ zIndex: 60 }}>
            <div className="w-full h-full rounded-full bg-indigo-600 flex items-center justify-center">
              <svg className="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 000 8v4a8 8 0 01-8-8z"></path>
              </svg>
            </div>
          </div>
        </div>
      )}

      {/* Phase 4: Complete - Normal floating button (handled by existing logic) */}
      {animationPhase === 'complete' && !isCompleted && (
        <div className="fixed left-4 bottom-4 z-50">
          <button
            onClick={() => setIsPanelOpen(prev => !prev)}
            className="w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-lg hover:bg-indigo-700 transition-colors"
            aria-label="Toggle processing panel"
            title="Video is processing"
          >
            <svg className="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 000 8v4a8 8 0 01-8-8z"></path>
            </svg>
          </button>
        </div>
      )}

      {/* Completion Modal - Shows when video is completed */}
      {isCompleted && finalResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Video Created Successfully!</h3>
              <p className="text-gray-600 mb-6">{finalResult?.title}</p>
              
              {finalResult?.output_url && (
                <div className="mb-6">
                  <p className="text-sm text-gray-500 mb-2">Output URL:</p>
                  <p className="text-xs text-gray-400 break-all bg-gray-50 p-2 rounded">
                    {finalResult.output_url}
                  </p>
                </div>
              )}
              
              <div className="flex gap-3">
                <button
                  onClick={onClose}
                  className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
                >
                  View Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Slide-out panel - Shows when floating button is clicked */}
      {animationPhase === 'complete' && !isCompleted && (
        <div
          className={`fixed inset-y-0 left-0 z-40 transform transition-transform duration-300 ${
            isPanelOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
          aria-hidden={!isPanelOpen}
        >
          <div className="h-full w-full max-w-md flex items-center justify-center">
            <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 ml-20">
              <h3 className="text-xl font-semibold mb-6 text-center">Creating Your Video</h3>
              
              {/* Progress Bar */}
              <div className="mb-6">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span>{Math.round((progress.current_step / progress.total_steps) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-indigo-600 h-3 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${Math.round((progress.current_step / progress.total_steps) * 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Status and Step Info */}
              <div className="text-center mb-6">
                <p className="text-lg text-gray-800 mb-2">{progress.status}</p>
                <p className="text-sm text-gray-500">
                  Step {progress.current_step} of {progress.total_steps}
                  {progress.stage && ` • ${progress.stage}`}
                </p>
              </div>

              {/* Task Info */}
              <div className="text-xs text-gray-400 text-center">
                <p>Video ID: {videoId}</p>
                <p>Task ID: {taskId}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};