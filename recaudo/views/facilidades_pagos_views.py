from recaudo.serializers.pagos_serializers import (
    TipoActuacionSerializer,
    DatosContactoDeudorSerializer,
)

from recaudo.serializers.garantias_serializers import (
    RolesGarantiasSerializer,
    TipoBienSerializer,
    BienSerializer,
    BienesDeudorSerializer
    )

from recaudo.serializers.facilidades_pagos_serializers import (
    AvaluosSerializer,
    FacilidadesPagoSerializer,
    GarantiasFacilidadSerializer
)

from recaudo.models.procesos_models import Bienes, Avaluos

from recaudo.models.pagos_models import FacilidadesPago

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


### VISTAS QUE SE MUESTRAN AL MOMENTO DE CREAR UNA FACILIDAD

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
            'cod_funcionario_perito': 1,
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

        return Response({'success':True, 'detail':'Se crea la relación de facilidades de pago y bienes mediante garantías', 'data':self.serializer_class(garantias_facilidad).data}, status=status.HTTP_201_CREATED)


class FacilidadPagoCreateView(generics.CreateAPIView):
    serializer_class = FacilidadesPagoSerializer
    
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        periodicidad = serializer.validated_data.get('periodicidad')
        cuotas = serializer.validated_data.get('cuotas')
        total_plazos = periodicidad * cuotas
        if total_plazos > 61:
            raise PermissionDenied('Las cuotas deben ser menor de 60 meses')
        else:
            serializer.save()
            return Response({'success': True, 'detail':'Se crea una facilidad de pago', 'data':serializer.data},status=status.HTTP_200_OK)
        


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
        return facilidad_pago

    def crear_avaluo(self, data):
        serializer = AvaluosSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        avaluo = serializer.save()
        return avaluo

    def crear_garantias_facilidad(self, data):
        serializer = GarantiasFacilidadSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        garantias_facilidad = serializer.save()
        return garantias_facilidad

    def post(self, request):
        data_in = request.data

        bien_data = {
            'id_deudor' : data_in['id_deudor'],
            'descripcion' : data_in['descripcion']
        }

        # CREAR BIEN
        instancia_bien = BienCreateView()
        response_data = instancia_bien.obligaciones_deudor()
        
        bien = self.crear_bien(data_in)

        # CREAR AVALUO
        avaluo_data = {
            'id_bien': bien.id,
            'fecha_avaluo': date.today(),
            'fecha_fin_vigencia': date.today() + timedelta(days=bien.id_tipo_bien.vigencia_avaluo),
            'cod_funcionario_perito': 1,
            'valor': data_in.get('valor')
        }
        avaluo = self.crear_avaluo(avaluo_data)

        facilidad_pago = self.crear_facilidad_pago(data_in)


        # CREAR GARANTIAS FACILIDAD
        garantias_facilidad_data = {
            'id_avaluo': avaluo.id,
            'id_facilidad_pago': facilidad_pago.id
        }

        garantias_facilidad = self.crear_garantias_facilidad(garantias_facilidad_data)


        

        if not facilidad_pago:
            raise ValidationError('No se pudo crear la relacion')

        return Response({'success':True, 'detail':'Se crea la relación de facilidades de pago y bienes mediante garantías', 'data':self.serializer_class(facilidad_pago).data}, status=status.HTTP_201_CREATED)
