from rest_framework import serializers
from gestion_documental.models.trd_models import TablaRetencionDocumental
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from transversal.models import Organigramas

class OrganigramaSerializer(serializers.ModelSerializer):
    usado = serializers.SerializerMethodField()

    def get_usado(self,obj):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_organigrama=obj.id_organigrama)
        usado = True if ccd else False
        return usado

    class Meta:
        model= Organigramas
        fields= '__all__'
    
class OrganigramaCambioActualSerializer(serializers.ModelSerializer):
    class Meta:
        model= Organigramas
        fields=['justificacion_nueva_version']