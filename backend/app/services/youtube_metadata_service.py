import json
import logging
from typing import Dict, Any, Optional
import yt_dlp

logger = logging.getLogger(__name__)

class VideoMetadataNotAvailableError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Video metadata not available: {reason}")

class YouTubeMetadataService:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': True, # Fast extraction, does not download video
        }

    def fetch_metadata(self, url: str) -> Dict[str, Any]:
        """
        Fetches metadata for a given YouTube URL.
        Returns:
            dict: {
                "title": str,
                "description": str,
                "channel_name": str,
                "duration": int (optional),
                "view_count": int (optional)
            }
        Raises:
            VideoMetadataNotAvailableError: If metadata cannot be retrieved.
        """
        if not url:
             raise VideoMetadataNotAvailableError("Empty URL provided")

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except yt_dlp.utils.DownloadError as e:
                    raise VideoMetadataNotAvailableError(str(e))
                
                if not info:
                    raise VideoMetadataNotAvailableError("No info returned from yt-dlp")

                # Parse relevant fields
                metadata = {
                    "title": info.get("title"),
                    "description": info.get("description"),
                    "channel_name": info.get("uploader") or info.get("channel"),
                    "duration": info.get("duration"),
                    "view_count": info.get("view_count"),
                    "video_id": info.get("id")
                }
                
                # Check critical fields
                if not metadata["title"]:
                     raise VideoMetadataNotAvailableError("Could not retrieve video title")
                     
                return metadata

        except Exception as e:
            if isinstance(e, VideoMetadataNotAvailableError):
                raise e
            logger.error(f"Error fetching metadata for {url}: {e}")
            raise VideoMetadataNotAvailableError(f"Unexpected error: {str(e)}")
