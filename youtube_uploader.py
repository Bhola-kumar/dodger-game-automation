import os
import time
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger("app.uploader")

def get_youtube_client():
    """
    Builds the YouTube API client using environment variables.
    """
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")

    if not all([refresh_token, client_id, client_secret]):
        logger.error("Missing YouTube Environment Variables!")
        raise ValueError("YT_REFRESH_TOKEN, YT_CLIENT_ID, and YT_CLIENT_SECRET must be set.")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    
    return build("youtube", "v3", credentials=creds, cache_discovery=False)

def upload_video(file_path: str, title: str, description: str, tags: list = None, privacy_status: str = "public"):
    """
    Uploads the specified video file to YouTube.
    """
    youtube = get_youtube_client()
    
    if tags is None:
        tags = ["gameplay", "shorts", "gaming"]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "20" # 20 is the category ID for 'Gaming'
        },
        "status": {
            "privacyStatus": privacy_status, # 'private', 'unlisted', or 'public'
            "selfDeclaredMadeForKids": False
        }
    }

    # Chunk size 4MB is a good balance for reliability
    media = MediaFileUpload(file_path, chunksize=4*1024*1024, resumable=True, mimetype="video/mp4")

    logger.info(f"Starting upload for: {title}")
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    max_retries = 3
    retry_count = 0
    
    while response is None and retry_count < max_retries:
        try:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Upload progress: {int(status.progress() * 100)}%")
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"Upload failed after {max_retries} retries: {e}")
                raise Exception(f"YouTube upload failed: {str(e)}")
            logger.warning(f"Upload chunk failed, retrying ({retry_count}/{max_retries}): {e}")
            time.sleep(2)  # Wait before retry

    if response is None:
        raise Exception("YouTube upload failed: No response received")
    
    video_id = response.get("id")
    if not video_id:
        raise Exception("YouTube upload failed: No video ID in response")
    
    logger.info(f"Upload Complete! Video ID: {video_id}")
    return video_id