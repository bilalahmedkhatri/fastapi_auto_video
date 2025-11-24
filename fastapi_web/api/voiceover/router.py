"""
Main voiceover router
Combines all voiceover endpoints
"""
from fastapi import APIRouter

from .create import router as create_router
from .get_all import router as get_all_router
from .get_by_id import router as get_by_id_router
from .update_by_id import router as update_router
from .delete_by_id import router as delete_router
from .samples import router as samples_router
from .free_tool import router as free_tool_router

# Main voiceover router
voiceover_router = APIRouter(prefix="/api/voiceover", tags=["voiceover"])

# Include all sub-routers
voiceover_router.include_router(create_router)
voiceover_router.include_router(get_all_router)
voiceover_router.include_router(get_by_id_router)
voiceover_router.include_router(update_router)
voiceover_router.include_router(delete_router)
voiceover_router.include_router(samples_router)
voiceover_router.include_router(free_tool_router)
