# YouTube Downloader

A professional **YouTube video downloader** built with Python.
Ships with a **web application** (runs in your browser) and a **command-line interface** — both powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

---

## Features

| Feature | Web App | CLI |
|---|:---:|:---:|
| Download a single video | ✅ | ✅ |
| Analyze video before downloading (preview info, codec list) | ✅ | ✅ |
| Choose video quality / codec (AV1, VP9, H.264) | ✅ | ✅ |
| Download multiple URLs at once (batch) | ✅ | ✅ |
| Upload a `.txt` file of URLs | ✅ | ✅ |
| Download an entire playlist | ✅ | ✅ |
| Preview playlist contents before downloading | ✅ | ✅ |
| Live download progress (speed, ETA, % per video) | ✅ | ✅ |
| Playlist progress counter (3 / 12 videos done) | ✅ | ✅ |
| Skip unavailable / deleted playlist videos automatically | ✅ | ✅ |
| Background download jobs (non-blocking) | ✅ | — |
| Cancel a running download | ✅ | — |
| ffmpeg auto-detection with fallback | ✅ | ✅ |
| Download history database (SQLite) | ✅ | — |
| Persistent logs | ✅ | — |

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10 or newer |
| yt-dlp | installed via `requirements.txt` |
| ffmpeg | **Optional** — required for 1080p+ merged quality |

> **Without ffmpeg** the app still works, but downloads the best *pre-merged* stream
> (typically 720p). Install ffmpeg to unlock full HD quality.

---

## Installation

### Step 1 — Clone or download the project


git clone <repo-url>
cd youtube-downloader


### Step 2 — Install dependencies

Double-click **`update.bat`** and choose option **4 — Install Everything**.

Or run manually:


pip install -r requirements.txt


### Step 3 — (Optional) Install ffmpeg for HD quality


winget install --id Gyan.FFmpeg


Then **restart your terminal** (or the server). The app auto-detects ffmpeg on startup and shows a green banner in the browser.

---

## Running the Web App

### Development mode (auto-reloads on code changes)

Double-click **`run_dev.bat`**  
or run:


uvicorn app:app --reload


### Production mode

Double-click **`run_prod.bat`**  
or run:


uvicorn app:app


Then open your browser at:


http://127.0.0.1:8000


---

## Web App — How to Use

### Single Video Download

1. Paste a YouTube URL into the **Video URL(s)** box.
2. Click **Analyze & Choose Quality**.
3. The app fetches video info and shows:
   - Thumbnail, title, uploader, duration
   - All available codecs (AV1, VP9, H.264)
   - A dropdown with every quality option
4. Pick your quality from the dropdown.
5. Click **⬇ Download This Video**.
6. A live progress bar shows speed, ETA, and percentage.
7. When done, click **↩ Download Another** to reset.

### Batch Download (multiple URLs)

1. Paste multiple YouTube URLs into the box — **one URL per line**.
2. Click **Download All (Best Quality)**.
3. Every URL becomes an independent background job.
4. A **Download Queue** appears showing each job's live status.

### Upload a TXT File

1. Click **Upload TXT File** and select a `.txt` file.
2. URLs from the file are appended to the URL box.
3. Then use either **Analyze** (single) or **Download All** (batch).

### Playlist Download

1. Paste a YouTube playlist URL into the **Playlist Download** box.
2. Click **Preview Playlist** — the app lists all videos with titles and durations.
3. Click **⬇ Download Entire Playlist**.
4. A single background job downloads all videos into a named subfolder  
   inside `downloads/`.
5. Progress shows:
   - Overall percentage bar
   - Videos counter: `3 / 24`
   - Speed
   - Currently downloading file name
6. Unavailable or deleted videos are **skipped automatically** — the rest still download.

---

## Command-Line Interface (CLI)

Run `python cli.py --help` to see all commands.


Commands:
  info           Preview formats/codecs for a video (no download)
  download       Download one or more videos
  playlist-info  Preview all videos in a playlist (no download)
  playlist       Download all videos in a playlist


---

### `info` — Preview video formats


python cli.py info https://www.youtube.com/watch?v=VIDEO_ID


Shows a table of every available quality option for the video.

---

### `download` — Download videos


