from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional
import re

class YouTubeService:
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extracts video ID from various YouTube URL formats.
        """
        # Supported patterns:
        # youtube.com/watch?v=VIDEO_ID
        # youtu.be/VIDEO_ID
        # youtube.com/embed/VIDEO_ID
        
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def get_transcript(url: str) -> str:
        """
        Fetches transcript for a given YouTube URL.
        Returns the combined text of the transcript.
        Raises exception if transcript cannot be retrieved.
        """
        video_id = YouTubeService.extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        try:
            # 1. Try default (English)
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            except Exception:
                # 2. If default fails, look for any available transcript
                transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # 3. Prefer manually created transcripts, fallback to generated
                # Get the first available transcript (manual or generated)
                # We can iterate or just pick one. 
                # .find_transcript(['en']) might fail if en is not there.
                
                # Let's try to get a manual transcript first
                try:
                    transcript_obj = transcript_list_obj.find_manually_created_transcript()
                except:
                    # Fallback to any generated transcript
                    try:
                        transcript_obj = transcript_list_obj.find_generated_transcript(['hi', 'en', 'es', 'fr', 'de', 'ja', 'ko', 'pt', 'ru', 'it']) 
                        # Or just iterate
                        # simpler: just take the first one from iteration if above fails or just:
                    except:
                        # If finding specific failed, just grab the first one
                        transcript_obj = next(iter(transcript_list_obj))

                transcript_list = transcript_obj.fetch()

            # Combine all text parts
            full_text = " ".join([item['text'] for item in transcript_list])
            return full_text
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            raise e
