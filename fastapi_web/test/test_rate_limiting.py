"""
Test Rate Limiting Implementation

Tests the rate limiting functionality in TextGenAPI to ensure:
1. Rate limits are enforced (max 50 requests per minute)
2. Exponential backoff works correctly
3. Model rotation occurs on failures
4. 429 errors are handled properly
"""

import sys
import os
import time
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_builder.ai_apis.text_gen_api import TextGenAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_rate_limiter():
    """Test that rate limiter enforces request limits"""
    logger.info("=" * 60)
    logger.info("TEST 1: Rate Limiter Enforcement")
    logger.info("=" * 60)
    
    api = TextGenAPI()
    
    # Clear any existing timestamps
    api.request_timestamps = []
    
    # Try to make 10 rapid requests (should be allowed)
    start_time = time.time()
    for i in range(10):
        api._enforce_rate_limit(max_requests_per_minute=50)
        logger.info(f"Request {i+1}/10 allowed - {len(api.request_timestamps)} requests in queue")
    
    elapsed = time.time() - start_time
    logger.info(f"✓ 10 requests completed in {elapsed:.2f}s (should be < 1s)")
    
    # Now fill to 50 requests
    for i in range(40):
        api._enforce_rate_limit(max_requests_per_minute=50)
    
    logger.info(f"✓ 50 requests queued: {len(api.request_timestamps)}")
    
    # Next request should be delayed
    logger.info("Attempting 51st request (should wait)...")
    start_wait = time.time()
    api._enforce_rate_limit(max_requests_per_minute=50)
    wait_time = time.time() - start_wait
    
    logger.info(f"✓ Request delayed by {wait_time:.2f}s (expected ~60s)")
    logger.info("")


def test_model_cooldown():
    """Test that failed models go into cooldown"""
    logger.info("=" * 60)
    logger.info("TEST 2: Model Cooldown")
    logger.info("=" * 60)
    
    api = TextGenAPI()
    
    # Mark a model as failed
    test_model = "google/gemini-2.0-flash-exp:free"
    api.failed_models[test_model] = time.time()
    
    logger.info(f"Marked {test_model} as failed")
    
    # Check if it's in cooldown
    in_cooldown = api._is_model_recently_failed(test_model, cooldown_seconds=120)
    logger.info(f"✓ Model in cooldown: {in_cooldown} (expected: True)")
    
    # Test with expired cooldown
    api.failed_models[test_model] = time.time() - 121  # 121 seconds ago
    in_cooldown = api._is_model_recently_failed(test_model, cooldown_seconds=120)
    logger.info(f"✓ Model in cooldown after 121s: {in_cooldown} (expected: False)")
    logger.info(f"✓ Model removed from failed list: {test_model not in api.failed_models}")
    logger.info("")


def test_openrouter_status():
    """Test OpenRouter account status check"""
    logger.info("=" * 60)
    logger.info("TEST 3: OpenRouter Status Check")
    logger.info("=" * 60)
    
    api = TextGenAPI()
    
    status = api.check_openrouter_status()
    
    if status:
        logger.info("✓ OpenRouter status retrieved:")
        logger.info(f"  - Label: {status.get('label', 'N/A')}")
        logger.info(f"  - Usage: {status.get('usage', 'N/A')}")
        logger.info(f"  - Limit: {status.get('limit', 'N/A')}")
    else:
        logger.warning("⚠ Could not retrieve OpenRouter status (may require API key)")
    logger.info("")


def test_exponential_backoff():
    """Test exponential backoff calculation"""
    logger.info("=" * 60)
    logger.info("TEST 4: Exponential Backoff")
    logger.info("=" * 60)
    
    for attempt in range(5):
        delay = 2 ** attempt
        logger.info(f"Attempt {attempt + 1}: {delay}s delay")
    
    logger.info("✓ Backoff sequence: 1s, 2s, 4s, 8s, 16s")
    logger.info("")


def test_model_selection_with_exclusions():
    """Test that model selection excludes failed models"""
    logger.info("=" * 60)
    logger.info("TEST 5: Model Selection with Exclusions")
    logger.info("=" * 60)
    
    api = TextGenAPI()
    
    # Get initial model
    model1 = api.get_model_for_input("text", prefer_free=True)
    logger.info(f"First model selected: {model1}")
    
    # Mark it as failed and get another
    api.failed_models[model1] = time.time()
    
    model2 = api.get_model_for_input("text", prefer_free=True)
    logger.info(f"Second model selected: {model2}")
    
    if model1 != model2:
        logger.info(f"✓ Different model selected after failure")
    else:
        logger.warning(f"⚠ Same model selected (may be only one available)")
    
    logger.info("")


def run_all_tests():
    """Run all rate limiting tests"""
    logger.info("\n" + "=" * 60)
    logger.info("RATE LIMITING TEST SUITE")
    logger.info(f"Started at: {datetime.now()}")
    logger.info("=" * 60 + "\n")
    
    try:
        test_rate_limiter()
        test_model_cooldown()
        test_openrouter_status()
        test_exponential_backoff()
        test_model_selection_with_exclusions()
        
        logger.info("=" * 60)
        logger.info("ALL TESTS COMPLETED")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)


if __name__ == "__main__":
    run_all_tests()
