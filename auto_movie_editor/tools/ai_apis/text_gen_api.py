import os
import re
import logging
import json
from pprint import pprint
from click import prompt
from openai import OpenAI
from dotenv import load_dotenv
try:
    from .api_utils import ErrorLogger
except ImportError:
    from api_utils import ErrorLogger


load_dotenv()

class TextGenAPI:
    def __init__(self):
        self.apis_token = os.getenv("QWEN_3_KEY_OPENROUTER")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.apis_token,
        )
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.StreamHandler()]
        )

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
    def get_model_for_input(input_type: str, response: dict = {}, text_gen_failed: bool = False) -> str:
        """Return the model name based on input type."""
        # Easily extend this function for more models in the future
        if input_type and text_gen_failed:
            if "error" in response:
                return "deepseek/deepseek-r1-0528:free"
            return "google/gemini-2.5-flash-preview-05-20"
        elif input_type == "url":
            return "openai/gpt-4o-mini-search-preview-2025-03-11"
        elif input_type == "text":
            # return "qwen/qwen3-235b-a22b:free"
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
        user: str = "unknown"
    ) -> dict:
        """
        Generate YouTube content using AI, with robust handling for ambiguous or missing input.
        """
        # Defensive: Check for empty or too-short input
        if not user_message or len(user_message.strip()) < 5:
            return {"error": "Please provide a valid URL or a detailed topic/description."}

        input_type = self.detect_input_type(user_message)
        model_name = self.get_model_for_input(input_type, text_gen_failed=text_gen_failed)
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
            # Defensive: If AI returns a clarification request, catch and handle it
            clarification_phrases = [
                "please resubmit your request",
                "would you please",
                "i don't see any provided url",
                "i need either",
                "to create your youtube content package"
            ]
            if isinstance(result, str) and any(phrase in result.lower() for phrase in clarification_phrases):
                return {"error": "AI could not generate content. Please provide a more detailed topic or try again."}
            if isinstance(result, dict):
                return result
            try:
                if isinstance(result, str):
                    cleaned = re.sub(r'\s+', ' ', result)
                    cleaned = re.sub(r'//.*?\n', '', cleaned)  # Remove // comments
                    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                    if match:
                        clean_result = match.group()
                    else:
                        clean_result = cleaned
                    import sys
                    ErrorLogger.log_ai_response_error(
                        error=None,
                        response=clean_result,
                        user=user,
                        error_line=0,
                        file_name=__file__+"testing",
                        log_dir="logs"
                    )
                    return json.loads(clean_result)
                else:
                    logging.error("AI response is not a string and cannot be parsed.")
                    return {"error": "AI response is not a string."}
            except Exception as json_err:
                logging.error(f"Error parsing AI response to dict: {json_err}")
                # Use ErrorLogger to save error details, including file name and log directory
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
                return {"error": "AI response could not be parsed as JSON."}
        except Exception as e:
            logging.error(f"Error generating YouTube prompt: {e}")
            # Use ErrorLogger for general errors as well
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
            return {"error": str(e)}
        
    def generation_text(
        self,
        user_message: str,
        voiceover_language: str = "English",
        platforms: list[str] = ["YouTube"],
        category: str = "",
        user: str = "unknown",
        max_retries: int = 2
    ):
        """
        Retry text generation with alternative models if error detected.
        Returns a valid response or error dict after all retries.
        """
        response = self.ai_generated_text(
            user_message=user_message,
            voiceover_language=voiceover_language,
            platforms=platforms,
            category=category,
            user=user,
            text_gen_failed=False,
        )
        if not self.is_error_response(response):
            return response

        attempt = 1
        while attempt <= max_retries and self.is_error_response(response):
            logging.info(f"Retrying text generation, attempt {attempt}...")
            res = self.ai_generated_text(
                user_message=user_message,
                voiceover_language=voiceover_language,
                platforms=platforms,
                category=category,
                user=user,
                text_gen_failed=True,
            )
            if not self.is_error_response(res):
                return res
            attempt += 1

    def generate_search_keywords(self, platforms: list[str], topic: str, max_keywords: int = 8) -> dict:
        """
        Generate search keywords for a given topic and platforms.
        Returns a dict with keywords or an error message.
        """
        print('checking topic:', type(topic), topic)
        if not topic or len(topic) < 3:
            return {"error": "Please provide a valid topic."}

        model_name = "deepseek/deepseek-r1-0528:free"
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
                    logging.error("No JSON object found in AI response.")
                    return {"error": "No JSON object found in AI response."}
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing AI response: {e}")
                return {"error": "AI response could not be parsed as JSON."}
        except Exception as e:
            logging.error(f"Error generating search keywords: {e}")
            return {"error": str(e)}

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

        try:
            logging.info("Sending prompt to AI API...")
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": description}
                ],
                stream=False
            )
            result = response.choices[0].message.content
            return result
        except Exception as e:
            logging.error(f"Error generating search query: {e}")
            return ""

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