# Single video — best quality
python cli.py download https://www.youtube.com/watch?v=VIDEO_ID

# Single video — specific codec
python cli.py download https://www.youtube.com/watch?v=VIDEO_ID --codec VP9
python cli.py download https://www.youtube.com/watch?v=VIDEO_ID --codec AV1
python cli.py download https://www.youtube.com/watch?v=VIDEO_ID --codec H264

# Multiple URLs at once
python cli.py download URL1 URL2 URL3

# From a .txt file (one URL per line)
python cli.py download --file links.txt

# Custom output folder
python cli.py download URL1 --output D:\Videos


**Options:**

| Flag | Short | Description |
|---|---|---|
| `--file PATH` | `-f` | Path to a `.txt` file with one URL per line |
| `--codec TEXT` | `-c` | Preferred codec: `AV1`, `VP9`, `H264` |
| `--output PATH` | `-o` | Output folder (default: `downloads/`) |

---

### `playlist-info` — Preview playlist


python cli.py playlist-info https://www.youtube.com/playlist?list=PLAYLIST_ID


Lists every video in the playlist with title and duration — no download.

---

### `playlist` — Download entire playlist


# Best quality
python cli.py playlist https://www.youtube.com/playlist?list=PLAYLIST_ID

# Specific codec
python cli.py playlist https://www.youtube.com/playlist?list=PLAYLIST_ID --codec VP9

# Custom output folder
python cli.py playlist https://www.youtube.com/playlist?list=PLAYLIST_ID --output D:\Videos


Videos are saved as:

downloads/
  Playlist Title/
    01 - Video Title.mp4
    02 - Video Title.mp4
    ...


**Options:**

| Flag | Short | Description |
|---|---|---|
| `--codec TEXT` | `-c` | Preferred codec: `AV1`, `VP9`, `H264` |
| `--output PATH` | `-o` | Output folder (default: `downloads/`) |

---

## Maintenance

Double-click **`update.bat`** for a menu:


1. Install / Update Project Dependencies
2. Update yt-dlp
3. Update pip
4. Install Everything (Recommended)
5. Exit


Run **option 2** regularly to keep yt-dlp up to date — YouTube changes its internals
frequently and an outdated yt-dlp is the most common cause of download failures.

---

## Project Structure


youtube-downloader/
│
├── app.py                  # FastAPI application entry point
├── cli.py                  # Command-line interface (Typer)
├── requirements.txt        # Python dependencies
├── run_dev.bat             # Start development server (Windows)
├── run_prod.bat            # Start production server (Windows)
├── update.bat              # Dependency maintenance menu (Windows)
│
├── core/
│   ├── config.py           # Settings (paths, server host/port, etc.)
│   ├── database.py         # SQLAlchemy engine + session factory
│   └── logger.py           # Loguru logger (console + file)
│
├── downloader/
│   ├── analyzer.py         # Fetch video/playlist metadata via yt-dlp
│   ├── ytdlp.py            # Download engine (single video + playlist)
│   ├── selector.py         # Format/codec selection helpers
│   ├── progress.py         # yt-dlp progress hook → DownloadProgress model
│   ├── models.py           # VideoFormat, VideoInfo dataclasses
│   └── exceptions.py       # AnalyzeError, DownloadError, etc.
│
├── jobs/
│   ├── job.py              # DownloadJob dataclass (status, progress, counters)
│   ├── store.py            # In-memory job store (dict)
│   ├── manager.py          # JobManager — create, cancel, list jobs
│   └── worker.py           # Background thread workers (video + playlist)
│
├── models/
│   └── download.py         # SQLAlchemy Download ORM model + DownloadStatus enum
│
├── repositories/
│   └── download_repository.py   # All DB queries for downloads
│
├── services/
│   └── download_service.py      # Business logic layer over the repository
│
├── web/
│   ├── routes.py           # All FastAPI route handlers (API + HTML)
│   ├── schemas.py          # Pydantic request/response models
│   ├── templates/
│   │   ├── base.html       # Base HTML layout
│   │   └── index.html      # Main page template
│   └── static/
│       ├── css/style.css   # Dark-theme stylesheet
│       └── js/app.js       # All browser-side logic
│
├── downloads/              # Default output folder for downloaded files
├── data/
│   └── history.db          # SQLite download history database
└── logs/
    ├── app.log             # Application log (rotates at 10 MB)
    └── error.log           # Error-only log (rotates at 10 MB)


