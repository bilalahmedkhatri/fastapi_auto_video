from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import logging
import json
import time
from pathlib import Path
from sqlmodel import Session, select

# Import database models and session
try:
    from models.db_models import ScriptGeneration, SocialMediaContent, VideoGenerationProcess, VideoProcessStep, get_session
except ImportError:
    # Fallback if import fails
    logging.warning("Failed to import database models")
    ScriptGeneration = None
    SocialMediaContent = None
    VideoGenerationProcess = None
    get_session = None

# Import AI text generation API
try:
    from .ai_apis.text_gen_api import TextGenAPI
except ImportError:
    # Fallback if import fails
    logging.warning("Failed to import TextGenAPI")
    TextGenAPI = None

# Create API router
router = APIRouter(prefix="/script-generator", tags=["Script Generator"])

# Request/Response models
class ScriptGenerationRequest(BaseModel):
    """Request model for generating multiple scripts"""
    user_prompt: str
    script_types: Optional[List[str]] = ["short", "medium", "long"]
    voiceover_language: str = "English"
    category: str = "General"
    user_id: str = "anonymous"

class ScriptOptionResponse(BaseModel):
    """Response model for individual script options"""
    id: Optional[str] = None  # Database ID for the script
    script_type: str
    title: str
    description: str
    voiceover_script: str
    tags: List[str]
    category: str
    language: str
    duration_estimate: str
    word_count: int
    
    # NEW: Generation metadata fields (commented for future implementation)
    # generation_time: Optional[datetime] = None  # When the script was generated
    # ai_model_used: Optional[str] = None  # Which AI model generated this script
    # generation_parameters: Optional[Dict[str, Any]] = None  # Parameters used for generation
    # prompt_used: Optional[str] = None  # Original user prompt that generated this
    # processing_duration: Optional[float] = None  # Time taken to generate in seconds
    # quality_score: Optional[float] = None  # AI-calculated quality score (0-100)
    # generation_method: Optional[str] = None  # 'ai_generated', 'user_edited', 'merged'
    # generation_status: Optional[str] = None  # 'generating', 'completed', 'failed'
    # retry_count: Optional[int] = 0  # Number of retry attempts for generation
    # api_response_time: Optional[float] = None  # Time taken by AI API to respond
    # token_usage: Optional[Dict[str, int]] = None  # Tokens used: {'input': 150, 'output': 300}
    # generation_cost: Optional[float] = None  # Cost of generation in USD
    # user_feedback: Optional[Dict[str, Any]] = None  # User ratings and feedback

class ScriptGenerationResponse(BaseModel):
    """Response model for multiple script generation"""
    success: bool
    message: str
    scripts: List[ScriptOptionResponse]
    total_scripts: int
    
    # NEW: Batch generation metadata (commented for future implementation)
    # batch_generation_id: Optional[str] = None  # Unique ID for this generation batch
    # batch_start_time: Optional[datetime] = None  # When batch generation started
    # batch_end_time: Optional[datetime] = None  # When batch generation completed
    # total_processing_time: Optional[float] = None  # Total time for all scripts
    # successful_generations: Optional[int] = None  # Number of successful generations
    # failed_generations: Optional[int] = None  # Number of failed generations
    # average_quality_score: Optional[float] = None  # Average quality across all scripts
    # total_cost: Optional[float] = None  # Total cost for batch generation
    # ai_models_used: Optional[List[str]] = None  # List of AI models used in batch
    # generation_statistics: Optional[Dict[str, Any]] = None  # Detailed stats

class ScriptEditRequest(BaseModel):
    """Request model for editing a script"""
    script_index: int
    edit_instructions: str
    user_id: str = "anonymous"

class ScriptMergeRequest(BaseModel):
    """Request model for merging scripts"""
    script_indices: List[int]
    merge_instructions: Optional[str] = ""
    user_id: str = "anonymous"

class ScriptRegenerateRequest(BaseModel):
    """Request model for regenerating scripts"""
    user_prompt: str
    script_types: Optional[List[str]] = ["short", "medium", "long"] 
    voiceover_language: str = "English"
    category: str = "General"
    user_id: str = "anonymous"

class SocialMediaRequest(BaseModel):
    """Request model for generating social media descriptions"""
    script_index: int
    user_id: str = "anonymous"
    platforms: Optional[List[str]] = ["youtube", "instagram", "tiktok", "linkedin", "twitter", "facebook"]
    script_data: Optional[Dict[str, Any]] = None

