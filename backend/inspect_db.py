import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Default docker-compose credentials. Update if yours differ.
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/videorepurposing"

async def inspect_db():
    try:
        engine = create_async_engine(DATABASE_URL)
        async with engine.connect() as conn:
            print("--- Checking Database Connection ---")
            
            # Check Transcripts (Step 1)
            print("\n=== STEP 1: Transcripts (Last 3) ===")
            try:
                rows = await conn.execute(text("SELECT id, status, left(raw_text, 50) as snippet, error_message FROM transcripts ORDER BY id DESC LIMIT 3"))
                transcripts = rows.fetchall()
                for t in transcripts:
                    print(f"ID: {t.id} | Status: {t.status} | Error: {t.error_message} | Text: {t.snippet}...")

                if not transcripts:
                    print("No transcripts found.")
                    return
                
                latest_id = transcripts[0].id
            except Exception as e:
                print(f"Error reading transcripts: {e}")
                return
            
            # Check Atoms (Step 2)
            print(f"\n=== STEP 2: Content Atoms for Transcript {latest_id} ===")
            try:
                rows = await conn.execute(text(f"SELECT id, type, left(text, 50) as snippet FROM content_atoms WHERE transcript_id = '{latest_id}'"))
                atoms = rows.fetchall()
                for a in atoms:
                    print(f"Atom ID: {a.id} | Type: {a.type} | Text: {a.snippet}...")
                    
                if not atoms:
                    print("No content atoms found for the latest transcript.")
            except Exception as e:
                print(f"Error reading atoms: {e}")

            # Check Posts (Step 3)
            print(f"\n=== STEP 3: Generated Posts for Transcript {latest_id} ===")
            try:
                # Join with atoms to filter by transcript
                query = f"""
                    SELECT p.id, p.platform, left(p.text, 50) as snippet 
                    FROM posts p
                    JOIN content_atoms a ON p.content_atom_id = a.id
                    WHERE a.transcript_id = '{latest_id}'
                """
                rows = await conn.execute(text(query))
                posts = rows.fetchall()
                for p in posts:
                    print(f"Post ID: {p.id} | Platform: {p.platform} | Text: {p.snippet}...")
                
                if not posts:
                    print("No posts found for the latest transcript.")
            except Exception as e:
                print(f"Error reading posts: {e}")

    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_db())