---

## How It Works — Architecture


Browser / CLI
     │
     ▼
 FastAPI (app.py)
     │
     ├── /analyze          → YTDLPAnalyzer.analyze()
     ├── /analyze-playlist → YTDLPAnalyzer.analyze_playlist()
     ├── /download         → JobManager.create_job(type="video")
     ├── /download-playlist→ JobManager.create_job(type="playlist")
     ├── /batch-download   → JobManager.create_job() × N
     ├── /progress/:id     → JobStore.get(id) → ProgressResponse
     ├── /cancel/:id       → JobManager.cancel_job(id)
     └── /jobs             → JobStore.all()

JobManager
     │
     └── DownloadWorker (background Thread)
              │
              ├── _run_video()
              │     └── YTDLPDownloader.download_best()
              │         or download_video() for specific format
              │
              └── _run_playlist()
                    ├── YTDLPAnalyzer.analyze_playlist()  (metadata only)
                    └── YTDLPDownloader.download_playlist()
                          └── yt-dlp downloads each video
                                ignoreerrors=True → skips unavailable
                                entry_hook → updates job counters per video


**Progress flow:**
1. Browser polls `GET /progress/{job_id}` every second.
2. The server reads the live `DownloadJob` object from memory.
3. `DownloadJob.progress`, `.speed`, `.eta`, `.completed_count` are updated
   in real time by the background thread via yt-dlp progress hooks.
4. Browser updates the progress bar and counters from the JSON response.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `POST` | `/analyze` | Fetch single video metadata + format list |
| `POST` | `/analyze-playlist` | Fetch playlist metadata + all video titles |
| `POST` | `/download` | Start single-video download job |
| `POST` | `/download-playlist` | Start playlist download job |
| `POST` | `/batch-download` | Start one job per URL in the list |
| `POST` | `/upload-txt` | Upload `.txt` file, start one job per URL |
| `GET` | `/progress/{job_id}` | Poll job status, progress, speed, ETA |
| `POST` | `/cancel/{job_id}` | Cancel a running job |
| `GET` | `/jobs` | List all jobs (id, status, progress, filename) |
| `GET` | `/stats` | Job counts (total, active, completed, failed) |
| `GET` | `/system-info` | ffmpeg availability |
| `GET` | `/health` | Server health check |

---

## Configuration

Settings are in [`core/config.py`](core/config.py) and can be overridden with a `.env` file in the project root.

| Variable | Default | Description |
|---|---|---|
| `HOST` | `127.0.0.1` | Server bind address |
| `PORT` | `8000` | Server port |
| `DOWNLOAD_DIR` | `downloads/` | Where files are saved |
| `DATA_DIR` | `data/` | Database location |
| `LOG_DIR` | `logs/` | Log file location |
| `DATABASE_FILE` | `history.db` | SQLite filename |

**Example `.env`:**

HOST=0.0.0.0
PORT=9000
DOWNLOAD_DIR=D:\MyVideos


---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ERROR: Requested format is not available` | Run `python -m pip install --upgrade yt-dlp` |
| `ffmpeg not found` — only 720p downloads | Run `winget install --id Gyan.FFmpeg`, restart server |
| Playlist folder name error on Windows | Already handled — folder names are auto-sanitised to ASCII ≤ 60 chars |
| Unavailable video fails entire playlist | Already handled — unavailable videos are skipped, rest still download |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` or use `update.bat` option 4 |
| Port 8000 already in use | Add `PORT=9000` to `.env` and restart |

---

## Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | Web framework — API routes + HTML serving |
| `uvicorn` | ASGI server that runs FastAPI |
| `jinja2` | HTML template engine |
| `python-multipart` | File upload support (`.txt` files) |
| `yt-dlp` | Core download engine |
| `typer` | CLI framework |
| `rich` | CLI progress bars and tables |
| `sqlalchemy` | ORM for download history (SQLite) |
| `pydantic` | Request/response data validation |
| `pydantic-settings` | `.env` file config loading |
| `aiofiles` | Async file I/O |
| `python-dotenv` | `.env` file support |
| `loguru` | Structured logging to file + console |
