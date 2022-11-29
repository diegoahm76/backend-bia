from almacen.models.generics_models import Bodegas
from rest_framework import generics
from rest_framework.views import APIView
from almacen.serializers.bienes_serializers import (
    CatalogoBienesSerializer
)  
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

class CreateCatalogoDeBienes(generics.CreateAPIView):
    serializer_class = CatalogoBienesSerializer
    def post(self, request):
        print(request)