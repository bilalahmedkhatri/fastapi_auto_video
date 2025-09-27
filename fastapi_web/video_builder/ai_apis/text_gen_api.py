import os
import re
import logging
import json
from pprint import pprint
from openai import OpenAI
from dotenv import load_dotenv
from sqlmodel import Session, select
try:
    from .api_utils import ErrorLogger
except ImportError:
    from api_utils import ErrorLogger

# Import database models for dynamic model selection
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.db_models import AIModel, engine

load_dotenv()

# Get module-specific logger (inherits from main app configuration)
logger = logging.getLogger(__name__)

class TextGenAPI:
    def __init__(self):
        self.apis_token = os.getenv("QWEN_3_KEY_OPENROUTER")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.apis_token,
        )
    
    def get_available_models_info(self, limit: int = 10) -> dict:
        """
        Get information about available models from the database.
        
        Args:
            limit: Maximum number of models to return
            
        Returns:
            Dictionary with model information
        """
        try:
            with Session(engine) as session:
                # Get top free models by quality
                free_models = session.exec(
                    select(AIModel)
                    .where(AIModel.active == True, AIModel.is_free == True)
                    .order_by(AIModel.quality_score.desc())
                    .limit(limit)
                ).all()
                
                # Get top paid models by quality
                paid_models = session.exec(
                    select(AIModel)
                    .where(AIModel.active == True, AIModel.is_free == False)
                    .order_by(AIModel.quality_score.desc())
                    .limit(limit)
                ).all()
                
                return {
                    "free_models": [
                        {
                            "model_name": m.model_name,
                            "display_name": m.display_name,
                            "quality_score": m.quality_score,
                            "context_length": m.context_length,
                            "provider": m.provider
                        } for m in free_models
                    ],
                    "paid_models": [
                        {
                            "model_name": m.model_name,
                            "display_name": m.display_name,
                            "quality_score": m.quality_score,
                            "context_length": m.context_length,
                            "provider": m.provider,
                            "pricing_prompt": m.pricing_prompt
                        } for m in paid_models
                    ]
                }
        except Exception as e:
            logging.error(f"Error getting models info: {e}")
            return {"error": str(e)}

    @staticmethod
    def detect_input_type(user_message: str) -> str:
        """Detect if the user_message is a URL or plain text."""
        url_pattern = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:\S+)$', re.IGNORECASE)
        if url_pattern.match(user_message.strip()):
            return "url"
        return "text"

    @staticmethod
    def get_model_for_input(
        input_type: str, 
        response: dict = {}, 
        text_gen_failed: bool = False, 
        prefer_free: bool = True,
        min_quality_score: float = 5.0,
        fallback_attempts: int = 0
    ) -> str:
        """
        Return the model name based on input type, quality score, and availability.
        
        Args:
            input_type: Type of input ("url", "text", etc.)
            response: Previous response (for error checking)
            text_gen_failed: Whether previous generation failed
            prefer_free: Whether to prefer free models
            min_quality_score: Minimum quality score threshold
            fallback_attempts: Number of fallback attempts made
            
        Returns:
            Model name string
        """
        try:
            with Session(engine) as session:
                # Base query for active models
                query = select(AIModel).where(AIModel.active == True)
                
                # Apply filters based on preferences and fallback level
                if fallback_attempts == 0:
                    # First attempt: Best quality free models
                    if prefer_free:
                        query = query.where(AIModel.is_free == True)
                    if min_quality_score > 0:
                        query = query.where(AIModel.quality_score >= min_quality_score)
                    
                elif fallback_attempts == 1:
                    # Second attempt: Lower quality threshold or include paid models
                    if prefer_free:
                        query = query.where(AIModel.is_free == True)
                        query = query.where(AIModel.quality_score >= max(1.0, min_quality_score - 3.0))
                    else:
                        # Include low-cost paid models
                        query = query.where(
                            (AIModel.is_free == True) | 
                            (AIModel.pricing_prompt <= 0.001)  # Very cheap models
                        )
                        
                elif fallback_attempts == 2:
                    # Third attempt: Any decent model (free or cheap paid)
                    query = query.where(
                        (AIModel.is_free == True) | 
                        (AIModel.pricing_prompt <= 0.01)  # Moderately cheap
                    ).where(AIModel.quality_score >= 1.0)
                    
                else:
                    # Final fallback: Any active model
                    pass  # No additional filters
                
                # Order by quality score and free status
                query = query.order_by(
                    AIModel.is_free.desc(),  # Free models first
                    AIModel.quality_score.desc(),  # Higher quality first
                    AIModel.context_length.desc()  # Longer context preferred
                )
                
                # Get models based on input type preferences
                models = session.exec(query).all()
                
                if not models:
                    # If no models found, use hardcoded fallbacks
                    return TextGenAPI._get_hardcoded_fallback(input_type, text_gen_failed, response)
                
                # Filter by input type capabilities if possible
                suitable_models = []
                for model in models:
                    if TextGenAPI._is_model_suitable_for_input(model, input_type):
                        suitable_models.append(model)
                
                # If no suitable models found, use any available model
                if not suitable_models:
                    suitable_models = models
                
                # Return the best model
                best_model = suitable_models[0]
                logging.info(f"Selected model: {best_model.model_name} (Quality: {best_model.quality_score}, Free: {best_model.is_free})")
                return best_model.model_name
                
        except Exception as e:
            logging.error(f"Error selecting model from database: {e}")
            return TextGenAPI._get_hardcoded_fallback(input_type, text_gen_failed, response)

    @staticmethod
    def _is_model_suitable_for_input(model: AIModel, input_type: str) -> bool:
        """Check if a model is suitable for the given input type."""
        try:
            if not model.capabilities:
                return True  # Assume suitable if no capability info
                
            capabilities = json.loads(model.capabilities)
            input_modalities = capabilities.get('input_modalities', [])
            
            # For URL input, prefer models that can handle web content
            if input_type == "url":
                # Prefer models with web search capabilities or multimodal input
                if 'web' in str(capabilities).lower() or len(input_modalities) > 1:
                    return True
                # OpenAI models generally handle web content well
                if 'openai' in model.model_name.lower():
                    return True
                    
            # For text input, any text-capable model is fine
            elif input_type == "text":
                return 'text' in input_modalities or len(input_modalities) == 0
                
            return True  # Default to suitable
            
        except Exception:
            return True  # Assume suitable on error

    @staticmethod
    def _get_hardcoded_fallback(input_type: str, text_gen_failed: bool, response: dict) -> str:
        """Hardcoded fallback models when database lookup fails."""
        if input_type and text_gen_failed:
            if "error" in response:
                return "deepseek/deepseek-r1-0528:free"
            return "google/gemini-2.5-flash-preview-05-20"
        elif input_type == "url":
            return "openai/gpt-4o-mini-search-preview-2025-03-11"
        elif input_type == "text":
            return "tngtech/deepseek-r1t2-chimera:free"
        else:
            return "openai/gpt-4o-mini"


    @staticmethod
    def is_error_response(response) -> bool:
        """
        Detect if the response contains an error.
        """
        if isinstance(response, dict) and "error" in response:
            return True
        if isinstance(response, str):
            error_phrases = [
                "could not generate",
                "please provide",
                "error",
                "failed",
                "not able to",
                "unable to",
                "clarification"
            ]
            if any(phrase in response.lower() for phrase in error_phrases):
                return True
        return False

    def ai_generated_text(
        self,
        user_message: str,
        voiceover_language: str = "English",
        platforms: list[str] = ["YouTube"],
        category: str = "",
        text_gen_failed: bool = False,
        user: str = "unknown",
        fallback_attempts: int = 0,
        max_fallbacks: int = 3
    ) -> dict:
        """
        Generate YouTube content using AI, with robust handling for ambiguous or missing input.
        """
        # Defensive: Check for empty or too-short input
        if not user_message or len(user_message.strip()) < 5:
            return {"error": "Please provide a valid URL or a detailed topic/description."}

        input_type = self.detect_input_type(user_message)
        model_name = self.get_model_for_input(
            input_type, 
            text_gen_failed=text_gen_failed,
            fallback_attempts=fallback_attempts
        )
        # Force the AI to always generate content, even if input is ambiguous
        # - Please output the transcript in JSON with segments containing 'id', 'seek', 'start', 'end', 'text', and a 'words' list for each word including its 'text','start','end','confidence'.
        prompt = f"""
        You are a professional assistant for creating YouTube, tiktok, facebook, and snapchat short and full video content about {category} on {user_message}.

        Instructions:
        1. If a URL is provided in the user input, extract the news content from that URL.
        2. If no URL is present, treat the user input as a topic or description and generate content as best as possible, even if the input is ambiguous or short.
        3. Based on the news content or topic, do the following:
        - Generate a short, 1-minute voiceover script in {voiceover_language}.
        - Generate a catchy and professional video title.
        - Create a detailed, informative, and SEO-optimized {platforms} description.
        - Generate a list of 8-12 relevant tags.
        If the input is ambiguous, do your best to infer the topic and proceed. Do NOT ask the user for clarification, always generate a result.
        Output must be a valid and clean JSON object with this structure:
        {{
            "title": "string",
            "description": "string",
            "voiceover_script": "string",
            "Category": {{"Integer": "str"}},
            "tags": ["string", "string", "..."],
            "language": "{voiceover_language}",
        }}"""
        
        # prompt = f"""
        # You are a professional assistant for creating YouTube content about breaking news on {user_message}.

        # Instructions:
        # 1. If a URL is provided in the user input, extract the news content from that URL.
        # 2. If no URL is present, treat the user input as a topic or description and generate content as best as possible, even if the input is ambiguous or short.
        # 3. Based on the news content or topic, do the following:
        # - Generate a short, 1-minute voiceover script in {voiceover_language}.
        # - Generate a catchy and professional video title.
        # - Create a detailed, informative, and SEO-optimized {platforms} description.
        # - Generate a list of 8-12 relevant tags.
        # - Choose the best matching category from this list {categories}. 
        # If the input is ambiguous, do your best to infer the topic and proceed. Do NOT ask the user for clarification, always generate a result.
        # Output must be a valid and clean JSON object with this structure:
        # {{
        #     "title": "string",
        #     "description": "string",
        #     "voiceover_script": "string",
        #     "Category": {{"Integer": "str"}},
        #     "tags": ["string", "string", "..."],
        #     "language": "{voiceover_language}",
        # }}"""
        
        try:
            logging.info(
                f"Sending {input_type} to openrouter.io API for content generation...")
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            result = response.choices[0].message.content
            logging.info(f"Received response from OpenAI API and generating data using {model_name}.")
            
            # Check if AI returns a clarification request - treat as error
            clarification_phrases = [
                "please resubmit your request",
                "would you please",
                "i don't see any provided url",
                "i need either",
                "to create your youtube content package"
            ]
            if isinstance(result, str) and any(phrase in result.lower() for phrase in clarification_phrases):
                error_msg = "AI could not generate content. Please provide a more detailed topic or try again."
                logging.error(error_msg)
                return {"error": error_msg}
            
            # If result is already a dict, return it
            if isinstance(result, dict):
                return result
                
            # Try to parse JSON response
            try:
                if isinstance(result, str):
                    cleaned = re.sub(r'\s+', ' ', result)
                    cleaned = re.sub(r'//.*?\n', '', cleaned)  # Remove // comments
                    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                    if match:
                        clean_result = match.group()
                    else:
                        clean_result = cleaned
                    
                    # Log the response for debugging
                    import sys
                    ErrorLogger.log_ai_response_error(
                        error=None,
                        response=clean_result,
                        user=user,
                        error_line=0,
                        file_name=__file__+"testing",
                        log_dir="logs"
                    )
                    
                    parsed_result = json.loads(clean_result)
                    
                    # Validate that we have the required fields
                    required_fields = ["title", "description", "voiceover_script", "tags"]
                    missing_fields = [field for field in required_fields if field not in parsed_result]
                    if missing_fields:
                        error_msg = f"API response missing required fields: {missing_fields}"
                        logging.error(error_msg)
                        return {"error": error_msg}
                    
                    return parsed_result
                else:
                    error_msg = "AI response is not a string and cannot be parsed."
                    logging.error(error_msg)
                    return {"error": error_msg}
                    
            except Exception as json_err:
                logging.error(f"Error parsing AI response to dict: {json_err}")
                # Use ErrorLogger to save error details
                import sys
                error_line = sys.exc_info()[-1].tb_lineno if sys.exc_info()[-1] else 0
                ErrorLogger.log_ai_response_error(
                    error=json_err,
                    response=result,
                    user=user,
                    error_line=error_line,
                    file_name=__file__,
                    log_dir="logs"
                )
                return {"error": f"AI response could not be parsed as JSON: {str(json_err)}"}
                
        except Exception as e:
            # Check if we can try a fallback model
            if fallback_attempts < max_fallbacks:
                logging.warning(f"Model {model_name} failed (attempt {fallback_attempts + 1}), trying fallback...")
                return self.ai_generated_text(
                    user_message=user_message,
                    voiceover_language=voiceover_language,
                    platforms=platforms,
                    category=category,
                    text_gen_failed=True,
                    user=user,
                    fallback_attempts=fallback_attempts + 1,
                    max_fallbacks=max_fallbacks
                )
            
            # Use ErrorLogger for general errors
            import sys
            error_line = sys.exc_info()[-1].tb_lineno if sys.exc_info()[-1] else 0
            ErrorLogger.log_ai_response_error(
                error=e,
                response="Error in ai_generated_text",
                user=user,
                error_line=error_line,
                file_name=__file__,
                log_dir="logs"
            )
            return {"error": f"API call failed after {fallback_attempts + 1} attempts: {str(e)}"}
        
    def generation_text(
        self,
        user_message: str,
        voiceover_language: str = "English",
        platforms: list[str] = ["YouTube"],
        category: str = "",
        user: str = "unknown",
        max_retries: int = 0  # Set to 0 to disable retries
    ):
        """
        Generate text content with no retry mechanism.
        Returns a valid response or immediately stops with error.
        """
        response = self.ai_generated_text(
            user_message=user_message,
            voiceover_language=voiceover_language,
            platforms=platforms,
            category=category,
            user=user,
            text_gen_failed=False,
        )
        
        # If there's an error, stop immediately and return the error
        if self.is_error_response(response):
            return response  # Return the error response
        
        # Only return if we got a valid response
        return response

    def generate_search_keywords(self, platforms: list[str], topic: str, max_keywords: int = 8) -> dict:
        """
        Generate search keywords for a given topic and platforms.
        Returns a dict with keywords or an error message. No retry mechanism.
        """
        if not topic or len(topic) < 3:
            error_msg = "Please provide a valid topic."
            logging.error(error_msg)
            return {"error": error_msg}

        model_name = self.get_model_for_input("text", prefer_free=True, min_quality_score=3.0)
        prompt = f"""
        Generate {max_keywords} relevant search keywords for the topic '{topic}'.
        Consider the following platforms: {', '.join(platforms)}.
        For each platform, suggest category that are relevant to the topic.
        Return an only JSON object.
        """

        try:
            logging.info("Sending prompt to AI API for keyword generation...")
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            result = response.choices[0].message.content
            
            if not result or result.strip() == "":
                error_msg = "API returned empty response for keyword generation"
                logging.error(error_msg)
                return {"error": error_msg}
            
            try:
                # Extract only the JSON object from the response
                match = re.search(r'\{.*\}', result, re.DOTALL)
                if match:
                    cleaned = match.group()
                    cleaned = re.sub(r'//.*?\n', '', cleaned)  # Remove // comments
                    dt = json.loads(cleaned)
                    print(type(dt), dt)
                    return dt
                else:
                    error_msg = "No JSON object found in AI response."
                    logging.error(error_msg)
                    return {"error": error_msg}
            except json.JSONDecodeError as e:
                error_msg = f"Error parsing AI response: {e}"
                logging.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error generating search keywords: {e}"
            logging.error(error_msg)
            return {"error": error_msg}

    def ai_select_youtube_category(self, title: str, description: str, categories: list, model_name: str = None) -> dict:
        """
        Use AI to select the best YouTube category from the list, given title and description.
        Returns a dict: {"id": ..., "title": ...}
        """
        if not model_name:
            model_name = self.get_model_for_input("text", None)
        prompt = (
            "Given the following YouTube video title and description, "
            "choose the best matching category from this list. "
            "Return ONLY a JSON object with the best category's id and title.\n\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Categories: {json.dumps(categories)}\n\n"
            "Respond with: {\"id\": \"...\", \"title\": \"...\"}"
        )
        try:
            logging.info("Sending prompt to AI API...")
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            result = response.choices[0].message.content
            if isinstance(result, dict) and "id" in result and "title" in result:
                return result
            try:
                match = re.search(r'\{.*\}', str(result), re.DOTALL)
                if match:
                    return json.loads(match.group())
                return {}
            except Exception as json_err:
                logging.error(f"Error parsing AI category response: {json_err} | Response: {result}")
                return {}
        except Exception as e:
            logging.error(f"Error selecting YouTube category: {e}")
            return {}
        
    
    def generate_search_query(self, description: str) -> str:
        """Generate search query with no retry mechanism. Returns empty string on failure."""
        try:
            model_name = self.get_model_for_input("text", prefer_free=True, min_quality_score=2.0)
            logging.info("Sending prompt to AI API...")
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": description}
                ],
                stream=False
            )
            result = response.choices[0].message.content
            
            if not result or result.strip() == "":
                logging.error("API returned empty search query")
                return ""
                
            return result.strip()
        except Exception as e:
            logging.error(f"Error generating search query: {e}")
            return ""  # Return empty string to indicate failure

    def generate_social_media_content(self, prompt: str) -> dict:
        """
        Generate social media content using AI.
        
        Args:
            prompt: The formatted prompt for social media generation
            
        Returns:
            Dictionary with social media content or empty dict on failure
        """
        try:
            model_name = self.get_model_for_input("text", prefer_free=True, min_quality_score=4.0)
            logging.info("Generating social media content with AI...")
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a social media marketing expert specialized in creating platform-specific content."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            result = response.choices[0].message.content
            
            if not result or result.strip() == "":
                logging.error("API returned empty social media content")
                return {}
                
            # Try to extract JSON from the response
            try:
                match = re.search(r'\{.*\}', result, re.DOTALL)
                if match:
                    social_data = json.loads(match.group())
                    return social_data
                else:
                    # Try parsing the entire response as JSON
                    return json.loads(result)
            except json.JSONDecodeError as json_err:
                logging.error(f"Error parsing social media JSON: {json_err} | Response: {result}")
                return {}
                
        except Exception as e:
            logging.error(f"Error generating social media content: {e}")
            return {}

