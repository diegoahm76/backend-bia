
from gestion_documental.views.configuracion_tipos_radicados_views import actualizar_conf_agno_sig
from tramites.models.tramites_models import Tramites
from transversal.funtions.alertas import  generar_alerta_segundo_plano
from transversal.models.alertas_models import AlertasProgramadas
import json


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


def update_tramites_bia(radicado):
	# AÑADIR LO DE ACTUALIZAR TRAMITE EN T273 DE ACUERDO A LO INSERTADO EN T318
	tramites_values = Tramites.objects.filter(radicate_bia=radicado).values()
	
	if tramites_values:
		organized_data = {
			'procedure_id': tramites_values[0]['procedure_id'],
			'radicate_bia': tramites_values[0]['radicate_bia'],
			'proceeding_id': tramites_values[0]['proceeding_id'],
		}
		
		for item in tramites_values:
			field_name = item['name_key']
			if item['type_key'] == 'json':
				value = json.loads(item['value_key'])
			else:
				value = item['value_key']
			organized_data[field_name] = value