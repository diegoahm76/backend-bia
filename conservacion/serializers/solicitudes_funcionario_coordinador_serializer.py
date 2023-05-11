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
    primer_nombre_persona_solicita = serializers.ReadOnlyField(source='id_persona_solicita.primer_nombre', default=None)
    primer_apellido_persona_solicita = serializers.ReadOnlyField(source='id_persona_solicita.primer_apellido', default=None)
    nombre_unidad_para_la_que_solicita = serializers.ReadOnlyField(source='id_unidad_para_la_que_solicita.nombre', default=None)
    class Meta:
        model = SolicitudesViveros
        fields = (
            "id_solicitud_vivero",
            "nro_solicitud",
            "fecha_solicitud",
            "id_persona_solicita",
            "primer_nombre_persona_solicita",
            "primer_apellido_persona_solicita",
            "id_unidad_para_la_que_solicita",
            "nombre_unidad_para_la_que_solicita",
        )


class GetSolicitudesViveroResponsableSerializer(serializers.ModelSerializer):
    primer_nombre_persona_solicita = serializers.ReadOnlyField(source='id_persona_solicita.primer_nombre', default=None)
    primer_apellido_persona_solicita = serializers.ReadOnlyField(source='id_persona_solicita.primer_apellido', default=None)
    primer_nombre_persona_responsable = serializers.ReadOnlyField(source='id_funcionario_responsable_und_destino.primer_nombre', default=None)
    primer_apellido_persona_responsable = serializers.ReadOnlyField(source='id_funcionario_responsable_und_destino.primer_apellido', default=None)
    nombre_unidad_para_la_que_solicita = serializers.ReadOnlyField(source='id_unidad_para_la_que_solicita.nombre', default=None)
    class Meta:
        model = SolicitudesViveros
        fields = (
            "id_solicitud_vivero",
            "nro_solicitud",
            "fecha_solicitud",
            "id_persona_solicita",
            "primer_nombre_persona_solicita",
            "primer_apellido_persona_solicita",
            "id_funcionario_responsable_und_destino",
            "primer_nombre_persona_responsable",
            "primer_apellido_persona_responsable",
            "fecha_aprobacion_responsable",
            "id_unidad_para_la_que_solicita",
            "nombre_unidad_para_la_que_solicita",
        )


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