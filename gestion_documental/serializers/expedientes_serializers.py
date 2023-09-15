from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max 
from gestion_documental.models.expedientes_models import ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura
from gestion_documental.models.trd_models import TablaRetencionDocumental, TipologiasDoc


######################### SERIALIZERS DEPOSITO #########################

#Buscar-Expediente
class ExpedienteSearchSerializer(serializers.ModelSerializer):

    nombre_serie_origen = serializers.ReadOnlyField(source='id_serie_origen.nombre', default=None)
    nombre_subserie_origen = serializers.ReadOnlyField(source='id_subserie_origen.nombre', default=None)
    nombre_unidad_org = serializers.ReadOnlyField(source='id_und_seccion_propietaria_serie.nombre', default=None)
    nombre_trd_origen = serializers.ReadOnlyField(source='id_trd_origen.nombre', default=None)

    class Meta:
        model =  ExpedientesDocumentales
        fields = ['codigo_exp_und_serie_subserie','id_expediente_documental','titulo_expediente','id_und_seccion_propietaria_serie','nombre_unidad_org','id_serie_origen','nombre_serie_origen','id_subserie_origen','nombre_subserie_origen','nombre_subserie_origen','id_trd_origen','nombre_trd_origen','fecha_apertura_expediente']


class ListarTRDSerializer(serializers.ModelSerializer):
    nombre_tdr_origen = serializers.ReadOnlyField(source='id_trd_origen.nombre', default=None)
    actual_tdr_origen = serializers.ReadOnlyField(source='id_trd_origen.actual', default=None)
    fecha_retiro_produccion_tdr_origen = serializers.ReadOnlyField(source='id_trd_origen.fecha_retiro_produccion', default=None)
    estado_actual = serializers.SerializerMethodField()  # Nuevo campo para el estado actual

    class Meta:
        model = ExpedientesDocumentales
        fields = ['id_trd_origen', 'nombre_tdr_origen', 'actual_tdr_origen', 'fecha_retiro_produccion_tdr_origen', 'estado_actual']

    def get_estado_actual(self, obj):
        return "ACTUAL" if obj.id_trd_origen.actual else "NO ACTUAL"
    

#Orden_Siguiente_Expediente
class ExpedienteGetOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = '__all__'


#
class AgregarArchivoSoporteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = '__all__'
        read_only_fields = ['fecha_incorporacion_doc_a_Exp']


class ListarTipologiasSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipologiasDoc
        fields = ['id_tipologia_documental', 'nombre']
  