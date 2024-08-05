from decimal import Decimal
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Sum
from itertools import groupby
from operator import itemgetter
from django.db.models import Value as V
from transversal.models.personas_models import Personas
from django.db.models.functions import Concat
from datetime import datetime, timezone, timedelta
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.base_models import RangosEdad, TipoRenta
from recaudo.models.facilidades_pagos_models import DetallesFacilidadPago, FacilidadesPago
from recaudo.models.cobros_models import Cartera, ConceptoContable
from recaudo.serializers.reportes_serializers import (
    CarteraDeudaYEtapaSerializer,
    CarteraGeneralSerializer,
    CarteraGeneralDetalleSerializer,
    CarteraEdadesSerializer,
    CarteraSerializer,
    CarteraSumSerializer,
    ConceptoContableSerializer,
    DeudorSerializer,
    # DeudorSumSerializer,
    RangosEdadSerializer,
    ReporteFacilidadesPagosSerializer,
    ReporteFacilidadesPagosDetalleSerializer,
    TipoRentaSerializer,
)
from collections import defaultdict
from heapq import nlargest
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Value
from rest_framework.views import APIView
from django.core.cache import cache
from django.db import models


class CustomPagination(PageNumberPagination):
    page_size = 10  # Número de elementos por página
    page_size_query_param = 'page_size'
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'siguiente': self.get_next_link(),
                'anterior': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


# class ReporteCarteraGeneralView(generics.ListAPIView):
#     serializer_class = CarteraGeneralSerializer
#     pagination_class = CustomPagination

#     def get(self, request, *args, **kwargs):
#         fecha_corte_str = self.kwargs['fin']
#         fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
#         cartera = Cartera.objects.filter(fin=fecha_corte)
#         if cartera.exists():
#             page = self.paginate_queryset(cartera)
#             if page is not None:
#                 serializer = self.serializer_class(page, many=True)
#                 total_general = cartera.aggregate(total=Sum(F('valor_sancion') + F('valor_intereses')))['total']
#                 return self.get_paginated_response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data})
#         else:
#             raise ValidationError('No se encuentran registros de reportes en la fecha')


class ReporteCarteraGeneralView(generics.ListAPIView):
    serializer_class = CarteraGeneralSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        fecha_corte_str = self.kwargs['fin']
        
        if not fecha_corte_str:
            raise ValidationError('Falta ingresar fecha de corte')

        fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
        cartera = ConceptoContable.objects.all()

        if cartera.exists():
            page = self.paginate_queryset(cartera)
            if page is not None:
                serializer = self.serializer_class(page, context={'fecha_corte_s': fecha_corte}, many=True)
                data = serializer.data
                total_general = sum(dato['valor_sancion'] for dato in data)
                return self.get_paginated_response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data, 'total_general': total_general})
        else:
            raise ValidationError('No se encuentran registros de reportes en la fecha')


class ReporteCarteraGeneralGraficaView(generics.ListAPIView):
    serializer_class = CarteraGeneralSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        fecha_corte_str = self.kwargs['fin']
        
        if not fecha_corte_str:
            raise ValidationError('Falta ingresar fecha de corte')

        fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
        cartera = ConceptoContable.objects.all()

        if cartera.exists():
            serializer = self.serializer_class(cartera, context={'fecha_corte_s': fecha_corte}, many=True)
            #return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data})
            data = serializer.data
            total_general = sum(dato['valor_sancion'] for dato in data)
            return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data, 'total_general': total_general})
        
        else:
            raise ValidationError('No se encuentran registros de reportes en la fecha')


class ReporteCarteraGeneralDetalleView(generics.ListAPIView):
    serializer_class = CarteraGeneralDetalleSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        cartera = Cartera.objects.all()
        codigo_contable = self.request.query_params.get('codigo_contable', None)
        nombre_deudor = self.request.query_params.get('nombre_deudor', None)

        if codigo_contable:
            cartera = cartera.filter(codigo_contable__codigo_contable__icontains=codigo_contable)

        if nombre_deudor:
            nombres_apellidos = nombre_deudor.split()
            cartera = cartera.annotate(nombre_deudor=Concat('id_deudor__nombres', V(' '), 'id_deudor__apellidos'))

            for nombre_apellido in nombres_apellidos:
                cartera = cartera.filter(nombre_deudor__icontains=nombre_apellido)

        if cartera.exists():
            page = self.paginate_queryset(cartera)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                total_general = cartera.aggregate(total=Sum(F('valor_sancion') + F('valor_intereses')))['total']
                return self.get_paginated_response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data, 'total_general': total_general})
        else:
            raise ValidationError('No se encuentran registros de reportes en la fecha')
        

# class ReporteCarteraEdadesView(generics.ListAPIView):
#     serializer_class = CarteraEdadesSerializer

#     def get_queryset(self):
#         rango_edad = self.request.query_params.get('rango_edad', None)
#         queryset = Cartera.objects.all()

#         if rango_edad == '0 a 180 días':
#             queryset = queryset.filter(id_rango__inicial__gte=0, id_rango__final__lte=180)
#         elif rango_edad == '181 a 360 días':
#             queryset = queryset.filter(id_rango__inicial__gte=181, id_rango__final__lte=360)
#         elif rango_edad == 'mayor a 361 días':
#             queryset = queryset.filter(id_rango__inicial__gte=361)
#         return queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         total_general = queryset.aggregate(total_sanciones=Sum(F('valor_sancion') + F('valor_intereses')))['total_sanciones']
#         return Response({'success':True, 'detail':'Resultados de la búsqueda', 'data':serializer.data, 'total_general':total_general}, status=status.HTTP_200_OK)

