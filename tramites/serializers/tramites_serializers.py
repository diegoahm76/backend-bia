from rest_framework import serializers
from django.contrib import auth

from tramites.models.tramites_models import PermisosAmbientales, SolicitudesTramites
from transversal.models.base_models import Departamento
from transversal.models.personas_models import Personas

class ListTramitesGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = PermisosAmbientales
        fields = '__all__'
        
class PersonaTitularInfoGetSerializer(serializers.ModelSerializer):
    cod_departamento_notificacion = serializers.SerializerMethodField()
    departamento_notificacion = serializers.SerializerMethodField()
    municipio_notificacion_nal = serializers.ReadOnlyField(source='cod_municipio_notificacion_nal.nombre', default=None)
    
    def get_cod_departamento_notificacion(self, obj):
        cod_departamento_notificacion = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio_notificacion_nal.cod_municipio[:2]).first() if obj.cod_municipio_notificacion_nal else None
        if departamento:
            cod_departamento_notificacion = departamento.cod_departamento
        return cod_departamento_notificacion
    
    def get_departamento_notificacion(self, obj):
        departamento_notificacion = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio_notificacion_nal.cod_municipio[:2]).first() if obj.cod_municipio_notificacion_nal else None
        if departamento:
            departamento_notificacion = departamento.nombre
        return departamento_notificacion

    class Meta:
        model = Personas
        fields = [
            'id_persona',
            'cod_departamento_notificacion',
            'departamento_notificacion',
            'cod_municipio_notificacion_nal',
            'municipio_notificacion_nal',
            'direccion_notificaciones',
            'direccion_notificacion_referencia',
            'ubicacion_georeferenciada',
            'ubicacion_georeferenciada_lon'
        ]
        
class InicioTramiteCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SolicitudesTramites
        fields = [
            'id_solicitud_tramite',
            'id_persona_titular',
            'id_persona_interpone',
            'cod_relacion_con_el_titular',
            'cod_tipo_operacion_tramite',
            'nombre_proyecto',
            'costo_proyecto',
            'id_medio_solicitud',
            'id_persona_registra',
            'id_estado_actual_solicitud',
            'fecha_ini_estado_actual'
        ]
        extra_kwargs = {
            'id_solicitud_tramite': {'read_only': True},
            'id_persona_titular': {'required': True, 'allow_null': False},
            'id_persona_interpone': {'required': True, 'allow_null': False},
            'cod_relacion_con_el_titular': {'required': True, 'allow_null': False, 'allow_blank': False},
            'cod_tipo_operacion_tramite': {'required': True, 'allow_null': False, 'allow_blank': False},
            'nombre_proyecto': {'required': True, 'allow_null': False, 'allow_blank': False},
            'costo_proyecto': {'required': True, 'allow_null': False},
            'id_medio_solicitud': {'required': True, 'allow_null': False},
            'id_persona_registra': {'required': True, 'allow_null': False},
            'id_estado_actual_solicitud': {'required': True, 'allow_null': False},
            'fecha_ini_estado_actual': {'required': True, 'allow_null': False}
        }