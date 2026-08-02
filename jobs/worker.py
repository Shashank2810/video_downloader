"""
jobs/worker.py

Background download worker.
"""

from __future__ import annotations

from pathlib import Path
from threading import Thread

from downloader.analyzer import YTDLPAnalyzer
from downloader.exceptions import DownloadError
from downloader.progress import DownloadProgress
from downloader.progress import ProgressHook
from downloader.selector import FormatSelector
from downloader.ytdlp import YTDLPDownloader

from jobs.job import DownloadJob


class DownloadWorker:
    """
    Executes a download in a background thread.
    Supports both single-video jobs and playlist jobs.
    """

    def __init__(self):

        self.downloader = YTDLPDownloader()

        self.analyzer = YTDLPAnalyzer()

    # ---------------------------------------------------------
    # Start
    # ---------------------------------------------------------

    def start(self, job: DownloadJob):

        thread = Thread(
            target=self._run,
            args=(job,),
            daemon=True,
        )

        thread.start()

    # ---------------------------------------------------------
    # Dispatcher
    # ---------------------------------------------------------

    def _run(self, job: DownloadJob):

        if job.job_type == "playlist":
            self._run_playlist(job)
        else:
            self._run_video(job)

    # ---------------------------------------------------------
    # Single-video worker
    # ---------------------------------------------------------

    def _run_video(self, job: DownloadJob):

        try:

            job.start()

            info = self.analyzer.analyze(job.url)

            selector = FormatSelector(info)

            def update(progress: DownloadProgress):

                job.progress = round(progress.percent, 2)

                if progress.speed:
                    job.speed = f"{progress.speed / 1024 / 1024:.2f} MB/s"

                job.eta = progress.eta

                if progress.filename:
                    job.filename = progress.filename

            hook = ProgressHook(callback=update)

            if job.format_id == "best":

                file = self.downloader.download_best(
                    job.url,
                    progress_hook=hook,
                )

            else:

                video = next(
                    (f for f in info.video_formats if f.format_id == job.format_id),
                    None,
                )

                if video is None:
                    raise ValueError(f"Format {job.format_id} not found.")

                file = self.downloader.download_video(
                    url=job.url,
                    video=video,
                    progress_hook=hook,
                )

            job.complete(Path(file).name)

        except Exception as exc:

            job.fail(str(exc))

    # ---------------------------------------------------------
    # Playlist worker
    # ---------------------------------------------------------

    def _run_playlist(self, job: DownloadJob):

        try:

            job.start()

            # Step 1: fetch playlist metadata (fast — no downloads)
            job.filename = "Fetching playlist info…"
            playlist_info = self.analyzer.analyze_playlist(job.url)

            job.total = playlist_info.count
            job.filename = f"{playlist_info.title} (0 / {job.total})"

            # Step 2: per-fragment progress → update job.progress for current video
            def on_progress(progress: DownloadProgress):
                # progress within the current video (0-100)
                # blend with completed videos: overall = (done + current/100) / total * 100
                if job.total > 0:
                    overall = (job.completed_count + progress.percent / 100) / job.total * 100
                    job.progress = round(overall, 2)
                else:
                    job.progress = round(progress.percent, 2)

                if progress.speed:
                    job.speed = f"{progress.speed / 1024 / 1024:.2f} MB/s"

                job.eta = progress.eta

            hook = ProgressHook(callback=on_progress)

            # Step 3: called after each video finishes
            def on_entry(completed: int, _total: int, filename: str):
                job.completed_count = completed
                job.filename = (
                    f"{playlist_info.title} "
                    f"({completed} / {job.total}) — {filename}"
                )
                if job.total > 0:
                    job.progress = round(completed / job.total * 100, 2)

            # Step 4: download the whole playlist
            # Returns (folder_path, completed_count, skipped_count)
            folder, downloaded, skipped = self.downloader.download_playlist(
                url=job.url,
                playlist_title=playlist_info.title,
                progress_hook=hook,
                entry_hook=on_entry,
            )

            if skipped > 0:
                # Partial success — some videos were unavailable/deleted
                job.complete(
                    f"{folder.name} "
                    f"({downloaded} downloaded, {skipped} unavailable)"
                )
            else:
                job.complete(folder.name)

        except Exception as exc:

            job.fail(str(exc))
