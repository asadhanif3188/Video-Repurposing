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

    def get_transcript(self, video_url: str) -> str:
        """
        Fetches the transcript for the given YouTube URL.
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
            # The fetch() method performs the actual parsing of the transcript XML/JSON
            transcript_data = transcript.fetch()
            
            if not transcript_data:
                 raise TranscriptNotAvailableError(reason="empty_transcript_content")
            
            return " ".join([t['text'] for t in transcript_data])

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # Trigger Whisper Fallback
            from app.workers.tasks import transcribe_video_task
            try:
                transcribe_video_task.delay(video_id)
                return "TRANSCRIPT_PROCESSING"
            except Exception as task_error:
                print(f"Failed to enqueue Whisper task: {task_error}")
                raise TranscriptNotAvailableError(f"Transcript unavailable and fallback failed: {str(e)}")
                
        except (VideoUnavailable, AgeRestricted) as e:
            raise TranscriptAccessDeniedError(f"Video is inaccessible (private, age-restricted, or members-only). Alert: {str(e)}")
        
        except TranscriptNotAvailableError as e:
             # Trigger Whisper Fallback for our own raised errors (e.g. language_not_supported)
            from app.workers.tasks import transcribe_video_task
            try:
                transcribe_video_task.delay(video_id)
                return "TRANSCRIPT_PROCESSING"
            except Exception as task_error:
                print(f"Failed to enqueue Whisper task: {task_error}")
                raise e
                
        except Exception as e:
            # Handle generic exceptions including XML parsing errors from the library
            # "no element found" or "ExpatError"
            error_msg = str(e)
            if "no element found" in error_msg:
                 # Trigger fallback for empty response error too
                 from app.workers.tasks import transcribe_video_task
                 transcribe_video_task.delay(video_id)
                 return "TRANSCRIPT_PROCESSING"
                 
            raise e
