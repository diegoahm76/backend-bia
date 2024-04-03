
from gestion_documental.views.configuracion_tipos_radicados_views import actualizar_conf_agno_sig
from tramites.models.tramites_models import Tramites
from transversal.funtions.alertas import  generar_alerta_segundo_plano
from transversal.models.alertas_models import AlertasProgramadas
from datetime import datetime, timedelta
import json
from recaudo.Extraccion.ExtraccionBaseDatosPimisis import  extraccion_pimisis_job  # Importa la función ExtraccionBaseDatosPimisis


def generar_alerta():
	generar_alerta_segundo_plano() 
	#alertas_generadas=AlertasProgramadas.objects.all()
	#print(alertas_generadas)
	print('TAREA FINALIZADA')

def generar_conf_radicado_gest():
	actualizar_conf_agno_sig()
	print("TAREA FINALIZADA")
	
def ExtraccionBaseDatosPimisis():
     extraccion_pimisis_job()
     print("Extraccion Exitoda")


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


def update_estado_pago(id_pago, request, scheduler, VerificarPagoView):
	verificar_pago = VerificarPagoView()
	request.query_params._mutable = True
	request.query_params['id_pago'] = id_pago
	response_pago = verificar_pago.create(request)
 
	if response_pago.status_code == 201:
		response_pago_data = response_pago.data.get('data').get('res_pago')[0]
		estado_pago = response_pago_data.get('int_estado_pago').strip()
		medio_pago = response_pago_data.get('int_id_forma_pago').strip()
		execution_time = datetime.now() + timedelta(minutes=10)

		if estado_pago not in ["1","1000","4000","4003"]:
			print(f"PAGO {id_pago} PENDIENTE")
			if estado_pago == '999' and medio_pago == '42':
				print("PENDIENTE PAGO {id_pago} GANA - CAJAS")
				execution_time = datetime.now() + timedelta(hours=1)
            
			if scheduler:
				scheduler.add_job(update_estado_pago, args=[id_pago, request, scheduler, VerificarPagoView], trigger='date', run_date=execution_time)
		else:
			print("PAGO ACEPTADO/RECHAZADO")
	else:
		print("Ocurrió un error al intententar obtener el estado del pago")