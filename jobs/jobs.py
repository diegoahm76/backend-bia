
import requests
import json
import os
from gestion_documental.views.configuracion_tipos_radicados_views import actualizar_conf_agno_sig
from recaudo.models.base_models import ValoresVariables
from recaudo.models.liquidaciones_models import LiquidacionesBase
from recaudo.models.pagos_models import Pagos
from recaudo.serializers.liquidaciones_serializers import HistEstadosLiqPostSerializer
from tramites.models.tramites_models import PermisosAmbSolicitudesTramite, PermisosAmbientales, SolicitudesTramites, Tramites
from transversal.funtions.alertas import  generar_alerta_segundo_plano
from transversal.models.alertas_models import AlertasProgramadas
from datetime import datetime, timedelta

from transversal.models.base_models import Municipio
# from recaudo.Extraccion.ExtraccionBaseDatosPimisis import  extraccion_pimisis_job  # Importa la función ExtraccionBaseDatosPimisis


def generar_alerta():
	generar_alerta_segundo_plano() 
	#alertas_generadas=AlertasProgramadas.objects.all()
	#print(alertas_generadas)
	print('TAREA FINALIZADA')

def generar_conf_radicado_gest():
	actualizar_conf_agno_sig()
	print("TAREA FINALIZADA")
	
def ExtraccionBaseDatosPimisis():
     #extraccion_pimisis_job() # PENDIENTE VALIDACION DE LIBRERIA
     print("Extraccion Exitoda")


def actualizar_estado_variable_recaudo():
	current_date = datetime.now().date()
	valores_variables = ValoresVariables.objects.filter(fecha_fin__lt=current_date)
	for valor in valores_variables:
		valor.estado = False
		valor.save()
	print("SE ACTUALIZARON ESTADOS VARIABLES - RECAUDO")


def actualizar_estados_liquidaciones():
	current_date = datetime.now()
	liquidaciones_vencidas = LiquidacionesBase.objects.filter(vencimiento__lt=current_date)
	for liquidacion in liquidaciones_vencidas:
		liquidacion.estado = 'NO PAGADO'
		liquidacion.save()

		# Guardar historico liquidacion
		data_historico = {
			'liquidacion_base': liquidacion.id,
			'estado_liq': 'NO PAGADO',
			'fecha_estado': current_date
		}
		serializer_historico = HistEstadosLiqPostSerializer(data=data_historico)
		serializer_historico.is_valid(raise_exception=True)
		serializer_historico.save()
	print("SE ACTUALIZARON ESTADOS LIQUIDACIONES - RECAUDO")


def update_tramites_bia(radicado):
	# AÑADIR LO DE ACTUALIZAR TRAMITE EN T280 DE ACUERDO A LO INSERTADO EN T318
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
	
		# ACTUALIZAR TRAMITE EN T273
		radicado_split = radicado.split("-")
		prefijo_radicado = radicado_split[0]
		agno_radicado = radicado_split[1]
		nro_radicado = radicado_split[2].strip("0")

		tramite_bia = SolicitudesTramites.objects.filter(id_radicado__prefijo_radicado=prefijo_radicado, id_radicado__agno_radicado=agno_radicado, id_radicado__nro_radicado=nro_radicado).first()
		permiso_ambiental_tramite = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=tramite_bia.id_solicitud_tramite)
		if tramite_bia and not permiso_ambiental_tramite:
			str_permiso_ambiental = organized_data.get('typeRequest')
			direccion = organized_data.get('Direccion')
			municipio_id = organized_data.get('Municipio_value')

			permiso_ambiental = PermisosAmbientales.objects.filter(nombre__icontains=str_permiso_ambiental).first()
			municipio = Municipio.objects.filter(cod_municipio=municipio_id).first()

			if permiso_ambiental and direccion and municipio:
				PermisosAmbSolicitudesTramite.objects.create(
					id_permiso_ambiental=permiso_ambiental,
					id_solicitud_tramite=tramite_bia,
					direccion=direccion,
					cod_municipio=municipio
				)

def update_estado_pago(id_pago, request, scheduler, VerificarPagoView):
	verificar_pago = VerificarPagoView()
	request.query_params._mutable = True

	request.query_params['id_pago'] = id_pago
	response_pago = verificar_pago.create(request)
	print("LLEGÓ A LA SONDA")
 
	if response_pago.status_code == 201:
		print("VERIFICACION DE PAGO CORRECTO EN SONDA")
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
			# if id_comercio == id_comercio_bia:
			pago = Pagos.objects.filter(id_pago=id_pago).first()
			
			# ACTUALIZAR EN TABLA PAGOS
			if pago and pago.estado_pago != estado_pago:
				pago.estado_pago = estado_pago
				pago.fecha_pago = datetime.now()
				pago.notificacion = True
				pago.save()
			# else:
			# 	url_get_pimysis = "http://cormacarena.myvnc.com/SoliciDocs/ASP/PIMISICARResponsePasarela.asp"
			# 	params = {'id_pago': id_pago, 'id_comercio': id_comercio}

			# 	# ENVIAR NOTIFICACION A PIMYSIS
			# 	notificacion_pimysis = requests.get(url_get_pimysis, params=params)
	else:
		print("Ocurrió un error al intententar obtener el estado del pago")