class ReporteCarteraEdadesView(generics.ListAPIView):
    serializer_class = CarteraEdadesSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        rango_edad = self.request.query_params.get('rango_edad', None)
        rango_edad_filters = {
            '0 a 180 días': Q(id_rango__inicial__gte=0, id_rango__final__lte=180),
            '181 a 360 días': Q(id_rango__inicial__gte=181, id_rango__final__lte=360),
            'mayor a 361 días': Q(id_rango__inicial__gte=361)
        }
        cartera = Cartera.objects.all()
        if rango_edad in rango_edad_filters:
            cartera = cartera.filter(rango_edad_filters[rango_edad])
      
        if cartera.exists():
            page = self.paginate_queryset(cartera)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                total_general = cartera.aggregate(total_sanciones=Sum(F('valor_sancion') + F('valor_intereses')))['total_sanciones']
                return self.get_paginated_response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data, 'total_general': total_general})
        else:
            raise ValidationError('No se encuentran registros de reportes en la fecha')
        

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

# class ReporteFacilidadesPagosDetalleView(generics.ListAPIView):
#     serializer_class = ReporteFacilidadesPagosDetalleSerializer

#     def get(self, request, *args, **kwargs):
#         tipo_cobro = request.GET.get('tipo_cobro')
#         identificacion = request.GET.get('identificacion')
#         nombre_deudor = request.GET.get('nombre_deudor')
#         cod_expediente = request.GET.get('cod_expediente')
#         numero_resolucion = request.GET.get('numero_resolucion')
#         numero_factura = request.GET.get('numero_factura')

#         detalles_facilidad_pago = DetallesFacilidadPago.objects.all()

#         if tipo_cobro:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(id_cartera__tipo_cobro=tipo_cobro)

#         if identificacion:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(
#                 id_facilidad_pago__id_deudor__identificacion=identificacion
#             )

#         if nombre_deudor:
#             nombres_apellidos = nombre_deudor.split()
#             detalles_facilidad_pago = detalles_facilidad_pago.annotate(
#                 nombre_deudor=Concat('id_facilidad_pago__id_deudor__nombres', V(' '),
#                                      'id_facilidad_pago__id_deudor__apellidos')
#             )
#             for nombre_apellido in nombres_apellidos:
#                 detalles_facilidad_pago = detalles_facilidad_pago.filter(nombre_deudor__icontains=nombre_apellido)

#         if cod_expediente:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(
#                 id_cartera__id_expediente__cod_expediente=cod_expediente
#             )

#         if numero_resolucion:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(
#                 id_cartera__id_expediente__numero_resolucion=numero_resolucion
#             )

#         if numero_factura:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(id_cartera__numero_factura=numero_factura)

#         resultados = []
#         total_cobro_coactivo = 0
#         total_cobro_persuasivo = 0

#         for detalle in detalles_facilidad_pago:
#             facilidad_pago = detalle.id_facilidad_pago
#             deudor = facilidad_pago.id_deudor
#             cartera = detalle.id_cartera
#             expediente = cartera.id_expediente

#             valor_sancion = cartera.valor_sancion
#             valor_intereses = cartera.valor_intereses

#             valor_total = valor_sancion + valor_intereses

#             resultado = {
#                 'tipo_cobro': detalle.id_cartera.tipo_cobro,
#                 'identificacion': deudor.identificacion,
#                 'nombre_deudor': f'{deudor.nombres} {deudor.apellidos}',
#                 'concepto_deuda': cartera.codigo_contable.descripcion,
#                 'cod_expediente': expediente.cod_expediente,
#                 'numero_resolucion': expediente.numero_resolucion,
#                 'numero_factura': cartera.numero_factura,
#                 'valor_sancion': valor_total
#             }

#             resultados.append(resultado)

#             if detalle.id_cartera__tipo_cobro == 'coactivo':
#                 total_cobro_coactivo += valor_total
#             elif detalle.id_cartera__tipo_cobro == 'persuasivo':
#                 total_cobro_persuasivo += valor_total

#         serializer = self.get_serializer(resultados, many=True)

#         return Response({'success': True,'detail': 'Resultados de la búsqueda','data': serializer.data,'total_cobro_coactivo': total_cobro_coactivo,'total_cobro_persuasivo': total_cobro_persuasivo,'total_general': total_cobro_coactivo + total_cobro_persuasivo}, status=status.HTTP_200_OK)


