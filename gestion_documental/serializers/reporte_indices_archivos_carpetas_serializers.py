from rest_framework import serializers

from gestion_documental.models.expedientes_models import ExpedientesDocumentales

class ReporteIndicesTodosGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpedientesDocumentales
        fields = '__all__'
