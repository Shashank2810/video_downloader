from time import sleep

from jobs.job import DownloadJob
from jobs.worker import DownloadWorker

job = DownloadJob(

    url="https://www.youtube.com/watch?v=e9ZupmL9BcM",

    format_id="best",

)

worker = DownloadWorker()

worker.start(job)

while True:

    print(

        job.status,

        job.progress,

        job.speed,

        job.eta,

    )

    if job.status in ("completed", "failed"):

        print()

        print(job)

        break

    sleep(1)