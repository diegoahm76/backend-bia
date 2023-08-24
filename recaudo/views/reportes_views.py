from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F
from django.db.models import Value as V
from django.db.models.functions import Concat
from datetime import datetime, timezone, timedelta
from django.db.models import Sum
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.facilidades_pagos_models import DetallesFacilidadPago, FacilidadesPago
from recaudo.models.cobros_models import Cartera 
from recaudo.serializers.reportes_serializers import (
    CarteraGeneralSerializer,
    CarteraGeneralDetalleSerializer,
    CarteraEdadesSerializer,
    ReporteFacilidadesPagosSerializer,
    ReporteFacilidadesPagosDetalleSerializer,
)

class ReporteCarteraGeneralView(generics.ListAPIView):
    serializer_class = CarteraGeneralSerializer

    def get(self, request, *args, **kwargs):
        fecha_corte_str = self.kwargs['fin']
        fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
        queryset = Cartera.objects.filter(fin=fecha_corte).order_by('-valor_sancion')
        
        if queryset.exists():
            serializer = self.serializer_class(queryset, many=True)
            total_general = self.calcular_total_general(queryset) 
            return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data, 'total_general': total_general}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('No se encuentran registros de reportes en la fecha')

    def calcular_total_general(self, queryset):
        total_general = queryset.aggregate(total=Sum(F('valor_sancion') + F('valor_intereses')))['total']
        return total_general

class ReporteCarteraGeneralDetalleView(generics.ListAPIView):
    serializer_class = CarteraGeneralDetalleSerializer

    def get(self, request, *args, **kwargs):
        queryset = Cartera.objects.all()
        codigo_contable = request.GET.get('codigo_contable')
        nombre_deudor = request.GET.get('nombre_deudor')

        if codigo_contable:
            queryset = queryset.filter(codigo_contable=codigo_contable)

        if nombre_deudor: 
            queryset = queryset.annotate(nombre_deudor=Concat('id_obligacion__id_expediente__id_deudor__nombres', V(' '), 'id_obligacion__id_expediente__id_deudor__apellidos')).filter(nombre_deudor__icontains=nombre_deudor)

        if not queryset.exists():
            raise NotFound("No se encontraron reportes en la búsqueda")

        serializer = self.get_serializer(queryset, many=True)
        total_general = queryset.aggregate(total_sanciones=Sum(F('valor_sancion') + F('valor_intereses')))['total_sanciones']
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
            queryset = queryset.filter(id_rango__inicial__gte=361)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_general = queryset.aggregate(total_sanciones=Sum(F('valor_sancion') + F('valor_intereses')))['total_sanciones']
        return Response({'success':True, 'detail':'Resultados de la búsqueda', 'data':serializer.data, 'total_general':total_general}, status=status.HTTP_200_OK)

class ReporteFacilidadesPagoView(generics.ListAPIView):
    serializer_class = ReporteFacilidadesPagosSerializer

    def get(self, request, *args, **kwargs):
        sanciones_coactivo = DetallesFacilidadPago.objects.filter(id_cartera__tipo_cobro='coactivo')
        sanciones_persuasivo = DetallesFacilidadPago.objects.filter(id_cartera__tipo_cobro='persuasivo')

        total_sanciones_coactivo = sanciones_coactivo.aggregate(total_sanciones_coactivo=Sum('id_cartera__valor_sancion'))
        total_sanciones_persuasivo = sanciones_persuasivo.aggregate(total_sanciones_persuasivo=Sum('id_cartera__valor_sancion'))

        total_sanciones_coactivo_intereses = sanciones_coactivo.aggregate(total_sanciones_coactivo_intereses=Sum('id_cartera__valor_intereses'))
        total_sanciones_persuasivo_intereses = sanciones_persuasivo.aggregate(total_sanciones_persuasivo_intereses=Sum('id_cartera__valor_intereses'))

        total_sanciones_coactivo = total_sanciones_coactivo['total_sanciones_coactivo'] or 0
        total_sanciones_persuasivo = total_sanciones_persuasivo['total_sanciones_persuasivo'] or 0
        total_sanciones_coactivo_intereses = total_sanciones_coactivo_intereses['total_sanciones_coactivo_intereses'] or 0
        total_sanciones_persuasivo_intereses = total_sanciones_persuasivo_intereses['total_sanciones_persuasivo_intereses'] or 0

        total_sanciones_coactivo += total_sanciones_coactivo_intereses
        total_sanciones_persuasivo += total_sanciones_persuasivo_intereses

        total_general = total_sanciones_coactivo + total_sanciones_persuasivo

        resultados = {
            "total_sanciones_coactivo": total_sanciones_coactivo,
            "total_sanciones_persuasivo": total_sanciones_persuasivo,
            "total_general": total_general
        }

        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': resultados}, status=status.HTTP_200_OK)

