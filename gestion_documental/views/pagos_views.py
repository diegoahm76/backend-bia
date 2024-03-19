import requests
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from xml.etree import ElementTree

from django.db.models import Q
from django.db import transaction
from rest_framework import generics

class IniciarPagoView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        persona_logueada = request.user.persona
        
        headers = {'Content-Type': 'text/xml'}
        target_url = 'https://www.zonapagos.com/ws_inicio_pagov2/Zpagos.asmx'
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
                    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                        <soap:Body>
                            <inicio_pagoV2 xmlns="http://www.zonapagos.com">
                                <!--Required:-->
                                <id_tienda>33982</id_tienda>
                                <!--Required:-->
                                <clave>Cormacarena*</clave>
                                <!--Required:-->
                                <total_con_iva>5000</total_con_iva>
                                <!--Required:-->
                                <valor_iva>0</valor_iva>
                                <!--Required:-->
                                <id_pago>1000012345</id_pago>
                                <!--Required:-->
                                <descripcion_pago>Descripción pago</descripcion_pago>
                                <!--Required:-->
                                <email>zona@prueba.com.co</email>
                                <!--Required:-->
                                <id_cliente>123456789</id_cliente>
                                <!--Required:-->
                                <tipo_id>1</tipo_id>
                                <!--Required:-->
                                <nombre_cliente>Cormacarena</nombre_cliente>
                                <!--Required:-->
                                <apellido_cliente>Pruebas</apellido_cliente>
                                <!--Required:-->
                                <telefono_cliente>123456789</telefono_cliente>
                                <!--Required:-->
                                <info_opcional1>0</info_opcional1>
                                <!--Required:-->
                                <info_opcional2>0</info_opcional2>
                                <!--Required:-->
                                <info_opcional3>0</info_opcional3>
                                <!--Required:-->
                                <codigo_servicio_principal>2701</codigo_servicio_principal>
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
            return Response({"success": True, "message": "Inicio de pago exitoso", "data": {"id_transaccion": id_transaccion}}, status=status.HTTP_201_CREATED)
        else:
            return ValidationError('Ocurrió un error obteniendo el ID de la transacción')

class VerificarPagoView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        id_pago = request.query_params.get('id_pago')
        if not id_pago:
            raise ValidationError('El ID de la transacción es requerido')

        headers = {'Content-Type': 'text/xml'}
        target_url = 'https://www.zonapagos.com/WsVerificarPagoV4/VerificarPagos.asmx'
        xml_data = f"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <verificar_pago_v4 xmlns="http://www.zonapagos.com/ws_verificar_pagosV4">
                            <int_id_comercio>33982</int_id_comercio>
                            <str_usr_comercio>Cormacarena</str_usr_comercio>
                            <str_pwd_Comercio>Cormacarena*</str_pwd_Comercio>
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
                    res_pago.append({
                        "int_n_pago": pago_data[0],
                        "int_estado_pago": pago_data[1],
                        "dbl_valor_pagado": pago_data[2],
                        "dbl_valor_iva_pagado": pago_data[3],
                        "str_descripcion": pago_data[4],
                        "str_id_cliente": pago_data[5],
                        "str_nombre": pago_data[6],
                        "str_apellido": pago_data[7],
                        "str_telefono": pago_data[8],
                        "str_email": pago_data[9],
                        "str_campo1": pago_data[10],
                        "str_campo2": pago_data[11],
                        "str_campo3": pago_data[12],
                        "dat_fecha": pago_data[13],
                        "int_id_forma_pago": pago_data[14]
                    })
            
            data_response = {
                "cantidad_pagos": cantidad_pagos.text,
                "res_pago": res_pago
            }
            return Response({"success": True, "message": "Verificación de pago exitosa", "data": data_response}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError(f'Ocurrió un error: {error_detail.text}')