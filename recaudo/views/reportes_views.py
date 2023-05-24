from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import datetime, timezone, timedelta
from django.db.models import Sum
from recaudo.models.cobros_models import ( 
    Cartera 
)
from recaudo.serializers.reportes_serializers import (
    CarteraGeneralSerializer,
    CarteraGeneralDetalleSerializer,
    CarteraEdadesSerializer,
)

class ReporteCarteraGeneralView(generics.ListAPIView): 
    serializer_class = CarteraGeneralSerializer
    
    def get(self, request, *args, **kwargs):
        fecha_corte_str = self.kwargs['fin']
        fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
        queryset = Cartera.objects.filter(fin=fecha_corte).order_by('-valor_sancion')
        
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            total_general = self.calcular_total_general(queryset) 
            return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data, 'total_general': total_general}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('No se encuentran registros de reportes en la fecha')

    def calcular_total_general(self, queryset):
        total_general = queryset.aggregate(total=Sum('valor_sancion'))
        return total_general['total'] if total_general['total'] else 0

class ReporteCarteraGeneralDetalleView(generics.ListAPIView):
    serializer_class = CarteraGeneralDetalleSerializer

    def get(self, request, *args, **kwargs):
        queryset = Cartera.objects.all()
        codigo_contable = self.request.query_params.get('codigo_contable')
        nombre_deudor = self.request.query_params.get('nombre_deudor') 

        if codigo_contable:
            queryset = queryset.filter(codigo_contable=codigo_contable)
        if nombre_deudor:
            queryset = queryset.filter(id_obligacion__cod_factura__icontains=nombre_deudor)

        if not queryset.exists():
            raise NotFound("No se encontraron reportes con la coincidencia de búsqueda")

        serializer = self.get_serializer(queryset, many=True)
        total_general = queryset.aggregate(total_sanciones=Sum('valor_sancion'))['total_sanciones']
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data':serializer.data, 'total_general':total_general}, status=status.HTTP_200_OK)

class ReporteCarteraEdadesView(generics.ListAPIView):
    serializer_class = CarteraEdadesSerializer

    def get_queryset(self):
        rango_edad = self.request.query_params.get('rango_edad', None)
        queryset = Cartera.objects.all()

        if rango_edad == '0 a 180 días':
            queryset = queryset.filter(id_rango__inicial__gte=0, id_rango__final__lte=180)
        elif rango_edad == '181 a 360 días':
            queryset = queryset.filter(id_rango__inicial__gte=181, id_rango__final__lte=360)
        elif rango_edad == 'mayor a 361 días':
            queryset = queryset.filter(id_rango__inicial__gt=361)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_general = queryset.aggregate(total_sanciones=Sum('valor_sancion'))['total_sanciones']
        return Response({'success':True, 'detail':'Resultados de la búsqueda', 'data':serializer.data, 'total_general':total_general}, status=status.HTTP_200_OK)

