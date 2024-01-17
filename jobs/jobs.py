
from gestion_documental.views.configuracion_tipos_radicados_views import actualizar_conf_agno_sig
from transversal.funtions.alertas import  generar_alerta_segundo_plano
from transversal.models.alertas_models import AlertasProgramadas


def generar_alerta():
	generar_alerta_segundo_plano() 
	#alertas_generadas=AlertasProgramadas.objects.all()
	#print(alertas_generadas)
	print('TAREA FINALIZADA')

# def generar_conf_radicado_gest():
# 	actualizar_conf_agno_sig()
# 	print("TAREA FINALIZADA")


def actualizar_estado_variable_recuado():
	# print("Dato actualizado")
	pass


