#!/usr/bin/env python3
"""
Demo script showing the updated CurrentVideoGenerate class with integer IDs.
This demonstrates how the video generation process tracking works with auto-incrementing IDs.
"""

import sys
import os

# Add the parent directory to the path so we can import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.db_models import get_session, create_db_and_tables
from models.video_process_manager import VideoGenerationProcessManager

def demo_video_process():
    """Demonstrate the video generation process with integer IDs."""
    print("🎬 CurrentVideoGenerate Class Demo - Updated with Integer IDs")
    print("=" * 60)
    
    # Ensure tables exist
    create_db_and_tables()
    
    # Get database session
    session = next(get_session())
    
    try:
        # Initialize the manager
        manager = VideoGenerationProcessManager(session)
        print("✅ VideoGenerationProcessManager initialized")
        
        # Create a new video generation process
        process_id = manager.initialize_video_generation(
            user_id="demo_user",
            initial_data={
                "prompt": "Create an educational video about renewable energy",
                "category": "Education",
                "language": "English",
                "duration": "medium"
            },
            session_id="demo_session_001",
            priority="normal"
        )
        
        print(f"🆔 New process created with ID: {process_id} (integer, starts from 1)")
        
        # Simulate progressing through the workflow steps
        steps = ["input", "loading", "scripts", "editing", "voiceover", "social-media", "media", "video-effects"]
        
        for i, step in enumerate(steps, 1):
            if i <= 3:  # Complete first 3 steps
                manager.update_step_progress(
                    step_name=step,
                    status="completed",
                    data={"demo_data": f"Step {step} completed successfully"},
                    quality_score=0.9,
                    tokens_used=100 + i * 50
                )
                print(f"✅ Step {i}: {step} - COMPLETED")
            else:
                print(f"⏳ Step {i}: {step} - pending")
        
        # Get current status
        current = manager.get_current_step()
        print(f"\n📊 Current Status:")
        print(f"   - Current Step: {current['current_step']}")
        print(f"   - Overall Progress: {current['overall_progress']}%")
        print(f"   - Process ID: {process_id} (integer)")
        
        # Get analytics
        analytics = manager.get_process_analytics()
        print(f"\n📈 Analytics:")
        print(f"   - Total Steps: {analytics['step_statistics']['total_steps']}")
        print(f"   - Completed: {analytics['step_statistics']['completed_steps']}")
        print(f"   - Success Rate: {analytics['step_statistics']['success_rate']:.1f}%")
        
        print("\n🎉 Demo completed successfully!")
        print("💡 Key Features:")
        print("   ✓ Integer IDs starting from 1")
        print("   ✓ Auto-incrementing primary keys")
        print("   ✓ Comprehensive step tracking")
        print("   ✓ Progress analytics")
        print("   ✓ Database persistence")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    demo_video_process()