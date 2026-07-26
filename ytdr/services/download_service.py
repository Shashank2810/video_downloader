"""
services/download_service.py

Business logic for download operations.
"""

from typing import Optional

from sqlalchemy.orm import Session

from models.download import Download
from models.download import DownloadStatus
from repositories.download_repository import DownloadRepository


class DownloadService:
    """
    Business logic for download operations.
    """

    def __init__(self, db: Session):
        self.repository = DownloadRepository(db)

    # ======================================================
    # Create
    # ======================================================

    def create_download(
        self,
        title: str,
        url: str,
    ) -> Download:
        """
        Create a new download if it does not already exist.
        """

        existing = self.repository.get_by_url(url)

        if existing:
            return existing

        return self.repository.create(
            title=title,
            url=url,
        )

    # ======================================================
    # Read
    # ======================================================

    def get_download(
        self,
        download_id: int,
    ) -> Optional[Download]:
        return self.repository.get_by_id(download_id)

    def list_downloads(self) -> list[Download]:
        return self.repository.get_all()

    # ======================================================
    # Status
    # ======================================================

    def mark_analyzed(
        self,
        download: Download,
    ) -> Download:

        return self.repository.update_status(
            download,
            DownloadStatus.ANALYZED,
        )

    def mark_downloading(
        self,
        download: Download,
    ) -> Download:

        return self.repository.update_status(
            download,
            DownloadStatus.DOWNLOADING,
        )

    def mark_completed(
        self,
        download: Download,
    ) -> Download:

        return self.repository.update_status(
            download,
            DownloadStatus.COMPLETED,
        )

    def mark_failed(
        self,
        download: Download,
    ) -> Download:

        return self.repository.update_status(
            download,
            DownloadStatus.FAILED,
        )

    def mark_cancelled(
        self,
        download: Download,
    ) -> Download:

        return self.repository.update_status(
            download,
            DownloadStatus.CANCELLED,
        )

    # ======================================================
    # Delete
    # ======================================================

    def delete_download(
        self,
        download: Download,
    ) -> None:

        self.repository.delete(download)

    # ======================================================
    # Statistics
    # ======================================================

    def total_downloads(self) -> int:
        return self.repository.count()

    def pending_downloads(self):
        return self.repository.pending()

    def completed_downloads(self):
        return self.repository.completed()