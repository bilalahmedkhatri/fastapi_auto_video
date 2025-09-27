'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useTheme } from '@/components/ThemeProvider';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'react-hot-toast';

export default function Profile() {
  const router = useRouter();
  const { theme: currentTheme, setTheme } = useTheme();
  const { isAuthenticated, isLoading: authLoading, user: authUser } = useAuth();
  const [profileData, setProfileData] = useState({
    // Personal Info
    name: '',
    email: '',
    avatar: '',
    bio: '',
    phone: '',
    
    // Preferences
    preferredLanguage: 'English',
    notificationEnabled: true,
    theme: 'light',
    
    // Professional Info
    company: '',
    jobTitle: '',
    website: '',
    
    // Social Media
    twitter: '',
    instagram: '',
    youtube: '',
    tiktok: '',
    
    // Additional Settings
    apiKey: '',
    storagePreference: 'cloud',
    downloadFormat: 'mp4',
    maxGenerationsPerMonth: 10
  });
  
  const [activeTab, setActiveTab] = useState('personal');
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [authChecking, setAuthChecking] = useState(true);
  
  // Protect the route
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      toast.error('Please login to access your Profile');
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);
  
  // Fetch user profile data
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await fetch('/api/auth/me', {
          credentials: 'include' // Include cookies for authentication
        });
        
        if (!response.ok) {
          if (response.status === 401) {
            router.push('/login');
            return;
          }
          throw new Error('Failed to fetch user data');
        }
        
        const userData = await response.json();
        
        // Set user's theme preference in the app
        if (userData.theme) {
          setTheme(userData.theme);
        }
        
        setProfileData({
          ...profileData,
          ...userData,
          // Convert any null values to empty strings for form fields
          name: userData.name || '',
          email: userData.email || '',
          avatar: userData.avatar || '',
          bio: userData.bio || '',
          phone: userData.phone || '',
          preferredLanguage: userData.preferredLanguage || 'English',
          notificationEnabled: userData.notificationEnabled !== false, // default to true
          theme: userData.theme || 'light',
          company: userData.company || '',
          jobTitle: userData.jobTitle || '',
          website: userData.website || '',
          twitter: userData.twitter || '',
          instagram: userData.instagram || '',
          youtube: userData.youtube || '',
          tiktok: userData.tiktok || '',
          apiKey: userData.apiKey || '',
          storagePreference: userData.storagePreference || 'cloud',
          downloadFormat: userData.downloadFormat || 'mp4',
          maxGenerationsPerMonth: userData.maxGenerationsPerMonth || 10
        });
        setAuthChecking(false);
      } catch (error) {
        console.error('Error fetching user profile:', error);
        setAuthChecking(false);
      }
    };
    
    fetchUserData();
  }, [router, setTheme]);
  
  // Initialize form data when editing starts
  useEffect(() => {
    if (isEditing) {
      setFormData({
        ...profileData,
        // Use the current active theme from context to ensure radio buttons reflect actual state
        theme: currentTheme
      });
    }
  }, [isEditing, profileData, currentTheme]);
  
  // Auto-dismiss notification after 5 seconds
  useEffect(() => {
    if (message.text) {
      const timer = setTimeout(() => {
        setMessage({ type: '', text: '' });
      }, 5000);
      
      // Clean up timer on component unmount or when message changes
      return () => clearTimeout(timer);
    }
  }, [message.text]);
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    // Update form data
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // If the theme is changed, update it immediately for a better user experience
    if (name === 'theme') {
      // Apply theme immediately for preview, even in edit mode
      setTheme(value);
      
      console.log('Theme changed to:', value);
    }
  };
  
  const handleMultiSelect = (option, category) => {
    setFormData(prev => {
      const current = [...(prev[category] || [])];
      
      if (current.includes(option)) {
        return {
          ...prev,
          [category]: current.filter(item => item !== option)
        };
      } else {
        return {
          ...prev,
          [category]: [...current, option]
        };
      }
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ type: '', text: '' });
    
    try {
      const response = await fetch('/api/profile/update', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
        credentials: 'include' // Include cookies for authentication
      });
      
      if (!response.ok) {
        throw new Error('Failed to update profile');
      }
      
      const data = await response.json();
      
      // Update profile data
      setProfileData({
        ...profileData,
        ...data.user
      });
      
      // Make sure the theme is applied correctly
      if (data.user.theme) {
        setTheme(data.user.theme);
      }
      
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating profile:', error);
      setMessage({ type: 'error', text: 'Failed to update profile. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center transition-colors duration-200">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading your profile...</p>
        </div>
      </div>
    );
  }

  // Don't render anything if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200">
      {/* Fixed position notification */}
      {message.text && (
        <div className={`fixed bottom-5 left-5 z-50 p-4 rounded-md shadow-lg max-w-md animate-fade-in ${
          message.type === 'success' 
            ? 'bg-green-50 border border-green-200 text-green-800' 
            : 'bg-red-50 border border-red-200 text-red-800'
        }`}>
          <div className="flex items-center">
            {message.type === 'success' ? (
              <svg className="h-5 w-5 text-green-400 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="h-5 w-5 text-red-400 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            )}
            <span>{message.text}</span>
          </div>
        </div>
      )}
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="flex flex-col md:flex-row">
              {/* Left sidebar */}
              <div className="w-full md:w-1/4 bg-gray-50 p-6 border-r border-gray-200">
                <div className="flex flex-col items-center text-center mb-6">
                  <div className="relative w-24 h-24 rounded-full overflow-hidden bg-gray-300 mb-4">
                    {profileData.avatar ? (
                      <Image
                        src={profileData.avatar}
                        alt="Profile"
                        fill
                        className="object-cover"
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full bg-indigo-100 text-indigo-500">
                        <span className="text-2xl font-semibold">
                          {profileData.name?.charAt(0) || 'U'}
                        </span>
                      </div>
                    )}
                  </div>
                  <h2 className="text-xl font-semibold text-gray-900">{profileData.name}</h2>
                  <p className="text-gray-500 text-sm">{profileData.email}</p>
                </div>
                
                <nav className="space-y-1">
                  <button 
                    onClick={() => setActiveTab('personal')}
                    className={`w-full px-3 py-2 text-left rounded-md ${
                      activeTab === 'personal' 
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Personal Information
                  </button>
                  <button 
                    onClick={() => setActiveTab('preferences')}
                    className={`w-full px-3 py-2 text-left rounded-md ${
                      activeTab === 'preferences' 
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    App Preferences
                  </button>
                  <button 
                    onClick={() => setActiveTab('professional')}
                    className={`w-full px-3 py-2 text-left rounded-md ${
                      activeTab === 'professional' 
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Professional Info
                  </button>
                  <button 
                    onClick={() => setActiveTab('social')}
                    className={`w-full px-3 py-2 text-left rounded-md ${
                      activeTab === 'social' 
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Social Media
                  </button>
                  <button 
                    onClick={() => setActiveTab('settings')}
                    className={`w-full px-3 py-2 text-left rounded-md ${
                      activeTab === 'settings' 
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    Additional Settings
                  </button>
                </nav>
              </div>
              
              {/* Main content */}
              <div className="w-full md:w-3/4 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">
                    {activeTab === 'personal' && 'Personal Information'}
                    {activeTab === 'preferences' && 'App Preferences'}
                    {activeTab === 'professional' && 'Professional Information'}
                    {activeTab === 'social' && 'Social Media Profiles'}
                    {activeTab === 'settings' && 'Additional Settings'}
                  </h2>
                  
                  {!isEditing ? (
                    <button
                      onClick={() => setIsEditing(true)}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                    >
                      Edit
                    </button>
                  ) : (
                    <div className="flex space-x-3">
                      <button
                        onClick={() => setIsEditing(false)}
                        className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleSubmit}
                        disabled={isLoading}
                        className="px-4 py-2 bg-indigo-600 text-white roundu have Node.js and npm properly configured), you would use:
                        
                        ed-md hover:bg-indigo-700 disabled:opacity-70"
                      >
                        {isLoading ? 'Saving...' : 'Save Changes'}
                      </button>
                    </div>
                  )}
                </div>
                
                {/* Notification moved to a fixed position component at the bottom of the page */}
                
                <form onSubmit={handleSubmit}>
                  {/* Personal Information */}
                  {activeTab === 'personal' && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="name" className="block text-sm font-medium text-gray-700">Full Name</label>
                          <input
                            id="name"
                            name="name"
                            type="text"
                            className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            value={isEditing ? formData.name : profileData.name}
                            onChange={handleChange}
                            disabled={!isEditing}
                          />
                        </div>
                        <div>
                          <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
                          <input
                            id="email"
                            name="email"
                            type="email"
                            className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            value={isEditing ? formData.email : profileData.email}
                            onChange={handleChange}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label htmlFor="bio" className="block text-sm font-medium text-gray-700">Bio</label>
                        <textarea
                          id="bio"
                          name="bio"
                          rows={3}
                          className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                          value={isEditing ? formData.bio : profileData.bio}
                          onChange={handleChange}
                          disabled={!isEditing}
                        />
                      </div>
                      {/* Description template moved to social media tab */}
                      
                      <div>
                        <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Phone Number</label>
                        <input
                          id="phone"
                          name="phone"
                          type="tel"
                          className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                          value={isEditing ? formData.phone : profileData.phone}
                          onChange={handleChange}
                          disabled={!isEditing}
                        />
                      </div>
                      
                      {isEditing && (
                        <div>
                          <label htmlFor="avatar" className="block text-sm font-medium text-gray-700">Profile Picture URL</label>
                          <input
                            id="avatar"
                            name="avatar"
                            type="text"
                            placeholder="https://example.com/avatar.jpg"
                            className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            value={formData.avatar || ''}
                            onChange={handleChange}
                          />
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* App Preferences */}
                  {activeTab === 'preferences' && (
                    <div className="space-y-4">
                      <div>
                        <label htmlFor="preferredLanguage" className="block text-sm font-medium text-gray-700">Preferred Language</label>
                        <select
                          id="preferredLanguage"
                          name="preferredLanguage"
                          className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                          value={isEditing ? formData.preferredLanguage : profileData.preferredLanguage}
                          onChange={handleChange}
                          disabled={!isEditing}
                        >
                          <option value="English">English</option>
                          <option value="Spanish">Spanish</option>
                          <option value="French">French</option>
                          <option value="German">German</option>
                          <option value="Chinese">Chinese</option>
                          <option value="Japanese">Japanese</option>
                        </select>
                      </div>
                      
                      <div className="flex items-center">
                        <input
                          id="notificationEnabled"
                          name="notificationEnabled"
                          type="checkbox"
                          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                          checked={isEditing ? formData.notificationEnabled : profileData.notificationEnabled}
                          onChange={handleChange}
                          disabled={!isEditing}
                        />
                        <label htmlFor="notificationEnabled" className="ml-2 block text-sm text-gray-700">
                          Enable Notifications
                        </label>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Theme</label>
                        <div className="mt-2 space-x-4 flex items-center">
                          <div className="flex items-center">
                            <input
                              id="theme-light"
                              name="theme"
                              type="radio"
                              value="light"
                              className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"
                              checked={isEditing ? (formData.theme === 'light') : (currentTheme === 'light')}
                              onChange={handleChange}
                              disabled={!isEditing}
                            />
                            <label htmlFor="theme-light" className="ml-2 block text-sm text-gray-700">
                              Light
                            </label>
                          </div>
                          <div className="flex items-center">
                            <input
                              id="theme-dark"
                              name="theme"
                              type="radio"
                              value="dark"
                              className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"
                              checked={isEditing ? (formData.theme === 'dark') : (currentTheme === 'dark')}
                              onChange={handleChange}
                              disabled={!isEditing}
                            />
                            <label htmlFor="theme-dark" className="ml-2 block text-sm text-gray-700">
                              Dark
                            </label>
                          </div>
                          <div className="flex items-center">
                            <input
                              id="theme-advanced-dark"
                              name="theme"
                              type="radio"
                              value="advanced-dark"
                              className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"
                              checked={isEditing ? (formData.theme === 'advanced-dark') : (currentTheme === 'advanced-dark')}
                              onChange={handleChange}
                              disabled={!isEditing}
                            />
                            <label htmlFor="theme-advanced-dark" className="ml-2 block text-sm text-gray-700">
                              Advanced Dark
                            </label>
                          </div>
                          <div className="flex items-center">
                            <input
                              id="theme-modern-dark"
                              name="theme"
                              type="radio"
                              value="modern-dark"
                              className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"
                              checked={isEditing ? (formData.theme === 'modern-dark') : (currentTheme === 'modern-dark')}
                              onChange={handleChange}
                              disabled={!isEditing}
                            />
                            <label htmlFor="theme-modern-dark" className="ml-2 block text-sm text-gray-700">
                              Modern Dark
                            </label>
                          </div>
                          <div className="flex items-center">
                            <input
                              id="theme-system"
                              name="theme"
                              type="radio"
                              value="system"
                              className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"
                              checked={isEditing ? (formData.theme === 'system') : (currentTheme === 'system')}
                              onChange={handleChange}
                              disabled={!isEditing}
                            />
                            <label htmlFor="theme-system" className="ml-2 block text-sm text-gray-700">
                              System Default
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Video Preferences section removed - now in Create Video page */}
                  
                  {/* Professional Info */}
                  {activeTab === 'professional' && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="company" className="block text-sm font-medium text-gray-700">Company</label>
                          <input
                            id="company"
                            name="company"
                            type="text"
                            className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            value={isEditing ? formData.company : profileData.company}
                            onChange={handleChange}
                            disabled={!isEditing}
                          />
                        </div>
                        <div>
                          <label htmlFor="jobTitle" className="block text-sm font-medium text-gray-700">Job Title</label>
                          <input
                            id="jobTitle"
                            name="jobTitle"
                            type="text"
                            className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                            value={isEditing ? formData.jobTitle : profileData.jobTitle}
                            onChange={handleChange}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label htmlFor="website" className="block text-sm font-medium text-gray-700">Website</label>
                        <input
                          id="website"
                          name="website"
                          type="url"
                          placeholder="https://example.com"
                          className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                          value={isEditing ? formData.website : profileData.website}
                          onChange={handleChange}
                          disabled={!isEditing}
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Social Media */}
                  {activeTab === 'social' && (
                    <div className="space-y-4">
                      <div>
                        <label htmlFor="twitter" className="block text-sm font-medium text-gray-700">Twitter Username</label>
                        <div className="mt-1 flex rounded-md shadow-sm">
                          <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm">
                            @
                          </span>
                          <input
                            type="text"
                            name="twitter"
                            id="twitter"
                            className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="username"
                            value={isEditing ? formData.twitter : profileData.twitter}
                            onChange={handleChange}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label htmlFor="instagram" className="block text-sm font-medium text-gray-700">Instagram Username</label>
                        <div className="mt-1 flex rounded-md shadow-sm">
                          <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm">
                            @
                          </span>
                          <input
                            type="text"
                            name="instagram"
                            id="instagram"
                            className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="username"
                            value={isEditing ? formData.instagram : profileData.instagram}
                            onChange={handleChange}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label htmlFor="youtube" className="block text-sm font-medium text-gray-700">YouTube Channel</label>
                        <input
                          type="text"
                          name="youtube"
                          id="youtube"
                          className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                          placeholder="https://youtube.com/c/yourchannel"
                          value={isEditing ? formData.youtube : profileData.youtube}
                          onChange={handleChange}
                          disabled={!isEditing}
                        />
                      </div>
                      
                      <div>
                        <label htmlFor="tiktok" className="block text-sm font-medium text-gray-700">TikTok Username</label>
                        <div className="mt-1 flex rounded-md shadow-sm">
                          <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm">
                            @
                          </span>
                          <input
                            type="text"
                            name="tiktok"
                            id="tiktok"
                            className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="username"
                            value={isEditing ? formData.tiktok : profileData.tiktok}
                            onChange={handleChange}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>

                      <div className="pt-5 border-t border-gray-200">
                        <label htmlFor="descriptionTemplate" className="block text-sm font-medium text-gray-700">Youtube Description Template</label>
                        <textarea
                          id="descriptionTemplate"
                          name="descriptionTemplate"
                          rows={4}
                          className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                          value={isEditing ? formData.descriptionTemplate : profileData.descriptionTemplate}
                          onChange={handleChange}
                          disabled={!isEditing}
                          placeholder="e.g. This video was generated using AI with the following prompt: {prompt}"
                        />
                        <p className="text-xs text-gray-500 mt-1">You can use <code>{'{prompt}'}</code> as a placeholder for the video prompt.</p>
                      </div>
                    </div>
                  )}
                  
                  {/* Additional Settings */}
                  {activeTab === 'settings' && (
                    <div className="space-y-4">
                      <div>
                        <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700">API Key</label>
                        <input
                          id="apiKey"
                          name="apiKey"
                          type="password"
                          className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                          value={isEditing ? formData.apiKey : profileData.apiKey}
                          onChange={handleChange}
                          disabled={!isEditing}
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Storage Preference</label>
                        <div className="mt-2 space-x-4 flex items-center">
                          <div className="flex items-center">
                            <input
                              id="storage-cloud"
                              name="storagePreference"
                              type="radio"
                              value="cloud"
                              className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"
                              checked={(isEditing ? formData.storagePreference : profileData.storagePreference) === 'cloud'}
                              onChange={handleChange}
                              disabled={!isEditing}
                            />
                            <label htmlFor="storage-cloud" className="ml-2 block text-sm text-gray-700">
                              Cloud
                            </label>
                          </div>
                          <div className="flex items-center">
                            <input
                              id="storage-local"
                              name="storagePreference"
                              type="radio"
                              value="local"
                              className="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"
                              checked={(isEditing ? formData.storagePreference : profileData.storagePreference) === 'local'}
                              onChange={handleChange}
                              disabled={!isEditing}
                            />
                            <label htmlFor="storage-local" className="ml-2 block text-sm text-gray-700">
                              Local
                            </label>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <label htmlFor="downloadFormat" className="block text-sm font-medium text-gray-700">Download Format</label>
                        <select
                          id="downloadFormat"
                          name="downloadFormat"
                          className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                          value={isEditing ? formData.downloadFormat : profileData.downloadFormat}
                          onChange={handleChange}
                          disabled={!isEditing}
                        >
                          <option value="mp4">MP4</option>
                          <option value="mov">MOV</option>
                          <option value="avi">AVI</option>
                          <option value="webm">WebM</option>
                        </select>
                      </div>
                      
                      <div>
                        <label htmlFor="maxGenerationsPerMonth" className="block text-sm font-medium text-gray-700">Max Generations Per Month</label>
                        <input
                          id="maxGenerationsPerMonth"
                          name="maxGenerationsPerMonth"
                          type="number"
                          min="1"
                          max="100"
                          className="mt-1 block w-full px-3 py-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                          value={isEditing ? formData.maxGenerationsPerMonth : profileData.maxGenerationsPerMonth}
                          onChange={handleChange}
                          disabled={!isEditing}
                        />
                      </div>
                    </div>
                  )}
                </form>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
