'use client';

export default function Overview() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Overview</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-2">Dashboard overview of your video projects and activity</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Projects</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">24</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
              <span className="text-blue-600 dark:text-blue-400 text-xl">📁</span>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <span className="text-green-600 dark:text-green-400">↗ 12%</span>
              <span className="text-gray-600 dark:text-gray-400 ml-2">vs last month</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Videos Created</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">156</p>
            </div>
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
              <span className="text-green-600 dark:text-green-400 text-xl">🎬</span>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <span className="text-green-600 dark:text-green-400">↗ 23%</span>
              <span className="text-gray-600 dark:text-gray-400 ml-2">vs last month</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Hours Saved</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">2,847</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
              <span className="text-purple-600 dark:text-purple-400 text-xl">⏱️</span>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <span className="text-green-600 dark:text-green-400">↗ 8%</span>
              <span className="text-gray-600 dark:text-gray-400 ml-2">vs last month</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Team Members</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">12</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg flex items-center justify-center">
              <span className="text-yellow-600 dark:text-yellow-400 text-xl">👥</span>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <span className="text-green-600 dark:text-green-400">↗ 2</span>
              <span className="text-gray-600 dark:text-gray-400 ml-2">new this month</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {[
              { action: 'Created new project', project: 'Marketing Video Q4', time: '2 hours ago' },
              { action: 'Completed video render', project: 'Product Demo', time: '4 hours ago' },
              { action: 'Updated script', project: 'Tutorial Series', time: '1 day ago' },
              { action: 'Shared project', project: 'Brand Introduction', time: '2 days ago' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-indigo-600 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {activity.action}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {activity.project}
                  </p>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {activity.time}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            <button className="p-4 text-left bg-indigo-50 dark:bg-indigo-900/20 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 rounded-lg transition-colors">
              <div className="text-2xl mb-2">🎬</div>
              <div className="font-medium text-gray-900 dark:text-white text-sm">New Project</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Start creating</div>
            </button>
            <button className="p-4 text-left bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30 rounded-lg transition-colors">
              <div className="text-2xl mb-2">📝</div>
              <div className="font-medium text-gray-900 dark:text-white text-sm">Generate Script</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">AI powered</div>
            </button>
            <button className="p-4 text-left bg-purple-50 dark:bg-purple-900/20 hover:bg-purple-100 dark:hover:bg-purple-900/30 rounded-lg transition-colors">
              <div className="text-2xl mb-2">👥</div>
              <div className="font-medium text-gray-900 dark:text-white text-sm">Invite Team</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Collaborate</div>
            </button>
            <button className="p-4 text-left bg-yellow-50 dark:bg-yellow-900/20 hover:bg-yellow-100 dark:hover:bg-yellow-900/30 rounded-lg transition-colors">
              <div className="text-2xl mb-2">📊</div>
              <div className="font-medium text-gray-900 dark:text-white text-sm">View Reports</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Analytics</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
