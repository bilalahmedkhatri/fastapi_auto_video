import requests
import os
import pickle
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path


class Authentication:
    
    def __init__(self):
        pass
    
    def get_token_directory(self) -> Path:
        """Get the directory path for storing token files."""
        base_dir = Path(__file__).resolve().parent.parent
        token_dir = base_dir / "youtube_credentials"
        os.makedirs(token_dir, exist_ok=True)
        return token_dir

    def get_token_files(self) -> tuple[Path, Path]:
        """Get paths for client secrets and token files."""
        token_dir = self.get_token_directory()
        client_secrets = token_dir / "client.json"
        token_file = token_dir / "token.pickle"
    
        if not client_secrets.exists():
            raise FileNotFoundError(f"Client secrets file not found at: {client_secrets}")
        
        print(f"client secrets: {client_secrets}, token file: {token_file}")
        return client_secrets, token_file
        
    def get_authenticated_service(self):
        """
        Authenticate and return a YouTube API service instance.
        """
        creds = None
        # Use a list for scopes, not a string!
        scopes = [
            "https://www.googleapis.com/auth/youtube.upload", 
            # "https://www.googleapis.com/auth/youtube.force-ssl", not tested.
        ]
        
        client_secrets_file, token_file = self.get_token_files()
        
        # Verify file paths
        if not os.path.exists(client_secrets_file):
            raise FileNotFoundError(f"Client secrets file not found at: {client_secrets_file}")
        
        try:
            if os.path.exists(token_file):
                with open(token_file, "rb") as token:
                    try:
                        creds = pickle.load(token)
                    except (pickle.UnpicklingError, EOFError):
                        print(f"Warning: Token file corrupted, will create new token")
                        os.remove(token_file)
                        
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print(f"Error refreshing credentials: {e}")
                        creds = None
                
                if not creds:
                    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
                    creds = flow.run_local_server(port=0)  # Use a fixed port
                    
                with open(token_file, "wb") as token:
                    pickle.dump(creds, token)
                    
            return build("youtube", "v3", credentials=creds)
        
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with YouTube API: {str(e)}")

def get_youtube_categories(api_key: str, region_code: str = "US") -> list:
    """
    Fetches YouTube video categories and their IDs for a given region.

    Args:
        api_key: Your YouTube Data API v3 key.
        region_code: The region code (default "US").

    Returns:
        List of dicts with 'id' and 'title' for each category.
    """
    url = "https://www.googleapis.com/youtube/v3/videoCategories"
    params = {
        "part": "snippet",
        "regionCode": region_code,
        "key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch categories: {response.status_code} {response.text}")
        return []
    data = response.json()
    categories = []
    for item in data.get("items", []):
        categories.append({
            "id": item["id"],
            "title": item["snippet"]["title"]
        })
    return categories

def get_youtube_categories_oauth(youtube, region_code: str = "US") -> list:
    """
    Fetches YouTube video categories and their IDs for a given region using OAuth 2.0.

    Args:
        youtube: Authenticated YouTube API client (from googleapiclient.discovery.build)
        region_code: The region code (default "US").

    Returns:
        List of dicts with 'id' and 'title' for each category.
    """
    request = youtube.videoCategories().list(
        part="snippet",
        regionCode=region_code
    )
    response = request.execute()
    categories = []
    for item in response.get("items", []):
        categories.append({
            "id": item["id"],
            "title": item["snippet"]["title"]
        })
    return categories

class ErrorLogger:
    
    @staticmethod
    def ensure_log_dir(log_dir: str, user: str) -> Path:
        """
        Ensure the log directory exists, create it with the user name if not.
        Returns the Path to the directory.
        """
        base_dir = Path(log_dir)
        user_dir = base_dir / user
        if not user_dir.exists():
            user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    @staticmethod
    def log_ai_response_error(
        error,
        response,
        user="unknown",
        error_line: int = 0,
        save_log_file_path: str = "",
        file_name: str = "",
        log_dir: str = "logs"
    ):
        """
        Log AI response parse errors to a file, creating it if it doesn't exist.
        Includes user, datetime, error line, and source file name.
        Creates log directory with user name if not present.
        """
        now = datetime.datetime.now()
        log_directory = ErrorLogger.ensure_log_dir(log_dir, user)
        log_file_name = f'{file_name}_{now.strftime("%Y_%m_%d")}.txt'
        log_file = log_directory / log_file_name
        if not log_file.exists():
            log_file.touch()
        today = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("==== AI RESPONSE PARSE ERROR ====\n")
            f.write(f"Datetime: {today}\n")
            f.write(f"File: {file_name}\n")
            f.write(f"Line number: {error_line}, Error: {error}\n")
            f.write(f"Response: {response}\n\n")


