"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Play, CheckCircle } from 'lucide-react';
import VoiceService from '@/lib/voice-service';

const VoicePicker = ({ 
  onVoiceSelect, 
  selectedVoice = null, 
  filters = {},
  className = "" 
}) => {
  const [voices, setVoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadVoices = async () => {
      try {
        setLoading(true);
        const data = await VoiceService.getVoices(filters);
        setVoices(data.voices || []);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadVoices();
  }, [filters]);

  const playVoiceSample = async (voice) => {
    try {
      if (voice.sample_url) {
        const audio = new Audio(`http://localhost:8000${voice.sample_url}`);
        await audio.play();
      }
    } catch (error) {
      console.error('Error playing voice sample:', error);
    }
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="text-center text-red-600">
            <p>Error loading voices: {error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Select Voice ({voices.length} available)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {voices.map((voice) => (
            <div
              key={voice.voice_id}
              className={`p-3 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                selectedVoice?.voice_id === voice.voice_id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => onVoiceSelect(voice)}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-sm">{voice.name}</h3>
                <div className="flex gap-1">
                  {voice.sample_url && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={(e) => {
                        e.stopPropagation();
                        playVoiceSample(voice);
                      }}
                    >
                      <Play className="w-3 h-3" />
                    </Button>
                  )}
                  {selectedVoice?.voice_id === voice.voice_id && (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  )}
                </div>
              </div>
              
              <div className="flex flex-wrap gap-1 mb-2">
                <Badge variant="secondary" className="text-xs">
                  {voice.gender}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {voice.accent.replace('_', ' ')}
                </Badge>
              </div>
              
              <p className="text-xs text-gray-600 line-clamp-2">
                {voice.description}
              </p>
            </div>
          ))}
        </div>
        
        {voices.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <p>No voices found matching the current filters.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default VoicePicker;
