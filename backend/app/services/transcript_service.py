import re
from typing import Optional
from youtube_transcript_api import (
    YouTubeTranscriptApi, 
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable
)

# Note: AgeRestricted might not be directly importable in older versions or might be under VideoUnavailable
# Check if available, otherwise just use VideoUnavailable which is the base for many.
# Based on previous `dir()` output, AgeRestricted is available.
try:
    from youtube_transcript_api import AgeRestricted
except ImportError:
    # Fallback if not available or renamed
    AgeRestricted = VideoUnavailable

class TranscriptNotAvailableError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)

class TranscriptAccessDeniedError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)

class TranscriptService:
    def extract_video_id(self, video_url: str) -> Optional[str]:
        """
        Extracts video ID from various YouTube URL formats.
        """
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
        return None

    def get_transcript(self, video_url: str) -> str | dict:
        """
        Fetches the transcript for the given YouTube URL.
        If transcript is unavailable, falls back to fetching metadata.
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise TranscriptNotAvailableError(f"Could not extract video ID from URL: {video_url}")

        try:
            # list_transcripts() checks availability and returns a TranscriptList object
            # If this fails (e.g. video private), it raises VideoUnavailable etc.
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            transcript = None
            
            # 1. Try manually created transcripts in English variants
            try:
                transcript = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB'])
            except:
                pass
            
            # 2. If not found, try auto-generated transcripts in English
            if transcript is None:
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                except:
                    pass
            
            # Internal guard: Parsing (fetching) is only attempted if transcript exists
            if transcript is None:
                raise TranscriptNotAvailableError(reason="language_not_supported")
                
            # Fetch the content
            transcript_data = transcript.fetch()
            
            if not transcript_data:
                 raise TranscriptNotAvailableError(reason="empty_transcript_content")
            
            return " ".join([t['text'] for t in transcript_data])

        except (TranscriptsDisabled, NoTranscriptFound, TranscriptNotAvailableError, Exception) as e:
            # Check for Access Denied errors first (don't fallback for private videos)
            if isinstance(e, (VideoUnavailable, AgeRestricted)):
                 raise TranscriptAccessDeniedError(f"Video is inaccessible: {str(e)}")
            
            # Fallback to Metadata
            # Note: "no element found" or "ExpatError" are generic libs errors for empty/bad XML, treat as fallback case
            print(f"Transcript unavailable ({e}). Falling back to Metadata.")
            
            try:
                from app.services.youtube_metadata_service import YouTubeMetadataService
                meta_service = YouTubeMetadataService()
                metadata = meta_service.fetch_metadata(video_url)
                
                return {
                    "mode": "metadata",
                    "data": metadata
                }
            except Exception as meta_e:
                # If metadata also fails, then we truly fail
                print(f"Metadata fallback failed: {meta_e}")
                # Raise original error or new one? User said "Only raise error if Video is private..."
                # But if metadata also fails, we have nothing.
                raise TranscriptNotAvailableError(f"Transcript and Metadata both unavailable. Transcript error: {e}. Metadata error: {meta_e}")
