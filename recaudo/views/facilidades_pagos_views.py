from recaudo.serializers.pagos_serializers import (
    TipoActuacionSerializer,
    DatosContactoDeudorSerializer,
)

from recaudo.serializers.facilidades_pagos_serializers import (
    AvaluosSerializer,
    FacilidadesPagoSerializer,
    GarantiasFacilidadSerializer,
    DetallesBienFacilidadPagoSerializer,
    CumplimientoRequisitosSerializer,
    BienesDeudorSerializer,
    TipoBienSerializer,
    BienSerializer
)

from recaudo.models.procesos_models import Bienes

from recaudo.models.pagos_models import FacilidadesPago, RequisitosActuacion

from recaudo.models.base_models import TiposBien

from datetime import timedelta, date

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Concat
from seguridad.models import Personas, ClasesTerceroPersona, User
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.cobros_models import Obligaciones, Expedientes, Deudores, Cartera
from recaudo.models.liquidaciones_models import Deudores
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

import random
import string


### VISTAS QUE SE MUESTRAN AL MOMENTO DE CREAR UNA FACILIDAD

class TipoActuacionView(generics.ListAPIView):
    queryset = TipoActuacion.objects.all()
    serializer_class = TipoActuacionSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            'success': True, 
            'detail':'Se muestran los tipos de actuacion de deudor', 
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

class DatosContactoDeudorView(generics.ListAPIView):
    serializer_class = DatosContactoDeudorSerializer

    def get(self, request, id):
        queryset = Deudores.objects.filter(id=id).first()

        if not queryset:
            raise NotFound('No se encontró ningun registro con el parámetro ingresado')
        queryset = Personas.objects.filter(numero_documento = queryset.identificacion).first()
        serializer = self.serializer_class(queryset)
        return Response({
            'success': True, 
            'detail':'Se muestra los datos de contacto del deudor', 
            'data': serializer.data
        }, status=status.HTTP_200_OK) 


class TiposBienesView(generics.ListAPIView):
    serializer_class = TipoBienSerializer
    queryset = TiposBien.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Se muestra los tipos de bienes', 'data': serializer.data}, status=status.HTTP_200_OK)



### VISTAS QUE SE CREAN AL MOMENTO DE CREAR UNA FACILIDAD