class ReporteFacilidadesPagosDetalleView(generics.ListAPIView):
    serializer_class = ReporteFacilidadesPagosDetalleSerializer

    def get_queryset(self):
        tipo_cobro = self.request.GET.get('tipo_cobro')
        identificacion = self.request.GET.get('identificacion')
        nombre_deudor = self.request.GET.get('nombre_deudor')
        cod_expediente = self.request.GET.get('cod_expediente')
        numero_resolucion = self.request.GET.get('numero_resolucion')
        numero_factura = self.request.GET.get('numero_factura')

        detalles_facilidad_pago = DetallesFacilidadPago.objects.all()

        if tipo_cobro:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(id_cartera__tipo_cobro=tipo_cobro)

        if identificacion:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(
                id_facilidad_pago__id_deudor__identificacion=identificacion
            )

        if nombre_deudor:
            nombres_apellidos = nombre_deudor.split()
            detalles_facilidad_pago = detalles_facilidad_pago.annotate(
                nombre_deudor=Concat('id_facilidad_pago__id_deudor__nombres', V(' '),
                                     'id_facilidad_pago__id_deudor__apellidos')
            )
            for nombre_apellido in nombres_apellidos:
                detalles_facilidad_pago = detalles_facilidad_pago.filter(nombre_deudor__icontains=nombre_apellido)

        if cod_expediente:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(
                id_cartera__id_expediente__cod_expediente=cod_expediente
            )

        if numero_resolucion:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(
                id_cartera__id_expediente__numero_resolucion=numero_resolucion
            )

        if numero_factura:
            detalles_facilidad_pago = detalles_facilidad_pago.filter(id_cartera__numero_factura=numero_factura)

        return detalles_facilidad_pago

    def get(self, request, *args, **kwargs):
        detalles_facilidad_pago = self.get_queryset()

        resultados = []
        total_cobro_coactivo = 0
        total_cobro_persuasivo = 0

        for detalle in detalles_facilidad_pago:
            facilidad_pago = detalle.id_facilidad_pago
            deudor = facilidad_pago.id_deudor
            cartera = detalle.id_cartera
            expediente = cartera.id_expediente

            valor_sancion = cartera.valor_sancion
            valor_intereses = cartera.valor_intereses

            valor_total = valor_sancion + valor_intereses

            resultado = {
                'tipo_cobro': detalle.id_cartera.tipo_cobro,
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

        response_data = {
            'success': True,
            'detail': 'Resultados de la búsqueda',
            'data': serializer.data,
            'total_cobro_coactivo': total_cobro_coactivo,
            'total_cobro_persuasivo': total_cobro_persuasivo,
            'total_general': total_cobro_coactivo + total_cobro_persuasivo
        }

        return Response(response_data, status=status.HTTP_200_OK)

# from rest_framework import generics, status
# from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from django.core.exceptions import ObjectDoesNotExist
# from django.db.models import Q, F
# from django.db.models import Value as V
# from django.db.models.functions import Concat
# from datetime import datetime, timezone, timedelta
# from django.db.models import Sum
# from recaudo.models.liquidaciones_models import Deudores
# from recaudo.models.facilidades_pagos_models import DetallesFacilidadPago, FacilidadesPago
# from recaudo.models.cobros_models import Cartera 
# from recaudo.serializers.reportes_serializers import (
#     CarteraGeneralSerializer,
#     CarteraGeneralDetalleSerializer,
#     CarteraEdadesSerializer,
#     ReporteFacilidadesPagosSerializer,
#     ReporteFacilidadesPagosDetalleSerializer,
# )

# class ReporteCarteraGeneralView(generics.ListAPIView):
#     serializer_class = CarteraGeneralSerializer

#     def get(self, request, *args, **kwargs):
#         fecha_corte_str = self.kwargs['fin']
#         fecha_corte = datetime.strptime(fecha_corte_str, '%Y-%m-%d').date()
#         queryset = Cartera.objects.filter(fin=fecha_corte).order_by('-valor_sancion')
        
#         if queryset.exists():
#             serializer = self.serializer_class(queryset, many=True)
#             total_general = self.calcular_total_general(queryset) 
#             return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data, 'total_general': total_general}, status=status.HTTP_200_OK)
#         else:
#             raise ValidationError('No se encuentran registros de reportes en la fecha')

#     def calcular_total_general(self, queryset):
#         total_general = queryset.aggregate(total=Sum(F('valor_sancion') + F('valor_intereses')))['total']
#         return total_general

# class ReporteCarteraGeneralDetalleView(generics.ListAPIView):
#     serializer_class = CarteraGeneralDetalleSerializer

#     def get(self, request, *args, **kwargs):
#         queryset = Cartera.objects.all()
#         codigo_contable = request.GET.get('codigo_contable')
#         nombre_deudor = request.GET.get('nombre_deudor')
#         nombres_apellidos = nombre_deudor.split()

#         if codigo_contable:
#             queryset = queryset.filter(codigo_contable=codigo_contable)

#         if nombre_deudor: 
#             queryset = queryset.annotate(nombre_deudor=Concat('id_deudor__nombres', V(' '), 'id_deudor__apellidos'))

#             for nombre_apellido in nombres_apellidos:
#                 queryset = queryset.filter(nombre_deudor__icontains=nombre_apellido)

#         if not queryset.exists():
#             raise NotFound("No se encontraron reportes en la búsqueda")

#         serializer = self.get_serializer(queryset, many=True)
#         total_general = queryset.aggregate(total_sanciones=Sum(F('valor_sancion') + F('valor_intereses')))['total_sanciones']
#         return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data':serializer.data, 'total_general':total_general}, status=status.HTTP_200_OK)

# class ReporteCarteraEdadesView(generics.ListAPIView):
#     serializer_class = CarteraEdadesSerializer

#     def get_queryset(self):
#         rango_edad = self.request.query_params.get('rango_edad', None)
#         queryset = Cartera.objects.all()

#         if rango_edad == '0 a 180 días':
#             queryset = queryset.filter(id_rango__inicial__gte=0, id_rango__final__lte=180)
#         elif rango_edad == '181 a 360 días':
#             queryset = queryset.filter(id_rango__inicial__gte=181, id_rango__final__lte=360)
#         elif rango_edad == 'mayor a 361 días':
#             queryset = queryset.filter(id_rango__inicial__gte=361)
#         return queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         total_general = queryset.aggregate(total_sanciones=Sum(F('valor_sancion') + F('valor_intereses')))['total_sanciones']
#         return Response({'success':True, 'detail':'Resultados de la búsqueda', 'data':serializer.data, 'total_general':total_general}, status=status.HTTP_200_OK)

# class ReporteFacilidadesPagoView(generics.ListAPIView):
#     serializer_class = ReporteFacilidadesPagosSerializer

#     def get(self, request, *args, **kwargs):
#         sanciones_coactivo = DetallesFacilidadPago.objects.filter(id_cartera__tipo_cobro='coactivo')
#         sanciones_persuasivo = DetallesFacilidadPago.objects.filter(id_cartera__tipo_cobro='persuasivo')

#         total_sanciones_coactivo = sanciones_coactivo.aggregate(total_sanciones_coactivo=Sum('id_cartera__valor_sancion'))
#         total_sanciones_persuasivo = sanciones_persuasivo.aggregate(total_sanciones_persuasivo=Sum('id_cartera__valor_sancion'))

#         total_sanciones_coactivo_intereses = sanciones_coactivo.aggregate(total_sanciones_coactivo_intereses=Sum('id_cartera__valor_intereses'))
#         total_sanciones_persuasivo_intereses = sanciones_persuasivo.aggregate(total_sanciones_persuasivo_intereses=Sum('id_cartera__valor_intereses'))

#         total_sanciones_coactivo = total_sanciones_coactivo['total_sanciones_coactivo'] or 0
#         total_sanciones_persuasivo = total_sanciones_persuasivo['total_sanciones_persuasivo'] or 0
#         total_sanciones_coactivo_intereses = total_sanciones_coactivo_intereses['total_sanciones_coactivo_intereses'] or 0
#         total_sanciones_persuasivo_intereses = total_sanciones_persuasivo_intereses['total_sanciones_persuasivo_intereses'] or 0

#         total_sanciones_coactivo += total_sanciones_coactivo_intereses
#         total_sanciones_persuasivo += total_sanciones_persuasivo_intereses

#         total_general = total_sanciones_coactivo + total_sanciones_persuasivo

#         resultados = {
#             "total_sanciones_coactivo": total_sanciones_coactivo,
#             "total_sanciones_persuasivo": total_sanciones_persuasivo,
#             "total_general": total_general
#         }

#         return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': resultados}, status=status.HTTP_200_OK)


# class ReporteFacilidadesPagosDetalleView(generics.ListAPIView):
#     serializer_class = ReporteFacilidadesPagosDetalleSerializer

#     def get_queryset(self):
#         tipo_cobro = self.request.GET.get('tipo_cobro')
#         identificacion = self.request.GET.get('identificacion')
#         nombre_deudor = self.request.GET.get('nombre_deudor')
#         cod_expediente = self.request.GET.get('cod_expediente')
#         numero_resolucion = self.request.GET.get('numero_resolucion')
#         numero_factura = self.request.GET.get('numero_factura')

#         detalles_facilidad_pago = DetallesFacilidadPago.objects.all()

#         if tipo_cobro:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(id_cartera__tipo_cobro=tipo_cobro)

#         if identificacion:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(
#                 id_facilidad_pago__id_deudor__identificacion=identificacion
#             )

#         if nombre_deudor:
#             nombres_apellidos = nombre_deudor.split()
#             detalles_facilidad_pago = detalles_facilidad_pago.annotate(
#                 nombre_deudor=Concat('id_facilidad_pago__id_deudor__nombres', V(' '),
#                                      'id_facilidad_pago__id_deudor__apellidos')
#             )
#             for nombre_apellido in nombres_apellidos:
#                 detalles_facilidad_pago = detalles_facilidad_pago.filter(nombre_deudor__icontains=nombre_apellido)

#         if cod_expediente:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(
#                 id_cartera__id_expediente__cod_expediente=cod_expediente
#             )

#         if numero_resolucion:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(
#                 id_cartera__id_expediente__numero_resolucion=numero_resolucion
#             )

#         if numero_factura:
#             detalles_facilidad_pago = detalles_facilidad_pago.filter(id_cartera__numero_factura=numero_factura)

#         return detalles_facilidad_pago

#     def get(self, request, *args, **kwargs):
#         detalles_facilidad_pago = self.get_queryset()

#         resultados = []
#         total_cobro_coactivo = 0
#         total_cobro_persuasivo = 0

#         for detalle in detalles_facilidad_pago:
#             facilidad_pago = detalle.id_facilidad_pago
#             deudor = facilidad_pago.id_deudor
#             cartera = detalle.id_cartera
#             expediente = cartera.id_expediente

#             valor_sancion = cartera.valor_sancion
#             valor_intereses = cartera.valor_intereses

#             valor_total = valor_sancion + valor_intereses

#             resultado = {
#                 'tipo_cobro': detalle.id_cartera.tipo_cobro,
#                 'identificacion': deudor.identificacion,
#                 'nombre_deudor': f'{deudor.nombres} {deudor.apellidos}',
#                 'concepto_deuda': cartera.codigo_contable.descripcion,
#                 'cod_expediente': expediente.cod_expediente,
#                 'numero_resolucion': expediente.numero_resolucion,
#                 'numero_factura': cartera.numero_factura,
#                 'valor_sancion': valor_total
#             }

#             resultados.append(resultado)

#             if detalle.id_cartera__tipo_cobro == 'coactivo':
#                 total_cobro_coactivo += valor_total
#             elif detalle.id_cartera__tipo_cobro == 'persuasivo':
#                 total_cobro_persuasivo += valor_total

#         serializer = self.get_serializer(resultados, many=True)

#         response_data = {
#             'success': True,
#             'detail': 'Resultados de la búsqueda',
#             'data': serializer.data,
#             'total_cobro_coactivo': total_cobro_coactivo,
#             'total_cobro_persuasivo': total_cobro_persuasivo,
#             'total_general': total_cobro_coactivo + total_cobro_persuasivo
#         }

#         return Response(response_data, status=status.HTTP_200_OK)


class RangosEdadListView(generics.ListAPIView):
    serializer_class = RangosEdadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RangosEdad.objects.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'detail': 'Datos de Rangos de Edad obtenidos exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class ConceptoContableView(generics.ListAPIView):
    serializer_class = ConceptoContableSerializer

    def get_queryset(self):
        queryset = ConceptoContable.objects.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'detail': 'Datos de Concepto Contable obtenidos exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class TipoRentaView(generics.ListAPIView):
    serializer_class = TipoRentaSerializer

    def get_queryset(self):
        queryset = TipoRenta.objects.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'detail': 'Datos de Tipo Renta obtenidos exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
    


def calcular_valor_sancion(monto_inicial, valor_intereses):
    monto_inicial = monto_inicial or 0
    valor_intereses = valor_intereses or 0
    return monto_inicial + valor_intereses




class CarteraListView(generics.ListAPIView):
    serializer_class = CarteraSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Desactiva la paginación

    def get_queryset(self):
        queryset = Cartera.objects.all()

        fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
        fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
        id_rango = self.request.query_params.get('id_rango')
        id_tipo_renta = self.request.query_params.get('id_tipo_renta')

        if fecha_facturacion_desde:
            queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

        if fecha_facturacion_hasta:
            queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

        if id_tipo_renta:
            queryset = queryset.filter(tipo_renta=id_tipo_renta)

        if id_rango:
            queryset = queryset.filter(id_rango=id_rango)

        return queryset.select_related('id_rango')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Anotar el valor_sancion calculado
        queryset = queryset.annotate(
            valor_sancion_calculado=ExpressionWrapper(
                F('monto_inicial') + (F('valor_intereses') or Value(0)),
                output_field=DecimalField(max_digits=30, decimal_places=4)
            )
        )

        # Cachear la consulta
        cache_key = f"cartera_list_{request.query_params}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'data': cached_data}, status=status.HTTP_200_OK)

        # Obtener la descripción de los rangos
        rangos = {rango.id: rango.descripcion for rango in RangosEdad.objects.all()}

        # Agrupar y sumar valor_sancion por id_rango
        grouped_data = {}
        for cartera in queryset:
            # Verificar si id_rango es None antes de acceder a id
            descripcion_rango = rangos.get(cartera.id_rango.id, 'Desconocido') if cartera.id_rango else 'Desconocido'
            
            total_sancion = calcular_valor_sancion(cartera.monto_inicial, cartera.valor_intereses)

            if descripcion_rango not in grouped_data:
                grouped_data[descripcion_rango] = 0

            grouped_data[descripcion_rango] += total_sancion

        # Convertir el diccionario a una lista de diccionarios
        result_data = [{'rango': rango, 'total_sancion': total} for rango, total in grouped_data.items()]

        cache.set(cache_key, result_data, 300)  # Cachear por 5 minutos

        return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'data': result_data}, status=status.HTTP_200_OK)
    
    
