from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recaudo.models.base_models import TiposBien
from recaudo.models.procesos_models import Bienes
from recaudo.serializers.procesos_serializers import AvaluosSerializer
from recaudo.models.garantias_models import RolesGarantias
from recaudo.serializers.garantias_serializers import (
    RolesGarantiasSerializer,
    GarantiasFacilidadSerializer,
    TipoBienSerializer,
    BienSerializer,
    BienesDeudorSerializer
    )

from datetime import timedelta, date


class RolesGarantiasView(generics.ListAPIView):
    serializer_class = RolesGarantiasSerializer
    queryset = RolesGarantias.objects.all() 

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail':'Se muestra los roles de garantias', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class GarantiasFacilidadView(generics.CreateAPIView):
    serializer_class = GarantiasFacilidadSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail':'Se crea la relacion de facilidades de pago y bienes mediante garantias', 'data':serializer.data})


class TiposBienesView(generics.ListAPIView):
    serializer_class = TipoBienSerializer
    queryset = TiposBien.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Se muestra los tipos de bienes', 'data': serializer.data}, status=status.HTTP_200_OK)


class CrearBienView(generics.CreateAPIView):
    serializer_class = BienSerializer
    serializer_class_avaluos = AvaluosSerializer
    
    def crear_bien(self, data):
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        bien_creado = serializer.save()
        return bien_creado

    def post(self, request):
        data_in = request.data

        # CREAR BIEN
        bien = self.crear_bien(data_in)

        # CREAR AVALUO
        fecha_avaluo = date.today()
        fecha_fin_vigencia = fecha_avaluo + timedelta(days=bien.id_tipo_bien.vigencia_avaluo)
        data = {
            'id_bien' : bien.id,
            'fecha_avaluo': fecha_avaluo,
            'fecha_fin_vigencia': fecha_fin_vigencia,
            'cod_funcionario_perito': 1,
            'valor': data_in['valor']
        }
        serializer = self.serializer_class_avaluos(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail':'Se crea el bien que coloca el deudor'},status=status.HTTP_200_OK)


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
    