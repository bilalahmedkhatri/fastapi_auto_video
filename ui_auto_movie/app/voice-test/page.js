"use client";

import React, { useState, useEffect } from 'react';

export default function VoiceTestPage() {
  const [status, setStatus] = useState('Testing...');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const testConnection = async () => {
      try {
        console.log('Testing voice API connection...');
        setStatus('Connecting to API...');
        
        const response = await fetch('http://localhost:8000/api/voice/voices');
        console.log('Response:', response);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('Data received:', result);
        
        setData(result);
        setStatus('Success!');
      } catch (err) {
        console.error('Test failed:', err);
        setError(err.message);
        setStatus('Failed');
      }
    };

    testConnection();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Voice API Test</h1>
      <p className="mb-2">Status: <span className="font-mono">{status}</span></p>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {data && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          <strong>Success!</strong> Received {data.voices?.length || 0} voices
        </div>
      )}
      
      {data && (
        <details className="mt-4">
          <summary className="cursor-pointer font-semibold">Raw API Response</summary>
          <pre className="bg-gray-100 p-4 mt-2 text-sm overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}
