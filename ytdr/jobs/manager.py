"""
jobs/manager.py

Central download manager.
"""

from __future__ import annotations

from jobs.job import DownloadJob
from jobs.store import job_store
from jobs.worker import DownloadWorker


class JobManager:
    """
    High-level manager responsible for creating,
    tracking and managing download jobs.
    """

    def __init__(self):

        self.store = job_store

        self.worker = DownloadWorker()

    # ---------------------------------------------------------
    # Create Job
    # ---------------------------------------------------------

    def create_job(
        self,
        url: str,
        format_id: str = "best",
        job_type: str = "video",
    ) -> DownloadJob:
        """
        Create a new download job and start it.
        job_type: "video" (default) or "playlist"
        """

        job = DownloadJob(
            url=url,
            format_id=format_id,
            job_type=job_type,
        )

        self.store.add(job)

        self.worker.start(job)

        return job

    # ---------------------------------------------------------
    # Get Job
    # ---------------------------------------------------------

    def get_job(
        self,
        job_id: str,
    ) -> DownloadJob | None:
        """
        Returns a job by ID.
        """

        return self.store.get(job_id)

    # ---------------------------------------------------------
    # Remove Job
    # ---------------------------------------------------------

    def remove_job(
        self,
        job_id: str,
    ) -> bool:
        """
        Remove a job.

        Returns True if removed.
        """

        if not self.store.exists(job_id):

            return False

        self.store.remove(job_id)

        return True

    # ---------------------------------------------------------
    # Cancel Job
    # ---------------------------------------------------------

    def cancel_job(
        self,
        job_id: str,
    ) -> bool:
        """
        Mark a job as cancelled.

        Returns True if the job was found and cancelled.
        yt-dlp runs in a thread and cannot be force-killed, but marking
        the status lets the UI reflect the cancellation immediately.
        """

        job = self.store.get(job_id)

        if job is None:
            return False

        # Only cancel jobs that are still active
        if job.status in ("queued", "downloading"):
            job.status = "cancelled"
            job.error = "Cancelled by user."

        return True

    # ---------------------------------------------------------
    # Exists
    # ---------------------------------------------------------

    def exists(
        self,
        job_id: str,
    ) -> bool:

        return self.store.exists(job_id)

    # ---------------------------------------------------------
    # All Jobs
    # ---------------------------------------------------------

    def all_jobs(self):

        return self.store.all()

    # ---------------------------------------------------------
    # Active Jobs
    # ---------------------------------------------------------

    def active_jobs(self):

        return [

            job

            for job in self.store.all()

            if job.status in (

                "queued",

                "downloading",

            )

        ]

    # ---------------------------------------------------------
    # Completed Jobs
    # ---------------------------------------------------------

    def completed_jobs(self):

        return [

            job

            for job in self.store.all()

            if job.status == "completed"

        ]

    # ---------------------------------------------------------
    # Failed Jobs
    # ---------------------------------------------------------

    def failed_jobs(self):

        return [

            job

            for job in self.store.all()

            if job.status == "failed"

        ]

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self) -> dict:

        return {

            "total": len(self.store.all()),

            "active": len(self.active_jobs()),

            "completed": len(self.completed_jobs()),

            "failed": len(self.failed_jobs()),

        }


# ==========================================================
# Singleton
# ==========================================================

job_manager = JobManager()