if __name__ == '__main__':
#     # user_message = "https://www.forbes.com/sites/phisanuphromchanya/2025/07/02/thailands-50-richest-2025-collective-wealth-led-by-the-red-bull-family-jumps-11-to-cross-170-billion/"
    # user_message = "Elon Musk's Secret AI Project Revealed: ChatGPT Killer Coming Soon?"
    # output = TextGenAPI().generation_text(
    #     user_message=,
    #     voiceover_language="English",
    #     category="news"
    # )
    # pprint(output)
    user_message = """
    You are an expert prompt engineer specializing in image search. Your task is to convert a user's natural language description into a single, concise, and highly effective one-line search query for an image API.

Your internal process will be:

Deconstruct the Idea: First, mentally break down the user's request into its core components. Identify the Subject (who or what), Action (what is happening), Setting (the environment), Mood (the feeling or atmosphere), and any implied Style/Composition (visual aesthetic).
Synthesize the Query: Combine the most powerful and descriptive keywords from your analysis into a single, cohesive search query. Prioritize words that capture the essence and emotion of the request.
The final output MUST be only the search query on a single line. Do not include any labels, explanations, or quotation marks.

--- USER IDEA ---

BREAKING NEWS: Elon Musk's xAI has unveiled a MAJOR upgrade to its Grok chatbot ecosystem! In this video, we cover:\n\n🔥 What's new in Grok's advanced reasoning and real-time capabilities\n🔥 How xAI's collaboration with Tesla and X (Twitter) could reshape AI\n🔥 Musk's bold claims about AGI timelines and open-source ambitions\n\nLike this video? SUBSCRIBE for daily AI news breakdowns!\n\n#ElonMusk #xAI #GrokAI #ArtificialIntelligence #TechNews\n\nDISCLAIMER: All information is based on publicly available sources. This is not financial advice.", 'voiceover_script': '(Upbeat tech-themed intro music fades)\n\n"Elon Musk just shook the AI world again! xAI's Grok chatbot received revolutionary updates that could change how we interact with AI forever. The new Grok reportedly handles complex reasoning 4x faster while integrating real-time data from Musk's X platform.\n\nIndustry insiders whisper this could be phase one of Tesla's rumored 'AI cockpit' - where Grok might eventually power self-driving systems. Even more explosive? Musk hinted at making xAI's models open-source during a Spaces Q&A yesterday.\n\nBut critics warn the rushed deployment might repeat Twitter's chaos. Will Grok become the people's AI or another Musk moonshot? Sound off below! This is AI revolution unfolding LIVE."\n\n(Outro music swells)
    """
    output = TextGenAPI().generate_search_query(
        description=user_message
    )
    pprint(output)