# class CarteraListView(generics.ListAPIView):
#     serializer_class = CarteraSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         queryset = Cartera.objects.all()

#         fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
#         fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
#         id_rango = self.request.query_params.get('id_rango')
#         id_tipo_renta = self.request.query_params.get('id_tipo_renta')

#         if fecha_facturacion_desde:
#             queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

#         if fecha_facturacion_hasta:
#             queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

#         if id_tipo_renta:
#             queryset = queryset.filter(tipo_renta=id_tipo_renta)

#         if id_rango:
#             queryset = queryset.filter(id_rango=id_rango)

#         return queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.serializer_class(queryset, many=True)

#         # Mapeo de IDs de rangos de días a nombres
#         nombres_rangos = {
#             1: "0 a 30 Dias",
#             2: "181 a 360 Dias",
#             3: "Mas 360 Dias"
#         }

#         # Agrupar la data por id_rango y sumar valor_sancion para cada grupo
#         grouped_data = {}
#         for key, group in groupby(serializer.data, key=itemgetter('id_rango')):
#             nombre_rango = nombres_rangos.get(int(key), "Desconocido")
#             total_sancion = sum(calcular_valor_sancion(float(item['monto_inicial']), float(item['valor_intereses']) if item['valor_intereses'] is not None else 0) for item in group)
#             grouped_data[nombre_rango] = total_sancion

