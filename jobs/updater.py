from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import generar_alerta

def start():
	scheduler = BackgroundScheduler()
	scheduler.add_job(generar_alerta, 'interval', seconds=10)
	scheduler.start()