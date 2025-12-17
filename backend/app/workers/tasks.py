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

from app.core.database import AsyncSessionLocal
from app.models.content import Transcript
from sqlalchemy import select

@celery_app.task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def transcribe_video_task(self, transcript_id: str):
    """
    Celery task for Whisper transcription.
    """
    try:
        # Resolve transcript_id to UUID
        t_id = UUID(transcript_id)
        
        # Async logic wrapper
        async def run_transcription():
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Transcript).where(Transcript.id == t_id))
                transcript = result.scalars().first()
                
                if not transcript:
                    print(f"Transcript {transcript_id} not found.")
                    return "TRANSCRIPT_NOT_FOUND"

                try:
                    # Extract video ID from URL stored in transcript
                    # We might need TranscriptService instance for extraction logic or just do it here
                    # For simplicity, let's use TranscriptService helper or just assume we pass video_id?
                    # No, we have the URL in DB. Let's re-use TranscriptService extraction logic or do it inline.
                    # Ideally we instantiated TranscriptService in the task.
                    from app.services.transcript_service import TranscriptService
                    ts = TranscriptService()
                    video_id = ts.extract_video_id(transcript.youtube_url)
                    
                    if not video_id:
                        raise Exception("Could not extract video ID from URL")

                    service = WhisperTranscriptionService()
                    transcript_text = service.transcribe(video_id)
                    
                    # Update Record
                    transcript.raw_text = transcript_text
                    # Trigger next step? 
                    # Actually, if we just save it, the Status is still 'processing'.
                    # We should trigger generation.
                    
                    db.add(transcript)
                    await db.commit()
                    
                    print(f"Whisper transcription completed for {video_id}. Triggering content generation.")
                    
                    # Chain the next task
                    generate_content_task.delay(str(transcript.id))
                    
                    return transcript_text
                    
                except Exception as inner_e:
                    print(f"Transcription failed: {inner_e}")
                    transcript.status = "failed"
                    transcript.error_message = str(inner_e)
                    db.add(transcript)
                    await db.commit()
                    raise inner_e

        return asyncio.run(run_transcription())

    except Exception as e:
        print(f"Error in Whisper task: {e}")
        raise e