#         return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'data': grouped_data}, status=status.HTTP_200_OK)
    



class ReporteGeneralCarteraDeuda(generics.ListAPIView):
    serializer_class = CarteraSerializer
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        queryset = Cartera.objects.all()

        fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
        fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
        id_rango = self.request.query_params.get('id_rango')
        id_tipo_renta = self.request.query_params.get('id_tipo_renta')

        if fecha_facturacion_desde:
            queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

        if fecha_facturacion_hasta:
            queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

        if id_tipo_renta:
            queryset = queryset.filter(tipo_renta=id_tipo_renta)

        if id_rango:
            queryset = queryset.filter(id_rango=id_rango)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Anotar el valor_sancion calculado
        queryset = queryset.annotate(
            valor_sancion_total=ExpressionWrapper(
                F('monto_inicial') + (F('valor_intereses') or Value(0)),
                output_field=DecimalField(max_digits=30, decimal_places=4)
            )
        )

        # Obtener la suma total de valor_sancion para cada tipo_renta
        total_por_tipo_renta = queryset.values('tipo_renta', 'tipo_renta__nombre_tipo_renta','tipo_renta__descripcion').annotate(valor_sancion_total=Sum('valor_sancion_total'))

        return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'data': total_por_tipo_renta}, status=status.HTTP_200_OK)
        

