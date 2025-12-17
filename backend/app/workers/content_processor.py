from uuid import UUID
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.content import Transcript, ContentAtom, Post
from app.services.ai_service import AIService
from app.services.ai_service import AIService
from app.services.transcript_service import TranscriptService

async def process_content(transcript_id: UUID):
    """
    Process transcript to extract content atoms.
    """
    print(f"Starting processing for transcript: {transcript_id}")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Fetch Transcript
            result = await db.execute(select(Transcript).where(Transcript.id == transcript_id))
            transcript = result.scalars().first()
            
            if not transcript:
                print(f"Transcript {transcript_id} not found.")
                return

            # Update Status: Processing
            transcript.status = "processing"
            db.add(transcript)
            await db.commit()
            
            # Ensure we have text
            # Ensure we have text or fall back to metadata
            mode = "transcript"
            metadata_payload = None

            if not transcript.raw_text:
                try:
                    print(f"Transcript text missing in DB. Fetching for URL: {transcript.youtube_url}")
                    ts = TranscriptService()
                    result = ts.get_transcript(transcript.youtube_url)
                    
                    if isinstance(result, dict) and result.get("mode") == "metadata":
                        print("Transcript unavailable. Swapping to Metadata mode.")
                        mode = "metadata"
                        metadata_payload = result.get("data")
                        transcript.raw_text = "METADATA_FALLBACK" # Placeholder value to satisfy not-null constraint
                        transcript.source_type = "metadata"
                        db.add(transcript)
                        await db.commit()
                    elif isinstance(result, str):
                        transcript.raw_text = result
                        transcript.source_type = "transcript"
                        db.add(transcript)
                        await db.commit()
                    else:
                        raise Exception("Unknown result from transcript service")

                except Exception as e:
                    print(f"Failed to fetch transcript/metadata: {e}")
                    transcript.status = "failed"
                    transcript.error_message = f"Failed to fetch content source: {str(e)}"
                    db.add(transcript)
                    await db.commit()
                    return

            # 2. Call AI Service
            ai_service = AIService()
            atoms_data = []
            
            if mode == "transcript":
                atoms_data = await ai_service.extract_content_atoms(transcript.raw_text)
            elif mode == "metadata":
                from app.services.ai.metadata_pipeline import MetadataPipeline
                pipeline = MetadataPipeline()
                atoms_data = await pipeline.generate_content_from_metadata(metadata_payload)
            
            if not atoms_data:
                print("No atoms extracted.")
                transcript.status = "failed"
                transcript.error_message = "No content atoms extracted from AI response."
                db.add(transcript)
                await db.commit()
                return

            # 3. Save to DB
            for atom in atoms_data:
                # Create Atom
                content_atom = ContentAtom(
                    transcript_id=transcript.id,
                    type=atom.get("type", "insight"),
                    text=atom.get("text", "")
                )
                db.add(content_atom)
                await db.flush() 
                
                # REWRITING
                platforms = ["twitter", "linkedin"]
                for platform in platforms:
                    rewritten_text = await ai_service.rewrite_content(content_atom.text, platform)
                    
                    post = Post(
                        content_atom_id=content_atom.id,
                        platform=platform,
                        text=rewritten_text,
                        included=True
                    )
                    db.add(post)
            
            # Update Status: Completed
            transcript.status = "completed"
            db.add(transcript)
            await db.commit()
            print(f"Successfully saved {len(atoms_data)} atoms for transcript {transcript_id}")

        except Exception as e:
            print(f"Error processing content: {e}")
            await db.rollback()
            # Try to update status to failed in a separate transaction if possible, 
            # or just log it. Since we rolled back, the 'processing' status might remain 
            # if that commit succeeded, which is fine for now.
            try:
                # Re-fetch because of rollback detaching objects
                async with AsyncSessionLocal() as db_err:
                    err_result = await db_err.execute(select(Transcript).where(Transcript.id == transcript_id))
                    err_transcript = err_result.scalars().first()
                    if err_transcript:
                        err_transcript.status = "failed"
                        err_transcript.error_message = str(e)
                        db_err.add(err_transcript)
                        await db_err.commit()
            except Exception as e2:
                print(f"Failed to update error status: {e2}")
            raise e # Re-raise for Celery retry

