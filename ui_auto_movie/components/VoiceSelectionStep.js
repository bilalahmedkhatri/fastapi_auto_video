"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Play, Pause, RotateCcw, CheckCircle, Volume2, Settings } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const VoiceSelectionStep = ({ 
  scriptData, 
  onNext, 
  onBack,
  userId = "test_user_123" 
}) => {
  const { toast } = useToast();
  const [voices, setVoices] = useState([]);
  const [filteredVoices, setFilteredVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [audioSettings, setAudioSettings] = useState({
    speed: 1.0,
    pitch: 0,
    tone: 'neutral',
    volume: 1.0
  });
  const [backgroundMusic, setBackgroundMusic] = useState({
    enabled: false,
    music_type: 'upbeat',
    volume: 0.3
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedAudio, setGeneratedAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [filters, setFilters] = useState({
    gender: '',
    accent: '',
    style: ''
  });
  const [showSettings, setShowSettings] = useState(false);
  
  const audioRef = useRef(null);

  // Voice filter options
  const filterOptions = {
    gender: ['male', 'female'],
    accent: ['American_English', 'British_English', 'Spanish', 'French', 'Japanese'],
    style: ['neutral', 'excited', 'calm', 'professional', 'friendly']
  };

  // Music type options
  const musicTypes = ['upbeat', 'calm', 'dramatic', 'corporate', 'tech', 'nature'];

  // Load available voices
  useEffect(() => {
    const loadVoices = async () => {
      try {
        const queryParams = new URLSearchParams();
        if (filters.gender) queryParams.append('gender', filters.gender);
        if (filters.accent) queryParams.append('accent', filters.accent);
        if (filters.style) queryParams.append('style', filters.style);
        
        const response = await fetch(`http://localhost:8000/api/voice/voices?${queryParams}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.voices && Array.isArray(data.voices)) {
          setVoices(data.voices);
          setFilteredVoices(data.voices);
          
          // Auto-select first voice if none selected
          if (!selectedVoice && data.voices.length > 0) {
            setSelectedVoice(data.voices[0]);
          }
        } else {
          throw new Error('Invalid response format from voices API');
        }
      } catch (error) {
        console.error('Error loading voices:', error);
        toast({
          title: "Error",
          description: `Failed to load available voices: ${error.message}`,
          variant: "destructive"
        });
      }
    };

    loadVoices();
  }, [filters]);

  // Play voice sample
  const playVoiceSample = async (voice) => {
    try {
      if (voice.sample_url) {
        const audio = new Audio(`http://localhost:8000${voice.sample_url}`);
        await audio.play();
      } else {
        toast({
          title: "No Sample Available",
          description: "This voice doesn't have a preview sample",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('Error playing voice sample:', error);
      toast({
        title: "Playback Error",
        description: "Failed to play voice sample",
        variant: "destructive"
      });
    }
  };

  // Generate voiceover
  const generateVoiceover = async () => {
    if (!selectedVoice || !scriptData) return;

    setIsGenerating(true);
    try {
      const request = {
        script_id: scriptData.id || 'temp_script',
        text: scriptData.voiceover_script || scriptData.script,
        voice_id: selectedVoice.voice_id,
        audio_settings: audioSettings,
        background_music: backgroundMusic,
        user_id: userId
      };

      const response = await fetch('http://localhost:8000/api/voice/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request)
      });

      const result = await response.json();
      
      if (result.success) {
        setGeneratedAudio(result);
        toast({
          title: "Voiceover Generated",
          description: `Audio generated in ${result.generation_time?.toFixed(2)}s`,
          variant: "default"
        });
      } else {
        throw new Error(result.error_message || 'Generation failed');
      }
    } catch (error) {
      console.error('Error generating voiceover:', error);
      toast({
        title: "Generation Error",
        description: error.message || "Failed to generate voiceover",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
    }
  };

  // Play generated audio
  const playGeneratedAudio = () => {
    if (!generatedAudio || !audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.src = `http://localhost:8000${generatedAudio.audio_url}`;
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  // Handle audio ended
  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  // Proceed to next step
  const handleNext = () => {
    if (!generatedAudio) {
      toast({
        title: "Generate Voiceover First",
        description: "Please generate and verify your voiceover before proceeding",
        variant: "destructive"
      });
      return;
    }

    const voiceoverData = {
      voice: selectedVoice,
      audio_settings: audioSettings,
      background_music: backgroundMusic,
      generated_audio: generatedAudio,
      script_data: scriptData
    };

    onNext(voiceoverData);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Step 3: Voice Selection & Voiceover
          </h1>
          <p className="text-gray-600">
            Choose an AI voice and generate your voiceover with custom settings
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Voice Selection Panel */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Available Voices</CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowSettings(!showSettings)}
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Filters
                  </Button>
                </div>
                
                {/* Filters */}
                {showSettings && (
                  <div className="flex gap-4 pt-4 border-t">
                    <Select value={filters.gender} onValueChange={(value) => setFilters({...filters, gender: value})}>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">All</SelectItem>
                        {filterOptions.gender.map(option => (
                          <SelectItem key={option} value={option}>
                            {option.charAt(0).toUpperCase() + option.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <Select value={filters.accent} onValueChange={(value) => setFilters({...filters, accent: value})}>
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="Accent" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">All</SelectItem>
                        {filterOptions.accent.map(option => (
                          <SelectItem key={option} value={option}>
                            {option.replace('_', ' ')}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <Select value={filters.style} onValueChange={(value) => setFilters({...filters, style: value})}>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Style" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">All</SelectItem>
                        {filterOptions.style.map(option => (
                          <SelectItem key={option} value={option}>
                            {option.charAt(0).toUpperCase() + option.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredVoices.map((voice) => (
                    <div
                      key={voice.voice_id}
                      className={`p-4 border rounded-lg cursor-pointer transition-all ${
                        selectedVoice?.voice_id === voice.voice_id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedVoice(voice)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold">{voice.name}</h3>
                        {voice.sample_url && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              playVoiceSample(voice);
                            }}
                          >
                            <Play className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                      
                      <div className="flex gap-2 mb-2">
                        <Badge variant="secondary">{voice.gender}</Badge>
                        <Badge variant="outline">{voice.accent.replace('_', ' ')}</Badge>
                        <Badge variant="outline">{voice.style}</Badge>
                      </div>
                      
                      <p className="text-sm text-gray-600">{voice.description}</p>
                      
                      {selectedVoice?.voice_id === voice.voice_id && (
                        <div className="mt-2">
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Settings & Controls Panel */}
          <div className="space-y-6">
            {/* Audio Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Audio Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Speed: {audioSettings.speed}x
                  </label>
                  <Slider
                    value={[audioSettings.speed]}
                    onValueChange={([value]) => setAudioSettings({...audioSettings, speed: value})}
                    min={0.5}
                    max={2.0}
                    step={0.1}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Pitch: {audioSettings.pitch}
                  </label>
                  <Slider
                    value={[audioSettings.pitch]}
                    onValueChange={([value]) => setAudioSettings({...audioSettings, pitch: value})}
                    min={-20}
                    max={20}
                    step={1}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Volume: {audioSettings.volume}x
                  </label>
                  <Slider
                    value={[audioSettings.volume]}
                    onValueChange={([value]) => setAudioSettings({...audioSettings, volume: value})}
                    min={0.1}
                    max={2.0}
                    step={0.1}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Background Music */}
            <Card>
              <CardHeader>
                <CardTitle>Background Music</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="bgMusic"
                    checked={backgroundMusic.enabled}
                    onChange={(e) => setBackgroundMusic({...backgroundMusic, enabled: e.target.checked})}
                  />
                  <label htmlFor="bgMusic" className="text-sm font-medium">
                    Enable Background Music
                  </label>
                </div>

                {backgroundMusic.enabled && (
                  <>
                    <Select
                      value={backgroundMusic.music_type}
                      onValueChange={(value) => setBackgroundMusic({...backgroundMusic, music_type: value})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Music Type" />
                      </SelectTrigger>
                      <SelectContent>
                        {musicTypes.map(type => (
                          <SelectItem key={type} value={type}>
                            {type.charAt(0).toUpperCase() + type.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Music Volume: {backgroundMusic.volume}
                      </label>
                      <Slider
                        value={[backgroundMusic.volume]}
                        onValueChange={([value]) => setBackgroundMusic({...backgroundMusic, volume: value})}
                        min={0.1}
                        max={1.0}
                        step={0.1}
                      />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Generation Controls */}
            <Card>
              <CardHeader>
                <CardTitle>Generate Voiceover</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button
                  onClick={generateVoiceover}
                  disabled={!selectedVoice || isGenerating}
                  className="w-full"
                >
                  {isGenerating ? (
                    <>
                      <RotateCcw className="w-4 h-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-4 h-4 mr-2" />
                      Generate Voiceover
                    </>
                  )}
                </Button>

                {generatedAudio && (
                  <div className="space-y-2">
                    <div className="p-3 bg-green-50 border border-green-200 rounded">
                      <p className="text-sm text-green-800">
                        ✓ Voiceover generated successfully!
                      </p>
                      <p className="text-xs text-green-600">
                        Duration: ~{generatedAudio.duration?.toFixed(1)}s | 
                        Size: {(generatedAudio.file_size / 1024).toFixed(1)}KB
                      </p>
                    </div>
                    
                    <Button
                      onClick={playGeneratedAudio}
                      variant="outline"
                      className="w-full"
                    >
                      {isPlaying ? (
                        <>
                          <Pause className="w-4 h-4 mr-2" />
                          Pause Audio
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4 mr-2" />
                          Play Audio
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Script Preview */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Script Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-800">
                {scriptData?.voiceover_script || scriptData?.script || "No script available"}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <Button variant="outline" onClick={onBack}>
            Back to Script
          </Button>
          
          <Button onClick={handleNext} disabled={!generatedAudio}>
            Continue to Video Generation
          </Button>
        </div>

        {/* Hidden audio element for playback */}
        <audio
          ref={audioRef}
          onEnded={handleAudioEnded}
          style={{ display: 'none' }}
        />
      </div>
    </div>
  );
};

export default VoiceSelectionStep;
