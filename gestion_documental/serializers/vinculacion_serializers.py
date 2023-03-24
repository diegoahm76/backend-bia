from rest_framework import serializers
from django.contrib import auth

from seguridad.models import Personas

class GetDesvinculacion_persona(serializers.ModelSerializer):
       
    class Meta:
        fields = '__all__'
        model = Personas