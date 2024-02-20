from rest_framework import serializers
from gestion_documental.models.trd_models import TablaRetencionDocumental
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from gestion_documental.models.tca_models import TablasControlAcceso
from transversal.models.organigrama_models import UnidadesOrganizacionales
from gestion_documental.models.trd_models import TablaRetencionDocumental, ConsecPorNivelesTipologiasDocAgno
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno

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

class TCASerializer(serializers.ModelSerializer):
    class Meta:
        model = TablasControlAcceso
        fields = ['id_tca', 'version','nombre']

class TRDSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablaRetencionDocumental
        fields = ['id_trd', 'version', 'nombre']

class CCDPosiblesSerializer(serializers.ModelSerializer):
    trd = serializers.SerializerMethodField()
    tca = serializers.SerializerMethodField()

    def get_trd(self,obj):
        trd = TablaRetencionDocumental.objects.filter(id_ccd=obj.id_ccd).first()
        serializer = TRDSerializer(trd)
        return serializer.data
    
    def get_tca(self,obj):
        trd = TablaRetencionDocumental.objects.filter(id_ccd=obj.id_ccd).first()
        tca = TablasControlAcceso.objects.filter(id_trd=trd.id_trd).first()
        serializer = TCASerializer(tca)
        return serializer.data

    class Meta:
        model = CuadrosClasificacionDocumental
        fields = ['id_ccd', 'nombre', 'version', 'trd', 'tca']


class CCDCambioActualSerializer(serializers.ModelSerializer):
    class Meta:
        model= CuadrosClasificacionDocumental
        fields=['actual','fecha_puesta_produccion','justificacion']

class TCACambioActualSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablasControlAcceso
        fields = ['actual','fecha_puesta_produccion']

class TRDCambioActualSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablaRetencionDocumental
        fields = ['actual','fecha_puesta_produccion']

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