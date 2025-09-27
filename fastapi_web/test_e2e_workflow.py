#!/usr/bin/env python3
"""
End-to-End Video Process Integration Test

This script tests the complete video generation workflow from API request
through Celery processing to completion status updates, validating the
entire backend integration.

Usage: python test_e2e_workflow.py
"""

import requests
import time
import json
from datetime import datetime


class VideoProcessE2ETest:
    """End-to-end test for video process workflow."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_api_health(self):
        """Test that the API is running and responsive."""
        try:
            response = self.session.get(f"{self.base_url}/")
            print(f"✅ API Health Check: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ API Health Check Failed: {e}")
            return False
    
    def start_video_process(self):
        """Start a new video generation process."""
        request_data = {
            "user_id": "e2e_test_user",
            "prompt": "Create an educational video about artificial intelligence and machine learning",
            "category": "Education", 
            "language": "English",
            "duration": "medium",
            "priority": "normal",
            "session_id": "e2e_test_session",
            "additional_settings": {
                "voice_type": "professional",
                "video_style": "modern"
            }
        }
        
        try:
            print("\n🚀 Starting video generation process...")
            print(f"Request: {json.dumps(request_data, indent=2)}")
            
            response = self.session.post(
                f"{self.base_url}/api/video-process/start",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Process started successfully!")
                print(f"   Process ID: {result['process_id']}")
                print(f"   Workflow Task ID: {result['workflow_task_id']}")
                print(f"   Status Endpoint: {result['status_endpoint']}")
                return result["process_id"]
            else:
                print(f"❌ Failed to start process: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting process: {e}")
            return None
    
    def monitor_process_status(self, process_id, max_wait_minutes=10):
        """Monitor process status until completion or timeout."""
        print(f"\n📊 Monitoring process {process_id} status...")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        last_step = None
        last_progress = -1
        
        while time.time() - start_time < max_wait_seconds:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/video-process/{process_id}/status"
                )
                
                if response.status_code == 200:
                    status = response.json()
                    
                    current_step = status.get("current_step")
                    progress = status.get("overall_progress", 0)
                    process_status = status.get("status")
                    
                    # Print updates only when there's a change
                    if current_step != last_step or progress != last_progress:
                        print(f"   Step: {current_step} | Progress: {progress}% | Status: {process_status}")
                        
                        if status.get("error_message"):
                            print(f"   ⚠️  Error: {status['error_message']}")
                        
                        last_step = current_step
                        last_progress = progress
                    
                    # Check completion conditions
                    if process_status == "completed":
                        print(f"✅ Process completed successfully!")
                        print(f"   Final progress: {progress}%")
                        print(f"   Duration: {(time.time() - start_time):.1f} seconds")
                        return True
                    elif process_status == "failed":
                        print(f"❌ Process failed!")
                        print(f"   Error: {status.get('error_message', 'Unknown error')}")
                        return False
                    
                elif response.status_code == 404:
                    print(f"❌ Process {process_id} not found")
                    return False
                else:
                    print(f"⚠️  Status check failed: {response.status_code}")
                
                # Wait before next check
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Error checking status: {e}")
                time.sleep(5)
        
        print(f"⏱️  Process monitoring timed out after {max_wait_minutes} minutes")
        return False
    
    def test_process_operations(self, process_id):
        """Test process control operations (pause, resume, etc.)."""
        print(f"\n🔧 Testing process operations for {process_id}...")
        
        # Test pause
        try:
            pause_response = self.session.post(
                f"{self.base_url}/api/video-process/{process_id}/pause",
                json={"user_id": "e2e_test_user", "reason": "Testing pause functionality"}
            )
            
            if pause_response.status_code == 200:
                print("✅ Process pause test successful")
            else:
                print(f"⚠️  Process pause test: {pause_response.status_code}")
                
        except Exception as e:
            print(f"❌ Process pause test error: {e}")
        
        # Test resume
        try:
            resume_response = self.session.post(
                f"{self.base_url}/api/video-process/{process_id}/resume",
                json={"user_id": "e2e_test_user"}
            )
            
            if resume_response.status_code == 200:
                print("✅ Process resume test successful")
            else:
                print(f"⚠️  Process resume test: {resume_response.status_code}")
                
        except Exception as e:
            print(f"❌ Process resume test error: {e}")
    
    def test_user_processes_api(self):
        """Test getting user processes."""
        print(f"\n👤 Testing user processes API...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/video-process/user/e2e_test_user"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User processes API successful")
                print(f"   Total processes: {data.get('total_count', 0)}")
                print(f"   Active: {data.get('active_count', 0)}")
                print(f"   Completed: {data.get('completed_count', 0)}")
            else:
                print(f"⚠️  User processes API: {response.status_code}")
                
        except Exception as e:
            print(f"❌ User processes API error: {e}")
    
    def run_complete_test(self):
        """Run the complete end-to-end test."""
        print("🧪 Starting End-to-End Video Process Test")
        print("=" * 50)
        
        # 1. Check API health
        if not self.test_api_health():
            print("❌ API is not running. Please start the FastAPI server.")
            return False
        
        # 2. Start video process
        process_id = self.start_video_process()
        if not process_id:
            print("❌ Failed to start video process")
            return False
        
        # 3. Test process operations (optional - might interfere with workflow)
        # self.test_process_operations(process_id)
        
        # 4. Monitor process to completion
        success = self.monitor_process_status(process_id)
        
        # 5. Test user processes API
        self.test_user_processes_api()
        
        # 6. Summary
        print("\n" + "=" * 50)
        if success:
            print("🎉 End-to-End Test PASSED!")
            print("✅ Video generation workflow completed successfully")
        else:
            print("⚠️  End-to-End Test INCOMPLETE")
            print("⚠️  Workflow may have failed or timed out")
        
        return success


def run_integration_test():
    """Run integration test with proper setup."""
    print("🔧 Video Process Backend Integration Test")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    # Check if server is likely running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print("✅ FastAPI server detected")
    except:
        print("⚠️  FastAPI server not detected on localhost:8000")
        print("   Please ensure the server is running with: fastapi dev main.py")
        return
    
    # Run the test
    test = VideoProcessE2ETest()
    test.run_complete_test()


if __name__ == "__main__":
    run_integration_test()