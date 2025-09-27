from os import getenv
import asyncio
from concurrent.futures import ThreadPoolExecutor
from googleapiclient.http import MediaFileUpload
from pathlib import Path
# FIX: Use relative import for api_utils
from .api_utils import Authentication
from sys import path
path.append(str(Path(__file__).resolve().parent.parent.parent))
from tools.utils import FileDirectory, BASE_DIR
from ai_apis.api_utils import ErrorLogger
import sys

# If modifying these SCOPES, delete the file token.pickle.

youtube_api = getenv('YOUTUBE_UPLOAD_VIDEO_API_KEY')

# output_dir = BASE_DIR / 'tools'  # Using BASE_DIR from utils
# file_dir = FileDirectory()

def upload_video(
    youtube,
    file_path,
    title,
    description,
    tags=None,
    category_id="25",
    privacy_status="private",
    made_for_kids=False,  # Not made for kids
    age_restriction=None,  # e.g. {"alcoholContent": False, "restricted": False}
    altered_content=None,  # Dict or bool, see below
    language=None,  # Video language
    default_language=None,  # Title/description language
    license_type=None,
    embeddable=True,
    public_stats_viewable=True,
    default_audio_language=None,
    recording_date=None,
    recording_location=None,  # dict: {"latitude": float, "longitude": float, "altitude": float}
    comments_disabled=False,
    ratings_disabled=False,
    caption_certification=None
):
    """
    Uploads a video to YouTube using the YouTube Data API with advanced options.

    Parameters:
        made_for_kids: Set to False if not made for kids.
        age_restriction: Dict, e.g. {"alcoholContent": False, "restricted": False}. Set "restricted" to False for "No, don't restrict my video to viewers over 18 only."
        altered_content: Dict or bool. If your video makes a real person appear to say/do something they didn't, alters real events/places, or generates realistic fake scenes, set accordingly. Otherwise, set to False or omit.
        language: The language spoken in the video.
        default_language: The language of the title and description.
        recording_date/recording_location: Only set if your video is about a real event or place and you want to provide this info. For most generated videos, you can omit these.
    """
    snippet = {
        "title": title,
        "description": description,
        "categoryId": category_id
    }
    if tags:
        snippet["tags"] = tags
    if language:
        snippet["defaultLanguage"] = language
    if default_language:
        snippet["defaultLanguage"] = default_language

    status = {
        "privacyStatus": privacy_status,
        "embeddable": embeddable,
        "publicStatsViewable": public_stats_viewable,
        "madeForKids": made_for_kids
    }
    if age_restriction:
        status["selfDeclaredMadeForKids"] = made_for_kids
        status["ageRestriction"] = age_restriction
    if license_type:
        status["license"] = license_type
    if comments_disabled:
        status["commentStatus"] = "disabled"
    if ratings_disabled:
        status["disableRatings"] = True

    body = {
        "snippet": snippet,
        "status": status
    }

    # Advanced: recording details
    if recording_date or recording_location:
        recording_details = {}
        if recording_date:
            recording_details["recordingDate"] = recording_date  # ISO 8601 format
        if recording_location:
            recording_details["location"] = recording_location
        body["recordingDetails"] = recording_details

    # Advanced: age gating
    if age_restriction:
        body["ageGating"] = age_restriction

    # Advanced: caption certification
    if caption_certification:
        body.setdefault("contentDetails", {})["captionCertification"] = caption_certification

    # Altered content (YouTube's "Altered content" policy)
    if altered_content is not None:
        body.setdefault("contentDetails", {})["alteredContent"] = altered_content

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload: {int(status.progress() * 100)}% complete")
    return response


async def async_upload_video_to_youtube(
    video_file_path,
    title,
    description,
    tags,
    category_id="25",
    privacy_status="private",
    made_for_kids=False,
    age_restriction=None,
    altered_content=None,
    language=None,
    default_language=None,
    license_type=None,
    embeddable=True,
    public_stats_viewable=True,
    default_audio_language=None,
    recording_date=None,
    recording_location=None,
    comments_disabled=False,
    ratings_disabled=False,
    caption_certification=None,
    user: str = "unknown"
):
    """
    Asynchronously uploads a video to YouTube with advanced options.
    See upload_video() for parameter details.
    Logs errors using ErrorLogger.
    """
    # jo video generate hui hay us ka poora paath aa raha hay ds_movie_6 say to es ko comment kiya gaya hay. ho skta hay future main use ho.
    # video_file_path = file_dir.get_video_files(output_dir, load_clips=False, file_name=file_name)
    # if not video_file_path:
    #     raise FileNotFoundError(f"No video file found in {output_dir} with name {file_name}" if file_name else "")
    
    auth = Authentication()
    loop = asyncio.get_event_loop()
    try:
        with ThreadPoolExecutor() as pool:
            youtube = await loop.run_in_executor(pool, auth.get_authenticated_service)
            response = await loop.run_in_executor(
                pool,
                upload_video,
                youtube,
                video_file_path,
                title,
                description,
                tags,
                category_id,
                privacy_status,
                made_for_kids,
                age_restriction,
                altered_content,
                language,
                default_language,
                license_type,
                embeddable,
                public_stats_viewable,
                default_audio_language,
                recording_date,
                recording_location,
                comments_disabled,
                ratings_disabled,
                caption_certification
            )
        return response
    except Exception as e:
        error_line = sys.exc_info()[-1].tb_lineno if sys.exc_info()[-1] else 0
        ErrorLogger.log_ai_response_error(
            error=e,
            response="Error in async_upload_video_to_youtube",
            user=user,
            error_line=error_line,
            file_name=__file__,
            log_dir="logs"
        )
        raise

# Dynamically get the built video file from the output directory, optionally by name
# video_file_name = "output_knw.mp4"  # Set to a filename like "output_knw.mp4" if you want a specific file
# output_dir = BASE_DIR / 'tools'  # Using BASE_DIR from utils
# file_dir = FileDirectory()
# video_files = file_dir.get_video_files(output_dir, load_clips=False, file_name=video_file_name)
# video_file = video_files[0] if video_files else None

# if not video_file:
#     raise FileNotFoundError(f"No video file found in {output_dir}" + (f" with name '{video_file_name}'" if video_file_name else ""))

# tags = ["tag1", "tag2", "tag3"]
# async def video_upload_youtube():
#     response = await async_upload_video_to_youtube(
#         video_file,
#         "My Title",
#         "My Description",
#         tags,
#     )
#     if response and 'id' in response:
#         print(f"Video uploaded successfully! Video ID: {response['id']}")
#         print(f"Watch it at: https://youtu.be/{response['id']}")
#     else:
#         print("Upload failed or no video ID returned.", response)

# if __name__ == "__main__":
#     asyncio.run(video_upload_youtube())