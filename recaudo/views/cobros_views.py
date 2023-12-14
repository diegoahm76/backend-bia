from recaudo.models.cobros_models import (
    Cartera
)
from recaudo.models.liquidaciones_models import (
    Deudores
)
from recaudo.serializers.cobros_serializers import (
    CarteraGeneralSerializer
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
        deudores = Deudores.objects.all()
        if nombres is not None:
            deudores = deudores.filter(nombres__contains=nombres)

        if apellidos is not None:
            deudores = deudores.filter(apellidos__contains=apellidos)

        queryset = Cartera.objects.filter(id_deudor__in=deudores)
        serializer = self.serializer_class(queryset, many=True)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