class ReporteGeneralCarteraDeudaYEtapa(generics.ListAPIView):
    serializer_class = CarteraDeudaYEtapaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Desactiva la paginación

    def get_queryset(self):
        queryset = Cartera.objects.all()

        fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
        fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
        id_tipo_renta = self.request.query_params.get('id_tipo_renta')
        id_rango = self.request.query_params.get('id_rango')
        etapa = self.request.query_params.get('etapa')

        if fecha_facturacion_desde:
            queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

        if fecha_facturacion_hasta:
            queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

        if id_tipo_renta:
            queryset = queryset.filter(tipo_renta=id_tipo_renta)

        if id_rango:
            queryset = queryset.filter(id_rango=id_rango)

        if etapa:
            queryset = queryset.filter(proceso_cartera__id_etapa=etapa).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        # Crear una clave única para la caché basada en los parámetros de consulta
        cache_key = f"reporte_general_cartera_deuda_y_etapa_{request.query_params}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'data': cached_data}, status=status.HTTP_200_OK)

        queryset = self.get_queryset()

        # Anotar el valor_sancion calculado usando la función del modelo
        queryset = queryset.annotate(
            valor_sancion_calculado=ExpressionWrapper(
                F('monto_inicial') + (F('valor_intereses') or Value(0)),
                output_field=DecimalField(max_digits=30, decimal_places=4)
            )
        )

        # Obtener la suma total de valor_sancion para cada tipo_renta
        total_por_tipo_renta = queryset.values(
            'tipo_renta', 
            'tipo_renta__nombre_tipo_renta'
        ).annotate(total_sancion=Sum('valor_sancion_calculado'))

        # Formatear la respuesta para incluir 'tipo_renta_valor'
        response_data = [
            {
                'tipo_renta': item['tipo_renta'],
                'nombre_renta': item['tipo_renta__nombre_tipo_renta'],
                'total_sancion': item['total_sancion']
            }
            for item in total_por_tipo_renta
        ]

        # Cachear los datos por 5 minutos
        cache.set(cache_key, response_data, 300)

        return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'data': response_data}, status=status.HTTP_200_OK)
    

class ReporteGeneralCarteraDeudaTop(generics.ListAPIView):
    serializer_class = CarteraSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Desactiva la paginación

    def get_queryset(self):
        queryset = Cartera.objects.all()

        fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
        fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
        id_tipo_renta = self.request.query_params.get('id_tipo_renta')
        id_rango = self.request.query_params.get('id_rango')

        if fecha_facturacion_desde:
            queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

        if fecha_facturacion_hasta:
            queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

        if id_tipo_renta:
            queryset = queryset.filter(tipo_renta=id_tipo_renta)

        if id_rango:
            queryset = queryset.filter(id_rango=id_rango)

        return queryset

    def list(self, request, *args, **kwargs):
        # Crear una clave única para la caché basada en los parámetros de consulta
        cache_key = f"reporte_general_cartera_deuda_top_{request.query_params}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'data': cached_data}, status=status.HTTP_200_OK)

        queryset = self.get_queryset()

        queryset = queryset.annotate(
            valor_sancion_calculado=ExpressionWrapper(
                F('monto_inicial') + (F('valor_intereses') or Value(0)),
                output_field=DecimalField(max_digits=30, decimal_places=4)
            )
        )

        total_por_tipo_renta = queryset.values(
            'tipo_renta', 
            'tipo_renta__nombre_tipo_renta'
        ).annotate(total_sancion=Sum('valor_sancion_calculado'))

        total_por_tipo_renta_list = list(total_por_tipo_renta)
        top_5 = nlargest(5, total_por_tipo_renta_list, key=lambda x: x['total_sancion'])

        top_5_dict = {item['tipo_renta__nombre_tipo_renta']: item['total_sancion'] for item in top_5}

        grouped_data_top_5 = {
            item['tipo_renta__nombre_tipo_renta']: {
                'tipo_renta': item['tipo_renta'],
                'total_sancion': item['total_sancion']
            }
            for item in total_por_tipo_renta_list
            if item['tipo_renta__nombre_tipo_renta'] in top_5_dict
        }

        # Cachear los datos por 5 minutos
        cache.set(cache_key, {
            'top_5_por_tipo_renta': top_5_dict,
            'detalles_por_tipo_renta': grouped_data_top_5
        }, 300)

        return Response({
            'success': True, 
            'detail': 'Datos de Cartera obtenidos exitosamente',
            'data': {
                'top_5_por_tipo_renta': top_5_dict,
                'detalles_por_tipo_renta': grouped_data_top_5
            }
        }, status=status.HTTP_200_OK)



class ReporteGeneralCarteraDeudaYEdad(generics.ListAPIView):
    serializer_class = CarteraSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None 
    
    def get_queryset(self):
        queryset = Cartera.objects.all()

        fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
        fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
        id_tipo_renta = self.request.query_params.get('id_tipo_renta')
        id_rango = self.request.query_params.get('id_rango')

        if fecha_facturacion_desde:
            queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

        if fecha_facturacion_hasta:
            queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

        if id_tipo_renta:
            queryset = queryset.filter(tipo_renta=id_tipo_renta)

        if id_rango:
            queryset = queryset.filter(id_rango=id_rango)

        return queryset

    def list(self, request, *args, **kwargs):
        cache_key = f"reporte_general_cartera_deuda_y_edad_{request.query_params}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'detalles_por_tipo_renta': cached_data}, status=status.HTTP_200_OK)

        queryset = self.get_queryset()

        # Anotar el valor_sancion calculado usando la función proporcionada
        queryset = queryset.annotate(
            valor_sancion_calculado=ExpressionWrapper(
                F('monto_inicial') + (F('valor_intereses') or Value(Decimal('0'))),
                output_field=DecimalField(max_digits=30, decimal_places=4)
            )
        ).values(
            'tipo_renta__descripcion',
            'id_rango'
        ).annotate(
            total_sancion=Sum('valor_sancion_calculado')
        )

        # Obtener la descripción del id_rango
        rangos = {rango.id: rango.descripcion for rango in RangosEdad.objects.all()}

        detalles_por_tipo_renta = defaultdict(lambda: defaultdict(Decimal))

        for item in queryset:
            tipo_renta = item['tipo_renta__descripcion']
            id_rango = item['id_rango']
            total_sancion = item['total_sancion']

            descripcion_rango = rangos.get(id_rango, 'Desconocido')

            detalles_por_tipo_renta[tipo_renta][descripcion_rango] += total_sancion

        # Convertir detalles_por_tipo_renta a un dict estándar antes de cachear
        detalles_por_tipo_renta = {k: dict(v) for k, v in detalles_por_tipo_renta.items()}

        # Cachear los datos por 5 minutos
        cache.set(cache_key, detalles_por_tipo_renta, 300)

        return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'detalles_por_tipo_renta': detalles_por_tipo_renta}, status=status.HTTP_200_OK)
    



