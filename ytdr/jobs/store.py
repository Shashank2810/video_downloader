"""
jobs/store.py

In-memory storage for download jobs.
"""

from jobs.job import DownloadJob


class JobStore:
    """
    Stores active download jobs.
    """

    def __init__(self):

        self._jobs: dict[str, DownloadJob] = {}

    # ---------------------------------------------------------
    # Add
    # ---------------------------------------------------------

    def add(self, job: DownloadJob):

        self._jobs[job.id] = job

    # ---------------------------------------------------------
    # Get
    # ---------------------------------------------------------

    def get(self, job_id: str) -> DownloadJob | None:

        return self._jobs.get(job_id)

    # ---------------------------------------------------------
    # Remove
    # ---------------------------------------------------------

    def remove(self, job_id: str):

        self._jobs.pop(job_id, None)

    # ---------------------------------------------------------
    # Exists
    # ---------------------------------------------------------

    def exists(self, job_id: str) -> bool:

        return job_id in self._jobs

    # ---------------------------------------------------------
    # List
    # ---------------------------------------------------------

    def all(self) -> list[DownloadJob]:

        return list(self._jobs.values())

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(self) -> int:

        return len(self._jobs)


# ==========================================================
# Singleton
# ==========================================================

job_store = JobStore()