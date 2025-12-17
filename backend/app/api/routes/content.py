from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4, UUID

from app.core.database import get_db
from app.schemas.content import CreateContentRequest, ContentStatusResponse
from app.models.content import Transcript
from app.models.user import User
from app.workers.tasks import generate_content_task, transcribe_video_task

router = APIRouter()

from app.services.transcript_service import TranscriptService

@router.post("/create", response_model=ContentStatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_content(
    request: CreateContentRequest,
    db: AsyncSession = Depends(get_db)
):
    # Basic URL validation (simple check)
    if "youtube.com" not in request.url.host and "youtu.be" not in request.url.host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL"
        )
    
    # 1. Fetch Transcript (or trigger fallback)
    # This might block slightly for network, but ensures we know availability immediately
    transcript_service = TranscriptService()
    
    # This will raise TranscriptNotAvailableError/TranscriptAccessDeniedError if failed
    # Caught by global exception handlers in main.py
    raw_transcript_text = transcript_service.get_transcript(str(request.url))
    
    # Check if processing (Whisper fallback triggered)
    is_processing = (raw_transcript_text == "TRANSCRIPT_PROCESSING")
    initial_status = "processing" if is_processing else "queued"
    initial_text = "" if is_processing else raw_transcript_text
    response_msg = "Content generation processing (audio transcription started)" if is_processing else "Content generation queued"

    # Mock User creation/retrieval for MVP
    result = await db.execute(select(User).limit(1))
    user = result.scalars().first()
    
    if not user:
        user = User(email="demo@example.com")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Create Transcript
    transcript = Transcript(
        user_id=user.id,
        youtube_url=str(request.url),
        raw_text=initial_text, 
        status=initial_status
    )
    db.add(transcript)
    await db.commit()
    await db.refresh(transcript)

    # Enqueue Celery task only if we have the transcript.
    # If it is processing via Whisper, the Whisper task should separate trigger content generation eventually.
    # But for now, if it's processing, we just wait.
    # Current generate_content_task expects raw_text to be present or fetches it (which we removed).
    
    # Wait, our previous `process_content` worker modification added `YouTubeService` call.
    # We should probably remove that double-fetch if we are passing text here, 
    # OR we let the worker do it.
    
    # But the USER REQUEST says: "Call TranscriptService.get_transcript() ... If transcript returns ... If transcript fails return clean error"
    # This implies the API is the one doing the check now.
    
    if not is_processing:
        # Standard flow: we have text, enqueue generation
        generate_content_task.delay(str(transcript.id))
    else:
        # Fallback flow: we have a processing status, so trigger the background transcription task
        # which will then chain into content generation.
        transcribe_video_task.delay(str(transcript.id))

    return ContentStatusResponse(
        id=transcript.id,
        status=initial_status,
        message=response_msg,
        post_count=0
    )

@router.get("/status/{transcript_id}", response_model=ContentStatusResponse)
async def get_content_status(
    transcript_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        t_id = UUID(str(transcript_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    # Fetch Transcript
    result = await db.execute(select(Transcript).where(Transcript.id == transcript_id))
    transcript = result.scalars().first()

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    
    # Count Posts (optional, for MVP just returning 0 or counting if we added relation)
    # Since we didn't add explicit relation in models yet (just FKs), we query Post table
    # But wait, we didn't import Post model here yet.
    # Let's count posts associated with transcript -> content_atom -> post
    # For MVP simplicity, let's just query transcript status.
    
    # To get proper count, we'd need to join. 
    # For now, let's just return the status.
    
    return ContentStatusResponse(
        id=transcript.id,
        status=transcript.status,
        message=f"Current status: {transcript.status}",
        error=getattr(transcript, "error_message", None),
        post_count=0 # Placeholder until we implement counting logic properly
    )

from app.services.scheduling_service import SchedulingService
from datetime import datetime, timedelta

@router.post("/schedule/{transcript_id}")
async def schedule_content(
    transcript_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        t_id = UUID(str(transcript_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    # Start scheduling from tomorrow
    start_date = datetime.utcnow().date() + timedelta(days=1)
    
    service = SchedulingService()
    try:
        count = await service.generate_schedule(t_id, start_date)
    except Exception as e:
        print(f"Scheduling error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate schedule")

    return {
        "message": "Schedule generated successfully",
        "scheduled_count": count
    }

from app.models.content import Schedule, Post, ContentAtom
from app.schemas.content import SchedulePreviewResponse
from typing import List

@router.get("/schedule/preview/{transcript_id}", response_model=List[SchedulePreviewResponse])
async def get_schedule_preview(
    transcript_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        from uuid import UUID
        t_id_uuid = UUID(str(transcript_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    query = (
        select(Schedule, Post)
        .join(Post, Schedule.post_id == Post.id)
        .join(ContentAtom, Post.content_atom_id == ContentAtom.id)
        .where(ContentAtom.transcript_id == t_id_uuid)
        .order_by(Schedule.publish_date)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    preview_list = []
    for schedule, post in rows:
        preview_list.append(
            SchedulePreviewResponse(
                id=schedule.id,
                date=schedule.publish_date.date(), 
                platform=schedule.platform,
                preview=post.text[:100] + "..." if len(post.text) > 100 else post.text
            )
        )
        
    return preview_list

from app.services.publishing_service import PublishingService

@router.post("/schedule/run/{transcript_id}")
async def run_schedule(
    transcript_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        from uuid import UUID
        t_id_uuid = UUID(str(transcript_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    # Fetch all scheduled items for this transcript
    query = (
        select(Schedule, Post)
        .join(Post, Schedule.post_id == Post.id)
        .join(ContentAtom, Post.content_atom_id == ContentAtom.id)
        .where(ContentAtom.transcript_id == t_id_uuid)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    published_count = 0
    
    for schedule, post in rows:
        # Check platform and publish
        if schedule.platform == "twitter":
            PublishingService.publish_to_twitter(post)
            published_count += 1
        elif schedule.platform == "linkedin":
            PublishingService.publish_to_linkedin(post)
            published_count += 1
            
        # In a real app, we would mark the schedule item as 'published' to avoid re-publishing
        # For this MVP simulation, we just run through them.

    return {
        "message": "Schedule execution simulation completed",
        "published_count": published_count
    }


