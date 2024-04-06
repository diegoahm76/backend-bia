import os
import requests
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from xml.etree import ElementTree

from django.db.models import Q
from django.db import transaction
from rest_framework import generics
from jobs.updater import scheduler
from datetime import datetime, timedelta
from jobs.jobs import update_estado_pago

from dotenv import load_dotenv

from recaudo.models.liquidaciones_models import LiquidacionesBase
from recaudo.models.pagos_models import Pagos
from recaudo.serializers.pagos_serializers import InicioPagoSerializer
from transversal.models.personas_models import Personas
load_dotenv()

class IniciarPagoView(generics.CreateAPIView):
    serializer_class = InicioPagoSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        
        # VALIDACIONES DATA
        id_liquidacion = data.get('id_liquidacion')
        if not id_liquidacion:
            raise ValidationError('Debe asociar la liquidación a la que le realizará el pago')
        
        id_persona_pago = data.get('id_persona_pago')
        if not id_persona_pago:
            raise ValidationError('Debe asociar la persona responsable del pago')
        
        liquidacion = LiquidacionesBase.objects.filter(id=id_liquidacion).first()
        if not liquidacion:
            raise ValidationError('La liquidación asociada no existe en el sistema')
        
        persona = Personas.objects.filter(id_persona=id_persona_pago).first()
        if not persona:
            raise ValidationError('La persona asociada no existe en el sistema')
        
        email = data.get('email') if data.get('email') else persona.email
        id_cliente = data.get('id_cliente') if data.get('id_cliente') else persona.numero_documento
        nombre_cliente = data.get('nombre_cliente') if data.get('nombre_cliente') else persona.primer_nombre
        apellido_cliente = data.get('apellido_cliente') if data.get('apellido_cliente') else persona.primer_apellido
        telefono_cliente = data.get('telefono_cliente') if data.get('telefono_cliente') else persona.telefono_celular

        # INSERTAR EN MODELO
        data['estado_pago'] = 999 # PAGO PENDIENTE POR FINALIZAR
        serializer_pago = self.serializer_class(data=data)
        serializer_pago.is_valid(raise_exception=True)
        pago_creado = serializer_pago.save()
        
        headers = {'Content-Type': 'text/xml'}
        target_url = 'https://www.zonapagos.com/ws_inicio_pagov2/Zpagos.asmx'
        
        xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
                    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                        <soap:Body>
                            <inicio_pagoV2 xmlns="http://www.zonapagos.com">
                                <!--Required:-->
                                <id_tienda>{os.environ.get('ZPAGOS_ID_TIENDA')}</id_tienda>
                                <!--Required:-->
                                <clave>{os.environ.get('ZPAGOS_CLAVE')}</clave>
                                <!--Required:-->
                                <total_con_iva>{liquidacion.valor}</total_con_iva>
                                <!--Required:-->
                                <valor_iva>0</valor_iva>
                                <!--Required:-->
                                <id_pago>{pago_creado.id_pago}</id_pago>
                                <!--Required:-->
                                <descripcion_pago>{data['descripcion_pago']}</descripcion_pago>
                                <!--Required:-->
                                <email>{email}</email>
                                <!--Required:-->
                                <id_cliente>{id_cliente}</id_cliente>
                                <!--Required:-->
                                <tipo_id>{data['tipo_id'] if data.get('tipo_id') else 0}</tipo_id>
                                <!--Required:-->
                                <nombre_cliente>{nombre_cliente}</nombre_cliente>
                                <!--Required:-->
                                <apellido_cliente>{apellido_cliente}</apellido_cliente>
                                <!--Required:-->
                                <telefono_cliente>{telefono_cliente}</telefono_cliente>
                                <!--Required:-->
                                <info_opcional1>0</info_opcional1>
                                <!--Required:-->
                                <info_opcional2>0</info_opcional2>
                                <!--Required:-->
                                <info_opcional3>0</info_opcional3>
                                <!--Required:-->
                                <codigo_servicio_principal>{os.environ.get('ZPAGOS_CODIGO_SERVICIO_PRINCIPAL')}</codigo_servicio_principal>
                                <!--Optional:-->
                                <lista_codigos_servicio_multicredito>
                                    <!--Zero or more repetitions:-->
                                    <string>0</string>
                                </lista_codigos_servicio_multicredito>
                                <!--Optional:-->
                                <lista_valores_iva>
                                    <double>0</double>
                                </lista_valores_iva>
                                <total_codigos_servicio>0</total_codigos_servicio>
                            </inicio_pagoV2>
                        </soap:Body>
                    </soap:Envelope>"""
        
        response = requests.post(target_url, data=xml_data, headers=headers)
        
        if response.status_code != 200:
            raise ValidationError('Ocurrió un error con el inicio del pago')

        tree = ElementTree.fromstring(response.content)
        
        namespace = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/', 'response': 'http://www.zonapagos.com'}
        result = tree.find('.//soap:Body/response:inicio_pagoV2Response/response:inicio_pagoV2Result', namespace)
        
        if result is not None:
            id_transaccion = result.text
            if id_transaccion.startswith('-1'):
                error_message = result.text.split('-1 ')[1]
                raise ValidationError(error_message)
            
            redirect_url = f"https://www.zonapagos.com/{os.environ.get('ZPAGOS_CODIGO_RUTA')}/pago.asp?estado_pago=iniciar_pago&identificador={id_transaccion}"

            # AÑADIR SONDA
            if scheduler:
                execution_time = datetime.now() + timedelta(minutes=10)
                scheduler.add_job(update_estado_pago, args=[pago_creado.id_pago, request, scheduler, VerificarPagoView], trigger='date', run_date=execution_time)

            return redirect(redirect_url)
            # return Response({"success": True, "message": "Inicio de pago exitoso", "data": {"id_transaccion": id_transaccion}}, status=status.HTTP_201_CREATED)
        else:
            return ValidationError('Ocurrió un error obteniendo el ID de la transacción')

class VerificarPagoView(generics.CreateAPIView):
    
    def create(self, request):
        id_pago = request.query_params.get('id_pago')
        id_comercio = request.query_params.get('id_comercio', os.environ.get('ZPAGOS_ID_TIENDA'))
        if not id_pago:
            raise ValidationError('El ID de la transacción es requerido')

        headers = {'Content-Type': 'text/xml'}
        target_url = 'https://www.zonapagos.com/WsVerificarPagoV4/VerificarPagos.asmx'
        xml_data = f"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <verificar_pago_v4 xmlns="http://www.zonapagos.com/ws_verificar_pagosV4">
                            <int_id_comercio>{id_comercio}</int_id_comercio>
                            <str_usr_comercio>{os.environ.get('ZPAGOS_COMERCIO')}</str_usr_comercio>
                            <str_pwd_Comercio>{os.environ.get('ZPAGOS_CLAVE')}</str_pwd_Comercio>
                            <str_id_pago>{id_pago}</str_id_pago>
                            <int_no_pago>-1</int_no_pago>
                        </verificar_pago_v4>
                    </soap:Body>
                </soap:Envelope>"""
        
        response = requests.post(target_url, data=xml_data, headers=headers)
        
        if response.status_code != 200:
            raise ValidationError('Ocurrió un error con la verificación del pago')

        tree = ElementTree.fromstring(response.content)
        
        namespace = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/', 'response': 'http://www.zonapagos.com/ws_verificar_pagosV4'}
        error_code = tree.find('.//soap:Body/response:verificar_pago_v4Response/response:int_error', namespace)
        error_detail = tree.find('.//soap:Body/response:verificar_pago_v4Response/response:str_detalle', namespace)
        cantidad_pagos = tree.find('.//soap:Body/response:verificar_pago_v4Response/response:int_cantidad_pagos', namespace)
        res_pago = tree.find('.//soap:Body/response:verificar_pago_v4Response/response:str_res_pago', namespace)
        
        if error_code.text == "0":
            list_pagos = res_pago.text.split('|;|')
            
            res_pago = []
            for pago in list_pagos:
                if pago != '':
                    pago_data = pago.split('|')
                    pago_obj = {
                        "int_n_pago": pago_data[0].strip(),
                        "int_estado_pago": pago_data[1].strip(),
                        "dbl_valor_pagado": pago_data[2].strip(),
                        "dbl_valor_iva_pagado": pago_data[3].strip(),
                        "str_descripcion": pago_data[4].strip(),
                        "str_id_cliente": pago_data[5].strip(),
                        "str_nombre": pago_data[6].strip(),
                        "str_apellido": pago_data[7].strip(),
                        "str_telefono": pago_data[8].strip(),
                        "str_email": pago_data[9].strip(),
                        "str_campo1": pago_data[10].strip(),
                        "str_campo2": pago_data[11].strip(),
                        "str_campo3": pago_data[12].strip(),
                        "dat_fecha": pago_data[13].strip(),
                        "int_id_forma_pago": pago_data[14].strip()
                    }
                    if pago_data[14].strip() == '29':
                        pago_obj['str_ticketID'] = pago_data[15].strip()
                        pago_obj['int_codigo_servico'] = pago_data[16].strip()
                        pago_obj['int_codigo_banco'] = pago_data[17].strip()
                        pago_obj['str_nombre_banco'] = pago_data[18].strip()
                        pago_obj['str_codigo_transaccion'] = pago_data[19].strip()
                        pago_obj['int_ciclo_transaccion'] = pago_data[20].strip()
                    elif pago_data[14].strip() == '32':
                        pago_obj['str_ticketID'] = pago_data[15].strip()
                        pago_obj['int_num_tarjeta'] = pago_data[16].strip()
                        pago_obj['str_franquicia'] = pago_data[17].strip()
                        pago_obj['int_cod_aprobacion'] = pago_data[18].strip()
                        pago_obj['int_num_recibo'] = pago_data[19].strip()
                        
                    res_pago.append(pago_obj)
            
            data_response = {
                "cantidad_pagos": cantidad_pagos.text,
                "res_pago": res_pago
            }
            return Response({"success": True, "message": "Verificación de pago exitosa", "data": data_response}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError(f'Ocurrió un error: {error_detail.text}')
        
class NotificarPagoView(generics.CreateAPIView):

    def create(self, request):
        print("ENTRO AL SERVICIO DE NOTIFICAR PAGO")
        print("LOS PARAMS ENVIADOS SON: ", request.query_params)
        print("EL BODY ES: ", request.data)
        id_comercio = request.query_params.get('id_comercio')
        id_pago = request.query_params.get('id_pago')

        if not id_comercio and not id_pago:
            raise ValidationError('El ID del comercio y el ID del pago son requeridos')
        
        id_comercio_bia = str(os.environ.get('ZPAGOS_ID_TIENDA'))
        
        verificar_pago = VerificarPagoView()
        verificar_pago_response = verificar_pago.create(request)

        if verificar_pago_response.status_code == 201:
            response_verificar_data = verificar_pago_response.data.get('data').get('res_pago')[0]
            estado_pago = response_verificar_data.get('int_estado_pago').strip()

            if estado_pago in ["1","1000","4000","4003"]:
                if id_comercio == id_comercio_bia:
                    pago = Pagos.objects.filter(id_pago=id_pago).first()
                    if not pago:
                        raise ValidationError("No existe el pago en Bia con el ID enviado")
                    
                    # ACTUALIZAR EN TABLA PAGOS
                    pago.estado_pago = estado_pago
                    pago.fecha_pago = datetime.now()
                    pago.notificacion = True
                    pago.save()
                else:
                    url_get_pimysis = "http://cormacarena.myvnc.com/SoliciDocs/ASP/PIMISICARResponsePasarela.asp"
                    params = {'id_pago': id_pago, 'id_comercio': id_comercio}

                    # ENVIAR NOTIFICACION A PIMYSIS
                    notificacion_pimysis = requests.get(url_get_pimysis, params=params)
        else:
            raise ValidationError("Ocurrió un error en la verificación del pago")

        return Response({'success':True, 'detail':'Estado del pago actualizado correctamente'}, status=status.HTTP_201_CREATED)