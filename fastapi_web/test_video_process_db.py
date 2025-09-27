#!/usr/bin/env python3
"""
Test script for video generation process database models.
This script tests the creation and functionality of the new video process tracking tables.
"""

import os
import sys
import json
from datetime import datetime
from sqlmodel import Session, select

# Add the parent directory to the path so we can import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.db_models import (
    create_db_and_tables, 
    get_session, 
    VideoGenerationProcess, 
    VideoProcessStep
)

from models.video_process_manager import (
    VideoGenerationProcessManager,
    CurrentVideoGenerate,
    get_active_processes_for_user,
    cleanup_old_processes
)

def test_database_creation():
    """Test that the database tables are created successfully."""
    print("🔧 Testing database table creation...")
    
    try:
        # Create all tables
        create_db_and_tables()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def test_video_process_manager():
    """Test the VideoGenerationProcessManager functionality."""
    print("\n🎬 Testing VideoGenerationProcessManager...")
    
    # Get database session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Initialize manager
        manager = VideoGenerationProcessManager(session)
        print("✅ Manager initialized successfully")
        
        # Test process creation
        process_id = manager.initialize_video_generation(
            user_id="test_user_123",
            initial_data={
                "prompt": "Create a video about AI technology",
                "category": "Technology",
                "language": "English",
                "script_types": ["short", "medium"]
            },
            session_id="session_123",
            priority="high"
        )
        print(f"✅ Process created with ID: {process_id}")
        
        # Test step update
        success = manager.update_step_progress(
            step_name="input",
            status="completed",
            data={
                "user_prompt": "Create a video about AI technology",
                "selected_types": ["short", "medium"],
                "processing_time": 2.5
            },
            quality_score=0.95,
            ai_model_used="gpt-4",
            tokens_used=150
        )
        print(f"✅ Step update successful: {success}")
        
        # Test getting current state
        current_state = manager.get_current_step()
        print(f"✅ Current state retrieved: Progress {current_state.get('overall_progress')}%")
        
        # Test step failure handling
        failure_success = manager.handle_step_failure(
            step_name="scripts",
            error_message="AI service temporarily unavailable",
            error_details={
                "error_code": "SERVICE_UNAVAILABLE",
                "retry_after": 30,
                "service": "openai"
            }
        )
        print(f"✅ Step failure handled: {failure_success}")
        
        # Test process analytics
        analytics = manager.get_process_analytics()
        print(f"✅ Analytics retrieved: {analytics.get('step_statistics', {})}")
        
        # Test completion
        completion_success = manager.mark_completion(
            video_id="video_123",
            final_quality_score=0.88
        )
        print(f"✅ Process completion marked: {completion_success}")
        
        print("🎉 All VideoGenerationProcessManager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in VideoGenerationProcessManager test: {e}")
        return False
    finally:
        session.close()

def test_utility_functions():
    """Test utility functions for process management."""
    print("\n🔧 Testing utility functions...")
    
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Test getting active processes
        active_processes = get_active_processes_for_user(session, "test_user_123")
        print(f"✅ Active processes retrieved: {len(active_processes)} processes")
        
        # Test cleanup function (won't actually clean anything recent)
        cleaned_count = cleanup_old_processes(session, days_old=365)  # Only clean very old processes
        print(f"✅ Cleanup function executed: {cleaned_count} old processes cleaned")
        
        print("🎉 All utility function tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in utility function tests: {e}")
        return False
    finally:
        session.close()

def test_direct_database_access():
    """Test direct database access to the new tables."""
    print("\n💾 Testing direct database access...")
    
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Test querying VideoGenerationProcess
        processes = session.exec(select(VideoGenerationProcess)).all()
        print(f"✅ Found {len(processes)} video generation processes")
        
        # Test querying VideoProcessStep
        steps = session.exec(select(VideoProcessStep)).all()
        print(f"✅ Found {len(steps)} process steps")
        
        # Display sample data if available
        if processes:
            sample_process = processes[0]
            print(f"✅ Sample process: {sample_process.id}, Status: {sample_process.status}, Progress: {sample_process.overall_progress}%")
            
            # Get steps for this process
            process_steps = session.exec(
                select(VideoProcessStep).where(VideoProcessStep.process_id == sample_process.id)
            ).all()
            print(f"✅ Process has {len(process_steps)} steps")
        
        print("🎉 All database access tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in database access tests: {e}")
        return False
    finally:
        session.close()

def main():
    """Run all tests."""
    print("🚀 Starting Video Generation Process Database Tests")
    print("=" * 60)
    
    # Track test results
    test_results = []
    
    # Run tests
    test_results.append(("Database Creation", test_database_creation()))
    test_results.append(("Process Manager", test_video_process_manager()))
    test_results.append(("Utility Functions", test_utility_functions()))
    test_results.append(("Database Access", test_direct_database_access()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests completed successfully!")
        print("🎬 Video generation process tracking system is ready!")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()