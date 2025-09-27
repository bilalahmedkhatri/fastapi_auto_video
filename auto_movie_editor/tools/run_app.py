"""Run application entry points and parameterized video builder."""

from __future__ import annotations

import asyncio
import logging
import random
import sys
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from moviepy import ImageClip, CompositeVideoClip, AudioFileClip

import video_builder as vb  # Re‑use existing helper functions
from utils import FileDirectory
from tools.ai_apis.text_gen_api import TextGenAPI
from tools.ai_apis.pixabay_api import get_images_videos
from ai_apis.voice_gen_api import download_voice_replicate
from whiper_X_transcription import WhisperTranscriber
from ai_audio import AudioManager
from ai_apis.youtube_api import async_upload_video_to_youtube
from ai_apis.api_utils import ErrorLogger
from apis.google_search_api import google_image_search, download_images

log = logging.getLogger(__name__)


@dataclass
class VideoBuildConfig:
	# Content & metadata
	prompt: str = "current news about elon's AI"
	category: str = "Breaking News"
	voiceover_language: str = "English"
	user_label: str = "user 3"
	voice: str = "am_puck"

	# Layout / timing
	target_format: str = "youtube_short"  # key in vb.TARGET_SIZE
	image_view_duration: float = 5.0
	transition_duration: float = 1.0
	zoom_ratio: float = 0.80
	max_words: int = 5  # per transcript segment for highlighting

	# Paths
	image_dir: str = "media/bikes_test"
	faces_dir: str = "media/faces"  # optional
	font_path: str = "BlackOpsOne-Regular.ttf"

	# Google Search Images
	use_google_search: bool = True  # Enable/disable Google image search
	google_search_query: Optional[str] = None  # If None, will generate from AI prompt
	google_search_count: int = 15  # Number of images to download
	google_social_media: Optional[str] = None  # Filter for social media format (instagram_post, youtube_thumbnail, etc.)
	google_fallback_to_local: bool = True  # Use local images if Google search fails

	# Rendering / export
	fps: int = 30
	codec: str = "h264_nvenc"
	crf: int = 18
	preset: str = "fast"
	pix_fmt: str = "yuv420p"
	# fps: int = 10
	# codec: str = "libx264"
	# crf: int = 18
	# preset: str = "fast"
	# pix_fmt: str = "yuv420p"
	upload_to_youtube: bool = True

	# Whisper / transcription
	whisper_language: str = "en"
	whisper_model_size: str = "small"  # currently only language passed (model fixed in class)

	# Style overrides (passed into highlight function)
	font_size: int = 100
	base_color: str = "white"
	highlight_color: str = "#ffe066"
	highlight_text_color: str = "black"
	border_color: str = "#ffae00"
	border_width: int = 4
	box_padding: int = 16
	position: tuple[str, str] = ("center", "bottom")

	def resolve_font(self, base_dir: Path) -> str:
		p = Path(self.font_path)
		if not p.is_absolute():
			return str(base_dir / p)
		return str(p)


def download_google_images(config: VideoBuildConfig, ai_data: Dict[str, Any]) -> Optional[List[Path]]:
	"""Download images from Google Search API based on config and AI data.
	
	Args:
		config: Video build configuration
		ai_data: AI-generated data containing title, description, etc.
		
	Returns:
		List of downloaded image paths or None if failed
	"""
	if not config.use_google_search:
		return None
		
	# Get API credentials
	api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
	cse_id = os.getenv("GOOGLE_SEARCH_ENGINE")
	
	if not api_key or not cse_id:
		log.warning("Google Search API credentials not found in environment variables")
		log.warning("Required: GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE")
		return None
	
	try:
		# Determine search query
		if config.google_search_query:
			search_query = config.google_search_query
		else:
			# Generate search query from AI data
			from ai_apis.text_gen_api import TextGenAPI
			text_gen_api = TextGenAPI()
			
			# Create a prompt to generate search query from AI content
			ai_title = ai_data.get("title", "")
			ai_description = ai_data.get("description", "")
			ai_content = f"{ai_title} {ai_description}".strip()
			
			if ai_content:
				search_query_prompt = f"""
				You are an expert prompt engineer specializing in image search. Convert this content into a single, concise, and highly effective one-line search query for an image API.
				
				Content: {ai_content}
				
				Output only the search query on a single line without any labels or explanations.
				"""
				search_query = text_gen_api.generate_search_query(search_query_prompt)
			else:
				search_query = config.prompt
		
		log.info(f"Searching Google Images for: {search_query}")
		
		# Search for images
		image_urls = google_image_search(
			api_key=api_key,
			cse_id=cse_id,
			search_ai_query=search_query,
			num_results=config.google_search_count
		)
		
		if not image_urls:
			log.warning("No image URLs returned from Google Search")
			return None
		
		log.info(f"Found {len(image_urls)} image URLs")
		
		# Download images
		# Create a safe query name for directory
		safe_query = "".join(c for c in search_query if c.isalnum() or c in (' ', '-', '_')).rstrip()
		safe_query = safe_query.replace(' ', '_')[:50]  # Limit length
		
		downloaded_images = download_images(
			image_urls=image_urls,
			query=safe_query,
			subdir="google_search_temp",
			social_media=config.google_social_media
		)
		
		if not downloaded_images:
			log.warning("No images were successfully downloaded")
			return None
			
		log.info(f"Successfully downloaded {len(downloaded_images)} images")
		return downloaded_images
		
	except Exception as e:
		log.error(f"Error downloading Google images: {e}")
		return None


