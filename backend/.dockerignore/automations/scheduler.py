from apscheduler.schedulers.background import BackgroundScheduler

from app.automations.automation_runner import (
    run_scraper,
    import_data
)

scheduler = BackgroundScheduler()

# Monthly scraper
scheduler.add_job(
    run_scraper,
    trigger="cron",
    day=1,
    hour=1,
    minute=0,
    id="monthly_scraper"
)

# Daily CSV import
scheduler.add_job(
    import_data,
    trigger="cron",
    hour=2,
    minute=0,
    id="daily_import"
)

# scheduler.add_job(
#     import_data,
#     trigger="interval",
#     minutes=1,
#     id="test_import"
# )


def start_scheduler():
    scheduler.start()

    print("Scheduler Started")