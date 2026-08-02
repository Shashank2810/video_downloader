"""
cli.py

Command-line interface for the YouTube Downloader.

Usage examples:
    # Download one URL (best quality)
    python cli.py download https://www.youtube.com/watch?v=xxxxx

    # Download one URL with a specific codec
    python cli.py download https://www.youtube.com/watch?v=xxxxx --codec AV1

    # Download multiple URLs
    python cli.py download URL1 URL2 URL3

    # Download from a txt file (one URL per line)
    python cli.py download --file links.txt

    # List available codecs/formats for a URL before downloading
    python cli.py info https://www.youtube.com/watch?v=xxxxx

    # Preview all videos in a playlist (no download)
    python cli.py playlist-info https://www.youtube.com/playlist?list=PLxxxx

    # Download an entire playlist
    python cli.py playlist https://www.youtube.com/playlist?list=PLxxxx

    # Download an entire playlist with a specific codec
    python cli.py playlist https://www.youtube.com/playlist?list=PLxxxx --codec VP9
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from core.config import settings
from downloader.analyzer import YTDLPAnalyzer
from downloader.exceptions import AnalyzeError, DownloadError
from downloader.progress import DownloadProgress, ProgressHook
from downloader.selector import FormatSelector
from downloader.ytdlp import YTDLPDownloader

# ==========================================================
# App
# ==========================================================

app = typer.Typer(
    name="ytdl",
    help="YouTube Downloader — powered by yt-dlp",
    add_completion=False,
)

console = Console()


# ==========================================================
# Helpers
# ==========================================================

def _load_urls_from_file(path: Path) -> list[str]:
    """Read one URL per non-blank line from a text file."""
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        raise typer.Exit(1)
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def _fmt_seconds(sec: int) -> str:
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


# ==========================================================
# info command
# ==========================================================

@app.command()
def info(
    url: Annotated[str, typer.Argument(help="YouTube URL to inspect")],
) -> None:
    """Show all available formats/codecs for a video without downloading."""

    console.print(f"\n[cyan]Analyzing:[/cyan] {url}\n")

    try:
        analyzer = YTDLPAnalyzer()
        video_info = analyzer.analyze(url)
    except AnalyzeError as exc:
        console.print(f"[red]Analyze error:[/red] {exc}")
        raise typer.Exit(1)

    # Video metadata panel
    meta_lines = [
        f"[bold]Title    :[/bold] {video_info.title}",
        f"[bold]Uploader :[/bold] {video_info.uploader or 'Unknown'}",
        f"[bold]Duration :[/bold] {_fmt_seconds(video_info.duration) if video_info.duration else '--'}",
    ]
    console.print(Panel("\n".join(meta_lines), title="Video Info", border_style="blue"))

    # Formats table
    selector = FormatSelector(video_info)
    options = selector.download_options()

    table = Table(title="Available Download Options", show_header=True, header_style="bold cyan")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Value (format_id)")
    table.add_column("Label")

    for i, opt in enumerate(options, start=1):
        table.add_row(str(i), opt["value"], opt["label"])

    console.print(table)


# ==========================================================
# download command
# ==========================================================

@app.command()
def download(
    urls: Annotated[
        Optional[list[str]],
        typer.Argument(help="One or more YouTube URLs"),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option("--file", "-f", help="Path to a .txt file with one URL per line"),
    ] = None,
    codec: Annotated[
        Optional[str],
        typer.Option(
            "--codec", "-c",
            help="Preferred video codec: AV1, VP9, H264 (default: best quality)",
        ),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output directory (default: downloads/)"),
    ] = None,
) -> None:
    """
    Download one or more YouTube videos.

    URLs can be given as arguments and/or read from a --file.
    Default quality is the best available. Use --codec to pick a specific codec.
    """

    all_urls: list[str] = list(urls or [])

    if file:
        all_urls.extend(_load_urls_from_file(file))

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_urls: list[str] = []
    for u in all_urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    if not unique_urls:
        console.print("[red]No URLs provided. Use arguments or --file.[/red]")
        raise typer.Exit(1)

    dest = output_dir or settings.DOWNLOAD_DIR
    dest.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[green]Downloading {len(unique_urls)} video(s) → {dest}[/green]\n")

    analyzer = YTDLPAnalyzer()
    downloader = YTDLPDownloader()

    for idx, url in enumerate(unique_urls, start=1):
        console.rule(f"[bold cyan]{idx}/{len(unique_urls)}[/bold cyan] {url}")

        # ── Analyze ──────────────────────────────────────────
        console.print("[dim]Analyzing…[/dim]")
        try:
            video_info = analyzer.analyze(url)
        except AnalyzeError as exc:
            console.print(f"[red]  ✗ Analyze failed:[/red] {exc}")
            continue

        console.print(f"[bold]  Title:[/bold] {video_info.title}")

        # ── Select format ─────────────────────────────────────
        selector = FormatSelector(video_info)
        selected_fmt = None
        format_string = "bv*+ba/b"   # yt-dlp best-quality selector

        if codec:
            fmt = selector.best_codec(codec.upper())
            if fmt is None:
                console.print(
                    f"[yellow]  Codec '{codec}' not available; falling back to best quality.[/yellow]"
                )
            else:
                selected_fmt = fmt
                format_string = f"{fmt.format_id}+ba/b"
                console.print(f"  Format: [cyan]{codec.upper()}[/cyan] {fmt.height}p (id={fmt.format_id})")
        else:
            console.print("  Format: [cyan]Best quality[/cyan]")

        # ── Progress bar ──────────────────────────────────────
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Downloading…", total=100)

            def on_progress(p: DownloadProgress) -> None:
                progress.update(task, completed=p.percent)

            hook = ProgressHook(callback=on_progress)

            try:
                if selected_fmt:
                    file_path = downloader.download_video(
                        url=url,
                        video=selected_fmt,
                        progress_hook=hook,
                    )
                else:
                    file_path = downloader.download_best(
                        url=url,
                        progress_hook=hook,
                    )
            except DownloadError as exc:
                console.print(f"[red]  ✗ Download failed:[/red] {exc}")
                continue

        console.print(f"[green]  ✓ Saved:[/green] {Path(file_path).name}\n")

    console.print("[bold green]Done.[/bold green]")


# ==========================================================
# playlist-info command
# ==========================================================

@app.command(name="playlist-info")
def playlist_info(
    url: Annotated[str, typer.Argument(help="YouTube playlist URL")],
) -> None:
    """Show all videos in a playlist without downloading anything."""

    console.print(f"\n[cyan]Fetching playlist:[/cyan] {url}\n")

    try:
        analyzer = YTDLPAnalyzer()
        pl = analyzer.analyze_playlist(url)
    except AnalyzeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    meta = [
        f"[bold]Title    :[/bold] {pl.title}",
        f"[bold]Uploader :[/bold] {pl.uploader or 'Unknown'}",
        f"[bold]Videos   :[/bold] {pl.count}",
    ]
    console.print(Panel("\n".join(meta), title="Playlist Info", border_style="blue"))

    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("#",      justify="right", style="dim", width=5)
    table.add_column("Title",  style="white")
    table.add_column("Duration", justify="right", style="dim")

    for e in pl.entries:
        dur = _fmt_seconds(e.duration) if e.duration else "--"
        table.add_row(str(e.index), e.title, dur)

    console.print(table)


# ==========================================================
# playlist command (download)
# ==========================================================

@app.command()
def playlist(
    url: Annotated[str, typer.Argument(help="YouTube playlist URL to download")],
    codec: Annotated[
        Optional[str],
        typer.Option("--codec", "-c", help="Preferred codec: AV1, VP9, H264 (default: best)"),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output directory (default: downloads/)"),
    ] = None,
) -> None:
    """
    Download all videos in a YouTube playlist into a named subfolder.

    Videos are saved as:  <output>/<playlist title>/<index> - <title>.<ext>
    """

    console.print(f"\n[cyan]Fetching playlist info:[/cyan] {url}\n")

    # ── Analyze playlist first ────────────────────────────
    try:
        analyzer = YTDLPAnalyzer()
        pl = analyzer.analyze_playlist(url)
    except AnalyzeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    meta = [
        f"[bold]Title    :[/bold] {pl.title}",
        f"[bold]Uploader :[/bold] {pl.uploader or 'Unknown'}",
        f"[bold]Videos   :[/bold] {pl.count}",
    ]
    console.print(Panel("\n".join(meta), title="Playlist Info", border_style="blue"))

    dest = output_dir or settings.DOWNLOAD_DIR
    dest.mkdir(parents=True, exist_ok=True)

    console.print(
        f"[green]Downloading {pl.count} video(s) → {dest / pl.title}[/green]\n"
    )

    downloader = YTDLPDownloader()
    completed_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        overall_task = progress.add_task(
            f"[cyan]{pl.title}[/cyan]", total=pl.count
        )
        video_task = progress.add_task("Waiting…", total=100)

        def on_progress(p: DownloadProgress) -> None:
            progress.update(video_task, completed=p.percent)

        def on_entry(completed: int, _total: int, filename: str) -> None:
            nonlocal completed_count
            completed_count = completed
            progress.update(overall_task, completed=completed)
            progress.update(video_task, completed=0,
                            description=f"[dim]{filename}[/dim]")

        hook = ProgressHook(callback=on_progress)

        try:
            folder = downloader.download_playlist(
                url=url,
                playlist_title=pl.title,
                progress_hook=hook,
                entry_hook=on_entry,
            )
        except DownloadError as exc:
            console.print(f"\n[red]Download failed:[/red] {exc}")
            raise typer.Exit(1)

        progress.update(overall_task, completed=pl.count)

    console.print(
        f"\n[bold green]✓ Done.[/bold green] "
        f"{completed_count} video(s) saved in [cyan]{folder}[/cyan]"
    )


# ==========================================================
# Entry point
# ==========================================================

if __name__ == "__main__":
    app()
