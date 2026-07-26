"""
repositories/download_repository.py

Repository for Download model.

All database operations related to downloads
should be performed here.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.download import Download
from models.download import DownloadStatus


class DownloadRepository:
    """
    Repository for Download model.
    """

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # Create
    # =====================================================

    def create(
        self,
        title: str,
        url: str,
    ) -> Download:
        """
        Create a new download record.
        """

        download = Download(
            title=title,
            url=url,
            status=DownloadStatus.PENDING,
        )

        self.db.add(download)
        self.db.commit()
        self.db.refresh(download)

        return download

    # =====================================================
    # Get
    # =====================================================

    def get_by_id(self, download_id: int) -> Optional[Download]:
        """
        Get download by ID.
        """

        return self.db.get(Download, download_id)

    def get_by_url(self, url: str) -> Optional[Download]:
        """
        Get download by URL.
        """

        stmt = select(Download).where(Download.url == url)

        return self.db.scalar(stmt)

    # =====================================================
    # List
    # =====================================================

    def get_all(self) -> list[Download]:
        """
        Get all downloads.
        """

        stmt = (
            select(Download)
            .order_by(Download.created_at.desc())
        )

        return list(self.db.scalars(stmt).all())

    # =====================================================
    # Update
    # =====================================================

    def update(self, download: Download) -> Download:
        """
        Save changes to an existing download.
        """

        self.db.add(download)
        self.db.commit()
        self.db.refresh(download)

        return download

    def update_status(
        self,
        download: Download,
        status: DownloadStatus,
    ) -> Download:
        """
        Update download status.
        """

        download.status = status

        self.db.commit()
        self.db.refresh(download)

        return download

    # =====================================================
    # Delete
    # =====================================================

    def delete(self, download: Download) -> None:
        """
        Delete a download.
        """

        self.db.delete(download)
        self.db.commit()

    # =====================================================
    # Statistics
    # =====================================================

    def count(self) -> int:
        """
        Total downloads.
        """

        stmt = select(Download)

        return len(self.db.scalars(stmt).all())

    def pending(self) -> list[Download]:
        """
        Get pending downloads.
        """

        stmt = select(Download).where(
            Download.status == DownloadStatus.PENDING
        )

        return list(self.db.scalars(stmt).all())

    def completed(self) -> list[Download]:
        """
        Get completed downloads.
        """

        stmt = select(Download).where(
            Download.status == DownloadStatus.COMPLETED
        )

        return list(self.db.scalars(stmt).all())