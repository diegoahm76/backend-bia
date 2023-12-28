from rest_framework import serializers
from gestion_documental.models.trd_models import TablaRetencionDocumental, ConsecPorNivelesTipologiasDocAgno
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from transversal.models import Organigramas, UnidadesOrganizacionales, TemporalPersonasUnidad


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


class CtrlAccesoClasificacionExpCCDSerializer(serializers.ModelSerializer):

    class Meta:
        model= CtrlAccesoClasificacionExpCCD
        fields= '__all__'


class PermisosUndsOrgActualesSerieExpCCDSerializer(serializers.ModelSerializer):

    class Meta:
        model= PermisosUndsOrgActualesSerieExpCCD
        fields= '__all__'


class ConfiguracionTipoExpedienteAgnoSerializer(serializers.ModelSerializer):

    class Meta:
        model= ConfiguracionTipoExpedienteAgno
        fields= '__all__'


class ConsecPorNivelesTipologiasDocAgnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsecPorNivelesTipologiasDocAgno
        fields = '__all__'


class TemporalPersonasUnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporalPersonasUnidad
        fields = '__all__'