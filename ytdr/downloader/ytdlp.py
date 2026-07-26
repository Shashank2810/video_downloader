"""
downloader/ytdlp.py

Download engine using the yt-dlp Python API.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Callable

from yt_dlp import YoutubeDL

from core.config import settings
from downloader.exceptions import DownloadError
from downloader.models import VideoFormat


# ==========================================================
# ffmpeg detection
# ==========================================================

def _ffmpeg_available() -> bool:
    """Return True if ffmpeg is findable on PATH."""
    return shutil.which("ffmpeg") is not None


def _best_format_string() -> str:
    """
    Return the best yt-dlp format selector for this machine.

    When ffmpeg is present  → "bv*+ba/b"  (best video + best audio, merged)
    When ffmpeg is absent   → "b"          (best single pre-merged stream)
    """
    if _ffmpeg_available():
        return "bv*+ba/b"
    return "b"          # best pre-merged stream — no ffmpeg needed


def _strip_ansi(text: str) -> str:
    """Remove ANSI/VT100 escape sequences from a string."""
    return re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", text)


def _safe_dirname(name: str, max_len: int = 60) -> str:
    """
    Turn an arbitrary string into a safe Windows directory name.

    Steps:
    1. Strip ANSI codes and leading/trailing whitespace.
    2. Remove characters Windows forbids in file/folder names.
    3. Remove emoji and other non-ASCII characters that can cause
       codec issues on some Windows locales.
    4. Collapse runs of spaces/underscores to a single space.
    5. Truncate to max_len characters (avoids MAX_PATH issues).
    6. Fall back to "playlist" if nothing is left.
    """
    s = _strip_ansi(name).strip()
    # Remove Windows-forbidden characters
    s = re.sub(r'[\\/:*?"<>|]', " ", s)
    # Remove emoji / non-BMP Unicode (causes issues on some Windows locales)
    s = re.sub(r"[^\x00-\x7F]", " ", s)
    # Collapse whitespace and underscores
    s = re.sub(r"[\s_]+", " ", s).strip()
    # Truncate
    s = s[:max_len].rstrip()
    return s or "playlist"


# ==========================================================
# Downloader
# ==========================================================

class YTDLPDownloader:
    """
    Download videos using yt-dlp.
    """

    def __init__(self) -> None:
        self.download_dir = settings.DOWNLOAD_DIR

    # =====================================================
    # Private
    # =====================================================

    def _options(
        self,
        format_string: str,
        progress_hook: Callable | None = None,
    ) -> dict:

        options = {
            "format": format_string,
            "outtmpl": str(
                self.download_dir / "%(title)s.%(ext)s"
            ),
            # Only set merge format when ffmpeg is available
            "noplaylist": True,
            "quiet": False,
            "no_warnings": True,
            "writesubtitles": False,
            "writeautomaticsub": False,
        }

        if _ffmpeg_available():
            options["merge_output_format"] = "mp4"

        if progress_hook:
            options["progress_hooks"] = [progress_hook]

        return options

    # =====================================================
    # Download Best
    # =====================================================

    def download_best(
        self,
        url: str,
        progress_hook: Callable | None = None,
    ) -> Path:

        return self._download(
            url=url,
            format_string=_best_format_string(),
            progress_hook=progress_hook,
        )

    # =====================================================
    # Download Selected Video Format
    # =====================================================

    def download_video(
        self,
        url: str,
        video: VideoFormat,
        best_audio: bool = True,
        progress_hook: Callable | None = None,
    ) -> Path:

        if best_audio and _ffmpeg_available():
            selector = f"{video.format_id}+ba/b"
        else:
            # No ffmpeg — fall back to the pre-merged best stream for this
            # resolution.  Using just the video format_id without audio would
            # give a silent video, so we fall back to the best single-file
            # stream instead.
            selector = f"{video.format_id}/b"

        return self._download(
            url=url,
            format_string=selector,
            progress_hook=progress_hook,
        )

    # =====================================================
    # Download Audio Only
    # =====================================================

    def download_audio(
        self,
        url: str,
        progress_hook: Callable | None = None,
    ) -> Path:

        return self._download(
            url=url,
            format_string="ba/b",
            progress_hook=progress_hook,
        )

    # =====================================================
    # Download Playlist
    # =====================================================

    def download_playlist(
        self,
        url: str,
        playlist_title: str,
        progress_hook: Callable | None = None,
        entry_hook: Callable[[int, int, str], None] | None = None,
    ) -> Path:
        """
        Download every video in a playlist into a dedicated subfolder.

        Args:
            url:            Playlist URL.
            playlist_title: Used to name the output subfolder.
            progress_hook:  yt-dlp per-fragment progress callback.
            entry_hook:     Called after each video finishes:
                            entry_hook(completed_index, total, filename)

        Returns the folder path where files were saved.
        """

        # Sanitise playlist title → safe folder name
        # Strip characters Windows forbids, collapse whitespace, and cap at 60 chars
        # so the full path stays well under the 260-char MAX_PATH limit.
        safe_title = _safe_dirname(playlist_title)
        out_dir = self.download_dir / safe_title
        out_dir.mkdir(parents=True, exist_ok=True)

        fmt = _best_format_string()

        options: dict = {
            "format": fmt,
            # %(title)s is further sanitised by yt-dlp when windowsfilenames=True
            "outtmpl": str(out_dir / "%(playlist_index)02d - %(title).80s.%(ext)s"),
            "noplaylist": False,
            "quiet": False,
            "no_warnings": True,
            "writesubtitles": False,
            "writeautomaticsub": False,
            # Tell yt-dlp to sanitise filenames for Windows automatically
            "windowsfilenames": True,
            # Skip unavailable / deleted / private videos instead of aborting
            "ignoreerrors": True,
            # Postprocessor hooks let us detect when each individual video finishes
            "postprocessor_hooks": [],
        }

        if _ffmpeg_available():
            options["merge_output_format"] = "mp4"

        if progress_hook:
            options["progress_hooks"] = [progress_hook]

        # Count completed and skipped entries through hooks
        completed: list[int] = [0]
        skipped:   list[int] = [0]

        def _pp_hook(d: dict) -> None:
            if d.get("status") == "finished":
                completed[0] += 1
                if entry_hook:
                    entry_hook(completed[0], 0, Path(d.get("filename", "")).name)

        def _progress_hook_wrapper(d: dict) -> None:
            # Track videos that were skipped/errored by yt-dlp
            if d.get("status") == "error":
                skipped[0] += 1
            if progress_hook:
                progress_hook(d)

        options["postprocessor_hooks"] = [_pp_hook]
        # Use wrapper so we can count errors without replacing the caller's hook
        options["progress_hooks"] = [_progress_hook_wrapper]

        # ignoreerrors makes yt-dlp return normally even if some entries fail,
        # so we don't wrap in try/except for the "some videos unavailable" case —
        # only catch genuine fatal errors (network down, invalid URL, etc.)
        try:
            with YoutubeDL(options) as ydl:
                ydl.download([url])
        except Exception as exc:
            # If nothing downloaded at all, treat as a real failure
            if completed[0] == 0:
                raise DownloadError(_strip_ansi(str(exc))) from exc
            # Otherwise some videos succeeded — return the folder and let
            # the caller note the partial failure via completed/skipped counts

        return out_dir, completed[0], skipped[0]

    # =====================================================
    # Generic Download
    # =====================================================

    def _download(
        self,
        url: str,
        format_string: str,
        progress_hook: Callable | None,
    ) -> Path:

        options = self._options(
            format_string=format_string,
            progress_hook=progress_hook,
        )

        try:

            with YoutubeDL(options) as ydl:

                info = ydl.extract_info(
                    url,
                    download=True,
                )

                filename = Path(
                    ydl.prepare_filename(info)
                )

                return filename

        except Exception as exc:
            raise DownloadError(_strip_ansi(str(exc))) from exc
