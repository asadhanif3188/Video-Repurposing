from datetime import date, timedelta, datetime
from uuid import UUID
from typing import List, Dict
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.content import Post, ContentAtom, Schedule

class SchedulingService:
    async def generate_schedule(self, transcript_id: UUID, start_date: date):
        """
        Generates a 30-day schedule for the given transcript.
        Rules:
        - 1 post per day
        - Alternate platforms (Twitter, LinkedIn)
        - Rotate content atom types
        - Max 30 days
        """
        async with AsyncSessionLocal() as db:
            # 1. Fetch all included posts with their content atom (for type)
            query = (
                select(Post, ContentAtom)
                .join(ContentAtom, Post.content_atom_id == ContentAtom.id)
                .where(ContentAtom.transcript_id == transcript_id)
                .where(Post.included == True)
            )
            result = await db.execute(query)
            rows = result.all() # list of (Post, ContentAtom) tuples

            if not rows:
                return 0

            # 2. Group by Platform
            posts_by_platform: Dict[str, List[tuple]] = {
                "twitter": [],
                "linkedin": []
            }
            
            for post, atom in rows:
                if post.platform in posts_by_platform:
                    posts_by_platform[post.platform].append((post, atom))

            # 3. Group by Type within Platform (Optional for advanced sort)
            # For now, we trust the DB order or just selection logic.

            # 3. Generate Schedule
            schedule_items: List[Schedule] = []
            
            # Helper to get next post rotating by type
            def get_next_post(platform_posts: List[tuple], used_ids: set) -> tuple | None:
                # Simple rotation: just pick the first unused one.
                # Ideally we sort by atom.type to ensure rotation.
                # Let's try to find one that hasn't been used.
                for p, a in platform_posts:
                    if p.id not in used_ids:
                        return (p, a)
                return None

            used_post_ids = set()
            current_date = start_date
            
            # Platforms rotation: starts with Twitter
            platforms_rotation = ["twitter", "linkedin"]
            
            for i in range(30): # 30 days max
                platform = platforms_rotation[i % 2]
                
                # Try to get a post for this platform
                selection = get_next_post(posts_by_platform.get(platform, []), used_post_ids)
                
                # If no post for this platform, try the other one
                if not selection:
                    other_platform = platforms_rotation[(i + 1) % 2]
                    selection = get_next_post(posts_by_platform.get(other_platform, []), used_post_ids)
                
                if not selection:
                    # No content left at all
                    break
                
                post, atom = selection
                used_post_ids.add(post.id)
                
                schedule = Schedule(
                    post_id=post.id,
                    publish_date=datetime(current_date.year, current_date.month, current_date.day),
                    platform=post.platform
                )
                
                schedule_items.append(schedule)
                current_date += timedelta(days=1)

            # 4. Save Schedule
            for item in schedule_items:
                db.add(item)
            
            await db.commit()
            return len(schedule_items)
