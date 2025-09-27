import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

try:
    from ai_apis.text_gen_api import TextGenAPI
    from ai_apis.api_utils import ErrorLogger
except ImportError:
    from video_builder.ai_apis.text_gen_api import TextGenAPI
    from video_builder.ai_apis.api_utils import ErrorLogger

# Configure logging
logger = logging.getLogger(__name__)
class ScriptType(Enum):
    """Enumeration of different script types/styles"""
    SHORT = "short"
    MEDIUM = "medium" 
    LONG = "long"
    EDUCATIONAL = "educational"
    STORYTELLING = "storytelling"
    ENTERTAINING = "entertaining"

@dataclass
class ScriptOption:
    """Data class for individual script options"""
    script_type: ScriptType
    title: str
    description: str
    voiceover_script: str
    tags: List[str]
    category: str
    language: str
    duration_estimate: str
    word_count: int

class ScriptGenerator:
    """Enhanced script generator for multiple video options"""
    
    def __init__(self):
        self.text_gen_api = TextGenAPI()
        self.base_dir = Path(__file__).resolve().parent
        
    def generate_multiple_scripts(
        self,
        user_prompt: str,
        script_types: List[ScriptType] = None,
        voiceover_language: str = "English",
        category: str = "General",
        user: str = "unknown"
    ) -> List[ScriptOption]:
        """
        Generate multiple script variations based on user prompt and selected types.
        
        Args:
            user_prompt: The topic or prompt provided by user
            script_types: List of script types to generate (defaults to SHORT, MEDIUM, LONG)
            voiceover_language: Language for voiceover
            category: Content category
            user: User identifier
            
        Returns:
            List of ScriptOption objects
        """
        if script_types is None:
            script_types = [ScriptType.SHORT, ScriptType.MEDIUM, ScriptType.LONG]
            
        scripts = []
        
        for script_type in script_types:
            try:
                logging.info(f"Generating {script_type.value} script for: {user_prompt}")
                
                script_data = self._generate_single_script(
                    user_prompt=user_prompt,
                    script_type=script_type,
                    voiceover_language=voiceover_language,
                    category=category,
                    user=user
                )
                
                if script_data and "error" not in script_data:
                    script_option = self._create_script_option(script_data, script_type)
                    scripts.append(script_option)
                else:
                    logging.error(f"Failed to generate {script_type.value} script: {script_data.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logging.error(f"Exception generating {script_type.value} script: {e}")
                ErrorLogger.log_ai_response_error(
                    error=e,
                    response=str(e),
                    user=user,
                    error_line=0,
                    file_name=__file__
                )
        
        return scripts
    
    def _generate_single_script(
        self,
        user_prompt: str,
        script_type: ScriptType,
        voiceover_language: str,
        category: str,
        user: str
    ) -> Dict:
        """Generate a single script based on type specifications"""
        
        # Define script specifications for each type
        script_specs = {
            ScriptType.SHORT: {
                "duration": "30-45 seconds",
                "word_count": "75-115 words", 
                "style": "Quick, punchy, attention-grabbing. Focus on key points only.",
                "structure": "Hook → Main Point → Call to Action"
            },
            ScriptType.MEDIUM: {
                "duration": "1-2 minutes",
                "word_count": "150-300 words",
                "style": "Balanced information with engaging delivery. Include context and examples.",
                "structure": "Hook → Context → Main Content → Examples → Conclusion"
            },
            ScriptType.LONG: {
                "duration": "3-5 minutes", 
                "word_count": "450-750 words",
                "style": "In-depth exploration with detailed explanations and multiple perspectives.",
                "structure": "Hook → Background → Detailed Analysis → Examples → Implications → Conclusion"
            },
            ScriptType.EDUCATIONAL: {
                "duration": "2-4 minutes",
                "word_count": "300-600 words",
                "style": "Clear, informative, step-by-step explanations. Use teaching techniques.",
                "structure": "Learning Objective → Explanation → Examples → Practice → Summary"
            },
            ScriptType.STORYTELLING: {
                "duration": "2-3 minutes",
                "word_count": "300-450 words", 
                "style": "Narrative approach with characters, conflict, and resolution. Emotional engagement.",
                "structure": "Setting → Character/Problem → Journey → Resolution → Lesson"
            },
            ScriptType.ENTERTAINING: {
                "duration": "1-2 minutes",
                "word_count": "150-300 words",
                "style": "Fun, engaging, humorous where appropriate. Keep audience entertained.",
                "structure": "Attention-Grabber → Entertaining Content → Surprising Facts → Fun Conclusion"
            }
        }
        
        spec = script_specs[script_type]
        
        prompt = f"""
        You are a professional video script writer specializing in creating engaging content for social media platforms.
        
        Topic: {user_prompt}
        Category: {category}
        Language: {voiceover_language}
        
        Script Requirements:
        - Type: {script_type.value.upper()}
        - Duration: {spec['duration']}
        - Word Count: {spec['word_count']}
        - Style: {spec['style']}
        - Structure: {spec['structure']}
        
        Instructions:
        1. Create a compelling script that follows the specified structure and style
        2. Ensure the word count fits within the specified range
        3. Make it suitable for voiceover (natural speech patterns, clear pronunciation)
        4. Include engaging hooks and clear transitions
        5. Optimize for the target platforms (YouTube Shorts, TikTok, Instagram Reels)
        
        Output must be a valid JSON object with this exact structure:
        {{
            "title": "Compelling video title (50-60 characters)",
            "description": "SEO-optimized description with relevant keywords and hashtags (150-300 words)",
            "voiceover_script": "Complete script for voiceover (follow word count requirements)",
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],
            "category": "{category}",
            "language": "{voiceover_language}",
            "script_type": "{script_type.value}",
            "estimated_duration": "{spec['duration']}",
            "word_count": "actual_word_count_number"
        }}
        """
        
        try:
            return self.text_gen_api.ai_generated_text(
                user_message=user_prompt,
                voiceover_language=voiceover_language,
                platforms=["YouTube", "TikTok", "Instagram"],
                category=category,
                user=user
            )
        except Exception as e:
            logging.error(f"Error in AI text generation: {e}")
            return {"error": str(e)}
    
    def _create_script_option(self, script_data: Dict, script_type: ScriptType) -> ScriptOption:
        """Create a ScriptOption object from AI response data"""
        
        # Count words in voiceover script
        word_count = len(script_data.get("voiceover_script", "").split())
        
        return ScriptOption(
            script_type=script_type,
            title=script_data.get("title", "Untitled"),
            description=script_data.get("description", ""),
            voiceover_script=script_data.get("voiceover_script", ""),
            tags=script_data.get("tags", []),
            category=script_data.get("category", "General"),
            language=script_data.get("language", "English"),
            duration_estimate=script_data.get("estimated_duration", "Unknown"),
            word_count=word_count
        )
    
    def regenerate_scripts(
        self,
        user_prompt: str,
        script_types: List[ScriptType] = None,
        voiceover_language: str = "English", 
        category: str = "General",
        user: str = "unknown"
    ) -> List[ScriptOption]:
        """
        Regenerate scripts if user doesn't like the initial options.
        This uses slightly different prompting to get varied results.
        """
        logging.info("Regenerating scripts with alternative approach...")
        
        if script_types is None:
            script_types = [ScriptType.SHORT, ScriptType.MEDIUM, ScriptType.LONG]
        
        # Add variation instruction to get different results
        original_prompt = user_prompt
        varied_prompt = f"{original_prompt} (Please provide a fresh, alternative perspective on this topic)"
        
        return self.generate_multiple_scripts(
            user_prompt=varied_prompt,
            script_types=script_types,
            voiceover_language=voiceover_language,
            category=category,
            user=user
        )
    
    def merge_scripts(
        self, 
        script_options: List[ScriptOption],
        merge_instructions: str = "",
        user: str = "unknown"
    ) -> Optional[ScriptOption]:
        """
        Merge multiple selected scripts into one cohesive script.
        
        Args:
            script_options: List of ScriptOption objects to merge
            merge_instructions: Optional instructions for how to merge
            user: User identifier
            
        Returns:
            New ScriptOption with merged content
        """
        if not script_options or len(script_options) < 2:
            logging.error("Need at least 2 scripts to merge")
            return None
            
        try:
            # Prepare content for merging
            scripts_content = []
            for i, option in enumerate(script_options, 1):
                scripts_content.append(f"""
                Script {i} ({option.script_type.value}):
                Title: {option.title}
                Script: {option.voiceover_script}
                """)
            
            merge_prompt = f"""
            You are a professional script editor. Your task is to merge the following scripts into one cohesive, engaging video script.
            
            Scripts to merge:
            {''.join(scripts_content)}
            
            Merge Instructions: {merge_instructions if merge_instructions else "Create a balanced combination that incorporates the best elements from each script."}
            
            Guidelines:
            1. Create a smooth, natural flow between different sections
            2. Eliminate redundancy while keeping important information
            3. Maintain engaging tone throughout
            4. Ensure the final script has good pacing for voiceover
            5. Keep the merged script between 200-500 words
            
            Output must be a valid JSON object with this structure:
            {{
                "title": "New title for merged script",
                "description": "SEO-optimized description for merged content",
                "voiceover_script": "Complete merged script",
                "tags": ["combined", "relevant", "tags"],
                "category": "General",
                "language": "English",
                "script_type": "merged",
                "estimated_duration": "estimated_duration",
                "word_count": "actual_word_count"
            }}
            """
            
            # Use text generation API for merging
            merge_result = self.text_gen_api.ai_generated_text(
                user_message=merge_prompt,
                voiceover_language="English",
                platforms=["YouTube", "TikTok", "Instagram"],
                category="General",
                user=user
            )
            
            if merge_result and "error" not in merge_result:
                return self._create_script_option(merge_result, ScriptType.MEDIUM)
            else:
                logging.error(f"Failed to merge scripts: {merge_result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logging.error(f"Exception merging scripts: {e}")
            ErrorLogger.log_ai_response_error(
                error=e,
                response=str(e),
                user=user,
                error_line=0,
                file_name=__file__
            )
            return None
    
    def generate_social_media_content(
        self, 
        script: ScriptOption,
        platforms: List[str] = None
    ) -> Optional[Dict]:
        """
        Generate platform-specific social media descriptions for a script.
        
        Args:
            script: The ScriptOption to generate social media content for
            platforms: List of platforms to generate content for
            
        Returns:
            Dictionary with platform descriptions, thumbnails, and SEO data
        """
        if platforms is None:
            platforms = ["youtube", "instagram", "tiktok", "linkedin", "twitter", "facebook"]
            
        try:
            logging.info(f"Generating social media content for script: {script.title}")
            
            social_media_prompt = f"""
            You are a social media marketing expert. Create platform-specific descriptions and marketing content for the following video script:
            
            SCRIPT DETAILS:
            Title: {script.title}
            Type: {script.script_type.value}
            Category: {script.category}
            Description: {script.description}
            Duration: {script.duration_estimate}
            Script Content: {script.voiceover_script[:500]}...
            
            Generate content for these platforms: {', '.join(platforms)}
            
            For each platform, consider:
            - YouTube: Long, keyword-rich descriptions with SEO optimization
            - Instagram/TikTok: Short, punchy with trending hashtags
            - LinkedIn: Professional, business-focused tone
            - Twitter/X: Concise hooks with engagement hashtags  
            - Facebook: Engaging but semi-formal, shareable content
            
            Also provide:
            1. Platform-specific descriptions with appropriate hashtags
            2. SEO keywords for each platform
            3. Thumbnail title suggestions (3-5 options)
            4. General trending hashtags
            5. Click-through optimized titles
            
            Output must be a valid JSON object with this exact structure:
            {{
                "platform_descriptions": [
                    {{
                        "platform": "youtube",
                        "title": "SEO optimized title",
                        "description": "Long detailed description with keywords",
                        "hashtags": ["#keyword1", "#keyword2"],
                        "seo_keywords": ["keyword1", "keyword2", "keyword3"]
                    }},
                    {{
                        "platform": "instagram",
                        "title": "Catchy short title",
                        "description": "Short engaging description", 
                        "hashtags": ["#trending1", "#viral2"],
                        "seo_keywords": ["trending1", "viral2"]
                    }}
                ],
                "thumbnail_suggestions": [
                    {{
                        "title": "SHOCKING: The Truth About...",
                        "style": "Bold text, bright colors",
                        "elements": ["Large text", "Contrasting colors", "Arrow pointing"],
                        "colors": ["#FF6B6B", "#4ECDC4", "#FFFFFF"]
                    }},
                    {{
                        "title": "5 SECRETS About...",
                        "style": "Number-focused design",
                        "elements": ["Big number", "Preview images", "Question mark"],
                        "colors": ["#FFD93D", "#6BCF7F", "#000000"]
                    }}
                ],
                "general_seo_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
                "trending_hashtags": ["#trending1", "#viral2", "#popular3", "#2024trend", "#mustwatch"]
            }}
            
            Make sure all content is engaging, platform-appropriate, and optimized for maximum reach and engagement.
            """
            
            # Generate social media content using AI
            response = self.text_gen_api.generate_social_media_content(social_media_prompt)
            
            if not response:
                logging.error("No response from AI for social media generation")
                return None
                
            # Parse the response
            if isinstance(response, str):
                try:
                    social_data = json.loads(response)
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to parse social media JSON: {e}")
                    return None
            else:
                social_data = response
            
            # Validate required fields
            required_fields = ['platform_descriptions', 'thumbnail_suggestions', 'general_seo_keywords', 'trending_hashtags']
            if not all(field in social_data for field in required_fields):
                logging.error("Social media response missing required fields")
                return None
            
            # Filter platform descriptions based on requested platforms
            filtered_descriptions = [
                desc for desc in social_data['platform_descriptions'] 
                if desc['platform'].lower() in [p.lower() for p in platforms]
            ]
            social_data['platform_descriptions'] = filtered_descriptions
            
            logging.info(f"Generated social media content for {len(filtered_descriptions)} platforms")
            return social_data
            
        except Exception as e:
            logging.error(f"Error generating social media content: {e}")
            ErrorLogger.log_ai_response_error(
                error=e,
                response=str(e),
                user="unknown",
                error_line=0,
                file_name=__file__
            )
            return None

    def edit_script(
        self,
        script_option: ScriptOption,
        edit_instructions: str,
        user: str = "unknown"
    ) -> Optional[ScriptOption]:
        """
        Edit an existing script based on user instructions.
        
        Args:
            script_option: ScriptOption to edit
            edit_instructions: Instructions for how to modify the script
            user: User identifier
            
        Returns:
            Modified ScriptOption
        """
        try:
            edit_prompt = f"""
            You are a professional script editor. Please edit the following script according to the user's instructions.
            
            Current Script:
            Title: {script_option.title}
            Type: {script_option.script_type.value}
            Script: {script_option.voiceover_script}
            
            Edit Instructions: {edit_instructions}
            
            Guidelines:
            1. Follow the edit instructions precisely
            2. Maintain the script's original tone and style unless specifically asked to change it
            3. Keep the script suitable for voiceover
            4. Preserve the approximate word count unless specifically asked to change length
            5. Ensure the edited script flows naturally
            
            Output must be a valid JSON object with this structure:
            {{
                "title": "Updated title (if needed)",
                "description": "Updated description reflecting changes",
                "voiceover_script": "Edited script",
                "tags": ["updated", "relevant", "tags"],
                "category": "{script_option.category}",
                "language": "{script_option.language}",
                "script_type": "{script_option.script_type.value}",
                "estimated_duration": "{script_option.duration_estimate}",
                "word_count": "actual_word_count"
            }}
            """
            
            edit_result = self.text_gen_api.ai_generated_text(
                user_message=edit_prompt,
                voiceover_language=script_option.language,
                platforms=["YouTube", "TikTok", "Instagram"],
                category=script_option.category,
                user=user
            )
            
            if edit_result and "error" not in edit_result:
                return self._create_script_option(edit_result, script_option.script_type)
            else:
                logging.error(f"Failed to edit script: {edit_result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logging.error(f"Exception editing script: {e}")
            ErrorLogger.log_ai_response_error(
                error=e,
                response=str(e),
                user=user,
                error_line=0,
                file_name=__file__
            )
            return None
    
    def save_scripts_to_file(
        self,
        scripts: List[ScriptOption],
        filename: str = None
    ) -> str:
        """
        Save generated scripts to a JSON file for later reference.
        
        Args:
            scripts: List of ScriptOption objects to save
            filename: Optional filename (will generate if not provided)
            
        Returns:
            Path to saved file
        """
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_scripts_{timestamp}.json"
        
        save_path = self.base_dir / "generated_scripts" / filename
        save_path.parent.mkdir(exist_ok=True)
        
        # Convert scripts to dictionary format for JSON serialization
        scripts_data = []
        for script in scripts:
            scripts_data.append({
                "script_type": script.script_type.value,
                "title": script.title,
                "description": script.description,
                "voiceover_script": script.voiceover_script,
                "tags": script.tags,
                "category": script.category,
                "language": script.language,
                "duration_estimate": script.duration_estimate,
                "word_count": script.word_count
            })
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(scripts_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Scripts saved to: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logging.error(f"Error saving scripts to file: {e}")
            return ""
    
    def load_scripts_from_file(self, filepath: str) -> List[ScriptOption]:
        """
        Load previously saved scripts from a JSON file.
        
        Args:
            filepath: Path to the JSON file containing saved scripts
            
        Returns:
            List of ScriptOption objects
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                scripts_data = json.load(f)
            
            scripts = []
            for script_data in scripts_data:
                script_type = ScriptType(script_data["script_type"])
                script_option = ScriptOption(
                    script_type=script_type,
                    title=script_data["title"],
                    description=script_data["description"], 
                    voiceover_script=script_data["voiceover_script"],
                    tags=script_data["tags"],
                    category=script_data["category"],
                    language=script_data["language"],
                    duration_estimate=script_data["duration_estimate"],
                    word_count=script_data["word_count"]
                )
                scripts.append(script_option)
            
            logging.info(f"Loaded {len(scripts)} scripts from: {filepath}")
            return scripts
            
        except Exception as e:
            logging.error(f"Error loading scripts from file: {e}")
            return []


# Interactive CLI interface for testing
def interactive_script_generator():
    """Interactive command-line interface for testing the script generator"""
    
    generator = ScriptGenerator()
    
    print("🎬 Multi-Script Video Generator")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Generate multiple scripts")
        print("2. Regenerate scripts") 
        print("3. Edit a script")
        print("4. Merge scripts")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            # Generate multiple scripts
            prompt = input("Enter your video topic/prompt: ").strip()
            if not prompt:
                print("❌ Please provide a valid topic.")
                continue
                
            print("\nSelect script types (comma-separated):")
            print("Options: short, medium, long, educational, storytelling, entertaining")
            types_input = input("Types (or press Enter for default: short,medium,long): ").strip()
            
            if types_input:
                try:
                    script_types = [ScriptType(t.strip()) for t in types_input.split(",")]
                except ValueError as e:
                    print(f"❌ Invalid script type: {e}")
                    continue
            else:
                script_types = [ScriptType.SHORT, ScriptType.MEDIUM, ScriptType.LONG]
            
            category = input("Enter category (or press Enter for 'General'): ").strip() or "General"
            
            print("\n🔄 Generating scripts...")
            scripts = generator.generate_multiple_scripts(
                user_prompt=prompt,
                script_types=script_types,
                category=category
            )
            
            if scripts:
                print(f"\n✅ Generated {len(scripts)} scripts:")
                for i, script in enumerate(scripts, 1):
                    print(f"\n--- Script {i}: {script.script_type.value.upper()} ---")
                    print(f"Title: {script.title}")
                    print(f"Duration: {script.duration_estimate}")
                    print(f"Word Count: {script.word_count}")
                    print(f"Script Preview: {script.voiceover_script[:100]}...")
                
                # Save option
                save = input("\nSave scripts to file? (y/n): ").strip().lower()
                if save == 'y':
                    filepath = generator.save_scripts_to_file(scripts)
                    print(f"📁 Scripts saved to: {filepath}")
            else:
                print("❌ No scripts were generated.")
        
        elif choice == "2":
            # Regenerate scripts
            prompt = input("Enter your video topic/prompt for regeneration: ").strip()
            if not prompt:
                print("❌ Please provide a valid topic.")
                continue
            
            print("\n🔄 Regenerating scripts with alternative approach...")
            scripts = generator.regenerate_scripts(user_prompt=prompt)
            
            if scripts:
                print(f"\n✅ Regenerated {len(scripts)} scripts:")
                for i, script in enumerate(scripts, 1):
                    print(f"\n--- Script {i}: {script.script_type.value.upper()} ---")
                    print(f"Title: {script.title}")
                    print(f"Script Preview: {script.voiceover_script[:100]}...")
            else:
                print("❌ No scripts were regenerated.")
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    # Run interactive interface for testing
    interactive_script_generator()
