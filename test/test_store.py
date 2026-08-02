from jobs.job import DownloadJob
from jobs.store import job_store

job1 = DownloadJob(url="https://youtube.com/watch?v=111")
job2 = DownloadJob(url="https://youtube.com/watch?v=222")

job_store.add(job1)
job_store.add(job2)

print("Jobs:", job_store.count())

print()

for job in job_store.all():
    print(job.id)
    print(job.url)
    print(job.status)
    print("-" * 40)

found = job_store.get(job1.id)

print("Found:", found.url)

job_store.remove(job1.id)

print("Remaining:", job_store.count())