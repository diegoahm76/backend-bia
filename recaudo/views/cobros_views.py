from django.db import connection
from recaudo.models.cobros_models import (
    Cartera,
    VistaCarteraTua
)
from recaudo.models.liquidaciones_models import (
    Deudores
)
from recaudo.serializers.cobros_serializers import (
    CarteraGeneralSerializer,
    VistaCarteraTuaSerializer
)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination


class CarteraGeneralView(generics.ListAPIView):
    queryset = Cartera.objects.all()
    serializer_class = CarteraGeneralSerializer
    pagination_class = LimitOffsetPagination
    page_size = 10

    def get(self, request):
        self.pagination_class.default_limit = self.page_size
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response({'success': True, 'data': serializer.data})
        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class CarteraDeudoresView(generics.ListAPIView):
    serializer_class = CarteraGeneralSerializer

    def get(self, request):
        nombres = request.GET.get('nombres', None)
        apellidos = request.GET.get('apellidos', None)
        identificacion = request.GET.get('identificacion', None)

        deudores = Deudores.objects.all()
        if nombres is not None:
            deudores = deudores.filter(nombres__contains=nombres)

        if apellidos is not None:
            deudores = deudores.filter(apellidos__contains=apellidos)

        if identificacion is not None:
            deudores = deudores.filter(identificacion__contains=identificacion)


        queryset = Cartera.objects.filter(id_deudor__in=deudores)
        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    

class VistaCarteraTuaView(generics.ListAPIView):
    #queryset = VistaCarteraTua.objects.only('fecha', 'cod_cia', 'tipo_renta', 'cuenta_contable', 'nit', 'nombre_deudor', 'fecha_fac', 'fecha_notificacion', 'fecha_en_firme', 'corte_desde', 'corte_hasta', 'num_factura', 'num_liquidacion', 'periodo', 'agno', 'expediente', 'num_resolucion', 'recurso', 'doc_auto', 'saldo_capital', 'saldo_intereses', 'dias_mora')
    serializer_class = VistaCarteraTuaSerializer
    pagination_class = LimitOffsetPagination
    page_size = 10

    def get(self, request):
        self.pagination_class.default_limit = self.page_size
        queryset = self.get_results()
        print(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response({'success': True, 'data': serializer.data})
        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    
    def get_results(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM public.vcarterabiatua")
            rows = cursor.fetchall()
        return rows
