'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">AI Video Generator</h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">Generate amazing videos with the power of AI</p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/video-builder" className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all text-lg font-medium">
            🎬 Try Script Generator
          </Link>
          <Link href="/signup" className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-lg font-medium">
            Sign Up
          </Link>
          <Link href="/login" className="px-8 py-4 bg-transparent text-blue-400 border border-blue-400 rounded-lg hover:bg-blue-900 transition-colors text-lg font-medium">
            Login
          </Link>
        </div>
      </div>

      <div className="mt-20">
        <h2 className="text-3xl font-semibold text-gray-900 dark:text-white text-center mb-12">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 text-center shadow-sm">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-medium text-blue-600 dark:text-blue-400 mb-3">Easy Generation</h3>
            <p className="text-gray-600 dark:text-gray-300">Create videos in just a few clicks with our intuitive interface</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 text-center shadow-sm">
            <div className="text-4xl mb-4">🎨</div>
            <h3 className="text-xl font-medium text-blue-600 dark:text-blue-400 mb-3">Advanced Profiles</h3>
            <p className="text-gray-600 dark:text-gray-300">Customize your profile with detailed preferences</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 text-center shadow-sm">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-medium text-blue-600 dark:text-blue-400 mb-3">Video Dashboard</h3>
            <p className="text-gray-600 dark:text-gray-300">Keep track of all your AI generated videos in one place</p>
          </div>
        </div>
      </div>
    </div>
  );
}