# class ReporteGeneralCarteraDeudaYEdadTop(generics.ListAPIView):
#     serializer_class = CarteraSerializer

#     def get_queryset(self):
#         queryset = Cartera.objects.all()

#         fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
#         fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
#         codigo_contable = self.request.query_params.get('codigo_contable')
#         id_rango = self.request.query_params.get('id_rango')

#         if fecha_facturacion_desde:
#             queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

#         if fecha_facturacion_hasta:
#             queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

#         if codigo_contable:
#             queryset = queryset.filter(codigo_contable=codigo_contable)

#         if id_rango:
#             queryset = queryset.filter(id_rango=id_rango)

#         return queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.serializer_class(queryset, many=True)

#         # Obtener la descripción del id_rango
#         rangos = {rango.id: rango.descripcion for rango in RangosEdad.objects.all()}

#         # Agrupar la data por codigo_contable y id_rango y obtener la descripcion, codigo_contable, id_rango y la sumatoria de valor_sancion para cada grupo
#         grouped_data = {}
#         for key, group in groupby(serializer.data, key=lambda x: (x['codigo_contable__descripcion'], x['id_rango'])):
#             group_data = list(group) 
#             descripcion = group_data[0]['codigo_contable__descripcion']  
#             codigo_contable = group_data[0]['codigo_contable']
#             id_rango = group_data[0]['id_rango']
#             total_sancion = sum(float(item['valor_sancion']) for item in group_data)  
#             # Obtener la descripción del id_rango
#             descripcion_rango = rangos.get(id_rango, 'Desconocido')
#             # Concatenar descripcion y descripcion_rango en una clave única
#             key = f"{descripcion}_{descripcion_rango}"
#             grouped_data[key] = {'descripcion': descripcion, 'id_rango':id_rango,'codigo_contable': codigo_contable, 'descripcion_rango': descripcion_rango, 'total_sancion': total_sancion}

#         # Ordenar el diccionario por el código contable
#         grouped_data_sorted = dict(sorted(grouped_data.items(), key=lambda x: x[0]))

#         # Obtener el top 5 basado en la suma total de sanciones
#         top_5 = nlargest(5, grouped_data_sorted.items(), key=lambda x: x[1]['total_sancion'])

#         # Convertir el resultado nuevamente en un diccionario
#         top_5_dict = {key: value for key, value in top_5}

#         # Retornar la respuesta con los datos procesados
#         return Response({'success': True, 'detail': 'Datos de Cartera obtenidos exitosamente', 'data': top_5_dict}, status=status.HTTP_200_OK)

class ReporteGeneralCarteraDeudaYEdadTop(generics.ListAPIView):
    serializer_class = CarteraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Cartera.objects.all()

        fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
        fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
        id_tipo_renta = self.request.query_params.get('id_tipo_renta')
        id_rango = self.request.query_params.get('id_rango')

        if fecha_facturacion_desde:
            queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

        if fecha_facturacion_hasta:
            queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

        if id_tipo_renta:
            queryset = queryset.filter(tipo_renta=id_tipo_renta)

        if id_rango:
            queryset = queryset.filter(id_rango=id_rango)

        return queryset

    def calcular_valor_sancion(self, monto_inicial, valor_intereses):
        """Calcula el valor de sanción utilizando la fórmula proporcionada."""
        return monto_inicial + (valor_intereses or Decimal('0'))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = queryset.annotate(
            valor_sancion_calculado=ExpressionWrapper(
                F('monto_inicial') + (F('valor_intereses') or Value(0)),
                output_field=DecimalField(max_digits=30, decimal_places=4)
            )
        )

        rangos = {rango.id: rango.descripcion for rango in RangosEdad.objects.all()}

        grouped_data = queryset.values(
            'tipo_renta__descripcion',
            'id_rango'
        ).annotate(
            total_sancion=Sum('valor_sancion_calculado')
        )

        total_sancion_por_tipo_renta = defaultdict(Decimal)
        for item in grouped_data:
            tipo_renta = item['tipo_renta__descripcion']
            total_sancion = item['total_sancion']
            total_sancion_por_tipo_renta[tipo_renta] += total_sancion

        # Obtener los top 5 basados en la suma total de total_sancion para cada tipo_renta
        top_5 = nlargest(5, total_sancion_por_tipo_renta.items(), key=lambda x: x[1])

        # Convertir el resultado nuevamente en un diccionario
        top_5_dict = {tipo_renta: float(value) for tipo_renta, value in top_5}

        # Crear un diccionario para almacenar la suma de valor_sancion por cada id_rango para cada tipo_renta del top 5
        detalles_por_tipo_renta = defaultdict(dict)
        for item in grouped_data:
            tipo_renta = item['tipo_renta__descripcion']
            id_rango = item['id_rango']
            if tipo_renta in top_5_dict:
                if id_rango in rangos:
                    detalles_por_tipo_renta[tipo_renta][rangos[id_rango]] = float(item['total_sancion'])

        return Response({
            'success': True,
            'detail': 'Datos de Cartera obtenidos exitosamente',
            'top_5_por_tipo_renta': top_5_dict,
            'detalles_por_tipo_renta': detalles_por_tipo_renta
        }, status=status.HTTP_200_OK)
    
