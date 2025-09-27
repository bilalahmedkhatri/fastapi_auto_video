"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Play, Pause, Download, Trash2, Clock, FileAudio, User, Calendar } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const VoiceoverHistory = ({ userId }) => {
  const [voiceovers, setVoiceovers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [playingId, setPlayingId] = useState(null);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const { toast } = useToast();

  const perPage = 10;

  useEffect(() => {
    if (userId) {
      fetchVoiceovers();
    }
  }, [userId, page]);

  const fetchVoiceovers = async () => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams({
        user_id: userId,
        page: page.toString(),
        per_page: perPage.toString()
      });
      
      const response = await fetch(`http://localhost:8000/api/voiceovers?${queryParams}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setVoiceovers(data.voiceovers || []);
      setTotal(data.total || 0);
      
    } catch (error) {
      console.error('Error fetching voiceovers:', error);
      toast({
        title: "Error",
        description: `Failed to load voiceover history: ${error.message}`,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const playVoiceover = async (voiceover) => {
    try {
      // Stop any currently playing audio
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        setCurrentAudio(null);
        setPlayingId(null);
      }

      if (playingId === voiceover.id) {
        return; // Already stopped
      }

      setPlayingId(voiceover.id);
      
      // Create new audio element
      const audio = new Audio();
      
      // Handle audio events
      audio.addEventListener('loadstart', () => {
        console.log('Loading voiceover:', voiceover.file_url);
      });
      
      audio.addEventListener('canplaythrough', () => {
        audio.play().catch(error => {
          console.error('Playback failed:', error);
          setPlayingId(null);
          toast({
            title: "Playback Error",
            description: "Failed to play the voiceover",
            variant: "destructive"
          });
        });
      });
      
      audio.addEventListener('ended', () => {
        setPlayingId(null);
        setCurrentAudio(null);
      });
      
      audio.addEventListener('error', (e) => {
        console.error('Audio error:', e);
        setPlayingId(null);
        setCurrentAudio(null);
        toast({
          title: "Audio Error",
          description: "Failed to load the voiceover file",
          variant: "destructive"
        });
      });
      
      setCurrentAudio(audio);
      
      // Set the source with proper CORS handling
      const audioUrl = `http://localhost:8000${voiceover.file_url}`;
      audio.crossOrigin = "anonymous";
      audio.src = audioUrl;
      
    } catch (error) {
      console.error('Error playing voiceover:', error);
      setPlayingId(null);
      toast({
        title: "Playback Error",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const stopPlayback = () => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
      setPlayingId(null);
    }
  };

  const deleteVoiceover = async (voiceoverId) => {
    if (!confirm('Are you sure you want to delete this voiceover?')) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8000/api/voiceovers/${voiceoverId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Refresh the list
      await fetchVoiceovers();
      
      toast({
        title: "Success",
        description: "Voiceover deleted successfully",
      });
      
    } catch (error) {
      console.error('Error deleting voiceover:', error);
      toast({
        title: "Error",
        description: `Failed to delete voiceover: ${error.message}`,
        variant: "destructive"
      });
    }
  };

  const downloadVoiceover = (voiceover) => {
    const audioUrl = `http://localhost:8000${voiceover.file_url}`;
    const link = document.createElement('a');
    link.href = audioUrl;
    link.download = voiceover.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'Unknown';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading voiceover history...</span>
      </div>
    );
  }

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Voiceover History</h2>
        <Badge variant="outline">
          {total} {total === 1 ? 'voiceover' : 'voiceovers'}
        </Badge>
      </div>

      {voiceovers.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <FileAudio className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No voiceovers yet</h3>
            <p className="text-gray-600">Your generated voiceovers will appear here.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {voiceovers.map((voiceover) => (
            <Card key={voiceover.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {voiceover.voice_name}
                      </h3>
                      <Badge variant="secondary">
                        {voiceover.voice_id}
                      </Badge>
                      {voiceover.status === 'completed' ? (
                        <Badge variant="default" className="bg-green-100 text-green-800">
                          Completed
                        </Badge>
                      ) : (
                        <Badge variant="destructive">
                          {voiceover.status}
                        </Badge>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {voiceover.text_content}
                    </p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(voiceover.created_at)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Clock className="h-4 w-4" />
                        <span>{formatDuration(voiceover.duration_seconds)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <FileAudio className="h-4 w-4" />
                        <span>{formatFileSize(voiceover.file_size)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <User className="h-4 w-4" />
                        <span>{voiceover.ai_provider || 'Unknown'}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    {playingId === voiceover.id ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={stopPlayback}
                        className="flex items-center space-x-1"
                      >
                        <Pause className="h-4 w-4" />
                        <span>Stop</span>
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => playVoiceover(voiceover)}
                        className="flex items-center space-x-1"
                      >
                        <Play className="h-4 w-4" />
                        <span>Play</span>
                      </Button>
                    )}
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadVoiceover(voiceover)}
                      className="flex items-center space-x-1"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteVoiceover(voiceover.id)}
                      className="flex items-center space-x-1 text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Showing {((page - 1) * perPage) + 1} to {Math.min(page * perPage, total)} of {total} voiceovers
          </p>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page - 1)}
              disabled={page <= 1}
            >
              Previous
            </Button>
            <span className="text-sm font-medium">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceoverHistory;
