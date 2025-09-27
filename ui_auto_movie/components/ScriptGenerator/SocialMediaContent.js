 'use client';

import React from 'react';
import { toast } from 'react-hot-toast';

const SocialMediaContent = ({
  socialMediaContent,
  loading,
  onRegenerateSocialMedia,
  onBackToScripts,
  onNext
}) => {
  if (!socialMediaContent) return null;

  const platformIcons = {
    youtube: '📺',
    instagram: '📸',
    tiktok: '🎵',
    linkedin: '💼',
    twitter: '🐦',
    facebook: '👥'
  };

  const platformColors = {
    youtube: 'border-red-500 bg-red-50 dark:bg-red-900/20 dark:border-red-400',
    instagram: 'border-pink-500 bg-pink-50 dark:bg-pink-900/20 dark:border-pink-400',
    tiktok: 'border-black bg-gray-50 dark:bg-gray-700 dark:border-gray-500',
    linkedin: 'border-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400',
    twitter: 'border-sky-500 bg-sky-50 dark:bg-sky-900/20 dark:border-sky-400',
    facebook: 'border-blue-800 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400'
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  // Export functions
  const exportToCSV = () => {
    if (!socialMediaContent.platform_descriptions) return;
    
    const csvContent = [
      ['Platform', 'Title', 'Description', 'Hashtags', 'SEO Keywords'],
      ...socialMediaContent.platform_descriptions.map(platform => [
        platform.platform,
        platform.title,
        platform.description.replace(/\n/g, ' '),
        platform.hashtags?.join(' ') || '',
        platform.seo_keywords?.join(', ') || ''
      ])
    ].map(row => row.map(field => `"${field}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `social-media-content-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success('CSV file downloaded!');
  };

  const exportToJSON = () => {
    const jsonContent = JSON.stringify(socialMediaContent, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `social-media-content-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success('JSON file downloaded!');
  };

  const copyAllContent = () => {
    if (!socialMediaContent.platform_descriptions) return;
    
    let allContent = `Social Media Content for: ${socialMediaContent.script_title}\n\n`;
    
    socialMediaContent.platform_descriptions.forEach(platform => {
      allContent += `=== ${platform.platform.toUpperCase()} ===\n`;
      allContent += `Title: ${platform.title}\n\n`;
      allContent += `Description:\n${platform.description}\n\n`;
      allContent += `Hashtags: ${platform.hashtags?.join(' ') || 'N/A'}\n\n`;
      allContent += `SEO Keywords: ${platform.seo_keywords?.join(', ') || 'N/A'}\n\n`;
      allContent += '---\n\n';
    });

    if (socialMediaContent.general_seo_keywords) {
      allContent += `General SEO Keywords: ${socialMediaContent.general_seo_keywords.join(', ')}\n\n`;
    }

    if (socialMediaContent.trending_hashtags) {
      allContent += `Trending Hashtags: ${socialMediaContent.trending_hashtags.join(' ')}\n`;
    }

    navigator.clipboard.writeText(allContent);
    toast.success('All content copied to clipboard!');
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          📱 Social Media Content
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-2">
          Platform-optimized descriptions for: <span className="font-semibold">{socialMediaContent.script_title}</span>
        </p>
        <span className="inline-block bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-3 py-1 rounded-full text-sm">
          {socialMediaContent.script_type}
        </span>
      </div>

      {/* Platform Descriptions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {socialMediaContent.platform_descriptions?.map((platform, index) => (
          <div
            key={index}
            className={`p-6 border-2 rounded-xl ${platformColors[platform.platform] || 'border-gray-200 bg-gray-50 dark:border-gray-600 dark:bg-gray-700'}`}
          >
            <div className="flex items-center mb-4">
              <span className="text-3xl mr-3">
                {platformIcons[platform.platform] || '📱'}
              </span>
              <h3 className="text-xl font-bold capitalize text-gray-900 dark:text-gray-100">
                {platform.platform}
              </h3>
            </div>
            
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-semibold text-gray-800 dark:text-gray-200">Title:</h4>
                <button
                  onClick={() => copyToClipboard(platform.title)}
                  className="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 text-sm"
                >
                  📋 Copy
                </button>
              </div>
              <p className="text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-600 p-3 rounded-lg border dark:border-gray-500">
                {platform.title}
              </p>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-semibold text-gray-800 dark:text-gray-200">Description:</h4>
                <button
                  onClick={() => copyToClipboard(platform.description)}
                  className="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 text-sm"
                >
                  📋 Copy
                </button>
              </div>
              <div className="text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-600 p-3 rounded-lg border dark:border-gray-500 max-h-32 overflow-y-auto">
                <p className="whitespace-pre-wrap">{platform.description}</p>
              </div>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-semibold text-gray-800 dark:text-gray-200">Hashtags:</h4>
                <button
                  onClick={() => copyToClipboard(platform.hashtags?.join(' ') || '')}
                  className="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 text-sm"
                >
                  📋 Copy All
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {platform.hashtags?.map((tag, tagIndex) => (
                  <span
                    key={tagIndex}
                    className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-2 py-1 rounded text-sm cursor-pointer hover:bg-blue-200 dark:hover:bg-blue-800/50"
                    onClick={() => copyToClipboard(tag)}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">SEO Keywords:</h4>
              <div className="flex flex-wrap gap-2">
                {platform.seo_keywords?.map((keyword, kwIndex) => (
                  <span
                    key={kwIndex}
                    className="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 px-2 py-1 rounded text-sm"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Thumbnail Suggestions */}
      {socialMediaContent.thumbnail_suggestions && (
        <div className="mb-8">
          <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">
            🖼️ Thumbnail Suggestions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {socialMediaContent.thumbnail_suggestions.map((thumbnail, index) => (
              <div
                key={index}
                className="p-4 border-2 border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 hover:shadow-lg transition-all"
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-gray-800 dark:text-gray-200">{thumbnail.title}</h4>
                  <button
                    onClick={() => copyToClipboard(thumbnail.title)}
                    className="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 text-xs"
                  >
                    📋
                  </button>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{thumbnail.style}</p>
                
                <div className="mb-3">
                  <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Elements:</p>
                  <div className="flex flex-wrap gap-1">
                    {thumbnail.elements?.map((element, elIndex) => (
                      <span key={elIndex} className="bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300 px-2 py-1 rounded text-xs">
                        {element}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Colors:</p>
                  <div className="flex gap-2">
                    {thumbnail.colors?.map((color, colorIndex) => (
                      <div
                        key={colorIndex}
                        className="w-6 h-6 rounded border border-gray-300 dark:border-gray-500"
                        style={{ backgroundColor: color }}
                        title={color}
                      ></div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SEO Keywords and Trending Hashtags */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="p-6 border-2 border-green-200 dark:border-green-600 rounded-xl bg-green-50 dark:bg-green-900/20">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-green-800 dark:text-green-300">
              🔍 General SEO Keywords
            </h3>
            <button
              onClick={() => copyToClipboard(socialMediaContent.general_seo_keywords?.join(', ') || '')}
              className="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300 text-sm"
            >
              📋 Copy All
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {socialMediaContent.general_seo_keywords?.map((keyword, index) => (
              <span
                key={index}
                className="bg-green-200 dark:bg-green-800/50 text-green-800 dark:text-green-300 px-3 py-1 rounded-full text-sm font-medium cursor-pointer hover:bg-green-300 dark:hover:bg-green-700/50"
                onClick={() => copyToClipboard(keyword)}
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>

        <div className="p-6 border-2 border-purple-200 dark:border-purple-600 rounded-xl bg-purple-50 dark:bg-purple-900/20">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-purple-800 dark:text-purple-300">
              🔥 Trending Hashtags
            </h3>
            <button
              onClick={() => copyToClipboard(socialMediaContent.trending_hashtags?.join(' ') || '')}
              className="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300 text-sm"
            >
              📋 Copy All
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {socialMediaContent.trending_hashtags?.map((hashtag, index) => (
              <span
                key={index}
                className="bg-purple-200 dark:bg-purple-800/50 text-purple-800 dark:text-purple-300 px-3 py-1 rounded-full text-sm font-medium cursor-pointer hover:bg-purple-300 dark:hover:bg-purple-700/50"
                onClick={() => copyToClipboard(hashtag)}
              >
                {hashtag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Content Export and Publishing Options */}
      <div className="mb-8 p-6 border-2 border-blue-200 dark:border-blue-600 rounded-xl bg-blue-50 dark:bg-blue-900/20">
        <h3 className="text-xl font-bold text-blue-800 dark:text-blue-300 mb-4">
          📤 Export & Publishing Tools
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => exportToCSV()}
            className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-all flex items-center justify-center"
          >
            📊 Export to CSV
          </button>
          <button
            onClick={() => exportToJSON()}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-all flex items-center justify-center"
          >
            📄 Export to JSON
          </button>
          <button
            onClick={() => copyAllContent()}
            className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition-all flex items-center justify-center"
          >
            📋 Copy All Content
          </button>
        </div>
        
        <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-600">
          <h4 className="font-semibold text-yellow-800 dark:text-yellow-300 mb-2">💡 Publishing Tips:</h4>
          <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
            <li>• Best posting times: 2-4 PM for most platforms</li>
            <li>• Use 3-5 hashtags for Instagram, 1-2 for Twitter</li>
            <li>• Include a call-to-action in your descriptions</li>
            <li>• Engage with comments within the first hour of posting</li>
          </ul>
        </div>
      </div>

      {/* Performance Analytics Placeholder */}
      <div className="mb-8 p-6 border-2 border-gray-200 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-800">
        <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          📈 Content Performance Tracking
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">0</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Posts Created</div>
          </div>
          <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">0</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Content Copied</div>
          </div>
          <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">6</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Platforms Ready</div>
          </div>
          <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">100%</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Optimization</div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="text-center space-x-4">
        <button
          onClick={onRegenerateSocialMedia}
          disabled={loading}
          className="bg-gradient-to-r from-pink-500 to-red-600 text-white px-6 py-2 rounded-lg hover:from-pink-600 hover:to-red-700 transition-all"
        >
          {loading ? 'Regenerating...' : '🔄 Regenerate'}
        </button>
        <button
          onClick={onBackToScripts}
          className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-all"
        >
          ← Back to Scripts
        </button>
        <button
          onClick={onNext}
          className="bg-gradient-to-r from-green-500 to-blue-600 text-white px-6 py-2 rounded-lg hover:from-green-600 hover:to-blue-700 transition-all"
        >
          Next: Media Manager 🎬
        </button>
      </div>
    </div>
  );
};

export default SocialMediaContent;