class PlatformDescription(BaseModel):
    """Model for platform-specific description"""
    platform: str
    title: str
    description: str
    hashtags: List[str]
    seo_keywords: List[str]

class ThumbnailSuggestion(BaseModel):
    """Model for thumbnail suggestions"""
    title: str
    style: str
    elements: List[str]
    colors: Union[List[str], Dict[str, str]]  # Allow both list and dictionary formats

class SocialMediaResponse(BaseModel):
    """Response model for social media content generation"""
    success: bool
    message: str
    script_title: str
    script_type: str
    platform_descriptions: List[PlatformDescription]
    thumbnail_suggestions: List[ThumbnailSuggestion]
    general_seo_keywords: List[str]
    trending_hashtags: List[str]

# Note: Scripts are now stored in database instead of memory

def generate_script_with_ai(user_prompt: str, script_type: str, voiceover_language: str, category: str, user_id: str) -> Dict[str, Any]:
    """
    Generate a single script using AI API
    """
    if not TextGenAPI:
        raise Exception("TextGenAPI not available")
    
    try:
        # Create TextGenAPI instance
        text_gen = TextGenAPI()
        
        # Create a specific prompt for the script type
        type_prompts = {
            "short": f"Create a short 30-45 second video script about: {user_prompt}. Keep it concise and punchy.",
            "medium": f"Create a comprehensive 1-2 minute video script about: {user_prompt}. Include detailed explanations and practical examples.",
            "long": f"Create an in-depth 3-5 minute video script about: {user_prompt}. Provide thorough analysis, case studies, and comprehensive coverage.",
            "educational": f"Create an educational 2-4 minute video script about: {user_prompt}. Focus on teaching and learning outcomes.",
            "storytelling": f"Create a storytelling 2-3 minute video script about: {user_prompt}. Use narrative structure and engaging storytelling techniques.",
            "entertaining": f"Create an entertaining 1-2 minute video script about: {user_prompt}. Make it fun, engaging and entertaining."
        }
        
        enhanced_prompt = type_prompts.get(script_type, f"Create a video script about: {user_prompt}")
        
        # Generate content using AI
        ai_response = text_gen.generation_text(
            user_message=enhanced_prompt,
            voiceover_language=voiceover_language,
            platforms=["YouTube", "TikTok", "Instagram"],
            category=category,
            user=user_id
        )
        
        # Check for errors in AI response
        if isinstance(ai_response, dict) and "error" in ai_response:
            raise Exception(f"AI generation failed: {ai_response['error']}")
        
        # Calculate duration and word count based on script type
        duration_map = {
            "short": "30-45 seconds",
            "medium": "1-2 minutes", 
            "long": "3-5 minutes",
            "educational": "2-4 minutes",
            "storytelling": "2-3 minutes",
            "entertaining": "1-2 minutes"
        }
        
        # Extract voiceover script and calculate word count
        voiceover_script = ai_response.get("voiceover_script", "")
        word_count = len(voiceover_script.split()) if voiceover_script else 0
        
        # Generate additional AI tags using our keyword function
        script_data_for_tags = {
            "title": ai_response.get("title", user_prompt),
            "description": ai_response.get("description", ""),
            "category": category,
            "script_type": script_type
        }
        ai_tags_result = generate_ai_keywords_and_tags(script_data_for_tags, ["YouTube", "TikTok", "Instagram"])
        
        # Combine AI response tags with generated tags
        # ye code abhi ke liye band kiya hay, ho skta hay ye static code ho ya kuch or.
        # original_tags = ai_response.get("tags", [script_type, "ai-generated", "video", "content"])
        
        enhanced_tags = list(set(
            ai_response.get("tags", []) + 
            ai_tags_result.get("script_tags", []) + 
            [script_type, "ai-generated", "video", "content"]
        ))[:15]  # Limit to 15 tags
        
        return {
            "script_type": script_type,
            "title": ai_response.get("title", f"{script_type.title()} Guide: {user_prompt[:50]}"),
            "description": ai_response.get("description", f"A {script_type} video script about {user_prompt}"),
            "voiceover_script": voiceover_script,
            "tags": enhanced_tags,
            "category": category,
            "language": voiceover_language,
            "duration_estimate": duration_map.get(script_type, "1-2 minutes"),
            "word_count": word_count
        }
        
    except Exception as e:
        logging.error(f"Error generating {script_type} script with AI: {str(e)}")
        raise Exception(f"Failed to generate {script_type} script: {str(e)}")

