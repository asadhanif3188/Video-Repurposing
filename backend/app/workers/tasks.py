from app.workers.celery_app import celery_app
from app.workers.content_processor import process_content
from time import sleep
import asyncio
from uuid import UUID

@celery_app.task
def test_celery_task(word: str):
    sleep(1)
    return f"Hello {word}"

@celery_app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def generate_content_task(self, transcript_id: str):
    """
    Celery task wrapper for async content processing.
    """
    try:
        # We need to run the async function in the synchronous Celery worker
        asyncio.run(process_content(UUID(transcript_id)))
        return f"Content generation completed for {transcript_id}"
    except Exception as e:
        # Logic to handle exceptions if needed beyond autoretry
        raise e

from app.services.whisper_service import WhisperTranscriptionService

@celery_app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def transcribe_video_task(self, video_id: str):
    """
    Celery task for Whisper transcription.
    """
    try:
        service = WhisperTranscriptionService()
        transcript_text = service.transcribe(video_id)
        # In a real impl, we would save this to the DB and perhaps trigger content generation
        print(f"Whisper transcription completed for {video_id}")
        return transcript_text
    except Exception as e:
        print(f"Error in Whisper task: {e}")
        raise e
