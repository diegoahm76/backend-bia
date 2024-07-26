import json

import requests
from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from recurso_hidrico.models.zonas_hidricas_models import TipoAguaZonaHidrica, ZonaHidrica, MacroCuencas,TipoZonaHidrica,SubZonaHidrica, CuencasSubZonas, TipoUsoAgua
from recurso_hidrico.serializers.zonas_hidricas_serializers import SubZonaHidricaTrSerializerr,CuencasTuaSerializerr, SubZonaHidricaValorRegionalSerializer, TipoAguaZonaHidricaSerializer, ZonaHidricaSerializer, MacroCuencasSerializer,TipoZonaHidricaSerializer,SubZonaHidricaSerializer, CuencasSerializer, TipoUsoAguaSerializer
import copy
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from tramites.models.tramites_models import SolicitudesTramites, Tramites, PermisosAmbSolicitudesTramite
from tramites.views.tramites_views import TramitesPivotGetView
from transversal.models.base_models import Municipio

# Vista get para las 4 tablas de zonas hidricas
class MacroCuencasListView (generics.ListAPIView):
    queryset = MacroCuencas.objects.all()
    serializer_class = MacroCuencasSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuencas = MacroCuencas.objects.all()
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class ZonaHidricaListView (generics.ListCreateAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = ZonaHidricaSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request,pk):
        zonas = ZonaHidrica.objects.filter(id_macro_cuenca=pk)
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class TipoZonaHidricaListView (generics.ListCreateAPIView):
    queryset = TipoZonaHidrica.objects.all()
    serializer_class = TipoZonaHidricaSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        zonas = TipoZonaHidrica.objects.all()
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class SubZonaHidricaListView (generics.ListCreateAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request,pk):
        zonas = SubZonaHidrica.objects.filter(id_zona_hidrica=pk)
        serializer = self.serializer_class(zonas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
class CuencasListView (generics.ListCreateAPIView):
    queryset = CuencasSubZonas.objects.all()
    serializer_class = CuencasSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request,pk):
        cuencas = CuencasSubZonas.objects.filter(id_sub_zona_hidrica=pk)
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    


