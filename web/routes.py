"""
web/routes.py

Application Routes
"""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session


from core.database import get_db


from downloader.analyzer import YTDLPAnalyzer
from downloader.selector import FormatSelector
from downloader.ytdlp import _ffmpeg_available


from jobs.manager import job_manager


from web.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchDownloadRequest,
    BatchDownloadResponse,
    DownloadOption,
    DownloadRequest,
    DownloadResponse,
    PlaylistAnalyzeResponse,
    PlaylistDownloadRequest,
    PlaylistEntry,
    ProgressResponse,
)



# ==========================================================
# Router
# ==========================================================

router = APIRouter()


templates = Jinja2Templates(
    directory="web/templates"
)





# ==========================================================
# Home
# ==========================================================

@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )







# ==========================================================
# Analyze Video
# ==========================================================

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
async def analyze_video(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
):

    try:

        analyzer = YTDLPAnalyzer()

        info = analyzer.analyze(payload.url)

        selector = FormatSelector(info)

        options = [
            DownloadOption(
                value=item["value"],
                label=item["label"],
            )
            for item in selector.download_options()
        ]

        return AnalyzeResponse(
            title=info.title,
            uploader=info.uploader,
            duration=info.duration,
            thumbnail=info.thumbnail,
            options=options,
            codecs=selector.codecs(),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )








# ==========================================================
# Start Download
# ==========================================================

@router.post(
    "/download",
    response_model=DownloadResponse,
)
async def download_video(
    payload: DownloadRequest,
):

    try:


        job = job_manager.create_job(

            url=payload.url,

            format_id=payload.format_id,

        )



        return DownloadResponse(

            success=True,

            message="Download started.",

            job_id=job.id,

            status=job.status,

        )



    except Exception as exc:


        raise HTTPException(

            status_code=500,

            detail=str(exc),

        )









# ==========================================================
# Download Progress
# ==========================================================

@router.get(
    "/progress/{job_id}",
    response_model=ProgressResponse,
)
async def progress(
    job_id: str
):


    job = job_manager.get_job(
        job_id
    )



    if job is None:


        raise HTTPException(

            status_code=404,

            detail="Job not found.",

        )



    return ProgressResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        speed=job.speed,
        eta=job.eta,
        filename=job.filename,
        error=job.error,
        total=job.total,
        completed_count=job.completed_count,
    )









# ==========================================================
# Cancel Download
# ==========================================================

@router.post(
    "/cancel/{job_id}"
)
async def cancel_download(
    job_id: str
):

    cancelled = job_manager.cancel_job(job_id)

    if not cancelled:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return {
        "success": True,
        "message": "Download cancelled.",
    }









# ==========================================================
# Batch Download
# ==========================================================

@router.post(
    "/batch-download",
    response_model=BatchDownloadResponse,
)
async def batch_download(
    payload: BatchDownloadRequest,
):
    """
    Start a download job for each URL in the list.
    All jobs use the same format_id.
    """

    try:

        jobs = []

        for url in payload.urls:

            job = job_manager.create_job(
                url=url,
                format_id=payload.format_id,
            )

            jobs.append(
                DownloadResponse(
                    success=True,
                    message="Download started.",
                    job_id=job.id,
                    status=job.status,
                )
            )

        return BatchDownloadResponse(jobs=jobs)

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ==========================================================
# Playlist — Analyze
# ==========================================================

@router.post("/analyze-playlist", response_model=PlaylistAnalyzeResponse)
async def analyze_playlist(payload: AnalyzeRequest):
    """
    Fetch metadata for every video in a YouTube playlist.
    Does NOT start any downloads.
    """
    try:
        analyzer = YTDLPAnalyzer()
        info = analyzer.analyze_playlist(payload.url)

        return PlaylistAnalyzeResponse(
            playlist_id=info.playlist_id,
            title=info.title,
            uploader=info.uploader,
            url=info.url,
            count=info.count,
            entries=[
                PlaylistEntry(
                    index=e.index,
                    video_id=e.video_id,
                    title=e.title,
                    url=e.url,
                    duration=e.duration,
                    thumbnail=e.thumbnail,
                )
                for e in info.entries
            ],
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ==========================================================
# Playlist — Download
# ==========================================================

@router.post("/download-playlist", response_model=DownloadResponse)
async def download_playlist(payload: PlaylistDownloadRequest):
    """
    Start a single background job that downloads the entire playlist.
    """
    try:
        job = job_manager.create_job(
            url=payload.url,
            format_id=payload.format_id,
            job_type="playlist",
        )
        return DownloadResponse(
            success=True,
            message="Playlist download started.",
            job_id=job.id,
            status=job.status,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ==========================================================
# Jobs List
# ==========================================================

@router.get("/jobs")
async def jobs():
    return [
        {
            "id": job.id,
            "status": job.status,
            "progress": job.progress,
            "filename": job.filename,
            "job_type": job.job_type,
            "total": job.total,
            "completed_count": job.completed_count,
        }
        for job in job_manager.all_jobs()
    ]









# ==========================================================
# Upload TXT file → queue batch downloads
# ==========================================================

@router.post("/upload-txt")
async def upload_txt(
    txt_file: UploadFile = File(...),
    format_id: str = Form("best"),
):
    """
    Accept a .txt file upload (one URL per line) and start
    a download job for every URL found.
    """

    content = await txt_file.read()
    lines = content.decode("utf-8", errors="replace").splitlines()
    urls = [line.strip() for line in lines if line.strip()]

    if not urls:
        raise HTTPException(status_code=400, detail="No URLs found in file.")

    jobs = []
    for url in urls:
        job = job_manager.create_job(url=url, format_id=format_id)
        jobs.append(
            DownloadResponse(
                success=True,
                message="Download started.",
                job_id=job.id,
                status=job.status,
            )
        )

    return BatchDownloadResponse(jobs=jobs)


# ==========================================================
# Statistics
# ==========================================================

@router.get(
    "/stats"
)
async def statistics():

    return job_manager.statistics()









# ==========================================================
# System Info
# ==========================================================

@router.get("/system-info")
async def system_info():
    """Returns runtime capabilities (ffmpeg availability, etc.)."""
    return {
        "ffmpeg": _ffmpeg_available(),
    }


# ==========================================================
# Health
# ==========================================================

@router.get(
    "/health"
)
async def health():

    return {
        "status": "ok",
        "application": "YouTube Downloader",
        "version": "1.0.0",
    }