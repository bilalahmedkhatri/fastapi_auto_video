#!/usr/bin/env python3
"""
Comprehensive Test Suite for Video Process Backend Integration

This test suite covers:
1. API endpoints testing
2. Celery task testing  
3. WebSocket connection testing
4. Error handling and retry scenarios
5. End-to-end workflow testing

Run with: python -m pytest test_video_process_backend.py -v
"""

import pytest
import json
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import time

# Test setup
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from models.db_models import create_db_and_tables, get_session
from models.video_process_manager import VideoGenerationProcessManager
from video_process_tasks import (
    process_video_input_task,
    generate_video_scripts_task,
    generate_voiceover_task,
    start_video_generation_workflow
)


class TestVideoProcessAPI:
    """Test video process API endpoints."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client."""
        create_db_and_tables()  # Ensure tables exist
        return TestClient(app)
    
    @pytest.fixture(scope="class")
    def sample_request_data(self):
        """Sample video generation request data."""
        return {
            "user_id": "test_user_123",
            "prompt": "Create a video about renewable energy",
            "category": "Education",
            "language": "English",
            "duration": "medium",
            "priority": "normal",
            "session_id": "test_session_456"
        }
    
    def test_start_video_process_success(self, client, sample_request_data):
        """Test successful video process start."""
        with patch('video_process_tasks.start_video_generation_workflow') as mock_workflow:
            mock_result = Mock()
            mock_result.get.return_value = {
                "process_id": 1,
                "workflow_task_id": "test-task-id-123",
                "status": "started"
            }
            mock_workflow.delay.return_value = mock_result
            
            response = client.post("/api/video-process/start", json=sample_request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "process_id" in data
            assert "workflow_task_id" in data
            assert "status_endpoint" in data
    
    def test_start_video_process_invalid_data(self, client):
        """Test video process start with invalid data."""
        invalid_data = {
            "user_id": "",  # Empty user ID
            "prompt": "",   # Empty prompt
        }
        
        response = client.post("/api/video-process/start", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_video_process_status_success(self, client):
        """Test getting video process status."""
        with patch('video_process_tasks.get_process_status_task') as mock_status:
            mock_result = Mock()
            mock_result.get.return_value = {
                "current_step_info": {
                    "process_id": 1,
                    "status": "active",
                    "current_step": "scripts",
                    "overall_progress": 25,
                    "step_progress": {"input": "completed", "loading": "in-progress"},
                    "started_at": "2025-09-22T10:00:00",
                    "estimated_completion": "2025-09-22T10:05:00"
                }
            }
            mock_status.delay.return_value = mock_result
            
            response = client.get("/api/video-process/1/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["process_id"] == 1
            assert data["status"] == "active"
            assert data["current_step"] == "scripts"
            assert data["overall_progress"] == 25
    
    def test_get_video_process_status_not_found(self, client):
        """Test getting status for non-existent process."""
        with patch('video_process_tasks.get_process_status_task') as mock_status:
            mock_result = Mock()
            mock_result.get.return_value = {"error": "Process not found"}
            mock_status.delay.return_value = mock_result
            
            response = client.get("/api/video-process/999/status")
            assert response.status_code == 404
    
    def test_pause_video_process(self, client):
        """Test pausing a video process."""
        with patch('models.video_process_manager.VideoGenerationProcessManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.load_process.return_value = True
            mock_manager.pause_process.return_value = True
            mock_manager._log_user_action = Mock()
            mock_manager_class.return_value = mock_manager
            
            pause_data = {"user_id": "test_user", "reason": "User requested pause"}
            response = client.post("/api/video-process/1/pause", json=pause_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "paused successfully" in data["message"]
    
    def test_resume_video_process(self, client):
        """Test resuming a paused video process."""
        with patch('models.video_process_manager.VideoGenerationProcessManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.load_process.return_value = True
            mock_manager.resume_process.return_value = True
            mock_manager._log_user_action = Mock()
            mock_manager_class.return_value = mock_manager
            
            resume_data = {"user_id": "test_user"}
            response = client.post("/api/video-process/1/resume", json=resume_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_retry_failed_step(self, client):
        """Test retrying a failed step."""
        with patch('models.video_process_manager.VideoGenerationProcessManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.load_process.return_value = True
            mock_manager.retry_failed_step.return_value = True
            mock_manager._log_user_action = Mock()
            mock_manager_class.return_value = mock_manager
            
            retry_data = {"user_id": "test_user", "reason": "Retry after fixing issue"}
            response = client.post("/api/video-process/1/retry/scripts", json=retry_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["step_name"] == "scripts"
    
    def test_get_user_processes(self, client):
        """Test getting processes for a user."""
        with patch('video_process_api.get_active_processes_for_user') as mock_get_processes:
            mock_get_processes.return_value = [
                {"id": 1, "status": "active", "created_at": "2025-09-22T10:00:00"},
                {"id": 2, "status": "completed", "created_at": "2025-09-22T09:00:00"}
            ]
            
            response = client.get("/api/video-process/user/test_user_123")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["processes"]) == 2
            assert data["total_count"] == 2
    
    def test_cancel_video_process(self, client):
        """Test cancelling a video process."""
        with patch('models.video_process_manager.VideoGenerationProcessManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.load_process.return_value = True
            mock_manager.handle_step_failure.return_value = True
            mock_manager.current_process = Mock()
            mock_manager.current_process.current_step = "scripts"
            mock_manager_class.return_value = mock_manager
            
            response = client.delete("/api/video-process/1?user_id=test_user")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "cancelled successfully" in data["message"]


class TestCeleryTasks:
    """Test Celery task functionality."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create mock VideoGenerationProcessManager."""
        manager = Mock()
        manager.update_step_progress.return_value = True
        manager.handle_step_failure.return_value = True
        return manager
    
    @patch('video_process_tasks.VideoProcessTaskBase.get_manager')
    def test_process_video_input_task_success(self, mock_get_manager, mock_manager):
        """Test successful video input processing."""
        mock_get_manager.return_value = mock_manager
        
        input_data = {
            "prompt": "Create educational video",
            "category": "Education",
            "language": "English",
            "duration": "medium"
        }
        
        # Mock the task instance
        mock_task = Mock()
        mock_task.request.id = "test-task-123"
        
        result = process_video_input_task(mock_task, 1, input_data)
        
        assert result["status"] == "completed"
        assert "processed_prompt" in result["data"]
        assert result["next_step"] == "loading"
        
        # Verify manager was called correctly
        assert mock_manager.update_step_progress.call_count == 2  # Start and complete
    
    @patch('video_process_tasks.VideoProcessTaskBase.get_manager')
    def test_process_video_input_task_failure(self, mock_get_manager, mock_manager):
        """Test video input processing failure."""
        mock_get_manager.side_effect = Exception("Database error")
        
        mock_task = Mock()
        mock_task.request.id = "test-task-123"
        mock_task.update_state = Mock()
        
        with pytest.raises(Exception):
            process_video_input_task(mock_task, 1, {})
        
        # Verify task state was updated with failure
        mock_task.update_state.assert_called_once()
    
    @patch('video_process_tasks.VideoProcessTaskBase.get_manager')
    def test_generate_video_scripts_task_success(self, mock_get_manager, mock_manager):
        """Test successful script generation."""
        mock_get_manager.return_value = mock_manager
        
        input_data = {
            "processed_prompt": "Educational content about AI",
            "category": "Technology"
        }
        
        mock_task = Mock()
        mock_task.request.id = "test-task-456"
        
        result = generate_video_scripts_task(mock_task, 1, input_data)
        
        assert result["status"] == "completed"
        assert "scripts" in result["data"]
        assert len(result["data"]["scripts"]) == 3  # Expected 3 script variations
        assert result["next_step"] == "editing"
    
    @patch('video_process_tasks.VideoProcessTaskBase.get_manager')
    def test_generate_voiceover_task_success(self, mock_get_manager, mock_manager):
        """Test successful voiceover generation."""
        mock_get_manager.return_value = mock_manager
        
        script_data = {
            "scripts": [
                {"id": "script_1", "content": "Test script", "duration_estimate": 45}
            ]
        }
        
        mock_task = Mock()
        mock_task.request.id = "test-task-789"
        
        result = generate_voiceover_task(mock_task, 1, script_data)
        
        assert result["status"] == "completed"
        assert "audio_file" in result["data"]
        assert result["data"]["voice_model"] == "elevenlabs_professional"
        assert result["next_step"] == "social-media"
    
    def test_workflow_orchestration_structure(self):
        """Test that workflow orchestration is properly structured."""
        # This would test the chain creation in start_video_generation_workflow
        # For now, we'll just verify the function exists and has correct signature
        import inspect
        
        sig = inspect.signature(start_video_generation_workflow)
        params = list(sig.parameters.keys())
        
        # Verify required parameters exist
        assert 'self' in params  # bind=True task
        assert 'user_id' in params
        assert 'input_data' in params


class TestErrorHandling:
    """Test error handling and retry mechanisms."""
    
    def test_task_retry_configuration(self):
        """Test that tasks are configured with proper retry settings."""
        # Check that tasks have autoretry_for configured
        assert hasattr(process_video_input_task, 'autoretry_for')
        assert hasattr(generate_video_scripts_task, 'autoretry_for')
        
        # Check retry kwargs
        input_task_options = process_video_input_task.options
        assert 'autoretry_for' in str(input_task_options)
    
    @patch('video_process_tasks.VideoProcessTaskBase.get_manager')
    def test_step_failure_handling(self, mock_get_manager):
        """Test proper failure handling in tasks."""
        # Setup manager to fail on step update
        mock_manager = Mock()
        mock_manager.update_step_progress.side_effect = Exception("Step update failed")
        mock_get_manager.return_value = mock_manager
        
        mock_task = Mock()
        mock_task.request.id = "test-task-error"
        mock_task.update_state = Mock()
        
        input_data = {"prompt": "Test prompt"}
        
        # Task should handle the exception and update Celery state
        with pytest.raises(Exception):
            process_video_input_task(mock_task, 1, input_data)
        
        # Verify error handling was called
        mock_task.update_state.assert_called()
        call_args = mock_task.update_state.call_args[1]
        assert call_args['state'] == 'FAILURE'
        assert 'error' in call_args['meta']
    
    @patch('video_process_tasks.VideoProcessTaskBase.get_manager')
    def test_manager_failure_recovery(self, mock_get_manager):
        """Test recovery when manager operations fail."""
        # First call fails, second succeeds (simulating retry)
        mock_manager = Mock()
        mock_manager.update_step_progress.side_effect = [
            Exception("Temporary failure"),
            True  # Success on retry
        ]
        mock_get_manager.return_value = mock_manager
        
        # In a real scenario, Celery would handle the retry
        # Here we just verify the failure path is properly handled
        mock_task = Mock()
        mock_task.request.id = "test-retry-task"
        mock_task.update_state = Mock()
        
        with pytest.raises(Exception):
            process_video_input_task(mock_task, 1, {"prompt": "test"})


class TestWebSocketIntegration:
    """Test WebSocket functionality."""
    
    def test_connection_manager_connect(self):
        """Test WebSocket connection management."""
        from video_process_api import VideoProcessConnectionManager
        
        manager = VideoProcessConnectionManager()
        
        # Mock WebSocket
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        
        # Test connection
        asyncio.run(manager.connect(mock_ws, 1))
        
        assert 1 in manager.active_connections
        assert mock_ws in manager.active_connections[1]
        mock_ws.accept.assert_called_once()
    
    def test_connection_manager_disconnect(self):
        """Test WebSocket disconnection."""
        from video_process_api import VideoProcessConnectionManager
        
        manager = VideoProcessConnectionManager()
        mock_ws = Mock()
        
        # Setup connection first
        manager.active_connections[1] = [mock_ws]
        
        # Test disconnection
        manager.disconnect(mock_ws, 1)
        
        assert 1 not in manager.active_connections  # Should be removed when empty
    
    def test_send_process_update(self):
        """Test sending updates to connected WebSocket clients."""
        from video_process_api import VideoProcessConnectionManager
        
        manager = VideoProcessConnectionManager()
        
        # Mock WebSocket that works
        mock_ws_good = Mock()
        mock_ws_good.send_json = AsyncMock()
        
        # Mock WebSocket that fails
        mock_ws_bad = Mock()
        mock_ws_bad.send_json = AsyncMock(side_effect=Exception("Connection lost"))
        
        manager.active_connections[1] = [mock_ws_good, mock_ws_bad]
        
        update_data = {"type": "status_update", "progress": 50}
        
        # Run the update
        asyncio.run(manager.send_process_update(1, update_data))
        
        # Good connection should receive update
        mock_ws_good.send_json.assert_called_once_with(update_data)
        
        # Bad connection should be removed
        assert mock_ws_bad not in manager.active_connections.get(1, [])


class TestEndToEndWorkflow:
    """Test complete workflow scenarios."""
    
    @pytest.fixture
    def workflow_setup(self):
        """Setup for workflow testing."""
        create_db_and_tables()
        
    def test_complete_workflow_simulation(self, workflow_setup):
        """Test complete video generation workflow simulation."""
        # This test simulates the entire workflow without actually running Celery
        
        # 1. Initialize process
        session = next(get_session())
        manager = VideoGenerationProcessManager(session)
        
        process_id = manager.initialize_video_generation(
            user_id="workflow_test_user",
            initial_data={"prompt": "Test video generation workflow"},
            session_id="workflow_session",
            priority="high"
        )
        
        assert process_id is not None
        
        # 2. Simulate each step completion
        steps = ["input", "loading", "scripts", "editing", "voiceover", "social-media", "media", "video-effects"]
        
        for i, step in enumerate(steps):
            success = manager.update_step_progress(
                step_name=step,
                status="completed",
                data={"step_data": f"Simulated {step} completion"},
                quality_score=0.85 + (i * 0.01)
            )
            assert success is True
        
        # 3. Complete the process
        completion_success = manager.mark_completion(
            video_id="test_video_output.mp4",
            final_quality_score=0.92
        )
        assert completion_success is True
        
        # 4. Verify final state
        final_status = manager.get_current_step()
        assert final_status["status"] == "completed"
        assert final_status["overall_progress"] == 100
        
        # 5. Verify analytics
        analytics = manager.get_process_analytics()
        assert analytics["step_statistics"]["completed_steps"] == 8
        assert analytics["step_statistics"]["success_rate"] == 100.0


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# Test runner convenience function
def run_tests():
    """Run all tests with proper configuration."""
    import pytest
    
    # Run tests with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--strict-markers"
    ])


if __name__ == "__main__":
    run_tests()