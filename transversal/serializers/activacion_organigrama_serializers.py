from rest_framework import serializers
from gestion_documental.models.trd_models import TablaRetencionDocumental
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from transversal.models import Organigramas, UnidadesOrganizacionales

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

class UnidadesDelegacionSerializer(serializers.ModelSerializer):
    id_organigrama = serializers.ReadOnlyField(source='id_organigrama.id_organigrama',default=None)

    class Meta:
        model = UnidadesOrganizacionales
        fields = ['id_unidad_organizacional', 'codigo', 'nombre', 'id_organigrama']


class UnidadesOrganizacionalesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnidadesOrganizacionales
        fields = ['id_unidad_org_actual_admin_series']