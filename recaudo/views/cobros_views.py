from recaudo.models.cobros_models import (
    Cartera
)
from recaudo.serializers.cobros_serializers import (
    CarteraGeneralSerializer
)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination


class CarteraView(generics.ListAPIView):
    queryset = Cartera.objects.all()
    serializer_class = CarteraGeneralSerializer
    pagination_class = LimitOffsetPagination
    page_size = 10

    def get(self, request):
        self.pagination_class.default_limit = self.page_size

        queryset = self.get_queryset()
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.serializer_class(page, many=True)
        #     return self.get_paginated_response({'success': True, 'data': serializer.data})
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