def build_video(config: VideoBuildConfig) -> Dict[str, Any]:
	"""Build a video using parameters in config.

	Returns dict with keys: output_path, youtube_video_id, ai_data, transcript_json_path
	"""
	base_dir = vb.BASE_DIR  # same base as original script
	file_directory = FileDirectory()
	clips_to_close: List = []
	audio_clip = None
	final_clip = None
	youtube_video_id: Optional[str] = None
	transcript_json_path: Optional[str] = None

	# Apply configurable globals (non-invasive; original module functions read these)
	if config.target_format in vb.TARGET_SIZE:
		vb.CURRENT_SIZE = vb.TARGET_SIZE[config.target_format]
	vb.IMAGE_VIEW_DURATION = config.image_view_duration
	vb.TRANSITION_DURATION = config.transition_duration
	vb.ZOOM_RATIO = config.zoom_ratio

	log.info("Starting video build with config: %s", asdict(config))

	# 1. AI text generation
	text_gen_api = TextGenAPI()
	ai_data = text_gen_api.generation_text(
		user_message=config.prompt,
		voiceover_language=config.voiceover_language,
		category=config.category,
		user=config.user_label,
	)
	if not isinstance(ai_data, dict):
		raise RuntimeError("AI text generation failed; expected dict result")

	# 2. Optionally fetch media (async)
	try:
		asyncio.run(get_images_videos(ai_data))
	except Exception as e:
		log.warning("Media fetch skipped/failed: %s", e)

	# 3. Voice generation
	ai_gen_file_path = str(base_dir / f"ai_voice_gen_{''.join(random.choices('123456789', k=3))}.mp3")
	voiceover_script = ai_data.get("voiceover_script") or ai_data.get("script")
	if not voiceover_script:
		raise RuntimeError("voiceover_script missing in ai_data")

	replicate_audio_path = asyncio.run(download_voice_replicate(
		text=voiceover_script,
		output_path=ai_gen_file_path,
		voice=config.voice
	))
	if not replicate_audio_path:
		raise RuntimeError("Voice generation returned no path")

	# 4. Transcription
	try:
		transcriber = WhisperTranscriber(language=config.whisper_language)
		voice_segments = transcriber.transcribe_audio_to_json(
			replicate_audio_path,
			max_words=config.max_words
		)
		transcript_json_path = Path(replicate_audio_path).with_suffix('.json')
	except Exception as e:
		ErrorLogger.log_ai_response_error(
			error=e,
			response=str(e),
			user=config.user_label,
			error_line=sys.exc_info()[-1].tb_lineno if sys.exc_info()[-1] else 0,
			file_name=__file__
		)
		raise

	# 5. Load images (Google Search + Local Fallback)
	image_paths = []
	
	# Try to download images from Google Search first
	if config.use_google_search:
		google_images = download_google_images(config, ai_data)
		if google_images:
			image_paths = [str(path) for path in google_images]
			log.info(f"Using {len(image_paths)} Google Search images")
		elif config.google_fallback_to_local:
			log.info("Google Search failed, falling back to local images")
		else:
			raise RuntimeError("Google Search failed and fallback to local images is disabled")
	
	# Fallback to local images if Google Search is disabled or failed
	if not image_paths and config.google_fallback_to_local:
		image_dir_path = base_dir / config.image_dir
		local_image_paths = file_directory.get_image_files(image_dir_path, load_clips=False)
		if local_image_paths:
			image_paths = local_image_paths
			log.info(f"Using {len(image_paths)} local images from {config.image_dir}")
		else:
			log.warning(f"No local images found in {image_dir_path}")
	
	if not image_paths:
		raise RuntimeError("No images found from Google Search or local directory")

	raw_clips = []
	for p in image_paths:
		try:
			img_clip = ImageClip(p)
			img_clip = vb.fit_to_screen(img_clip)
			base_clip = vb.create_base_composite_clip(
				img_clip,
				duration=config.image_view_duration,
				background_color=(0, 0, 0),
				overlays=None,
				size=vb.CURRENT_SIZE
			)
			raw_clips.append(base_clip)
			clips_to_close.extend([img_clip, base_clip])
		except Exception as e:
			log.error("Error processing image %s: %s", p, e)

	if not raw_clips:
		raise RuntimeError("Failed to build any image clips")

	# 6. Transitions
	final_clips = vb.add_transitions(raw_clips)
	clips_to_close.extend(final_clips)

	# 7. Overlays (face & words)
	overlays = []
	# Custom face overlay using provided directory (override original helper)
	faces_dir_path = base_dir / config.faces_dir
	face_files = file_directory.get_image_files(faces_dir_path, load_clips=False)
	if face_files:
		try:
			from moviepy.video.fx import Resize as FXResize  # alias if needed
			face_clip = ImageClip(random.choice(face_files)) \
				.with_duration(AudioManager.get_audio_duration(replicate_audio_path)) \
				.with_effects(vb.Resize(height=200)) \
				.with_position(('right', 'bottom')) \
				.with_layer(2)
			overlays.append(face_clip)
			clips_to_close.append(face_clip)
		except Exception as e:
			log.warning("Face overlay skipped: %s", e)

	if not voice_segments or "segments" not in voice_segments:
		raise RuntimeError("Transcription segments missing")

	font_full_path = config.resolve_font(base_dir)
	word_clips = vb.create_first5_words_highlighted_clips(
		voice_segments["segments"],
		size=vb.CURRENT_SIZE,
		font_size=config.font_size,
		base_color=config.base_color,
		highlight_color=config.highlight_color,
		highlight_text_color=config.highlight_text_color,
		border_color=config.border_color,
		border_width=config.border_width,
		box_padding=config.box_padding,
		font=font_full_path,
		position=config.position
	)
	for wc in word_clips:
		overlays.append(wc)
		clips_to_close.append(wc)

	# 8. Compose main video
	try:
		main_video = CompositeVideoClip([*final_clips, *overlays], size=vb.CURRENT_SIZE)
		clips_to_close.append(main_video)
	except Exception as e:
		raise RuntimeError(f"Failed to compose main video: {e}")

	# 9. Attach audio
	audio_duration = AudioManager.get_audio_duration(replicate_audio_path)
	try:
		audio_clip = AudioFileClip(replicate_audio_path).with_duration(audio_duration)
		clips_to_close.append(audio_clip)
		final_clip = main_video.with_audio(audio_clip)
	except Exception as e:
		log.warning("Audio attach failed (%s); continuing silently", e)
		final_clip = main_video

	# 10. Export
	output_name = f"output_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=3))}.mp4"
	output_path = str(base_dir / output_name)
	try:
		final_clip.write_videofile(
			output_path,
			fps=config.fps,
			codec=config.codec,
			preset=config.preset,
			ffmpeg_params=[
				'-crf', str(config.crf),
				'-movflags', '+faststart',
				'-pix_fmt', config.pix_fmt
			]
		)
	except Exception as e:
		raise RuntimeError(f"Export failed: {e}")

	# 11. Upload (optional)
	if config.upload_to_youtube:
		try:
			youtube_resp = asyncio.run(async_upload_video_to_youtube(
				output_path,
				title=ai_data.get("title", config.prompt[:70]),
				description=ai_data.get("description", config.prompt),
				tags=ai_data.get("tags", [])
			))
			if youtube_resp and 'id' in youtube_resp:
				youtube_video_id = youtube_resp['id']
				log.info("Uploaded to YouTube: https://youtu.be/%s", youtube_video_id)
		except Exception as e:
			log.warning("YouTube upload failed: %s", e)

	# 12. Cleanup
	for c in clips_to_close:
		vb.close_clip_safe(c)
	if final_clip and hasattr(final_clip, 'close'):
		vb.close_clip_safe(final_clip)
	if audio_clip and hasattr(audio_clip, 'close'):
		vb.close_clip_safe(audio_clip)

	return {
		"output_path": output_path,
		"youtube_video_id": youtube_video_id,
		"ai_data": ai_data,
		"transcript_json_path": str(transcript_json_path) if transcript_json_path else None
	}


def example_run():  # Optional quick launcher
	cfg = VideoBuildConfig(
		prompt="Top 5 breakthroughs in clean energy this week",
		category="Tech News",
		voice="am_puck",
		target_format="youtube_short",
		image_dir="media/bikes_test",
		faces_dir="media/faces",
		upload_to_youtube=False,  # disable for local test
		# Google Search Configuration
		use_google_search=True,
		google_search_query=None,  # Will auto-generate from AI content
		google_search_count=15,
		google_social_media="youtube_thumbnail",  # Filter for 16:9 horizontal images
		google_fallback_to_local=True
	)
	result = build_video(cfg)
	print("Video build result:", result)


if __name__ == "__main__":
	example_run()