class CuencasSubZonasCreate(generics.CreateAPIView):
    serializer_class = CuencasSerializer
    permission_classes = [IsAuthenticated]
    queryset = CuencasSubZonas.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            data_in = request.data
            
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            cuenca = serializer.save()

            return Response({'success': True, 'detail': 'Registro creado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            raise ValidationError(e.detail)
        

class CuencasSubZonasDeleteView(generics.DestroyAPIView):
    serializer_class = CuencasSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            data_in = request.data
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            cuenca = serializer.save()

            return Response({'success': True, 'detail': 'Registro creado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            raise ValidationError(e.detail)

    def delete(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            obj = CuencasSubZonas.objects.filter(id_cuenca=pk).first()
            
            if obj is None:
                return Response({'success': False, 'detail': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.serializer_class(obj)
            
            obj.delete()
            
            return Response({
                'success': True,
                'detail': 'Registro eliminado exitosamente',
                'data': serializer.data  
            }, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            raise ValidationError(e.detail)
        

class CuencasSubZonasUpdateView(generics.UpdateAPIView):
    serializer_class = CuencasSerializer
    permission_classes = [IsAuthenticated]
    queryset = CuencasSubZonas.objects.all()
    lookup_field = 'id_cuenca'  

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Crear un serializer con los datos del request y el objeto existente
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Obtener el objeto actualizado después de guardar
        updated_instance = self.get_object()
        updated_data = self.get_serializer(updated_instance).data
        
        return Response({
            "detail": "El registro se actualizó correctamente.",
            "data": updated_data
        }, status=status.HTTP_200_OK)

    

class CrearSubZonaHidricaVista(generics.CreateAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
                      
            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
           

#borrar lugar y rio 
class BorrarZonaHidricaVista(generics.DestroyAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = ZonaHidricaSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente'},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({e.detail})
        

class BorrarSubZonaHidricaVista(generics.DestroyAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaSerializer

    def destroy(self, request, *args, **kwargs):
            
            instance = self.get_object()
            
            if not instance:
                raise NotFound('No se encontró el registro')
            previus = copy.copy(instance)
            instance.delete()
            serializer = self.get_serializer(previus)
            return Response({'success': True, 'detail': 'Registro eliminado correctamente','data':serializer.data},
                            status=status.HTTP_200_OK)
        
        
class ActualizarZonaHidricaVista(generics.UpdateAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = ZonaHidricaSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ActualizarSubZonaHidricaVista(generics.UpdateAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaValorRegionalSerializer  # Utiliza un serializador específico

    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene la instancia existente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)  # Valida los datos
        serializer.save()  # Guarda la instancia con los datos actualizados

        return Response({'succes': True, 'detail':'Se actualizo correctamente', 'data':serializer.data,}, status=status.HTTP_200_OK)

class TipoAguaZonaHidricaListView (generics.ListAPIView):
    queryset = TipoAguaZonaHidrica.objects.all()
    serializer_class = TipoAguaZonaHidricaSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cuencas = TipoAguaZonaHidrica.objects.all()
        serializer = self.serializer_class(cuencas,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class CrearZonaHidricaVista(generics.CreateAPIView):
    queryset = ZonaHidrica.objects.all()
    serializer_class = ZonaHidricaSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
                  
            serializer.save()

            return Response({'success': True, 'detail': 'Registro creado correctamente', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Manejar la excepción de validación de manera adecuada, por ejemplo, devolver un mensaje específico
            raise ValidationError({'error': 'Error al crear el registro', 'detail': e.detail})
        
    



class EnviarSMSView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        telefono = request.data.get('telefono')
        mensaje = request.data.get('mensaje')

        if telefono and mensaje:
            # Llama a la función send_sms con los datos proporcionados
            Util.send_sms(telefono, mensaje)

            # Puedes personalizar la respuesta según tus necesidades
            return Response({'mensaje': 'SMS enviado correctamente'}, status=status.HTTP_200_OK)
        else:
            # Maneja el caso en el que no se proporcionan el teléfono o el mensaje
            return Response({'error': 'Por favor, proporciona el teléfono y el mensaje.'}, status=status.HTTP_400_BAD_REQUEST)
        



class EnviarCORREOView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        correo = request.data.get('correo')
        nombre = request.data.get('nombre')
        subject = request.data.get('asunto')
        mensaje = request.data.get('mensaje')

        if correo and nombre and subject:
            # Configuración del correo electrónico
            template = "alerta.html"

            # Crear el contexto para la plantilla
            context = {'Nombre_alerta': mensaje}

            # Renderizar la plantilla
            html_content = render_to_string(template, context)

            # Configuración del correo electrónico en formato HTML y texto plano
            email = EmailMessage()
            email.subject = subject
            email.body = html_content
            email.to = [correo]
            email.content_subtype = 'html'

            # Enviar el correo electrónico
            email.send()

            # Puedes personalizar la respuesta según tus necesidades
            return Response({'mensaje': 'Correo electrónico enviado correctamente'}, status=status.HTTP_200_OK)
        else:
            # Maneja el caso en el que no se proporciona el correo, el nombre o el asunto
            return Response({'error': 'Por favor, proporciona el correo, el nombre y el asunto.'}, status=status.HTTP_400_BAD_REQUEST)
        


class SubZonaHidricaTuaListVieww(generics.ListAPIView):
    serializer_class = CuencasTuaSerializerr
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data_rios = CuencasSubZonas.objects.all()
        serializer = self.serializer_class(data_rios,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class SubZonaHidricaTrListVieww(generics.ListAPIView):
    queryset = SubZonaHidrica.objects.all()
    serializer_class = SubZonaHidricaTrSerializerr
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dato_rios = SubZonaHidrica.objects.all()
        serializer = self.serializer_class(dato_rios,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    

class FuncionesAuxiliares:
    @staticmethod
    def get_tramite_sasoftco(tramite):
        cadena = ""
        radicado = tramite.id_solicitud_tramite.id_radicado
        organized_data = {}
        if radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=radicado.agno_radicado,cod_tipo_radicado=radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros

            tramites_values = Tramites.objects.filter(radicate_bia=cadena).values()

                
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
            else:
                raise NotFound('No se encontró el detalle del trámite elegido')
            
        return organized_data

    @staticmethod
    def convertir_coordenadas_dms(valor_decimal):
        print(valor_decimal)
        print(type(valor_decimal))
        #valor_absoluto = abs(int(valor_decimal))
        valor_decimal = float(valor_decimal)
        grados = int(valor_decimal)
        resto_decimal = (valor_decimal - grados) * 60
        minutos = int(resto_decimal)
        segundos = (resto_decimal - minutos) * 60
        return grados, minutos, segundos
    

    def obtener_altitud(self, latitud, longitud):
        print('aqui')
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={latitud},{longitud}"
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        print('es el json', respuesta)
        resultado = respuesta.json()
        print('holaaa')
        if resultado and 'results' in resultado and len(resultado['results']) > 0:
            print('hola', resultado)
            altitud = resultado['results'][0]['elevation']
            print('holaa')
            return altitud
        else:
            return None        


class ServicioCaptacionJuridicaView(generics.ListAPIView):
    def get(self, request):

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        tramites = PermisosAmbSolicitudesTramite.objects.filter(id_permiso_ambiental__nombre='Concesión para el uso de aguas superficiales')
        tramites = tramites.filter(id_solicitud_tramite__id_persona_titular__tipo_persona='J')
        
        if fecha_inicio:
            tramites = tramites.filter(id_solicitud_tramite__fecha_radicado__gte=fecha_inicio)
        if fecha_fin:
            tramites = tramites.filter(id_solicitud_tramite__fecha_radicado__lte=fecha_fin)
        #funciones_auxiliares = FuncionesAuxiliares()
        data_list = []

        for tramite in tramites:
            tramite_data = FuncionesAuxiliares.get_tramite_sasoftco(tramite)
            
            data = {
                'INFORMACION DE USUARIO': {
                    'TIPO DE USUARIO': tramite.id_solicitud_tramite.id_persona_titular.tipo_persona,
                    'RAZON SOCIAL': tramite.id_solicitud_tramite.id_persona_titular.razon_social,
                    'TIPO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.tipo_documento.nombre,
                    'NUMERO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.numero_documento,
                    'DIRECCION CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.direccion_notificaciones,
                    'E-MAIL': tramite.id_solicitud_tramite.id_persona_titular.email,
                    'TEL': tramite.id_solicitud_tramite.id_persona_titular.telefono_empresa,
                },

                'REPRESENTANTE LEGAL': {
                    'NOMBRE': f"{tramite.id_solicitud_tramite.id_persona_titular.representante_legal.primer_nombre} {tramite.id_solicitud_tramite.id_persona_titular.representante_legal.segundo_nombre}",
                    'APELLIDO': f"{tramite.id_solicitud_tramite.id_persona_titular.representante_legal.primer_apellido} {tramite.id_solicitud_tramite.id_persona_titular.representante_legal.segundo_apellido}",
                    'TIPO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.tipo_documento.nombre,
                    'NUMERO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.numero_documento,
                    'DEPTO DE CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.cod_municipio_notificacion_nal.cod_departamento.nombre,
                    'MUNICIPIO DE CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.cod_municipio_notificacion_nal.nombre,
                    'DIRECCION CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.direccion_notificaciones,
                    'Telefono': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.telefono_celular,
                },

                'INFORMACION DEL PREDIO': {
                    'NOMBRE PREDIO': tramite_data['Npredio'] if 'Npredio' in tramite_data else None,
                    'DEPTO PREDIO': tramite_data['DepPredio'],
                    'MUNICIPIO PREDIO': tramite_data['MunPredio'],
                    'CEDULA CATASTRAL': tramite_data['CCatas'],
                    'MATRICULA INMOBILIARIA': tramite_data['MatriInmobi'] if 'MatriInmobi' in tramite_data else None,
                    'DIRECCION DEL PREDIO': tramite_data['Dpredio'],

                },
                'GEOREFERENCIACION DEL PREDIO': {
                    'SISTEMA REF': 'Sistema GRS 1980 Magna Sirgas'
                },
                'INFORMACION PERMISO': {
                    'NÚMERO DEL EXPEDIENTE': tramite_data['NumExp'] if 'NumExp' in tramite_data else None,
                    'No. RESOLUCION': tramite_data['NumResol'] if 'NumResol' in tramite_data else None,
                    'FECHA EXPEDICION': tramite_data['Fecha_Resolu'] if 'Fecha_Resolu' in tramite_data else None,
                    'CAUDAL CONCESIONADO': tramite_data['Caudal_concesionado'] if 'Caudal_concesionado' in tramite_data else None,
                    
                },
                'INFORMACION CAPTACION': {
                    'FUENTE ABASTECEDORA': tramite_data['FuenCapTa'] if 'FuenCapTa' in tramite_data else None,
                    'DEPARTAMENTO CAPTACION': tramite_data['Dep_fuente'] if 'Dep_fuente' in tramite_data else None,
                    'MUNICIPIO CAPTACION': tramite_data['Mun_fuente'] if 'Mun_fuente' in tramite_data else None,
                },

                'GEOREFERENCIACION DE LA CAPTACION': {
                    'SISTEMA REF': 'Sistema GRS 1980 Magna Sirgas'
                }
                
            }

            #GEOREFERENCIACION DEL PREDIO
            if 'Mapa1' in tramite_data:
                latitud = tramite_data['Mapa1'].split(',')[0]
                longitud = tramite_data['Mapa1'].split(',')[1]
                grados_latitud, minutos_latitud, segundos_latitud = FuncionesAuxiliares.convertir_coordenadas_dms(latitud)
                grados_longitud, minutos_longitud, segundos_longitud = FuncionesAuxiliares.convertir_coordenadas_dms(longitud)
                data['GEOREFERENCIACION DEL PREDIO']['GRAD LAT'] = grados_latitud if grados_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['MIN LAT'] = minutos_latitud if minutos_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['SEG LAT'] = segundos_latitud if segundos_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['GRAD LONG'] = grados_longitud if grados_longitud else None
                data['GEOREFERENCIACION DEL PREDIO']['MIN LONG'] = minutos_longitud if minutos_longitud else None
                data['GEOREFERENCIACION DEL PREDIO']['SEG LONG'] = segundos_longitud if segundos_longitud else None

                #altitud = funciones_auxiliares.obtener_altitud(latitud, longitud)
                data['GEOREFERENCIACION DEL PREDIO']['ALTITUD'] = tramite_data['Altura_mnsnm'] if 'Altura_mnsnm' in tramite_data else None

            #GEOREFERENCIACION DE LA FUENTE DE CAPTACION
            if 'Mapa2' in tramite_data:
                latitud_captacion = tramite_data['Mapa2'].split(',')[0]
                longitud_captacion = tramite_data['Mapa2'].split(',')[1]
                grados_latitud_c, minutos_latitud_c, segundos_latitud_c = FuncionesAuxiliares.convertir_coordenadas_dms(latitud_captacion)
                grados_longitud_c, minutos_longitud_c, segundos_longitu_c = FuncionesAuxiliares.convertir_coordenadas_dms(longitud_captacion)
                data['GEOREFERENCIACION DE LA CAPTACION']['GRAD LAT'] = grados_latitud_c if grados_latitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['MIN LAT'] = minutos_latitud_c if minutos_latitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['SEG LAT'] = segundos_latitud_c if segundos_latitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['GRAD LONG'] = grados_longitud_c if grados_longitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['MIN LONG'] = minutos_longitud_c if minutos_longitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['SEG LONG'] = segundos_longitu_c if segundos_longitu_c else None

                #altitud_captacion = funciones_auxiliares.obtener_altitud(latitud_captacion, longitud_captacion)
                data['GEOREFERENCIACION DE LA CAPTACION']['ALTITUD'] = 0
                data['GEOREFERENCIACION DE LA CAPTACION']['Descripcion acceso captación'] = tramite_data['DesCapta'] if 'DesCapta' in tramite_data else None


            data_list.append(data)

            
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': data_list}, status=status.HTTP_200_OK)





class ServicioCaptacionNaturalView(generics.ListAPIView):
    def get(self, request):

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        tramites = PermisosAmbSolicitudesTramite.objects.filter(id_permiso_ambiental__nombre='Concesión para el uso de aguas superficiales')
        tramites = tramites.filter(id_solicitud_tramite__id_persona_titular__tipo_persona='N')
        if fecha_inicio:
            tramites = tramites.filter(id_solicitud_tramite__fecha_radicado__gte=fecha_inicio)
        if fecha_fin:
            tramites = tramites.filter(id_solicitud_tramite__fecha_radicado__lte=fecha_fin)
        #funciones_auxiliares = FuncionesAuxiliares()
        data_list = []

        for tramite in tramites:
            tramite_data = FuncionesAuxiliares.get_tramite_sasoftco(tramite)
            
            data = {
                'INFORMACION DE USUARIO': {
                    'TIPO DE USUARIO': tramite.id_solicitud_tramite.id_persona_titular.tipo_persona,
                    'NOMBRE': f"{tramite.id_solicitud_tramite.id_persona_titular.primer_nombre} {tramite.id_solicitud_tramite.id_persona_titular.segundo_nombre}",
                    'APELLIDO': f"{tramite.id_solicitud_tramite.id_persona_titular.primer_apellido} {tramite.id_solicitud_tramite.id_persona_titular.segundo_apellido}",
                    'TIPO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.tipo_documento.nombre,
                    'NUMERO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.numero_documento,
                    'DEPTO DE CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.cod_municipio_notificacion_nal.cod_departamento.nombre,
                    'MUNICIPIO DE CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.cod_municipio_notificacion_nal.nombre,
                    'DIRECCION CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.direccion_notificaciones,
                    'E-MAIL': tramite.id_solicitud_tramite.id_persona_titular.email,
                    'TEL': tramite.id_solicitud_tramite.id_persona_titular.telefono_empresa,
                },

                'INFORMACION DEL PREDIO': {
                    'NOMBRE PREDIO': tramite_data['Npredio'] if 'Npredio' in tramite_data else None,
                    'DEPTO PREDIO': tramite_data['DepPredio'],
                    'MUNICIPIO PREDIO': tramite_data['MunPredio'],
                    'CEDULA CATASTRAL': tramite_data['CCatas'],
                    'MATRICULA INMOBILIARIA': tramite_data['MatriInmobi'] if 'MatriInmobi' in tramite_data else None,
                    'DIRECCION DEL PREDIO': tramite_data['Dpredio'],

                },
                'GEOREFERENCIACION DEL PREDIO': {
                    'SISTEMA REF': 'Sistema GRS 1980 Magna Sirgas'
                },
                'INFORMACION PERMISO': {
                    'NÚMERO DEL EXPEDIENTE': tramite_data['NumExp'] if 'NumExp' in tramite_data else None,
                    'No. RESOLUCION': tramite_data['NumResol'] if 'NumResol' in tramite_data else None,
                    'FECHA EXPEDICION': tramite_data['Fecha_Resolu'] if 'Fecha_Resolu' in tramite_data else None,
                    'CAUDAL CONCESIONADO': tramite_data['Caudal_concesionado'] if 'Caudal_concesionado' in tramite_data else None,
                    
                },

                'INFORMACION CAPTACION': {
                    'FUENTE ABASTECEDORA': tramite_data['FuenCapTa'] if 'FuenCapTa' in tramite_data else None,
                    'DEPARTAMENTO CAPTACION': tramite_data['Dep_fuente'] if 'Dep_fuente' in tramite_data else None,
                    'MUNICIPIO CAPTACION': tramite_data['Mun_fuente'] if 'Mun_fuente' in tramite_data else None,
                },

                'GEOREFERENCIACION DE LA CAPTACION': {
                    'SISTEMA REF': 'Sistema GRS 1980 Magna Sirgas'
                }
                
            }

            #GEOREFERENCIACION DEL PREDIO
            if 'Mapa1' in tramite_data:
                latitud = tramite_data['Mapa1'].split(',')[0]
                longitud = tramite_data['Mapa1'].split(',')[1]
                grados_latitud, minutos_latitud, segundos_latitud = FuncionesAuxiliares.convertir_coordenadas_dms(latitud)
                grados_longitud, minutos_longitud, segundos_longitud = FuncionesAuxiliares.convertir_coordenadas_dms(longitud)
                data['GEOREFERENCIACION DEL PREDIO']['GRAD LAT'] = grados_latitud if grados_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['MIN LAT'] = minutos_latitud if minutos_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['SEG LAT'] = segundos_latitud if segundos_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['GRAD LONG'] = grados_longitud if grados_longitud else None
                data['GEOREFERENCIACION DEL PREDIO']['MIN LONG'] = minutos_longitud if minutos_longitud else None
                data['GEOREFERENCIACION DEL PREDIO']['SEG LONG'] = segundos_longitud if segundos_longitud else None

                #altitud = funciones_auxiliares.obtener_altitud(latitud, longitud)
                data['GEOREFERENCIACION DEL PREDIO']['ALTITUD'] = tramite_data['Altura_mnsnm'] if 'Altura_mnsnm' in tramite_data else None

            #GEOREFERENCIACION DE LA FUENTE DE CAPTACION
            if 'Mapa2' in tramite_data:
                latitud_captacion = tramite_data['Mapa2'].split(',')[0]
                longitud_captacion = tramite_data['Mapa2'].split(',')[1]
                grados_latitud_c, minutos_latitud_c, segundos_latitud_c = FuncionesAuxiliares.convertir_coordenadas_dms(latitud_captacion)
                grados_longitud_c, minutos_longitud_c, segundos_longitu_c = FuncionesAuxiliares.convertir_coordenadas_dms(longitud_captacion)
                data['GEOREFERENCIACION DE LA CAPTACION']['GRAD LAT'] = grados_latitud_c if grados_latitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['MIN LAT'] = minutos_latitud_c if minutos_latitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['SEG LAT'] = segundos_latitud_c if segundos_latitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['GRAD LONG'] = grados_longitud_c if grados_longitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['MIN LONG'] = minutos_longitud_c if minutos_longitud_c else None
                data['GEOREFERENCIACION DE LA CAPTACION']['SEG LONG'] = segundos_longitu_c if segundos_longitu_c else None

               # altitud_captacion = funciones_auxiliares.obtener_altitud(latitud_captacion, longitud_captacion)
                data['GEOREFERENCIACION DE LA CAPTACION']['ALTITUD'] = 0
                data['GEOREFERENCIACION DE LA CAPTACION']['Descripcion acceso captación'] = tramite_data['DesCapta'] if 'DesCapta' in tramite_data else None


            data_list.append(data)

            
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': data_list}, status=status.HTTP_200_OK)
    


class ServicioVertimientoNaturalView(generics.ListAPIView):
    def get(self, request):

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        tramites = PermisosAmbSolicitudesTramite.objects.filter(id_permiso_ambiental__nombre='Permiso de vertimientos al agua')
        tramites = tramites.filter(id_solicitud_tramite__id_persona_titular__tipo_persona='N')

        if fecha_inicio:
            tramites = tramites.filter(id_solicitud_tramite__fecha_radicado__gte=fecha_inicio)
        if fecha_fin:
            tramites = tramites.filter(id_solicitud_tramite__fecha_radicado__lte=fecha_fin)
        #funciones_auxiliares = FuncionesAuxiliares()
        data_list = []

        for tramite in tramites:
            tramite_data = FuncionesAuxiliares.get_tramite_sasoftco(tramite)
            
            data = {
                'INFORMACION DE USUARIO': {
                    'TIPO DE USUARIO': tramite.id_solicitud_tramite.id_persona_titular.tipo_persona,
                    'NOMBRE': f"{tramite.id_solicitud_tramite.id_persona_titular.primer_nombre} {tramite.id_solicitud_tramite.id_persona_titular.segundo_nombre}",
                    'APELLIDO': f"{tramite.id_solicitud_tramite.id_persona_titular.primer_apellido} {tramite.id_solicitud_tramite.id_persona_titular.segundo_apellido}",
                    'TIPO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.tipo_documento.nombre,
                    'NUMERO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.numero_documento,
                    'DEPTO DE CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.cod_municipio_notificacion_nal.cod_departamento.nombre,
                    'MUNICIPIO DE CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.cod_municipio_notificacion_nal.nombre,
                    'DIRECCION CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.direccion_notificaciones,
                    'E-MAIL': tramite.id_solicitud_tramite.id_persona_titular.email,
                    'TEL': tramite.id_solicitud_tramite.id_persona_titular.telefono_empresa,
                },

                'INFORMACION DEL PREDIO': {
                    'NOMBRE PREDIO': tramite_data['Npredio'] if 'Npredio' in tramite_data else None,
                    'DEPTO PREDIO': tramite_data['DepPredio'],
                    'MUNICIPIO PREDIO': tramite_data['MunPredio'],
                    'CEDULA CATASTRAL': tramite_data['CCatas'],
                    'MATRICULA INMOBILIARIA': tramite_data['MatriInmobi'] if 'MatriInmobi' in tramite_data else None,
                    'DIRECCION DEL PREDIO': tramite_data['Dpredio'],

                },
                'GEOREFERENCIACION DEL PREDIO': {
                    'SISTEMA REF': 'Sistema GRS 1980 Magna Sirgas'
                },
                'INFORMACION PERMISO': {
                    'NÚMERO DEL EXPEDIENTE': tramite_data['NumExp'] if 'NumExp' in tramite_data else None,
                    'No. RESOLUCION': tramite_data['NumResol'] if 'NumResol' in tramite_data else None,
                    'FECHA EXPEDICION': tramite_data['Fecha_Resolu'] if 'Fecha_Resolu' in tramite_data else None,
                    'CAUDAL AUTORIZADO VERTER': tramite_data['Caudal_concesionado'] if 'Caudal_concesionado' in tramite_data else None,
                    
                },

                'INFORMACION VERTIMIENTO': {
                    'TIPO VERTIMIENTO': tramite_data['TipVert'] if 'TipVert' in tramite_data else None,
                    #'DEPARTAMENTO CAPTACION': tramite_data['Dep_fuente'] if 'Dep_fuente' in tramite_data else None,
                    'MUNICIPIO CAPTACION': tramite_data['Muni_local_vertimiento'] if 'Muni_local_vertimiento' in tramite_data else None,
                },

                'CARACTERISTICAS DEL VERTIMIENTO': {
                    'Tipo de flujo': tramite_data['TipFlujDes'] if 'TipFlujDes' in tramite_data else None,
                    'Tiempo de descarga': tramite_data['TiemDescar'] if 'TiemDescar' in tramite_data else None,
                    'Frecuencia': tramite_data['FeqCap'] if 'FeqCap' in tramite_data else None,
                    'Caudal diseño STD': tramite_data['CaudAprox'] if 'CaudAprox' in tramite_data else None,
                },

                'GEOREFERENCIACION DEL VERTIMIENTO': {
                    'SISTEMA REF': 'Sistema GRS 1980 Magna Sirgas'
                }
                
            }

            departamento = None

            if 'Muni_local_vertimiento' in tramite_data:
                departamento = Municipio.objects.filter(nombre = tramite_data['Muni_local_vertimiento']).first()
            
            data['INFORMACION VERTIMIENTO']['DEPARTAMENTO CAPTACION'] = departamento.cod_departamento.nombre if departamento else None

            #GEOREFERENCIACION DEL PREDIO
            if 'Mapa1' in tramite_data:
                latitud = tramite_data['Mapa1'].split(',')[0]
                longitud = tramite_data['Mapa1'].split(',')[1]
                grados_latitud, minutos_latitud, segundos_latitud = FuncionesAuxiliares.convertir_coordenadas_dms(latitud)
                grados_longitud, minutos_longitud, segundos_longitud = FuncionesAuxiliares.convertir_coordenadas_dms(longitud)
                data['GEOREFERENCIACION DEL PREDIO']['GRAD LAT'] = grados_latitud if grados_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['MIN LAT'] = minutos_latitud if minutos_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['SEG LAT'] = segundos_latitud if segundos_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['GRAD LONG'] = grados_longitud if grados_longitud else None
                data['GEOREFERENCIACION DEL PREDIO']['MIN LONG'] = minutos_longitud if minutos_longitud else None
                data['GEOREFERENCIACION DEL PREDIO']['SEG LONG'] = segundos_longitud if segundos_longitud else None

                #altitud = funciones_auxiliares.obtener_altitud(latitud, longitud)
                data['GEOREFERENCIACION DEL PREDIO']['ALTITUD'] = tramite_data['Altura_mnsnm'] if 'Altura_mnsnm' in tramite_data else None

            #GEOREFERENCIACION VERTIMIENTO
            if 'Mapa2' in tramite_data:
                latitud_captacion = tramite_data['Mapa2'].split(',')[0]
                longitud_captacion = tramite_data['Mapa2'].split(',')[1]
                grados_latitud_c, minutos_latitud_c, segundos_latitud_c = FuncionesAuxiliares.convertir_coordenadas_dms(latitud_captacion)
                grados_longitud_c, minutos_longitud_c, segundos_longitu_c = FuncionesAuxiliares.convertir_coordenadas_dms(longitud_captacion)
                data['GEOREFERENCIACION DEL VERTIMIENTO']['GRAD LAT'] = grados_latitud_c if grados_latitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['MIN LAT'] = minutos_latitud_c if minutos_latitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['SEG LAT'] = segundos_latitud_c if segundos_latitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['GRAD LONG'] = grados_longitud_c if grados_longitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['MIN LONG'] = minutos_longitud_c if minutos_longitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['SEG LONG'] = segundos_longitu_c if segundos_longitu_c else None

                #altitud_captacion = funciones_auxiliares.obtener_altitud(latitud_captacion, longitud_captacion)
                data['GEOREFERENCIACION DEL VERTIMIENTO']['ALTITUD'] = 0
                data['GEOREFERENCIACION DEL VERTIMIENTO']['Descripcion acceso captación'] = tramite_data['DesCapta'] if 'DesCapta' in tramite_data else None


            data_list.append(data)

            
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': data_list}, status=status.HTTP_200_OK)
    


class ServicioVertimientoJuridicaView(generics.ListAPIView):
    def get(self, request):

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        tramites = PermisosAmbSolicitudesTramite.objects.filter(id_permiso_ambiental__nombre='Permiso de vertimientos al agua')
        tramites = tramites.filter(id_solicitud_tramite__id_persona_titular__tipo_persona='J')
        if fecha_inicio:
            tramites = tramites.filter(id_solicitud_tramite__fecha_radicado__gte=fecha_inicio)
        if fecha_fin:
            tramites = tramites.filter(id_solicitud_tramite__fecha_radicado__lte=fecha_fin)
        print(tramites)
        #funciones_auxiliares = FuncionesAuxiliares()
        data_list = []

        for tramite in tramites:
            tramite_data = FuncionesAuxiliares.get_tramite_sasoftco(tramite)
            print(tramite)
            print(tramite_data)
            
            data = {
                'INFORMACION DE USUARIO': {
                    'TIPO DE USUARIO': tramite.id_solicitud_tramite.id_persona_titular.tipo_persona,
                    'RAZON SOCIAL': tramite.id_solicitud_tramite.id_persona_titular.razon_social,
                    'TIPO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.tipo_documento.nombre,
                    'NUMERO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.numero_documento,
                    'DIRECCION CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.direccion_notificaciones,
                    'E-MAIL': tramite.id_solicitud_tramite.id_persona_titular.email,
                    'TEL': tramite.id_solicitud_tramite.id_persona_titular.telefono_empresa,
                },

                'REPRESENTANTE LEGAL': {
                    'NOMBRE': f"{tramite.id_solicitud_tramite.id_persona_titular.representante_legal.primer_nombre} {tramite.id_solicitud_tramite.id_persona_titular.representante_legal.segundo_nombre}",
                    'APELLIDO': f"{tramite.id_solicitud_tramite.id_persona_titular.representante_legal.primer_apellido} {tramite.id_solicitud_tramite.id_persona_titular.representante_legal.segundo_apellido}",
                    'TIPO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.tipo_documento.nombre,
                    'NUMERO DE IDENTIFICACION': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.numero_documento,
                    'DEPTO DE CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.cod_municipio_notificacion_nal.cod_departamento.nombre if tramite.id_solicitud_tramite.id_persona_titular.representante_legal else None,
                    'MUNICIPIO DE CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.cod_municipio_notificacion_nal.nombre,
                    'DIRECCION CORRESPONDENCIA': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.direccion_notificaciones,
                    'Telefono': tramite.id_solicitud_tramite.id_persona_titular.representante_legal.telefono_celular,
                },

                'INFORMACION DEL PREDIO': {
                    'NOMBRE PREDIO': tramite_data['Npredio'] if 'Npredio' in tramite_data else None,
                    'DEPTO PREDIO': tramite_data['DepPredio'],
                    'MUNICIPIO PREDIO': tramite_data['MunPredio'],
                    'CEDULA CATASTRAL': tramite_data['CCatas'],
                    'MATRICULA INMOBILIARIA': tramite_data['MatriInmobi'] if 'MatriInmobi' in tramite_data else None,
                    'DIRECCION DEL PREDIO': tramite_data['Dpredio'],

                },
                'GEOREFERENCIACION DEL PREDIO': {
                    'SISTEMA REF': 'Sistema GRS 1980 Magna Sirgas'
                },
                'INFORMACION PERMISO': {
                    'NÚMERO DEL EXPEDIENTE': tramite_data['NumExp'] if 'NumExp' in tramite_data else None,
                    'No. RESOLUCION': tramite_data['NumResol'] if 'NumResol' in tramite_data else None,
                    'FECHA EXPEDICION': tramite_data['Fecha_Resolu'] if 'Fecha_Resolu' in tramite_data else None,
                    'CAUDAL AUTORIZADO VERTER': tramite_data['Caudal_concesionado'] if 'Caudal_concesionado' in tramite_data else None,
                    
                },

                'INFORMACION VERTIMIENTO': {
                    'TIPO VERTIMIENTO': tramite_data['TipVert'] if 'TipVert' in tramite_data else None,
                    #'DEPARTAMENTO CAPTACION': tramite_data['Dep_fuente'] if 'Dep_fuente' in tramite_data else None,
                    'MUNICIPIO CAPTACION': tramite_data['Muni_local_vertimiento'] if 'Muni_local_vertimiento' in tramite_data else None,
                },

                'CARACTERISTICAS DEL VERTIMIENTO': {
                    'Tipo de flujo': tramite_data['TipFlujDes'] if 'TipFlujDes' in tramite_data else None,
                    'Tiempo de descarga': tramite_data['TiemDescar'] if 'TiemDescar' in tramite_data else None,
                    'Frecuencia': tramite_data['FeqCap'] if 'FeqCap' in tramite_data else None,
                    'Caudal diseño STD': tramite_data['CaudAprox'] if 'CaudAprox' in tramite_data else None,
                },

                'GEOREFERENCIACION DEL VERTIMIENTO': {
                    'SISTEMA REF': 'Sistema GRS 1980 Magna Sirgas'
                }
                
            }

            
            if 'Muni_local_vertimiento' in tramite_data:
                departamento = Municipio.objects.filter(nombre = tramite_data['Muni_local_vertimiento']).first()
            
            data['INFORMACION VERTIMIENTO']['DEPARTAMENTO CAPTACION'] = departamento.cod_departamento.nombre if departamento else None

            #GEOREFERENCIACION DEL PREDIO
            if 'Mapa1' in tramite_data:
                latitud = tramite_data['Mapa1'].split(',')[0]
                longitud = tramite_data['Mapa1'].split(',')[1]
                grados_latitud, minutos_latitud, segundos_latitud = FuncionesAuxiliares.convertir_coordenadas_dms(latitud)
                grados_longitud, minutos_longitud, segundos_longitud = FuncionesAuxiliares.convertir_coordenadas_dms(longitud)
                data['GEOREFERENCIACION DEL PREDIO']['GRAD LAT'] = grados_latitud if grados_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['MIN LAT'] = minutos_latitud if minutos_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['SEG LAT'] = segundos_latitud if segundos_latitud else None
                data['GEOREFERENCIACION DEL PREDIO']['GRAD LONG'] = grados_longitud if grados_longitud else None
                data['GEOREFERENCIACION DEL PREDIO']['MIN LONG'] = minutos_longitud if minutos_longitud else None
                data['GEOREFERENCIACION DEL PREDIO']['SEG LONG'] = segundos_longitud if segundos_longitud else None 

               # altitud = funciones_auxiliares.obtener_altitud(latitud, longitud)
                data['GEOREFERENCIACION DEL PREDIO']['ALTITUD'] = tramite_data['Altura_mnsnm'] if 'Altura_mnsnm' in tramite_data else None

            #GEOREFERENCIACION VERTIMIENTO
            if 'Mapa2' in tramite_data: 
                latitud_captacion = tramite_data['Mapa2'].split(',')[0]
                longitud_captacion = tramite_data['Mapa2'].split(',')[1]
                grados_latitud_c, minutos_latitud_c, segundos_latitud_c = FuncionesAuxiliares.convertir_coordenadas_dms(latitud_captacion)
                grados_longitud_c, minutos_longitud_c, segundos_longitu_c = FuncionesAuxiliares.convertir_coordenadas_dms(longitud_captacion)
                data['GEOREFERENCIACION DEL VERTIMIENTO']['GRAD LAT'] = grados_latitud_c if grados_latitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['MIN LAT'] = minutos_latitud_c if minutos_latitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['SEG LAT'] = segundos_latitud_c  if segundos_latitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['GRAD LONG'] = grados_longitud_c if grados_longitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['MIN LONG'] = minutos_longitud_c if minutos_longitud_c else None
                data['GEOREFERENCIACION DEL VERTIMIENTO']['SEG LONG'] = segundos_longitu_c if segundos_longitu_c else None

                #altitud_captacion = funciones_auxiliares.obtener_altitud(latitud_captacion, longitud_captacion)
                data['GEOREFERENCIACION DEL VERTIMIENTO']['ALTITUD'] = 0
                data['GEOREFERENCIACION DEL VERTIMIENTO']['Descripcion acceso captación'] = tramite_data['DesCapta'] if 'DesCapta' in tramite_data else None


            data_list.append(data)

            
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': data_list}, status=status.HTTP_200_OK)



class ServicioFuentesHidricasView(generics.ListAPIView):
    def get(self, request):

        fuentes = CuencasSubZonas.objects.all()
        funciones_auxiliares = FuncionesAuxiliares()
        data_list = []

        for fuente in fuentes:            
            data = {
                'FUENTE': {
                    'CODIGO DE LA FUENTE': fuente.codigo_cuenca,
                    'TIPO': fuente.tipo_fuente.nombre,
                    'NOMBRE DE LA FUENTE': fuente.nombre,
                    
                },
                'TRAMO': {
                    'AREA H': fuente.id_sub_zona_hidrica.id_zona_hidrica.id_macro_cuenca.nombre_macro_cuenca,
                    'ZONA H': fuente.id_sub_zona_hidrica.id_zona_hidrica.nombre_zona_hidrica,
                    'SUBZONA H': fuente.id_sub_zona_hidrica.nombre_sub_zona_hidrica,
                }
            }

class TipoUsoAguaView(generics.GenericAPIView):
    serializer_class = TipoUsoAguaSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        tipos_uso_agua = TipoUsoAgua.objects.all()
        if not tipos_uso_agua:
            raise NotFound('No se encontraron registros')
        
        serializer = self.serializer_class(tipos_uso_agua, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Registro creado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'detail': 'Error al crear el registro', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        tipo_uso_agua = TipoUsoAgua.objects.filter(id_tipo_uso_agua=pk).first()
        if not tipo_uso_agua:
            raise NotFound('No se encontró el registro')
        
        serializer = self.serializer_class(tipo_uso_agua, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'detail': 'Registro actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'success': False, 'detail': 'Error al actualizar el registro', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        tipo_uso_agua = TipoUsoAgua.objects.filter(id_tipo_uso_agua=pk).first()
        if not tipo_uso_agua:
            raise NotFound('No se encontró el registro')
        
        tipo_uso_agua.delete()
        return Response({'success': True, 'detail': 'Registro eliminado exitosamente'}, status=status.HTTP_200_OK)