def generate_multiple_scripts_with_ai(request: ScriptGenerationRequest) -> List[ScriptOptionResponse]:
    """
    Generate multiple script types using AI API
    """
    generated_scripts = []
    
    for script_type in request.script_types:
        try:
            script_data = generate_script_with_ai(
                user_prompt=request.user_prompt,
                script_type=script_type,
                voiceover_language=request.voiceover_language,
                category=request.category,
                user_id=request.user_id
            )
            
            generated_scripts.append(ScriptOptionResponse(**script_data))
            
        except Exception as e:
            logging.error(f"Failed to generate {script_type} script: {str(e)}")
            # Continue with other script types even if one fails
            continue
    
    return generated_scripts

def generate_ai_keywords_and_tags(script_data: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
    """
    Generate AI-powered keywords and tags for social media content
    Uses the existing AI functions from text_gen_api.py
    """
    try:
        if not TextGenAPI:
            logging.warning("TextGenAPI not available, falling back to static keywords")
            return {
                "seo_keywords": ["video", "content", "tutorial", "guide", "educational"],
                "hashtags": ["#Tutorial", "#Guide", "#Educational", "#Content"],
                "script_tags": ["tutorial", "guide", "content"]
            }
        
        # Create TextGenAPI instance
        text_gen = TextGenAPI()
        
        # Extract topic from script data
        topic = script_data.get('title', '') or script_data.get('description', '') or script_data.get('category', 'general content')
        
        # Generate AI-powered keywords using the existing function
        ai_keywords_result = text_gen.generate_search_keywords(
            platforms=platforms,
            topic=topic
        )
        
        # Extract keywords from AI result
        if ai_keywords_result and isinstance(ai_keywords_result, dict):
            seo_keywords = ai_keywords_result.get('keywords', [])
            if isinstance(seo_keywords, str):
                seo_keywords = [kw.strip() for kw in seo_keywords.split(',') if kw.strip()]
            
            # Generate hashtags from keywords
            hashtags = [f"#{kw.replace(' ', '').title()}" for kw in seo_keywords[:8]]
            
            # Add platform-specific hashtags
            for platform in platforms:
                if platform.lower() == "youtube":
                    hashtags.extend(["#YouTube", "#Tutorial", "#Guide"])
                elif platform.lower() == "instagram":
                    hashtags.extend(["#Instagram", "#Content", "#Amazing"])
                elif platform.lower() == "tiktok":
                    hashtags.extend(["#TikTok", "#fyp", "#viral"])
                elif platform.lower() == "linkedin":
                    hashtags.extend(["#LinkedIn", "#Professional", "#Industry"])
                elif platform.lower() == "twitter":
                    hashtags.extend(["#Twitter", "#Thread", "#Insights"])
                elif platform.lower() == "facebook":
                    hashtags.extend(["#Facebook", "#Community", "#Share"])
            
            # Remove duplicates and limit
            hashtags = list(dict.fromkeys(hashtags))[:15]
            seo_keywords = list(dict.fromkeys(seo_keywords))[:10]
            
            # CRITICAL FIX: Ensure we always return valid keywords (never empty)
            if not seo_keywords:
                # Fallback to extracting keywords from topic
                topic_words = [word.strip() for word in topic.lower().split() if len(word.strip()) > 3]
                seo_keywords = topic_words[:5] + ["video", "content", "tutorial"]
                seo_keywords = list(dict.fromkeys(seo_keywords))[:10]
            
            # Generate script tags (content-related tags)
            script_tags = [
                script_data.get('category', '').lower(),
                script_data.get('script_type', '').lower(),
                "ai-generated"
            ]
            script_tags.extend(seo_keywords[:5])  # Add top keywords as tags
            script_tags = [tag for tag in script_tags if tag]  # Remove empty tags
            
            logging.info(f"AI generated {len(seo_keywords)} SEO keywords and {len(hashtags)} hashtags for topic: {topic}")
            logging.info(f"SEO Keywords: {seo_keywords}")
            
            return {
                "seo_keywords": seo_keywords,
                "hashtags": hashtags, 
                "script_tags": script_tags
            }
        else:
            logging.warning("AI keyword generation returned empty or invalid result")
            # Fallback to enhanced static keywords based on script data
            category = script_data.get('category', 'general').lower()
            script_type = script_data.get('script_type', 'tutorial').lower()
            
            base_keywords = [category, script_type, "video", "content"]
            if 'technology' in topic.lower():
                base_keywords.extend(["tech", "innovation", "digital"])
            if 'tutorial' in topic.lower():
                base_keywords.extend(["howto", "guide", "learn"])
            
            hashtags = [f"#{kw.title()}" for kw in base_keywords[:8]]
            
            return {
                "seo_keywords": base_keywords,
                "hashtags": hashtags,
                "script_tags": base_keywords
            }
            
    except Exception as e:
        logging.error(f"Error generating AI keywords and tags: {str(e)}")
        # Fallback to basic static keywords
        return {
            "seo_keywords": ["video", "content", "tutorial", "guide"],
            "hashtags": ["#Tutorial", "#Guide", "#Content", "#Video"],
            "script_tags": ["tutorial", "guide", "content"]
        }

# Dummy data generator for now since the full script generator is complex
def generate_social_media_content(script_data: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
    """Generate social media content based on script data"""
    
    # Generate AI-powered keywords and tags
    ai_keywords_data = generate_ai_keywords_and_tags(script_data, platforms)
    
    platform_descriptions = []
    for platform in platforms:
        # Generate platform-specific content
        if platform == "youtube":
            title = f"🎬 {script_data.get('title', 'Video Title')} | Complete Guide"
            description = f"""Watch this comprehensive guide about {script_data.get('title', 'our topic')}!

{script_data.get('description', 'Amazing content awaits you in this video.')}

🔔 Subscribe for more content like this!
👍 Like if this helped you!
💬 Comment your thoughts below!

#YouTube #Tutorial #Guide"""
            hashtags = ["#YouTube", "#Tutorial", "#Guide", "#Educational", "#MustWatch"]
            
        elif platform == "instagram":
            title = f"✨ {script_data.get('title', 'Amazing Content')}"
            description = f"""{script_data.get('description', 'Check out this amazing content!')}

Follow for more! 👆

Tag someone who needs to see this! 👥"""
            hashtags = ["#Instagram", "#Content", "#Amazing", "#Follow", "#Share"]
            
        elif platform == "tiktok":
            title = f"🔥 {script_data.get('title', 'Viral Content')}"
            description = f"""POV: {script_data.get('description', 'You discover something amazing')}

Follow for Part 2! 👆

#fyp #viral #trending"""
            hashtags = ["#fyp", "#viral", "#trending", "#amazing", "#MustSee"]
            
        elif platform == "linkedin":
            title = f"Professional Insights: {script_data.get('title', 'Industry Knowledge')}"
            description = f"""Professional insight on {script_data.get('title', 'this important topic')}.

{script_data.get('description', 'Key takeaways for professionals in our industry.')}

What are your thoughts on this? Share in the comments below.

#LinkedIn #Professional #Industry #Insights"""
            hashtags = ["#LinkedIn", "#Professional", "#Industry", "#Insights", "#Business"]
            
        elif platform == "twitter":
            title = f"🧵 Thread: {script_data.get('title', 'Important Topic')}"
            description = f"""Thread on {script_data.get('title', 'this topic')} 🧵

{script_data.get('description', 'Key insights you need to know.')[:100]}...

1/5 👇"""
            hashtags = ["#Twitter", "#Thread", "#Important", "#MustRead", "#Insights"]
            
        elif platform == "facebook":
            title = f"📢 {script_data.get('title', 'Important Update')}"
            description = f"""Hey everyone! 👋

{script_data.get('description', 'Check out this important update!')}

What do you think? Let me know in the comments! 💬

Share if you found this helpful! 🔄"""
            hashtags = ["#Facebook", "#Update", "#Important", "#Share", "#Community"]
        
        else:
            title = f"{script_data.get('title', 'Great Content')}"
            description = f"{script_data.get('description', 'Amazing content for you!')}"
            hashtags = ["#Content", "#Amazing", "#MustSee"]
        
        # ye code abhi ke liye band kiya hay, ho skta hay ye static code ho ya kuch or.
        # seo_keywords=[script_data.get('category', 'general'), "content", "video", "tutorial", "guide"]
        
        # Use AI-generated keywords and merge with platform-specific hashtags
        # CRITICAL FIX: Ensure seo_keywords is always a list, never None or empty
        platform_seo_keywords = ai_keywords_data.get('seo_keywords', [])
        if not platform_seo_keywords or not isinstance(platform_seo_keywords, list):
            # Fallback to basic keywords if AI didn't generate any
            platform_seo_keywords = [
                script_data.get('category', 'general'),
                script_data.get('script_type', 'video'),
                "content", "tutorial", "guide", "educational"
            ]
        
        platform_hashtags = list(set(hashtags + ai_keywords_data.get('hashtags', [])[:10]))  # Merge and limit
        
        # IMPORTANT: Explicitly add seo_keywords to each platform object
        platform_descriptions.append(PlatformDescription(
            platform=platform,
            title=title,
            description=description,
            hashtags=platform_hashtags,
            seo_keywords=platform_seo_keywords  # ⭐ This ensures keywords are in platform object
        ))
    
    # Generate thumbnail suggestions
    thumbnail_suggestions = [
        ThumbnailSuggestion(
            title="Bold Text Overlay",
            style="High contrast with bold text",
            elements=["Large bold text", "Bright background", "Professional font"],
            colors=["#FF6B35", "#F7931E", "#FFD23F"]
        ),
        ThumbnailSuggestion(
            title="Face + Text Combination",
            style="Personal connection with clear messaging",
            elements=["Expressive face", "Clear text overlay", "Vibrant colors"],
            colors=["#4ECDC4", "#45B7D1", "#96CEB4"]
        ),
        ThumbnailSuggestion(
            title="Minimalist Design",
            style="Clean and professional",
            elements=["Simple text", "Clean background", "Modern typography"],
            colors=["#2C3E50", "#34495E", "#7F8C8D"]
        )
    ]
    
    # ye code abhi ke liye band kiya hay, ho skta hay ye static code ho ya kuch or.
    # "general_seo_keywords": ["video", "content", "tutorial", "guide", "educational", "helpful", "tips", "how-to"],
    # "trending_hashtags": ["#Trending", "#Viral", "#MustWatch", "#Educational", "#Amazing", "#Tutorial", "#Guide", "#Tips"]
    
    return {
        "success": True,
        "message": "Social media content generated successfully",
        "script_title": script_data.get("title", "Generated Content"),
        "script_type": script_data.get("script_type", "general"),
        "platform_descriptions": platform_descriptions,
        "thumbnail_suggestions": thumbnail_suggestions,
        "general_seo_keywords": ai_keywords_data.get('seo_keywords', ["video", "content", "tutorial", "guide"]),
        "trending_hashtags": ai_keywords_data.get('hashtags', ["#Tutorial", "#Guide", "#Content"])
    }

@router.post("/generate-social-media", response_model=SocialMediaResponse)
async def generate_social_media_content_endpoint(request: SocialMediaRequest, db: Session = Depends(get_session) if get_session else None):
    """
    Generate social media content for multiple platforms based on a script
    """
    try:
        logging.info(f"Generating social media content for user {request.user_id}, script index {request.script_index}")
        
        # Get script data from the request or database
        script_data = request.script_data
        
        if not script_data and db and ScriptGeneration:
            # Try to get user's scripts from database by index
            try:
                user_scripts_query = select(ScriptGeneration).where(
                    ScriptGeneration.user_id == request.user_id
                ).order_by(ScriptGeneration.created_at.desc())
                
                user_scripts = db.exec(user_scripts_query).all()
                
                if 0 <= request.script_index < len(user_scripts):
                    db_script = user_scripts[request.script_index]
                    script_data = {
                        "title": db_script.title,
                        "description": db_script.description,
                        "script_type": db_script.script_type,
                        "category": db_script.category,
                        "language": db_script.language,
                        "tags": json.loads(db_script.tags) if db_script.tags else []
                    }
            except Exception as e:
                logging.warning(f"Failed to retrieve script from database: {str(e)}")
        
        # If still no script data, create dummy data
        if not script_data:
            script_data = {
                "title": "Amazing Content Creation Guide",
                "description": "Learn how to create amazing content that engages your audience and drives results.",
                "script_type": "educational",
                "category": "Content Creation",
                "language": "English",
                "tags": ["content", "creation", "guide", "tutorial"]
            }
        
        # Generate social media content
        content_data = generate_social_media_content(script_data, request.platforms)
        
        # DEBUG: Log the generated content to verify seo_keywords are present
        logging.info(f"Generated social media content with {len(content_data['platform_descriptions'])} platforms")
        for idx, platform_desc in enumerate(content_data['platform_descriptions']):
            platform_obj = platform_desc if isinstance(platform_desc, dict) else platform_desc.dict()
            logging.info(f"Platform {idx} ({platform_obj.get('platform')}): "
                        f"hashtags={len(platform_obj.get('hashtags', []))}, "
                        f"seo_keywords={len(platform_obj.get('seo_keywords', []))} - {platform_obj.get('seo_keywords', [])[:3]}")
        
        # Convert to response model
        response = SocialMediaResponse(**content_data)
        
        # DEBUG: Verify response model has keywords
        logging.info(f"Response model: general_seo_keywords={response.general_seo_keywords[:5] if response.general_seo_keywords else 'EMPTY'}")
        logging.info(f"Response model: platform_descriptions[0].seo_keywords={response.platform_descriptions[0].seo_keywords[:5] if response.platform_descriptions and response.platform_descriptions[0].seo_keywords else 'EMPTY'}")
        
        # Store in database if available
        if SocialMediaContent and db:
            try:
                # Use script_index as temporary script_id since scripts aren't stored in DB yet
                temp_script_id = f"{request.user_id}_script_{request.script_index}"
                
                db_content = SocialMediaContent(
                    script_id=temp_script_id,
                    user_id=request.user_id,
                    platforms=json.dumps(request.platforms),
                    platform_descriptions=json.dumps([desc.dict() for desc in content_data["platform_descriptions"]]),
                    thumbnail_suggestions=json.dumps([thumb.dict() for thumb in content_data["thumbnail_suggestions"]]),
                    general_seo_keywords=json.dumps(content_data["general_seo_keywords"]),
                    trending_hashtags=json.dumps(content_data["trending_hashtags"]),
                    platforms_requested=json.dumps(request.platforms),
                    content_data=json.dumps(content_data),
                    generation_time_ms=100  # Mock value
                )
                db.add(db_content)
                db.commit()
                db.refresh(db_content)
                logging.info(f"Social media content saved to database with ID: {db_content.id}")
            except Exception as db_error:
                logging.error(f"Failed to save social media content to database: {str(db_error)}")
                # Continue without saving to database
        
        # Minimal update: mark 'social-media' step as completed in VideoGenerationProcess if active
        try:
            if VideoGenerationProcess:
                from models.video_process_manager import VideoGenerationProcessManager
                process_query = select(VideoGenerationProcess).where(
                    VideoGenerationProcess.user_id == request.user_id,
                    VideoGenerationProcess.status == "active"
                ).order_by(VideoGenerationProcess.started_at.desc())
                active_process = db.exec(process_query).first()
                if active_process:
                    manager = VideoGenerationProcessManager(db)
                    if manager.load_process(active_process.id):
                        manager.update_step_progress(
                            step_name="social-media",
                            status="completed",
                            data={"platforms": request.platforms}
                        )
        except Exception as step_error:
            logging.warning(f"Failed to update process step for social-media: {step_error}")
        
        return response
        
    except Exception as e:
        logging.error(f"Error generating social media content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Script Generator API",
        "database_available": ScriptGeneration is not None and get_session is not None,
        "endpoints": ["/generate", "/regenerate", "/generate-social-media", "/health"]
    }

# AI-powered script generation endpoints
@router.post("/generate", response_model=ScriptGenerationResponse)
async def generate_scripts(request: ScriptGenerationRequest, db: Session = Depends(get_session) if get_session else None):
    """Generate scripts using AI API and save to database"""
    
    print(f"Generating scripts with AI for: {request.user_prompt}")
    logging.info(f"Generating scripts for user {request.user_id} with request: {request}")
    
    try:
        # Check if database connection is available
        if not db or not ScriptGeneration or not get_session:
            return ScriptGenerationResponse(
                success=False,
                message="Database service unavailable. Please try again later.",
                scripts=[],
                total_scripts=0
            )
            
        # Check if TextGenAPI is available
        if not TextGenAPI:
            # Fallback to basic response if AI is not available
            return ScriptGenerationResponse(
                success=False,
                message="AI service temporarily unavailable. Please try again later.",
                scripts=[],
                total_scripts=0
            )
        
        generation_start_time = time.time()
        
        # Generate scripts using AI
        generated_scripts = generate_multiple_scripts_with_ai(request)
        
        if not generated_scripts:
            return ScriptGenerationResponse(
                success=False,
                message="Failed to generate scripts. Please check your prompt and try again.",
                scripts=[],
                total_scripts=0
            )
        
        generation_duration_ms = int((time.time() - generation_start_time) * 1000)
        
        # Save scripts to database instead of memory
        saved_scripts = []
        # Find the correct VideoProcessStep for "scripts" step of the active process
        step_process_id = None
        try:
            process_query = select(VideoGenerationProcess).where(
                VideoGenerationProcess.user_id == request.user_id,
                VideoGenerationProcess.status == "active"
            ).order_by(VideoGenerationProcess.started_at.desc())
            active_process = db.exec(process_query).first()
            if active_process:
                step_query = select(VideoProcessStep).where(
                    VideoProcessStep.process_id == active_process.id,
                    VideoProcessStep.step_name == "scripts"
                )
                step = db.exec(step_query).first()
                if step:
                    step_process_id = step.id
        except Exception as e:
            logging.warning(f"Could not find VideoProcessStep for scripts: {e}")

        for script in generated_scripts:
            try:
                # Create database record
                db_script = ScriptGeneration(
                    user_id=request.user_id,
                    user_prompt=request.user_prompt,
                    script_type=script.script_type,
                    category=script.category,
                    language=script.language,
                    title=script.title,
                    description=script.description,
                    voiceover_script=script.voiceover_script,
                    tags=json.dumps(script.tags) if isinstance(script.tags, list) else script.tags,
                    duration_estimate=script.duration_estimate,
                    word_count=script.word_count,
                    generation_duration_ms=generation_duration_ms,
                    ai_model_used="TextGenAPI",
                    step_process_id=step_process_id
                )
                # Save to database
                db.add(db_script)
                db.commit()
                db.refresh(db_script)
                # Add database ID to script response
                script_with_id = ScriptOptionResponse(
                    id=db_script.id,
                    script_type=script.script_type,
                    title=script.title,
                    description=script.description,
                    voiceover_script=script.voiceover_script,
                    tags=script.tags,
                    category=script.category,
                    language=script.language,
                    duration_estimate=script.duration_estimate,
                    word_count=script.word_count
                )
                saved_scripts.append(script_with_id)
                logging.info(f"Script saved to database with ID: {db_script.id}")
                
            except Exception as e:
                logging.error(f"Failed to save script to database: {str(e)}")
                # Continue with other scripts even if one fails to save
                continue
        
        if not saved_scripts:
            return ScriptGenerationResponse(
                success=False,
                message="Failed to save generated scripts to database.",
                scripts=[],
                total_scripts=0
            )
        
        logging.info(f"Successfully generated and saved {len(saved_scripts)} scripts for user {request.user_id}")
        
        # Update video process step if user has an active process
        try:
            if VideoGenerationProcess:
                from models.video_process_manager import VideoGenerationProcessManager
                # Get the most recent active process for this user
                process_query = select(VideoGenerationProcess).where(
                    VideoGenerationProcess.user_id == request.user_id,
                    VideoGenerationProcess.status == "active"
                ).order_by(VideoGenerationProcess.started_at.desc())
                
                active_process = db.exec(process_query).first()
                if active_process:
                    manager = VideoGenerationProcessManager(db)
                    if manager.load_process(active_process.id):
                        manager.update_step_progress(
                            step_name="scripts",
                            status="completed",
                            data={"scripts_count": len(saved_scripts), "generation_duration_ms": generation_duration_ms}
                        )
        except Exception as step_error:
            logging.warning(f"Failed to update process step: {step_error}")
        
        return ScriptGenerationResponse(
            success=True,
            message=f"Successfully generated {len(saved_scripts)} AI-powered scripts and saved to database!",
            scripts=saved_scripts,
            total_scripts=len(saved_scripts)
        )
        
    except Exception as e:
        logging.error(f"Error in script generation: {str(e)}")
        
        # Return error response
        return ScriptGenerationResponse(
            success=False,
            message=f"Script generation failed: {str(e)}",
            scripts=[],
            total_scripts=0
        )

@router.post("/regenerate", response_model=ScriptGenerationResponse)
async def regenerate_scripts(request: ScriptRegenerateRequest, db: Session = Depends(get_session) if get_session else None):
    """Regenerate scripts using AI with alternative approaches and save to database"""
    
    print(f"Regenerating scripts with AI for: {request.user_prompt}")
    logging.info(f"Regenerating scripts for user {request.user_id} with prompt: {request.user_prompt}")
    
    try:
        # Check if database connection is available
        if not db or not ScriptGeneration or not get_session:
            return ScriptGenerationResponse(
                success=False,
                message="Database service unavailable. Please try again later.",
                scripts=[],
                total_scripts=0
            )
            
        # Check if TextGenAPI is available
        if not TextGenAPI:
            return ScriptGenerationResponse(
                success=False,
                message="AI service temporarily unavailable. Please try again later.",
                scripts=[],
                total_scripts=0
            )
        
        generation_start_time = time.time()
        
        # Create modified prompts for regeneration (add variety keywords)
        variation_keywords = [
            "alternative approach to",
            "fresh perspective on", 
            "innovative method for",
            "creative take on",
            "revolutionary way to",
            "different angle on"
        ]
        
        regenerated_scripts = []
        
        for i, script_type in enumerate(request.script_types):
            try:
                # Add variation to the prompt for different results
                variation_keyword = variation_keywords[i % len(variation_keywords)]
                modified_prompt = f"{variation_keyword} {request.user_prompt}"
                
                script_data = generate_script_with_ai(
                    user_prompt=modified_prompt,
                    script_type=script_type,
                    voiceover_language=request.voiceover_language,
                    category=request.category,
                    user_id=request.user_id
                )
                
                regenerated_scripts.append(ScriptOptionResponse(**script_data))
                
            except Exception as e:
                logging.error(f"Failed to regenerate {script_type} script: {str(e)}")
                continue
        
        if not regenerated_scripts:
            return ScriptGenerationResponse(
                success=False,
                message="Failed to regenerate scripts. Please try again.",
                scripts=[],
                total_scripts=0
            )
        
        generation_duration_ms = int((time.time() - generation_start_time) * 1000)
        
        # Save regenerated scripts to database
        saved_scripts = []
        for script in regenerated_scripts:
            try:
                # Create database record
                db_script = ScriptGeneration(
                    user_id=request.user_id,
                    user_prompt=request.user_prompt,
                    script_type=script.script_type,
                    category=script.category,
                    language=script.language,
                    title=script.title,
                    description=script.description,
                    voiceover_script=script.voiceover_script,
                    tags=json.dumps(script.tags) if isinstance(script.tags, list) else script.tags,
                    duration_estimate=script.duration_estimate,
                    word_count=script.word_count,
                    generation_duration_ms=generation_duration_ms,
                    ai_model_used="TextGenAPI-Regenerated"
                )
                
                # Save to database
                db.add(db_script)
                db.commit()
                db.refresh(db_script)
                
                # Add database ID to script response
                script_with_id = ScriptOptionResponse(
                    id=db_script.id,
                    script_type=script.script_type,
                    title=script.title,
                    description=script.description,
                    voiceover_script=script.voiceover_script,
                    tags=script.tags,
                    category=script.category,
                    language=script.language,
                    duration_estimate=script.duration_estimate,
                    word_count=script.word_count
                )
                
                saved_scripts.append(script_with_id)
                logging.info(f"Regenerated script saved to database with ID: {db_script.id}")
                
            except Exception as e:
                logging.error(f"Failed to save regenerated script to database: {str(e)}")
                continue
        
        if not saved_scripts:
            return ScriptGenerationResponse(
                success=False,
                message="Failed to save regenerated scripts to database.",
                scripts=[],
                total_scripts=0
            )
        
        logging.info(f"Successfully regenerated and saved {len(saved_scripts)} scripts for user {request.user_id}")
        
        return ScriptGenerationResponse(
            success=True,
            message=f"Successfully regenerated {len(saved_scripts)} AI-powered scripts with fresh approaches and saved to database!",
            scripts=saved_scripts,
            total_scripts=len(saved_scripts)
        )
        
    except Exception as e:
        logging.error(f"Error in script regeneration: {str(e)}")
        
        return ScriptGenerationResponse(
            success=False,
            message=f"Script regeneration failed: {str(e)}",
            scripts=[],
            total_scripts=0
        )

@router.post("/edit/{script_index}", response_model=ScriptOptionResponse)
async def edit_script_mock(script_index: int, request: ScriptEditRequest):
    """Mock script editing endpoint"""
    raise HTTPException(status_code=501, detail="Script editing not implemented in mock version")

@router.post("/merge", response_model=ScriptOptionResponse)
async def merge_scripts_mock(request: ScriptMergeRequest):
    """Mock script merging endpoint"""
    raise HTTPException(status_code=501, detail="Script merging not implemented in mock version")

@router.post("/select/{script_index}")
async def select_script_for_video_mock(script_index: int, user_id: str):
    """Mock script selection endpoint"""
    return {
        "success": True,
        "message": "Script selected successfully (mock)",
        "ai_data": {"title": "Mock Script", "description": "Mock description"}
    }
