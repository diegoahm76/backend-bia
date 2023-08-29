from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .jobs import generar_alerta

def start():
	scheduler = BackgroundScheduler()
	trigger = CronTrigger(hour=23, minute=59, second=0)
	scheduler.add_job(generar_alerta, trigger=trigger)
	#scheduler.add_job(generar_alerta, 'interval', seconds=10)
	scheduler.start()