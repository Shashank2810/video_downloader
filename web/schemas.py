"""
web/schemas.py

Pydantic models used by the Web API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ==========================================================
# Analyze
# ==========================================================

class AnalyzeRequest(BaseModel):
    """Request for video analysis."""

    url: str = Field(..., min_length=1)


class DownloadOption(BaseModel):
    """Represents one downloadable video format."""

    value: str

    label: str


class AnalyzeResponse(BaseModel):
    """Response returned after analyzing a video."""

    title: str

    uploader: str | None = None

    duration: int | None = None

    thumbnail: str | None = None

    options: list[DownloadOption]

    # Available codec names (e.g. ["AV1", "VP9", "H264"])
    codecs: list[str] = []


# ==========================================================
# Download
# ==========================================================

class DownloadRequest(BaseModel):
    """Request to start a download."""

    url: str

    format_id: str = "best"


class DownloadResponse(BaseModel):
    """
    Returned immediately after creating
    a background download job.
    """

    success: bool

    message: str

    job_id: str

    status: str


class BatchDownloadRequest(BaseModel):
    """Request to start downloads for multiple URLs at once."""

    urls: list[str]

    format_id: str = "best"


class BatchDownloadResponse(BaseModel):
    """Returned after creating batch download jobs."""

    jobs: list[DownloadResponse]


# ==========================================================
# Playlist
# ==========================================================

class PlaylistEntry(BaseModel):
    """One video entry inside a playlist."""
    index: int
    video_id: str
    title: str
    url: str
    duration: int | None = None
    thumbnail: str | None = None


class PlaylistAnalyzeResponse(BaseModel):
    """Returned after analyzing a playlist URL."""
    playlist_id: str
    title: str
    uploader: str | None = None
    url: str
    count: int
    entries: list[PlaylistEntry]


class PlaylistDownloadRequest(BaseModel):
    """Request to download an entire playlist."""
    url: str
    format_id: str = "best"


# ==========================================================
# Progress
# ==========================================================

class ProgressResponse(BaseModel):
    """
    Current status of a download job.
    """

    job_id: str

    status: str

    progress: float

    speed: str

    eta: int

    filename: str | None = None

    error: str = ""

    # Playlist-specific (0 for single-video jobs)
    total: int = 0

    completed_count: int = 0