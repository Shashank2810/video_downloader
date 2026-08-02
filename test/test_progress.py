from downloader.progress import ProgressHook

hook = ProgressHook()

hook(
    {
        "status": "downloading",
        "filename": "movie.mp4",
        "downloaded_bytes": 50_000_000,
        "total_bytes": 100_000_000,
        "speed": 12_500_000,
        "eta": 4,
        "elapsed": 3,
    }
)

print(hook.as_dict())