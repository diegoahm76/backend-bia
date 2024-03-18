from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.expedientes_models import DocumentosDeArchivoExpediente, ExpedientesDocumentales
from gestion_documental.choices.cod_tipo_documento_choices import cod_tipo_documento_CHOICES
from transversal.models.base_models import HistoricoCargosUndOrgPersona


from gestion_documental.models.notificaciones_models import (
    NotificacionesCorrespondencia, 
    Registros_NotificacionesCorrespondecia, 
    AsignacionNotificacionCorrespondencia, 
    TiposNotificacionesCorrespondencia, 
    TiposAnexosSoporte, 
    Anexos_NotificacionesCorrespondencia, 
    EstadosNotificacionesCorrespondencia, 
    HistoricosEstados, 
    CausasOAnomalias
    )

class NotificacionesCorrespondenciaSerializer(serializers.ModelSerializer):
    cod_tipo_documento = serializers.CharField(source='get_cod_tipo_documento_display', read_only=True, default=None)
    registros_notificaciones = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    funcuinario_solicitante = serializers.SerializerMethodField()
    unidad_solicitante = serializers.CharField(source='id_und_org_oficina_solicita.nombre')

    class Meta:
        model = NotificacionesCorrespondencia
        fields = '__all__'

    def get_registros_notificaciones(self, obj):
        registros_notificaciones = Registros_NotificacionesCorrespondecia.objects.filter(id_notificacion_correspondencia=obj.id_notificacion_correspondencia)
        if registros_notificaciones:
            return Registros_NotificacionesCorrespondeciaSerializer(registros_notificaciones, many=True).data
        
    def get_expediente(self, obj):
        if obj.id_expediente_documental:
            return f"{obj.id_expediente_documental.codigo_exp_und_serie_subserie}.{obj.id_expediente_documental.codigo_exp_Agno}.{obj.id_expediente_documental.codigo_exp_consec_por_agno}"
        else:
            return None
    
    def get_funcuinario_solicitante(self, obj):
        return f"{obj.id_persona_solicita.primer_nombre} {obj.id_persona_solicita.primer_apellido}"
    

    
    

class Registros_NotificacionesCorrespondeciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registros_NotificacionesCorrespondecia
        fields = '__all__'


class AsignacionNotificacionCorrespondenciaSerializer(serializers.ModelSerializer):
    vigencia_contrato = serializers.SerializerMethodField()
    class Meta:
        model = AsignacionNotificacionCorrespondencia
        fields = '__all__'


    def get_vigencia_contrato(self, obj):
        vigencia_contrato = HistoricoCargosUndOrgPersona.objects.filter(id_persona=obj.id_persona_asignada)
        return HistoricoCargosUndOrgPersonaSerializer(vigencia_contrato, many=True).data

class HistoricoCargosUndOrgPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoCargosUndOrgPersona
        fields = ['fecha_final_historico']

