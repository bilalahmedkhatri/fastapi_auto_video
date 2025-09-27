'use client';

import { useState } from 'react';
import { 
  HomeIcon, 
  ChartBarIcon, 
  FolderIcon, 
  ClipboardDocumentListIcon,
  DocumentChartBarIcon,
  UsersIcon,
  UserIcon,
  BellIcon,
  ChartPieIcon,
  BookmarkIcon,
  CalendarIcon,
  CogIcon,
  QuestionMarkCircleIcon,
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
  MicrophoneIcon
} from '@heroicons/react/24/outline';
import { useTheme } from '@/components/ThemeProvider';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const Header = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, setTheme } = useTheme();
  const pathname = usePathname();

  const navigation = [
    { name: 'Home', href: '/', icon: HomeIcon },
    { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon, badge: '10' },
    { name: 'Video Generation', href: '/create-video', icon: ChartBarIcon },
    { name: 'Generated Script', href: '/generated-scripts', icon: FolderIcon },
    { name: 'Voiceovers', href: '/generated-voiceovers', icon: MicrophoneIcon },
    // { name: 'Projects', href: '/projects', icon: FolderIcon },
    { name: 'Tasks', href: '/tasks', icon: ClipboardDocumentListIcon },
    { name: 'Reporting', href: '/reporting', icon: DocumentChartBarIcon },
    { name: 'Profile', href: '/profile', icon: UsersIcon },
    { name: 'Users', href: '/users', icon: UsersIcon },
  ];

  const secondaryNavigation = [
    { name: 'Support', href: '/support', icon: QuestionMarkCircleIcon },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ];

  const rightNavigation = [
    { name: 'Overview', href: '/overview', icon: ChartPieIcon },
    { name: 'Notifications', href: '/notifications', icon: BellIcon, badge: '10' },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'Saved reports', href: '/saved-reports', icon: BookmarkIcon },
    { name: 'Scheduled reports', href: '/scheduled-reports', icon: CalendarIcon },
    { name: 'User reports', href: '/user-reports', icon: UserIcon },
    { name: 'Notifications', href: '/notification-settings', icon: BellIcon },
  ];

  const isActive = (href) => {
    return pathname === href || (href !== '/' && pathname.startsWith(href));
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 transform transition-transform duration-300 ease-in-out lg:hidden ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">UI</span>
            </div>
            <span className="ml-2 text-lg font-semibold text-gray-900 dark:text-white">Untitled UI</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>
        <MobileSidebarContent 
          navigation={navigation}
          secondaryNavigation={secondaryNavigation}
          isActive={isActive}
        />
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-40 lg:w-64 lg:flex lg:flex-col">
        <div className="flex flex-col flex-1 min-h-0 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
          {/* Logo */}
          <div className="flex items-center h-16 px-4 border-b border-gray-200 dark:border-gray-700">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">UI</span>
            </div>
            <span className="ml-2 text-lg font-semibold text-gray-900 dark:text-white">Untitled UI</span>
          </div>

          {/* Search */}
          <div className="p-4">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search"
                className="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 pb-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive(item.href)
                    ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <item.icon className="mr-3 w-5 h-5" />
                {item.name}
                {item.badge && (
                  <span className="ml-auto inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-full">
                    {item.badge}
                  </span>
                )}
              </Link>
            ))}
          </nav>

          {/* Secondary navigation */}
          <div className="px-4 pb-4">
            <div className="space-y-1">
              {secondaryNavigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    isActive(item.href)
                      ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <item.icon className="mr-3 w-5 h-5" />
                  {item.name}
                </Link>
              ))}
            </div>

            {/* Usage Stats */}
            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-900 dark:text-white">Used space</span>
                <span className="text-sm text-gray-500 dark:text-gray-400">80%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '80%' }}></div>
              </div>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Your team has used 80% of your available space. Need more?
              </p>
              <div className="mt-3 flex space-x-2">
                <button className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline">
                  Dismiss
                </button>
                <button className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline">
                  Upgrade plan
                </button>
              </div>
            </div>

            {/* User Profile */}
            <div className="mt-4 flex items-center p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">OR</span>
              </div>
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  Olivia Rhye
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  olivia@untitledui.com
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-30 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(true)}
                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 lg:hidden"
              >
                <Bars3Icon className="w-6 h-6" />
              </button>
            </div>

            {/* Right side navigation for larger screens */}
            <div className="hidden lg:flex lg:items-center lg:space-x-6">
              {rightNavigation.slice(0, 4).map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`relative flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    isActive(item.href)
                      ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <item.icon className="mr-2 w-4 h-4" />
                  {item.name}
                  {item.badge && (
                    <span className="ml-2 inline-flex items-center px-2 py-1 text-xs font-medium bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

// Mobile sidebar content component
const MobileSidebarContent = ({ navigation, secondaryNavigation, isActive }) => (
  <div className="flex flex-col flex-1 min-h-0">
    {/* Search */}
    <div className="p-4">
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search"
          className="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>
    </div>

    {/* Navigation */}
    <nav className="flex-1 px-4 pb-4 space-y-1 overflow-y-auto">
      {navigation.map((item) => (
        <Link
          key={item.name}
          href={item.href}
          className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
            isActive(item.href)
              ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
          }`}
        >
          <item.icon className="mr-3 w-5 h-5" />
          {item.name}
          {item.badge && (
            <span className="ml-auto inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-full">
              {item.badge}
            </span>
          )}
        </Link>
      ))}
    </nav>

    {/* Secondary navigation */}
    <div className="px-4 pb-4">
      <div className="space-y-1">
        {secondaryNavigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
              isActive(item.href)
                ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            <item.icon className="mr-3 w-5 h-5" />
            {item.name}
          </Link>
        ))}
      </div>

      {/* Usage Stats */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-900 dark:text-white">Used space</span>
          <span className="text-sm text-gray-500 dark:text-gray-400">80%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
          <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '80%' }}></div>
        </div>
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Your team has used 80% of your available space. Need more?
        </p>
        <div className="mt-3 flex space-x-2">
          <button className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline">
            Dismiss
          </button>
          <button className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline">
            Upgrade plan
          </button>
        </div>
      </div>

      {/* User Profile */}
      <div className="mt-4 flex items-center p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
        <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
          <span className="text-white font-medium text-sm">OR</span>
        </div>
        <div className="ml-3 flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
            Olivia Rhye
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
            olivia@untitledui.com
          </p>
        </div>
      </div>
    </div>
  </div>
);

export default Header;
