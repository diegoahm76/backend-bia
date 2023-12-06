from rest_framework import serializers
from gestion_documental.models.trd_models import TablaRetencionDocumental
from transversal.models import Organigramas



class CCDActiveSerializer(serializers.ModelSerializer):
    usado = serializers.SerializerMethodField()
    def get_usado(self,obj):
        trd = TablaRetencionDocumental.objects.filter(id_ccd=obj.id_ccd)
        usado = True if trd else False
        
        return usado
    
class OrganigramaCambioDeOrganigramaActualSerializer(serializers.ModelSerializer):
    class Meta:
        model= Organigramas
        fields=['justificacion_nueva_version']