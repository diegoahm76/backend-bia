from rest_framework import serializers

from gestion_documental.models.radicados_models import ComplementosUsu_PQR

class ComplementoPQRSDFPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplementosUsu_PQR
        fields = '__all__'

class ComplementoPQRSDFPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplementosUsu_PQR
        fields = '__all__'