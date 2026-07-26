"""
Downloader Data Models
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class VideoFormat:
    format_id: str

    ext: str

    width: int | None
    height: int | None

    resolution: str

    video_codec: str
    audio_codec: str

    fps: float | None

    filesize: int |None

    tbr: float | None

    protocol: str | None

    dynamic_range: str | None

    is_video_only: bool

    is_audio_only: bool


@dataclass(slots=True)
class VideoInfo:

    title: str

    url: str

    uploader: str | None

    duration: int | None

    thumbnail: str | None

    video_formats: list[VideoFormat] = field(default_factory=list)

    audio_formats: list[VideoFormat] = field(default_factory=list)

    combined_formats: list[VideoFormat] = field(default_factory=list)

    best_video: VideoFormat | None = None