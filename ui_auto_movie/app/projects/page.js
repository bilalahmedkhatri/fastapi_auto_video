'use client';

export default function Projects() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Projects</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-2">Manage your video projects and templates</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Sample project cards */}
        {[1, 2, 3, 4, 5, 6].map((project) => (
          <div key={project} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg mb-4"></div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Project {project}
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
              Video project description and details go here.
            </p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500 dark:text-gray-400">2 days ago</span>
              <button className="text-indigo-600 dark:text-indigo-400 text-sm font-medium hover:underline">
                Open
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
