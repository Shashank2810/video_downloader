"""
jobs/job.py

Download job model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class DownloadJob:
    """
    Represents one download task.
    job_type: "video" (default) or "playlist"
    """

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    id: str = field(default_factory=lambda: uuid4().hex)

    url: str = ""

    format_id: str = "best"

    job_type: str = "video"     # "video" | "playlist"

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    status: str = "queued"

    progress: float = 0.0

    speed: str = ""

    eta: int = 0

    # ---------------------------------------------------------
    # Result
    # ---------------------------------------------------------

    filename: str = ""          # final file (video) or folder name (playlist)

    error: str = ""

    # ---------------------------------------------------------
    # Playlist-specific counters
    # ---------------------------------------------------------

    total: int = 0              # total videos in playlist (0 = unknown / not playlist)

    completed_count: int = 0    # how many playlist videos have finished

    # ---------------------------------------------------------
    # Time
    # ---------------------------------------------------------

    created_at: datetime = field(default_factory=datetime.now)

    started_at: datetime | None = None

    completed_at: datetime | None = None

    # ---------------------------------------------------------
    # Helper Methods
    # ---------------------------------------------------------

    def start(self):

        self.status = "downloading"

        self.started_at = datetime.now()

    def complete(self, filename: str):

        self.status = "completed"

        self.progress = 100

        self.filename = filename

        self.completed_at = datetime.now()

    def fail(self, message: str):

        self.status = "failed"

        self.error = message

        self.completed_at = datetime.now()