# from django.db.models.functions import Coalesce

# class CarteraDeudoresTop(generics.ListAPIView):
#     serializer_class = CarteraSumSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         queryset = Cartera.objects.all()

#         fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
#         fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
#         id_tipo_renta = self.request.query_params.get('id_tipo_renta')
#         id_rango = self.request.query_params.get('id_rango')

#         if fecha_facturacion_desde:
#             queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

#         if fecha_facturacion_hasta:
#             queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

#         if id_tipo_renta:
#             queryset = queryset.filter(tipo_renta=id_tipo_renta)

#         if id_rango:
#             queryset = queryset.filter(id_rango=id_rango)

#         return queryset

#     def calcular_valor_sancion(self, monto_inicial, valor_intereses):
#         """Calcula el valor de sanción utilizando la fórmula proporcionada."""
#         return monto_inicial + (valor_intereses or 0)

#     def list(self, request, *args, **kwargs):
#         cache_key = 'top_10_deudores'
#         cached_data = cache.get(cache_key)

#         if cached_data:
#             return Response({'success': True, 'detail': 'Datos de deudores obtenidos exitosamente', 'top_10_deudores': cached_data}, status=status.HTTP_200_OK)

#         queryset = self.get_queryset()

#         queryset = queryset.select_related('id_deudor')

#         queryset = queryset.annotate(
#             valor_sancion_calculado=ExpressionWrapper(
#                 F('monto_inicial') + Coalesce(F('valor_intereses'), Value(0)),
#                 output_field=DecimalField(max_digits=30, decimal_places=4)
#             )
#         )

#         # Obtener los top 10 deudores basados en la suma total del valor_sancion calculado
#         top_10_deudores = queryset.values('id_deudor').annotate(
#             total_sancion=Sum('valor_sancion_calculado')
#         ).order_by('-total_sancion')[:10]

#         deudores_ids = [deudor['id_deudor'] for deudor in top_10_deudores]
#         deudores_objs = queryset.filter(id_deudor__in=deudores_ids)

#         # Crear un diccionario para mapear deudor_id a total_sancion
#         deudores_total_sancion = {deudor['id_deudor']: deudor['total_sancion'] for deudor in top_10_deudores}

#         deudores_data = []
#         for idx, deudor in enumerate(deudores_objs, start=1):
#             deudor.total_sancion = deudores_total_sancion.get(deudor.id_deudor, 0)
#             deudor_data = CarteraSumSerializer(deudor).data
#             deudor_data['ranking'] = idx
#             deudores_data.append(deudor_data)

#         # Guardar los datos en el caché por un periodo específico, p.ej., 1 hora (3600 segundos)
#         cache.set(cache_key, deudores_data, timeout=3600)

#         return Response({'success': True, 'detail': 'Datos de deudores obtenidos exitosamente', 'top_10_deudores': deudores_data}, status=status.HTTP_200_OK)


class CarteraDeudoresTop(generics.ListAPIView):
    serializer_class = CarteraSumSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Cartera.objects.all()

        fecha_facturacion_desde = self.request.query_params.get('fecha_facturacion_desde')
        fecha_facturacion_hasta = self.request.query_params.get('fecha_facturacion_hasta')
        id_tipo_renta = self.request.query_params.get('id_tipo_renta')
        id_rango = self.request.query_params.get('id_rango')

        if fecha_facturacion_desde:
            queryset = queryset.filter(fecha_facturacion__gte=fecha_facturacion_desde)

        if fecha_facturacion_hasta:
            queryset = queryset.filter(fecha_facturacion__lte=fecha_facturacion_hasta)

        if id_tipo_renta:
            queryset = queryset.filter(tipo_renta=id_tipo_renta)

        if id_rango:
            queryset = queryset.filter(id_rango=id_rango)

        return queryset

    # def calcular_valor_sancion(self, monto_inicial, valor_intereses):
    #     """Calcula el valor de sanción utilizando la fórmula proporcionada."""
    #     return monto_inicial + (valor_intereses or 0)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = queryset.annotate(
            valor_sancion_calculado=ExpressionWrapper(
                F('monto_inicial') + (F('valor_intereses') or Value(0)),
                output_field=DecimalField(max_digits=30, decimal_places=4)
            )
        )

        # Obtener los top 10 deudores basados en la suma total del valor_sancion calculado
        top_10_deudores = queryset.values('id_deudor').annotate(
            total_sancion=Sum('valor_sancion_calculado')
        ).order_by('-total_sancion')[:10]

        # Obtener las instancias de los deudores en el top 10
        deudores_ids = [deudor['id_deudor'] for deudor in top_10_deudores]
        deudores_objs = Personas.objects.filter(id_persona__in=deudores_ids)

        # Crear un diccionario para mapear deudor_id a total_sancion
        deudores_total_sancion = {deudor['id_deudor']: deudor['total_sancion'] for deudor in top_10_deudores}

        deudores_data = []
        for deudor in top_10_deudores:

            persona = deudores_objs.filter(id_persona = deudor['id_deudor']).first()
            deudor_data = CarteraSumSerializer(persona).data
            deudor_data.update(deudor)
            deudores_data.append(deudor_data)


        return Response({'success': True, 'detail': 'Datos de deudores obtenidos exitosamente', 'top_10_deudores': deudores_data}, status=status.HTTP_200_OK)

