from almacen.models.generics_models import Bodegas
from rest_framework import generics
from rest_framework.views import APIView
from almacen.serializers.generics_serializers import (
    SerializersMarca
    )   
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError