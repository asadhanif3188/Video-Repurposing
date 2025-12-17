import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Boolean, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    youtube_url: Mapped[str] = mapped_column(String, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="queued", nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String, default="transcript", nullable=False)

class ContentAtom(Base):
    __tablename__ = "content_atoms"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    transcript_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transcripts.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String, nullable=False) # insight, opinion, lesson, quote
    text: Mapped[str] = mapped_column(Text, nullable=False)

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    content_atom_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("content_atoms.id"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String, nullable=False) # twitter, linkedin
    text: Mapped[str] = mapped_column(Text, nullable=False)
    included: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id"), nullable=False
    )
    publish_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
