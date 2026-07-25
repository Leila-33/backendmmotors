from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

from core.scheduler.jobs.complete_rentals_job import (
    run_complete_rentals
)

from core.scheduler.jobs.expire_quotes_job import (
    run_expire_quotes
)


scheduler = AsyncIOScheduler()



def start_scheduler():

    scheduler.add_job(
        run_complete_rentals,
        trigger="interval",
        hours=24,
        id="complete_rentals"
    )


    scheduler.add_job(
        run_expire_quotes,
        trigger="cron",
        hour=2,
        minute=0,
        id="expire_quotes"
    )


    scheduler.start()

    print("Scheduler started")



def stop_scheduler():

    scheduler.shutdown()

    print("Scheduler stopped")