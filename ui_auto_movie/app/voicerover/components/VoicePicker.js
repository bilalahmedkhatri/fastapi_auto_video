"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Play, Pause, CheckCircle, AlertCircle } from 'lucide-react';

const VoicePicker = ({ 
  voices, 
  selectedVoice, 
  onSelectVoice, 
  onPlaySample, 
  playingVoice, 
  onStopAudio,
  className = "" 
}) => {
  if (!voices || voices.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p>No voices available matching your filters</p>
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 ${className}`}>
      {voices.map((voice) => (
        <Card 
          key={voice.voice_id} 
          className={`cursor-pointer transition-all hover:shadow-md ${
            selectedVoice?.voice_id === voice.voice_id 
              ? 'ring-2 ring-blue-500 dark:ring-blue-400' 
              : ''
          }`}
          onClick={() => onSelectVoice(voice)}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                {voice.name}
              </h3>
              {selectedVoice?.voice_id === voice.voice_id && (
                <CheckCircle className="h-5 w-5 text-blue-500 dark:text-blue-400" />
              )}
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {voice.description}
            </p>
            
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                <Badge variant="outline" className="text-xs">
                  {voice.gender}
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  {voice.style}
                </Badge>
                {voice.accent && (
                  <Badge variant="outline" className="text-xs">
                    {voice.accent.replace('_', ' ')}
                  </Badge>
                )}
              </div>
              
              {voice.sample_url ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (playingVoice === voice.voice_id) {
                      onStopAudio();
                    } else {
                      onPlaySample(voice);
                    }
                  }}
                >
                  {playingVoice === voice.voice_id ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
              ) : (
                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  No sample
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default VoicePicker;
