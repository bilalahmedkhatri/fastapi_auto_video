"""
Router Configuration for FastAPI Application

Centralized router management to keep main.py clean and maintainable.
All routers are registered here with their import paths and optional prefixes.

Usage in main.py:
    from routes import load_routers
    load_routers(app)
"""

import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

# Router Configuration
# Format: (module_path, router_name, optional_prefix, optional_tags)
ROUTERS: List[Tuple[str, str, Optional[str], Optional[List[str]]]] = [
    # Video Builder - Script Generation
    ("video_builder.script_api", "router", None, None),
    
    # Video Builder - Voice System (OLD - keep for backward compatibility)
    ("video_builder.voice_system.voice_controller", "voice_router", None, None),
    
    # Script Database API
    ("script_api", "router", None, None),
    
    # Voiceover API (OLD - DISABLED - using new modular API instead)
    # ("voiceover_api", "voiceover_router", None, None),
    
    # Media Processing API
    ("media_api", "router", None, None),
    
    # Video Process API
    ("video_process_api", "video_process_router", None, None),
    
    # WebSocket Routes
    ("ws_realtime.routes", "websocket_router", None, None),
    
    # NEW: Voiceover API (modular structure with free tool)
    ("api.voiceover.router", "voiceover_router", None, None),
]


def load_routers(app) -> int:
    """
    Load all configured routers into the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        int: Number of successfully loaded routers
        
    Example:
        from fastapi import FastAPI
        from routes import load_routers
        
        app = FastAPI()
        loaded = load_routers(app)
        logger.info(f"Loaded {loaded} routers")
    """
    loaded_count = 0
    
    for router_config in ROUTERS:
        # Unpack configuration
        module_path = router_config[0]
        router_name = router_config[1]
        prefix = router_config[2] if len(router_config) > 2 else None
        tags = router_config[3] if len(router_config) > 3 else None
        
        try:
            # Dynamic import
            module = __import__(module_path, fromlist=[router_name])
            router = getattr(module, router_name)
            
            # Include router with optional prefix and tags
            if prefix or tags:
                include_kwargs = {}
                if prefix:
                    include_kwargs['prefix'] = prefix
                if tags:
                    include_kwargs['tags'] = tags
                app.include_router(router, **include_kwargs)
            else:
                app.include_router(router)
            
            logger.info(f"[OK] Loaded router: {module_path}.{router_name}")
            loaded_count += 1
            
        except ImportError as e:
            logger.warning(f"[FAIL] Failed to import router {module_path}.{router_name}: {str(e)}")
        except AttributeError as e:
            logger.warning(f"[FAIL] Router {router_name} not found in {module_path}: {str(e)}")
        except Exception as e:
            logger.error(f"[FAIL] Error loading router {module_path}.{router_name}: {str(e)}")
    
    logger.info(f"Router loading complete: {loaded_count}/{len(ROUTERS)} routers loaded successfully")
    return loaded_count


def get_router_info() -> dict:
    """
    Get information about configured routers.
    
    Returns:
        dict: Router configuration summary
    """
    return {
        "total_configured": len(ROUTERS),
        "routers": [
            {
                "module": config[0],
                "router_name": config[1],
                "prefix": config[2] if len(config) > 2 else None,
                "tags": config[3] if len(config) > 3 else None
            }
            for config in ROUTERS
        ]
    }
