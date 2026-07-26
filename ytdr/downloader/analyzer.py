"""
Video Analyzer
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from yt_dlp import YoutubeDL

from downloader.exceptions import AnalyzeError
from downloader.models import VideoFormat
from downloader.models import VideoInfo


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", text)


# ==========================================================
# Playlist info model
# ==========================================================

@dataclass(slots=True)
class PlaylistEntry:
    """One video entry inside a playlist (lightweight — no format details)."""
    index: int          # 1-based position in playlist
    video_id: str
    title: str
    url: str
    duration: int | None
    thumbnail: str | None


@dataclass(slots=True)
class PlaylistInfo:
    """Metadata extracted from a playlist URL."""
    playlist_id: str
    title: str
    uploader: str | None
    url: str
    entries: list[PlaylistEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)


class YTDLPAnalyzer:

    def __init__(self):

        self.options = {

            "quiet": True,

            "skip_download": True,

            "no_warnings": True,

            "noplaylist": True,

        }

    def analyze(self, url: str) -> VideoInfo:

        try:

            with YoutubeDL(self.options) as ydl:

                info = ydl.extract_info(
                    url,
                    download=False,
                )

        except Exception as exc:

            raise AnalyzeError(_strip_ansi(str(exc)))

        video_formats = []

        audio_formats = []

        combined_formats = []

        for fmt in info.get("formats", []):

            width = fmt.get("width")

            height = fmt.get("height")

            resolution = (
                fmt.get("resolution")
                or (
                    f"{width}x{height}"
                    if width and height
                    else "Unknown"
                )
            )

            video_codec = fmt.get("vcodec", "none")

            audio_codec = fmt.get("acodec", "none")

            vf = VideoFormat(

                format_id=str(fmt.get("format_id", "")),

                ext=fmt.get("ext", ""),

                width=width,

                height=height,

                resolution=resolution,

                video_codec=video_codec,

                audio_codec=audio_codec,

                fps=fmt.get("fps"),

                filesize=fmt.get("filesize"),

                tbr=fmt.get("tbr"),

                protocol=fmt.get("protocol"),

                dynamic_range=fmt.get("dynamic_range"),

                is_video_only=(
                    video_codec != "none"
                    and audio_codec == "none"
                ),

                is_audio_only=(
                    video_codec == "none"
                    and audio_codec != "none"
                ),
            )

            if vf.is_video_only:

                video_formats.append(vf)

            elif vf.is_audio_only:

                audio_formats.append(vf)

            else:

                combined_formats.append(vf)

        # Highest resolution first
        video_formats.sort(
            key=lambda x: (
                x.height or 0,
                x.fps or 0,
            ),
            reverse=True,
        )

        best_video = video_formats[0] if video_formats else None

        return VideoInfo(

            title=info.get("title", ""),

            url=url,

            uploader=info.get("uploader"),

            duration=info.get("duration"),

            thumbnail=info.get("thumbnail"),

            video_formats=video_formats,

            audio_formats=audio_formats,

            combined_formats=combined_formats,

            best_video=best_video,
        )

    # =====================================================
    # Playlist Analyzer
    # =====================================================

    def analyze_playlist(self, url: str) -> PlaylistInfo:
        """
        Extract all video entries from a playlist URL.
        Does NOT download anything — only fetches metadata.
        """

        opts = {
            "quiet": True,
            "skip_download": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",   # fast: only entry metadata
            "noplaylist": False,             # allow playlist
        }

        try:
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as exc:
            raise AnalyzeError(_strip_ansi(str(exc)))

        # yt-dlp returns a dict with "_type": "playlist" for playlists
        if info.get("_type") not in ("playlist", "multi_video") and \
                "entries" not in info:
            raise AnalyzeError(
                "URL does not appear to be a playlist. "
                "Use the single-video section for individual videos."
            )

        raw_entries = info.get("entries") or []
        entries: list[PlaylistEntry] = []

        for i, entry in enumerate(raw_entries, start=1):
            if entry is None:
                continue
            video_id = entry.get("id") or entry.get("url", "")
            video_url = entry.get("url") or entry.get("webpage_url") or ""
            # flat extraction gives short IDs; build full URL if needed
            if video_url and not video_url.startswith("http"):
                video_url = f"https://www.youtube.com/watch?v={video_url}"

            entries.append(
                PlaylistEntry(
                    index=i,
                    video_id=video_id,
                    title=entry.get("title") or f"Video {i}",
                    url=video_url,
                    duration=entry.get("duration"),
                    thumbnail=entry.get("thumbnail"),
                )
            )

        return PlaylistInfo(
            playlist_id=info.get("id") or "",
            title=info.get("title") or "Untitled Playlist",
            uploader=info.get("uploader") or info.get("channel"),
            url=url,
            entries=entries,
        )
