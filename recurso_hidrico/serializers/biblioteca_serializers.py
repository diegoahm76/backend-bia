from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator

from recurso_hidrico.models.bibliotecas_models import Secciones,Subsecciones

class GetSeccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secciones
        fields = '__all__'

class RegistrarSeccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secciones
        fields = '__all__'


class GetSubseccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subsecciones
        fields = '__all__'

class ActualizarSubseccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subsecciones
        fields = '__all__'