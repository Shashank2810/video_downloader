"""
Download Model

Stores download history for videos.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from core.database import Base


# ==========================================================
# Download Status
# ==========================================================

class DownloadStatus(str, Enum):
    PENDING = "Pending"
    ANALYZED = "Analyzed"
    DOWNLOADING = "Downloading"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


# ==========================================================
# Download Model
# ==========================================================

class Download(Base):
    __tablename__ = "downloads"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Video Information
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        unique=True,
    )

    uploader: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    duration: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    thumbnail: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Video Format
    video_codec: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    audio_codec: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    resolution: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    filesize: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    output_path: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Status
    status: Mapped[DownloadStatus] = mapped_column(
        SqlEnum(DownloadStatus),
        default=DownloadStatus.PENDING,
        nullable=False,
    )

    # Dates
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # ------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<Download("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"status='{self.status.value}'"
            f")>"
        )