from rest_framework import serializers
from gestion_documental.models.trd_models import TablaRetencionDocumental
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental


class CCDSerializer(serializers.ModelSerializer):
    usado = serializers.SerializerMethodField()
    
    def get_usado(self,obj):
        trd = TablaRetencionDocumental.objects.filter(id_ccd=obj.id_ccd)
        usado = True if trd else False
        
        return usado
    
    class Meta:
        model = CuadrosClasificacionDocumental
        fields = (
            'id_ccd',
            'id_organigrama',
            'version',
            'nombre',
            'fecha_terminado',
            'usado',
            'fecha_puesta_produccion',
            'fecha_retiro_produccion',
            'justificacion',
            'ruta_soporte',
            'actual'
        )