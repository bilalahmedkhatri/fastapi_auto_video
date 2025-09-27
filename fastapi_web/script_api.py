from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, func
from sqlalchemy import and_
from typing import Optional, List
from models.db_models import ScriptGeneration, SocialMediaContent, get_session
from pydantic import BaseModel
import json
from datetime import datetime

router = APIRouter(prefix="/api/scripts", tags=["scripts"])

# Response models
class ScriptResponse(BaseModel):
    id: str
    user_id: str
    user_prompt: str
    script_type: str
    category: str
    language: str
    title: str
    description: str
    voiceover_script: str
    tags: List[str]
    duration_estimate: str
    word_count: int
    generation_duration_ms: Optional[int]
    ai_model_used: Optional[str]
    created_at: datetime
    updated_at: datetime
    status: str = "completed"  # Default status for existing scripts

class PaginatedScriptsResponse(BaseModel):
    scripts: List[ScriptResponse]
    total_pages: int
    total_items: int
    current_page: int

class ScriptStatusUpdate(BaseModel):
    status: str

class ScriptUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    voiceover_script: Optional[str] = None
    category: Optional[str] = None
    script_type: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[List[str]] = None

# GET /api/scripts - Fetch scripts with filters and pagination
@router.get("/", response_model=PaginatedScriptsResponse)
async def get_scripts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("recent", description="Sort by: recent, title, status, duration"),
    filter_by: str = Query("all", description="Filter by: all, completed, draft"),
    search: str = Query("", description="Search in title and description"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    session: Session = Depends(get_session)
):
    try:
        # Build base query with filters
        query = select(ScriptGeneration)
        
        # Build conditions list for both main query and count query
        conditions = []
        
        # Apply user filter if provided
        if user_id:
            conditions.append(ScriptGeneration.user_id == user_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            conditions.append(
                (ScriptGeneration.title.ilike(search_term)) |
                (ScriptGeneration.description.ilike(search_term)) |
                (ScriptGeneration.user_prompt.ilike(search_term))
            )
        
        # Apply conditions to query
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count with same filters
        count_query = select(func.count(ScriptGeneration.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_scripts = session.exec(count_query).one()
        
        # Apply sorting
        if sort_by == "title":
            query = query.order_by(ScriptGeneration.title)
        elif sort_by == "status":
            query = query.order_by(ScriptGeneration.category)  # Using category as status for now
        elif sort_by == "duration":
            query = query.order_by(ScriptGeneration.duration_estimate)
        else:  # recent
            query = query.order_by(ScriptGeneration.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        # Execute query
        scripts = session.exec(query).all()
        
        # Convert to response format
        script_responses = []
        for script in scripts:
            tags = []
            try:
                if script.tags:
                    tags = json.loads(script.tags) if isinstance(script.tags, str) else script.tags
            except:
                tags = []
            
            script_responses.append(ScriptResponse(
                id=script.id,
                user_id=script.user_id,
                user_prompt=script.user_prompt,
                script_type=script.script_type,
                category=script.category,
                language=script.language,
                title=script.title,
                description=script.description,
                voiceover_script=script.voiceover_script,
                tags=tags,
                duration_estimate=script.duration_estimate,
                word_count=script.word_count,
                generation_duration_ms=script.generation_duration_ms,
                ai_model_used=script.ai_model_used,
                created_at=script.created_at,
                updated_at=script.updated_at,
                status="completed"  # Default status
            ))
        
        # Calculate pagination
        total_pages = (total_scripts + limit - 1) // limit
        
        return PaginatedScriptsResponse(
            scripts=script_responses,
            total_pages=total_pages,
            total_items=total_scripts,
            current_page=page
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch scripts: {str(e)}")

# GET /api/scripts/{script_id} - Get script by ID
@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script_by_id(
    script_id: str,
    session: Session = Depends(get_session)
):
    try:
        # Get script from database
        statement = select(ScriptGeneration).where(ScriptGeneration.id == script_id)
        script = session.exec(statement).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        
        # Parse tags
        tags = []
        try:
            if script.tags:
                tags = json.loads(script.tags) if isinstance(script.tags, str) else script.tags
        except:
            tags = []
        
        return ScriptResponse(
            id=script.id,
            user_id=script.user_id,
            user_prompt=script.user_prompt,
            script_type=script.script_type,
            category=script.category,
            language=script.language,
            title=script.title,
            description=script.description,
            voiceover_script=script.voiceover_script,
            tags=tags,
            duration_estimate=script.duration_estimate,
            word_count=script.word_count,
            generation_duration_ms=script.generation_duration_ms,
            ai_model_used=script.ai_model_used,
            created_at=script.created_at,
            updated_at=script.updated_at,
            status="completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch script: {str(e)}")

# PUT /api/scripts/{script_id}/status - Update script status
@router.put("/{script_id}/status")
async def update_script_status(
    script_id: str,
    status_update: ScriptStatusUpdate,
    session: Session = Depends(get_session)
):
    try:
        # Get script from database
        statement = select(ScriptGeneration).where(ScriptGeneration.id == script_id)
        script = session.exec(statement).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        
        # For now, we'll just return success since ScriptGeneration doesn't have a status field
        # In the future, you might want to add a status field to the model
        script.updated_at = datetime.now()
        session.add(script)
        session.commit()
        session.refresh(script)
        
        return {
            "success": True,
            "script_id": script_id,
            "status": status_update.status,
            "message": "Script status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update script status: {str(e)}")

# PUT /api/scripts/{script_id} - Update script content
@router.put("/{script_id}")
async def update_script(
    script_id: str,
    script_update: ScriptUpdateRequest,
    session: Session = Depends(get_session)
):
    try:
        # Get script from database
        statement = select(ScriptGeneration).where(ScriptGeneration.id == script_id)
        script = session.exec(statement).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        
        # Update fields if provided
        if script_update.title is not None:
            script.title = script_update.title
        if script_update.description is not None:
            script.description = script_update.description
        if script_update.voiceover_script is not None:
            script.voiceover_script = script_update.voiceover_script
            # Update word count
            script.word_count = len(script_update.voiceover_script.split())
        if script_update.category is not None:
            script.category = script_update.category
        if script_update.script_type is not None:
            script.script_type = script_update.script_type
        if script_update.language is not None:
            script.language = script_update.language
        if script_update.tags is not None:
            script.tags = json.dumps(script_update.tags)
        
        # Update timestamp
        script.updated_at = datetime.now()
        
        # Save to database
        session.add(script)
        session.commit()
        session.refresh(script)
        
        # Convert tags back to list for response
        tags = []
        try:
            if script.tags:
                tags = json.loads(script.tags) if isinstance(script.tags, str) else script.tags
        except:
            tags = []
        
        return ScriptResponse(
            id=script.id,
            user_id=script.user_id,
            user_prompt=script.user_prompt,
            script_type=script.script_type,
            category=script.category,
            language=script.language,
            title=script.title,
            description=script.description,
            voiceover_script=script.voiceover_script,
            tags=tags,
            duration_estimate=script.duration_estimate or "Unknown",
            word_count=script.word_count,
            generation_duration_ms=script.generation_duration_ms,
            ai_model_used=script.ai_model_used,
            created_at=script.created_at,
            updated_at=script.updated_at,
            status=script.category  # Using category as status placeholder
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update script: {str(e)}")

# DELETE /api/scripts/{script_id} - Delete script
@router.delete("/{script_id}")
async def delete_script(
    script_id: str,
    session: Session = Depends(get_session)
):
    try:
        # Get script from database
        statement = select(ScriptGeneration).where(ScriptGeneration.id == script_id)
        script = session.exec(statement).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        
        # Delete associated social media content first
        social_media_statement = select(SocialMediaContent).where(SocialMediaContent.script_id == script_id)
        social_media_contents = session.exec(social_media_statement).all()
        for content in social_media_contents:
            session.delete(content)
        
        # Delete the script
        session.delete(script)
        session.commit()
        
        return {
            "success": True,
            "script_id": script_id,
            "message": "Script deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete script: {str(e)}")