class AvaluoCreateView(generics.CreateAPIView):
    serializer_class = AvaluosSerializer

    def crear_avaluo(self, data_in):
        bien = Bienes.objects.filter(id=data_in['id_bien']).first()
        
        if not bien:
            raise NotFound('No existe bien relacionado con la informacion ingresada')
        
        fecha_avaluo = date.today()
        fecha_fin_vigencia = fecha_avaluo + timedelta(days=bien.id_tipo_bien.vigencia_avaluo)
        data = {
            'id_bien' : bien.id,
            'fecha_avaluo': fecha_avaluo,
            'fecha_fin_vigencia': fecha_fin_vigencia,
            'cod_funcionario_perito': data_in['cod_funcionario_perito'],
            'valor': data_in['valor']
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        avaluo_creado = serializer.save()
        return avaluo_creado

    def post(self, request):
        data_in = request.data

        # CREAR AVALUO
        avaluo = self.crear_avaluo(data_in)

        if not avaluo:
            raise ValidationError('No se pudo crear el avaluo')
        
        return Response({'success': True, 'detail': 'Se crea el avalauo', 'data': self.serializer_class(avaluo).data}, status=status.HTTP_201_CREATED)


class BienCreateView(generics.CreateAPIView):
    serializer_class = BienSerializer

    def crear_bien(self, data):
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        bien_creado = serializer.save()
        return bien_creado

    def post(self, request):
        data = request.data

        # CREAR BIEN
        bien = self.crear_bien(data)

        if not bien:
            raise ValidationError('No se pudo crear el bien')

        return Response({'success': True, 'detail': 'Se crea el bien que coloca el deudor', 'data': self.serializer_class(bien).data}, status=status.HTTP_201_CREATED)


class DetallesBienFacilidadPagoCreateView(generics.CreateAPIView):
    serializer_class = DetallesBienFacilidadPagoSerializer

    def crear_bienes_facilidad(self, data):
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        bienes_facilidad = serializer.save()
        return bienes_facilidad

    def post(self, request):
        data = request.data

        # Crear relación de facilidades de pago y bienes
        bienes_facilidad = self.crear_bienes_facilidad(data)

        if not bienes_facilidad:
            raise ValidationError('No se pudo crear la relacion')

        return Response({'success':True, 'detail':'Se crea la relación de facilidades de pago y bienes', 'data':self.serializer_class(bienes_facilidad).data}, status=status.HTTP_201_CREATED)


class GarantiasFacilidadCreateView(generics.CreateAPIView):
    serializer_class = GarantiasFacilidadSerializer

    def crear_garantias_facilidad(self, data):
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        garantias_facilidad = serializer.save()
        return garantias_facilidad

    def post(self, request):
        data = request.data

        # Crear relación de facilidades de pago y bienes mediante garantías
        garantias_facilidad = self.crear_garantias_facilidad(data)

        if not garantias_facilidad:
            raise ValidationError('No se pudo crear la relacion')

        return Response({'success':True, 'detail':'Se crea la relación de facilidades de pago y garantías', 'data':self.serializer_class(garantias_facilidad).data}, status=status.HTTP_201_CREATED)


class CumplimientoRequisitosCreateView(generics.CreateAPIView):
    serializer_class = CumplimientoRequisitosSerializer

    def crear_cumplimiento_requisitos(self, data):
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        cumplimiento_requisitos = serializer.save()
        return cumplimiento_requisitos

    def post(self, request):
        data = request.data

        # Crear relación de facilidades de pago y bienes mediante garantías
        cumplimiento_requisitos = self.crear_cumplimiento_requisitos(data)

        if not cumplimiento_requisitos:
            raise ValidationError('No se pudo crear los cumplimientos')

        return Response({'success':True, 'detail':'Se crea los cumplimientos', 'data':self.serializer_class(cumplimiento_requisitos).data}, status=status.HTTP_201_CREATED)
   

class FacilidadPagoCreateView(generics.CreateAPIView):
    serializer_class = FacilidadesPagoSerializer

    def crear_facilidad_pago(self, data):
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        periodicidad = serializer.validated_data.get('periodicidad')
        cuotas = serializer.validated_data.get('cuotas')
        total_plazos = periodicidad * cuotas

        if total_plazos > 61:
            raise PermissionDenied('Las cuotas deben ser menores a 60 meses')

        facilidad_pago = serializer.save()
        return facilidad_pago, total_plazos
    
    def generar_numero_radicacion(self):
        # letras = ''.join(random.choices(string.ascii_uppercase, k=3))
        letras = 'FDP'
        numeros = ''.join(random.choices(string.digits, k=7))
        numero_radicacion = f"{letras}{numeros}"
        return numero_radicacion
    
    def post(self, request):
        data_in = request.data

        #CREAR FACILIDAD DE PAGO
        numero_radicado = self.generar_numero_radicacion()
        facilidad_pago = None

        facilidad_data = {
            'id_deudor': data_in['id_deudor'],
            'id_tipo_actuacion':data_in['id_tipo_actuacion'],
            'observaciones':data_in['observaciones'],
            'periodicidad':data_in['periodicidad'],
            'cuotas':data_in['cuotas'],
            'documento_soporte':data_in['documento_soporte'],
            'consignacion_soporte':data_in['consignacion_soporte'],
            'documento_no_enajenacion':data_in['documento_no_enajenacion'],
            'id_funcionario':data_in['id_funcionario'],
            'notificaciones':data_in['notificaciones'],
            'numero_radicacion': numero_radicado
        }

#         # if 'bienes' in data_in:
#         #     if data_in['bienes'] :
#         #         instancia_bien = BienCreateView()
#         #         instancia_avaluo = AvaluoCreateView()
#         #         instancia_det_bien_facilidad = DetallesBienFacilidadPagoCreateView()

#         #         for datos_bien in data_in['bienes']:

#         #             # CREAR BIEN
#         #             bien_data = {
#         #                 'id_deudor' : data_in['id_deudor'],
#         #                 'descripcion' : datos_bien['descripcion'],
#         #                 'direccion': datos_bien['direccion'],
#         #                 'id_tipo_bien':datos_bien['id_tipo_bien'],
#         #                 'documento_soporte':datos_bien['documento_soporte_bien'],
#         #                 'id_ubicacion': datos_bien['id_ubicacion']
#         #                 }
#         #             bien = instancia_bien.crear_bien(bien_data)

#         #             if not datos_bien['valor']:
#         #                 raise ValidationError('Falta agregar bienes')
                    
#         #             #CREAR AVALUO
#         #             avaluo_data = {
#         #                 'id_bien': bien.id,
#         #                 'cod_funcionario_perito': data_in['id_funcionario'],
#         #                 'valor': datos_bien['valor']
#         #                 }
#         #             avaluo = instancia_avaluo.crear_avaluo(avaluo_data)

#         #             #CREAR RELACION DE BIEN Y FACILIDAD
#         #             det_bien_facilidad_data = {
#         #                 'id_bien':bien.id,
#         #                 'id_facilidad_pago':facilidad_pago.id
#         #             }
#         #             det_bien_facilidad = instancia_det_bien_facilidad.crear_bienes_facilidad(det_bien_facilidad_data)

#         # else:
#         #     raise ValidationError('Falta agregar bienes')
        instancia_bien = BienCreateView()
        instancia_avaluo = AvaluoCreateView()
        instancia_det_bien_facilidad = DetallesBienFacilidadPagoCreateView()

        descripciones_bien = data_in.getlist('descripcion')
        direcciones_bien = data_in.getlist('direccion')
        id_tipos_bien = data_in.getlist('id_tipo_bien')
        documentos_soporte_bien = request.FILES.getlist('documento_soporte_bien')
        id_ubicaciones = data_in.getlist('id_ubicacion')
        avaluos_bien = data_in.getlist('valor')

        if len(descripciones_bien) != len(avaluos_bien):
            raise ValidationError("Todos los bienes deben tener un valor avaluado.")
        
        tamaños_campos = [len(descripciones_bien), len(direcciones_bien), len(id_tipos_bien), len(documentos_soporte_bien), len(id_ubicaciones)]

        for tamaño in tamaños_campos:
            if tamaños_campos[0] != tamaño:
                raise ValidationError("Faltan datos por ingresar en los bienes.")
            
        list_id_bienes = []

        for descripcion, direccion, id_tipo_bien, documento_soporte, id_ubicacion, valor in zip(
                descripciones_bien, direcciones_bien, id_tipos_bien, documentos_soporte_bien, id_ubicaciones,
                avaluos_bien):
            # CREAR BIEN
            bien_data = {
                'id_deudor': data_in['id_deudor'],
                'descripcion': descripcion,
                'direccion': direccion,
                'id_tipo_bien': id_tipo_bien,
                'documento_soporte': documento_soporte,
                'id_ubicacion': id_ubicacion
            }

            bien = instancia_bien.crear_bien(bien_data)

            if not bien:
                raise ValidationError('No se pudo crear el bien')

            # CREAR AVALUO
            avaluo_data = {
                'id_bien': bien.id,
                'cod_funcionario_perito': data_in['id_funcionario'],
                'valor': valor
            }
            avaluo = instancia_avaluo.crear_avaluo(avaluo_data)

            if not avaluo:
                raise ValidationError('No se pudo crear el avaluo')
            
            list_id_bienes.append(bien.id)

        if list_id_bienes:
            facilidad_pago, total_plazos = self.crear_facilidad_pago(facilidad_data)

            for id_bien in list_id_bienes:
                # CREAR RELACION DE BIEN Y FACILIDAD
                det_bien_facilidad_data = {
                    'id_bien': id_bien,
                    'id_facilidad_pago': facilidad_pago.id
                }
                det_bien_facilidad = instancia_det_bien_facilidad.crear_bienes_facilidad(det_bien_facilidad_data)
            
            # CREAR GARANTIAS FACILIDAD
            if total_plazos > 12:
                instancia_garantias_facilidad = GarantiasFacilidadCreateView()
                garantias_facilidad_data = {
                    'id_rol': data_in['id_rol'],
                    'id_facilidad_pago': facilidad_pago.id,
                    'documento_garantia': data_in['documento_garantia']
                }
                garantias_facilidad = instancia_garantias_facilidad.crear_garantias_facilidad(garantias_facilidad_data)

                if not garantias_facilidad:
                    raise ValidationError('No se pudo crear la solicitud por falta de datos en las garantias')
                
        documentos_deudor = request.FILES.getlist('documento_deudor')
        requisitos = RequisitosActuacion.objects.filter(id_tipo_actuacion=data_in['id_tipo_actuacion'])

        if len(documentos_deudor) != len(requisitos):
            raise ValidationError('No se pudo crear la solicitud por falta de documentos del deudor')
        
        instancia_cumplimiento = CumplimientoRequisitosCreateView()
        for documento, requisito in zip(documentos_deudor, requisitos):
            cumplimiento_data = {
                'id_facilidad_pago': facilidad_pago.id,
                'id_requisito_actuacion': requisito.id,
                'documento': documento
            }

            cumplimiento = instancia_cumplimiento.crear_cumplimiento_requisitos(cumplimiento_data)

            if not cumplimiento:
                raise ValidationError('No se pudo crear la solicitud por falta de datos del deudor en los requisitos')
        
        if not facilidad_pago:
            raise ValidationError('No se pudo crear la facilidad de pago')

        return Response({'success':True, 'detail':'Se crea la relación de facilidades de pago y bienes mediante garantías', 'data':self.serializer_class(facilidad_pago).data}, status=status.HTTP_201_CREATED)




### MOSTRAR LA FACILIDAD DE PAGO

class ListaBienesDeudorView(generics.ListAPIView):
    serializer_class = BienesDeudorSerializer
    queryset = Bienes.objects.all()

    def get(self, request, id):
        bienes_deudor = Bienes.objects.filter(id_deudor=id)
        bienes_deudor = [bien_deudor for bien_deudor in bienes_deudor]
        if not bienes_deudor:
            return Response({'success': False, 'detail': 'No se encontró ningun registro con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(bienes_deudor, many=True)
        return Response({'success': True, 'detail': 'Se muestra todos los bienes del deudor', 'data': serializer.data}, status=status.HTTP_200_OK) 
    