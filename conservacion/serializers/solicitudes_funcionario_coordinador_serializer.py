from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from conservacion.models.solicitudes_models import (
    SolicitudesViveros,
    ItemSolicitudViveros
)
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from almacen.models.bienes_models import (
    CatalogoBienes
)

class GetSolicitudesViverosFuncionarioSerializer(serializers.ModelSerializer):
    persona_solicita = serializers.SerializerMethodField()
    persona_responsable = serializers.SerializerMethodField()
    nombre_unidad_organizacional_destino = serializers.ReadOnlyField(source='id_unidad_para_la_que_solicita.nombre', default=None)
    
    def get_persona_solicita(self, obj):
        nombre_completo_solicita = None
        nombre_list = [obj.id_persona_solicita.primer_nombre, obj.id_persona_solicita.segundo_nombre,
                        obj.id_persona_solicita.primer_apellido, obj.id_persona_solicita.segundo_apellido]
        nombre_completo_solicita = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_solicita = nombre_completo_solicita if nombre_completo_solicita != "" else None
        return nombre_completo_solicita
    
    def get_persona_responsable(self, obj):
        nombre_completo_responsable = None
        nombre_list = [obj.id_funcionario_responsable_und_destino.primer_nombre, obj.id_funcionario_responsable_und_destino.segundo_nombre,
                        obj.id_funcionario_responsable_und_destino.primer_apellido, obj.id_funcionario_responsable_und_destino.segundo_apellido]
        nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'


class GetSolicitudesViveroResponsableSerializer(serializers.ModelSerializer):
    persona_solicita = serializers.SerializerMethodField()
    persona_responsable = serializers.SerializerMethodField()
    nombre_unidad_organizacional_destino = serializers.ReadOnlyField(source='id_unidad_para_la_que_solicita.nombre', default=None)
    
    def get_persona_solicita(self, obj):
        nombre_completo_solicita = None
        nombre_list = [obj.id_persona_solicita.primer_nombre, obj.id_persona_solicita.segundo_nombre,
                        obj.id_persona_solicita.primer_apellido, obj.id_persona_solicita.segundo_apellido]
        nombre_completo_solicita = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_solicita = nombre_completo_solicita if nombre_completo_solicita != "" else None
        return nombre_completo_solicita
    
    def get_persona_responsable(self, obj):
        nombre_completo_responsable = None
        nombre_list = [obj.id_funcionario_responsable_und_destino.primer_nombre, obj.id_funcionario_responsable_und_destino.segundo_nombre,
                        obj.id_funcionario_responsable_und_destino.primer_apellido, obj.id_funcionario_responsable_und_destino.segundo_apellido]
        nombre_completo_responsable = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_responsable = nombre_completo_responsable if nombre_completo_responsable != "" else None
        return nombre_completo_responsable
    
    class Meta:
        model = SolicitudesViveros
        fields = '__all__'


class GestionarSolicitudResponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = (
            "estado_aprobacion_responsable",
            "justificacion_aprobacion_responsable",
            "fecha_aprobacion_responsable",
            "revisada_responsable",
            "solicitud_abierta",
            "fecha_cierra_solicitud",
        )
        extra_kwargs = {
            'justificacion_aprobacion_responsable': {'required': True},
            'estado_aprobacion_responsable': {'required': True},
        }


class GestionarSolicitudCoordinadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViveros
        fields = (
            "estado_aprobacion_coord_viveros",
            "justificacion_aprobacion_coord_viveros",
            "fecha_aprobacion_coord_viv",
            "revisada_coord_viveros",
            "solicitud_abierta",
            "fecha_cierra_solicitud",
        )
        extra_kwargs = {
            'justificacion_aprobacion_responsable': {'required': True},
            'estado_aprobacion_responsable': {'required': True},
        }