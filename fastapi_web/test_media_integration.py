#!/usr/bin/env python3
"""
Test script for media processing system integration
Tests the complete flow from media processing tasks to API endpoints
"""

import asyncio
import tempfile
import base64
import json
from pathlib import Path
import time

# Test imports
try:
    from media_processor import ImageVideoProcessor
    from media_processing_tasks import process_single_media, get_task_status
    from celery_app import celery_app
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    exit(1)

def create_test_image():
    """Create a simple test image"""
    try:
        from PIL import Image, ImageDraw
        import io
        
        # Create a simple 200x200 RGB image
        img = Image.new('RGB', (200, 200), color='red')
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 150, 150], fill='blue')
        draw.text((10, 10), "Test Image", fill='white')
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_file.name, 'PNG')
        temp_file.close()
        
        return temp_file.name
        
    except Exception as e:
        print(f"✗ Error creating test image: {e}")
        return None

def test_media_processor():
    """Test the ImageVideoProcessor directly"""
    print("\n=== Testing ImageVideoProcessor ===")
    
    try:
        # Create test image
        test_image_path = create_test_image()
        if not test_image_path:
            return False
            
        print(f"✓ Created test image: {test_image_path}")
        
        # Initialize processor
        processor = ImageVideoProcessor()
        print("✓ Processor initialized")
        
        # Test media item
        media_item = {
            'id': 'test_image_001',
            'data': test_image_path,
            'type': 'image'
        }
        
        # Run analysis (sync version for testing)
        async def run_analysis():
            result = await processor._analyze_single_media(media_item)
            return result
        
        # Execute async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(run_analysis())
        finally:
            loop.close()
        
        # Check results
        if result.errors:
            print(f"✗ Analysis errors: {result.errors}")
            return False
        
        print(f"✓ Analysis successful")
        print(f"  - Technical specs: {len(result.technical_specs)} fields")
        print(f"  - Quality score: {result.quality_metrics.get('quality_score', 'N/A')}")
        print(f"  - Warnings: {len(result.warnings)}")
        
        # Cleanup
        Path(test_image_path).unlink()
        print("✓ Test image cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ Media processor test failed: {e}")
        return False

def test_celery_tasks():
    """Test Celery task registration and basic functionality"""
    print("\n=== Testing Celery Tasks ===")
    
    try:
        # Check if tasks are registered
        registered_tasks = list(celery_app.tasks.keys())
        media_tasks = [task for task in registered_tasks if 'media' in task.lower()]
        
        print(f"✓ Total registered tasks: {len(registered_tasks)}")
        print(f"✓ Media processing tasks found: {len(media_tasks)}")
        
        for task in media_tasks:
            print(f"  - {task}")
        
        # Test task status function
        fake_task_id = "test-task-12345"
        status = get_task_status(fake_task_id)
        
        if status['status'] == 'PENDING':
            print("✓ Task status function working (returns PENDING for unknown task)")
        else:
            print(f"✓ Task status function returned: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Celery tasks test failed: {e}")
        return False

def test_api_imports():
    """Test API endpoint imports"""
    print("\n=== Testing API Imports ===")
    
    try:
        from media_api import router
        print(f"✓ Media API router imported successfully")
        print(f"  - Prefix: {router.prefix}")
        print(f"  - Routes: {len(router.routes)}")
        
        # Test specific endpoint existence
        route_paths = [route.path for route in router.routes if hasattr(route, 'path')]
        expected_paths = [
            '/api/media/upload',
            '/api/media/process/batch',
            '/api/media/process/single',
            '/api/media/health'
        ]
        
        for path in expected_paths:
            if path in route_paths:
                print(f"  ✓ {path}")
            else:
                print(f"  ✗ Missing: {path}")
                
        return True
        
    except Exception as e:
        print(f"✗ API imports test failed: {e}")
        return False

def test_database_models():
    """Test database model imports and creation"""
    print("\n=== Testing Database Models ===")
    
    try:
        from models.db_models import MediaItem, ProcessingTask, MediaSequence, get_session
        print("✓ Database models imported successfully")
        
        # Test model creation (not actually saving to DB)
        media_item = MediaItem(
            filename="test.jpg",
            original_filename="test_original.jpg", 
            file_path="/tmp/test.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            media_type="image"
        )
        
        print("✓ MediaItem model creation successful")
        print(f"  - ID: {media_item.id}")
        print(f"  - Status: {media_item.status}")
        print(f"  - Upload time: {media_item.uploaded_at}")
        
        return True
        
    except Exception as e:
        print(f"✗ Database models test failed: {e}")
        return False

def run_integration_test():
    """Run complete integration test"""
    print("=" * 60)
    print("MEDIA PROCESSING SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    tests = [
        ("Media Processor", test_media_processor),
        ("Celery Tasks", test_celery_tasks), 
        ("API Imports", test_api_imports),
        ("Database Models", test_database_models)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name:.<30} {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Media processing system is ready.")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    run_integration_test()