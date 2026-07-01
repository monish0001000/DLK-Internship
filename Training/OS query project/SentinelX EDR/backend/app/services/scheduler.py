import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Background task scheduler started.")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Background task scheduler shutdown.")

    def add_job(self, func, interval_seconds, job_id, **kwargs):
        self.scheduler.add_job(
            func,
            trigger=IntervalTrigger(seconds=interval_seconds),
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"Added scheduled job: {job_id} every {interval_seconds} seconds.")

# Global scheduler instance
scheduler_instance = TaskScheduler()
