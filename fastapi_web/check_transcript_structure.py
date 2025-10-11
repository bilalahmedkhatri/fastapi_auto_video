"""
Quick diagnostic to check transcript structure in database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.db_models import get_session, VideoGenerationProcess
from sqlalchemy import desc
import json

def check_latest_videos():
    """Check the latest video processes in database for transcript structure"""
    session = next(get_session())
    
    # Get latest 3 video processes
    processes = session.query(VideoGenerationProcess).order_by(desc(VideoGenerationProcess.started_at)).limit(3).all()
    
    print(f"Found {len(processes)} recent video processes\n")
    
    for i, process in enumerate(processes, 1):
        print(f"\n{'='*80}")
        print(f"Process {i}: {process.id}")
        print(f"User ID: {process.user_id}")
        print(f"Started: {process.started_at}")
        print(f"Status: {process.status}")
        print(f"Current Step: {process.current_step}")
        print(f"Progress: {process.overall_progress}%")
        
        # Check if voiceover data exists
        if process.voiceover_data:
            try:
                voiceover = json.loads(process.voiceover_data) if isinstance(process.voiceover_data, str) else process.voiceover_data
                print(f"\n📝 Voiceover Data Structure:")
                print(f"  - Keys: {list(voiceover.keys())}")
                print(f"  - Has 'audio_file_path': {'audio_file_path' in voiceover}")
                print(f"  - Has 'transcript': {'transcript' in voiceover}")
                
                if 'transcript' in voiceover:
                    transcript = voiceover['transcript']
                    print(f"  - Transcript type: {type(transcript)}")
                    
                    if isinstance(transcript, dict):
                        print(f"  - Transcript keys: {list(transcript.keys())}")
                        if 'segments' in transcript:
                            segments = transcript['segments']
                            print(f"  - Number of segments: {len(segments)}")
                            if segments:
                                print(f"\n  📋 First segment sample:")
                                first_seg = segments[0]
                                print(f"     - Segment keys: {list(first_seg.keys())}")
                                if 'words' in first_seg:
                                    print(f"     - Number of words: {len(first_seg['words'])}")
                                    if first_seg['words']:
                                        print(f"     - First word sample: {first_seg['words'][0]}")
                                else:
                                    print(f"     ⚠️  No 'words' key in segment!")
                        else:
                            print(f"  ⚠️  No 'segments' key in transcript!")
                            print(f"  - Available keys: {list(transcript.keys())}")
                    elif isinstance(transcript, list):
                        print(f"  - Transcript is a list with {len(transcript)} items")
                        if transcript:
                            print(f"  - First item: {transcript[0]}")
                    else:
                        print(f"  ⚠️  Transcript is {type(transcript)}, not dict or list!")
                else:
                    print(f"  ⚠️  No 'transcript' in voiceover data!")
                    
            except Exception as e:
                print(f"  ❌ Error parsing voiceover data: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n⚠️  No voiceover_data!")
        
        # Check video effects config
        if process.video_effects_data:
            try:
                effects = json.loads(process.video_effects_data) if isinstance(process.video_effects_data, str) else process.video_effects_data
                print(f"\n🎨 Video Effects Data:")
                print(f"  - Keys: {list(effects.keys())}")
                if 'textStyles' in effects:
                    text_styles = effects['textStyles']
                    print(f"  - Text enabled: {text_styles.get('enabled', 'N/A')}")
                    print(f"  - Position: {text_styles.get('position', 'N/A')}")
                    print(f"  - Font size: {text_styles.get('fontSize', 'N/A')}")
                    print(f"  - Base color: {text_styles.get('baseColor', 'N/A')}")
                else:
                    print(f"  - No textStyles config")
            except Exception as e:
                print(f"  ❌ Error parsing effects data: {e}")
        else:
            print(f"\n⚠️  No video_effects_data!")

if __name__ == "__main__":
    check_latest_videos()
