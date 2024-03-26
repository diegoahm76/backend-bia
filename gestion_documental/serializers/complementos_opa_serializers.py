from datetime import timedelta
from rest_framework import serializers

from gestion_documental.models.radicados_models import  Anexos_PQR, ComplementosUsu_PQR



class ComplementoPQRSDFPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplementosUsu_PQR
        fields = '__all__'


class Anexos_RequerimientoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexos_PQR
        fields = '__all__'