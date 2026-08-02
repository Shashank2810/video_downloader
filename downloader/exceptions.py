"""
Custom exceptions for downloader.
"""


class DownloaderError(Exception):
    """Base downloader exception."""
    pass


class InvalidUrlError(DownloaderError):
    """Invalid URL."""
    pass


class AnalyzeError(DownloaderError):
    """Video analyze failed."""
    pass


class DownloadError(DownloaderError):
    """Download failed."""
    pass


class FFmpegNotFoundError(DownloaderError):
    """FFmpeg missing."""
    pass