class ReporteFacilidadesPagosDetalleView(generics.ListAPIView):
    serializer_class = ReporteFacilidadesPagosDetalleSerializer

    def get(self, request, *args, **kwargs):
        tipo_cobro = request.GET.get('tipo_cobro')
        identificacion = request.GET.get('identificacion')
        nombre_deudor = request.GET.get('nombre_deudor')
        cod_expediente = request.GET.get('cod_expediente')
        numero_resolucion = request.GET.get('numero_resolucion')
        numero_factura = request.GET.get('numero_factura')

        detalles_facilidad_pago = DetallesFacilidadPago.objects.all()

        if tipo_cobro:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(id_cartera__tipo_cobro=tipo_cobro)

        if identificacion:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(
                id_facilidad_pago__id_deudor__identificacion=identificacion
            )

        if nombre_deudor:
            detalles_facilidad_pago = detalles_facilidad_pago.annotate(
                nombre_deudor=Concat('id_facilidad_pago__id_deudor__nombres', V(' '),
                                     'id_facilidad_pago__id_deudor__apellidos')
            ).filter(nombre_deudor__icontains=nombre_deudor)

        if cod_expediente:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(
                id_cartera__id_obligacion__id_expediente__cod_expediente=cod_expediente
            )

        if numero_resolucion:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(
                id_cartera__id_obligacion__id_expediente__numero_resolucion=numero_resolucion
            )

        if numero_factura:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(id_cartera__numero_factura=numero_factura)

        resultados = []
        total_cobro_coactivo = 0
        total_cobro_persuasivo = 0

        for detalle in detalles_facilidad_pago:
            facilidad_pago = detalle.id_facilidad_pago
            deudor = facilidad_pago.id_deudor
            cartera = detalle.id_cartera
            expediente = cartera.id_obligacion.id_expediente

            valor_sancion = cartera.valor_sancion
            valor_intereses = cartera.valor_intereses

            valor_total = valor_sancion + valor_intereses

            resultado = {
                'tipo_cobro': detalle.id_cartera__tipo_cobro,
                'identificacion': deudor.identificacion,
                'nombre_deudor': f'{deudor.nombres} {deudor.apellidos}',
                'concepto_deuda': cartera.codigo_contable.descripcion,
                'cod_expediente': expediente.cod_expediente,
                'numero_resolucion': expediente.numero_resolucion,
                'numero_factura': cartera.numero_factura,
                'valor_sancion': valor_total
            }

            resultados.append(resultado)

            if detalle.id_cartera__tipo_cobro == 'coactivo':
                total_cobro_coactivo += valor_total
            elif detalle.id_cartera__tipo_cobro == 'persuasivo':
                total_cobro_persuasivo += valor_total

        serializer = self.get_serializer(resultados, many=True)

        return Response({'success': True,'detail': 'Resultados de la búsqueda','data': serializer.data,'total_cobro_coactivo': total_cobro_coactivo,'total_cobro_persuasivo': total_cobro_persuasivo,'total_general': total_cobro_coactivo + total_cobro_persuasivo}, status=status.HTTP_200_OK)
    