"""
downloader/progress.py

Progress tracking for yt-dlp downloads.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


# ==========================================================
# Progress State
# ==========================================================

@dataclass(slots=True)
class DownloadProgress:
    """
    Represents the current download progress.
    """

    status: str = ""

    filename: str = ""

    percent: float = 0.0

    downloaded_bytes: int = 0

    total_bytes: int = 0

    speed: float = 0.0

    eta: int = 0

    elapsed: float = 0.0

    completed: bool = False


# ==========================================================
# Progress Hook
# ==========================================================

class ProgressHook:
    """
    yt-dlp progress hook.

    Example:

        hook = ProgressHook()

        YoutubeDL({
            "progress_hooks": [hook]
        })

        print(hook.percent)

    You can also provide a callback:

        def update(progress):
            print(progress.percent)

        hook = ProgressHook(callback=update)
    """

    def __init__(
        self,
        callback: Callable[[DownloadProgress], None] | None = None,
    ) -> None:

        self.progress = DownloadProgress()

        self.callback = callback

    # ------------------------------------------------------

    def __call__(self, data: dict):

        status = data.get("status", "")

        self.progress.status = status

        # ----------------------------------------------
        # Downloading
        # ----------------------------------------------

        if status == "downloading":

            total = (
                data.get("total_bytes")
                or data.get("total_bytes_estimate")
                or 0
            )

            downloaded = data.get("downloaded_bytes", 0)

            percent = 0.0

            if total > 0:
                percent = downloaded * 100 / total

            self.progress.filename = Path(
                data.get("filename", "")
            ).name

            self.progress.downloaded_bytes = downloaded

            self.progress.total_bytes = total

            self.progress.percent = percent

            self.progress.speed = data.get("speed") or 0

            self.progress.eta = data.get("eta") or 0

            self.progress.elapsed = data.get("elapsed") or 0

            self.progress.completed = False

        # ----------------------------------------------
        # Finished
        # ----------------------------------------------

        elif status == "finished":

            self.progress.status = "finished"

            self.progress.percent = 100.0

            self.progress.completed = True

            self.progress.filename = Path(
                data.get("filename", "")
            ).name

        # ----------------------------------------------
        # Notify callback
        # ----------------------------------------------

        if self.callback:

            self.callback(self.progress)

    # ------------------------------------------------------

    @property
    def is_finished(self) -> bool:

        return self.progress.completed

    # ------------------------------------------------------

    @property
    def percent(self) -> float:

        return self.progress.percent

    # ------------------------------------------------------

    @property
    def speed(self) -> float:

        return self.progress.speed

    # ------------------------------------------------------

    @property
    def eta(self) -> int:

        return self.progress.eta

    # ------------------------------------------------------

    def reset(self) -> None:
        """
        Reset progress information.
        """

        self.progress = DownloadProgress()

    # ------------------------------------------------------

    def as_dict(self) -> dict:

        return {

            "status": self.progress.status,

            "filename": self.progress.filename,

            "percent": round(self.progress.percent, 2),

            "downloaded_bytes": self.progress.downloaded_bytes,

            "total_bytes": self.progress.total_bytes,

            "speed": self.progress.speed,

            "eta": self.progress.eta,

            "elapsed": self.progress.elapsed,

            "completed": self.progress.completed,

        }