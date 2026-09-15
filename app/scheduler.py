from apscheduler.schedulers.background import BackgroundScheduler
from app.services.sla_service import sla_service

scheduler = BackgroundScheduler()

def run_sla_monitoring(app):

    with app.app_context():
        try:
            print("Running automated SLA monitoring...")
            sla_service.monitor_open_complaints()
            print("SLA monitoring completed.")
        except Exception as e:
            print("ERROR IN SLA MONITORING:",repr(e))

def start_scheduler(app):
    if scheduler.running:
        return
    
    scheduler.add_job(
        func=run_sla_monitoring,
        args=[app],
        trigger="interval",
        minutes=1,
        id="sla_monitoring",
        replace_existing=True
    )

    scheduler.start()

    print("SLA scheduler started. Runs every 1 minutes.")