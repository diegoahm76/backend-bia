from datetime import datetime
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.solicitudes_models import (
    SolicitudesConsumibles,
    ItemsSolicitudConsumible
)
from seguridad.models import ClasesTerceroPersona, Personas
from seguridad.serializers.personas_serializers import PersonasFilterSerializer

class CrearSolicitudesPostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SolicitudesConsumibles
        fields = '__all__'
        
class SolicitudesPendientesAprobarSerializer(serializers.ModelSerializer):
    
    responsable_vinculado = serializers.SerializerMethodField()
    responsable_vinculacion_vencida = serializers.SerializerMethodField()
    responsable_unidad = serializers.SerializerMethodField()
    responsable_funcionario = serializers.SerializerMethodField()
    
    #verificar de que el solicitante este vinculado en la corporacion    
    def get_responsable_vinculado(self, obj):
        vinculado2 = False if obj.id_funcionario_responsable_unidad.id_cargo != None and obj.id_funcionario_responsable_unidad.id_unidad_organizacional_actual != None else True
        return vinculado2
    #VERIFICAR DE QUE LA FECHA DE VINCULACION DE LA PERSONA NO ESTE VENCIDA
    def get_responsable_vinculacion_vencida(self, obj):
        fecha_actual = datetime.now()
        fecha_vencida_responsable2 = True if obj.id_funcionario_responsable_unidad.fecha_a_finalizar_cargo_actual < fecha_actual else False
        return fecha_vencida_responsable2
    #VERIFICAR SI LA PERSONA ES RESPONSABLE DE LA UNIDAD
    def get_responsable_unidad(self, obj):        
        responsable_unidad2 = True if obj.id_funcionario_responsable_unidad.id_unidad_organizacional_actual != obj.id_unidad_org_del_responsable else False
        return responsable_unidad2
    #VALIDAR DE QUE LA PERSONA SIGA SIENDO FUNCIONARIO DE LA EMPRESA
    def get_responsable_funcionario(self, obj):
        funcionario_activo2 = ClasesTerceroPersona.objects.filter(id_persona=obj.id_funcionario_responsable_unidad.id_persona, id_clase_tercero=2).exists()
        return funcionario_activo2
    
    class Meta:
        model = SolicitudesConsumibles
        fields = '__all__'

class CrearItemsSolicitudConsumiblePostSerializer(serializers.ModelSerializer):
    #nro_posicion = serializers.IntegerField(validators=[UniqueValidator(queryset=ItemsSolicitudConsumible.objects.all())])
    codigo_bien = serializers.ReadOnlyField(source='id_bien.codigo_bien', default=None) 
    nombre_bien = serializers.ReadOnlyField(source='id_bien.nombre', default=None)
    
    class Meta:
        model = ItemsSolicitudConsumible
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ItemsSolicitudConsumible.objects.all(),
                fields=['id_bien', 'id_solicitud_consumibles'],
                message='No puede solicitar más de una vez el mismo bien en esta solicitud'
            )
        ]

class PersonasResponsablesFilterSerializer(PersonasFilterSerializer):
    nombre_unidad_organizacional_actual=serializers.ReadOnlyField(source='id_unidad_organizacional_actual.nombre',default=None)
    
    class Meta:
        model = Personas
        fields = PersonasFilterSerializer.Meta.fields + ['id_unidad_organizacional_actual','nombre_unidad_organizacional_actual']