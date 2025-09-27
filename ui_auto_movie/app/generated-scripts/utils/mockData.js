// Mock data generator for scripts
export const generateMockScripts = () => {
  const statuses = ['draft', 'script_ready', 'social_media_pending', 'social_media_ready', 'voiceover_pending', 'voiceover_ready', 'video_pending', 'video_ready'];
  const scriptTypes = ['short', 'medium', 'long', 'educational', 'storytelling'];
  const topics = [
    'AI in Healthcare', 'Climate Change Solutions', 'Space Exploration', 'Renewable Energy',
    'Mental Health Awareness', 'Future of Work', 'Digital Privacy', 'Ocean Conservation',
    'Educational Technology', 'Sustainable Agriculture', 'Virtual Reality Applications',
    'Blockchain Technology', 'Social Media Impact', 'Electric Vehicles', 'Remote Learning'
  ];

  return Array.from({ length: 25 }, (_, i) => ({
    id: `script_${i + 1}`,
    title: topics[i % topics.length],
    description: `Comprehensive script about ${topics[i % topics.length].toLowerCase()} covering key aspects and insights.`,
    script_type: scriptTypes[i % scriptTypes.length],
    status: statuses[i % statuses.length],
    duration_estimate: `${Math.floor(Math.random() * 8) + 1}-${Math.floor(Math.random() * 5) + 3} minutes`,
    word_count: Math.floor(Math.random() * 800) + 200,
    tags: ['trending', 'informative', 'engaging'].slice(0, Math.floor(Math.random() * 3) + 1),
    created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
    language: 'English',
    category: 'Technology',
    social_media_generated: Math.random() > 0.5,
    voiceover_generated: Math.random() > 0.7,
    video_generated: Math.random() > 0.8
  }));
};
