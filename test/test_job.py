from jobs.job import DownloadJob

job = DownloadJob(
    url="https://youtube.com/watch?v=123"
)

print(job)

job.start()

print(job.status)

job.complete("movie.mp4")

print(job.filename)
print(job.progress)