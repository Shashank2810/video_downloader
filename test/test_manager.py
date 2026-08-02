from time import sleep

from jobs.manager import job_manager

job = job_manager.create_job(

    url="https://www.youtube.com/watch?v=e9ZupmL9BcM",

    format_id="best",

)

print("Job ID :", job.id)

while True:

    job = job_manager.get_job(job.id)

    print(

        f"{job.status:12}",

        f"{job.progress:6.2f}%",

        job.speed,

        f"ETA: {job.eta}",

    )

    if job.status in (

        "completed",

        "failed",

    ):

        break

    sleep(1)

print()

print(job)

print()

print(job_manager.statistics())