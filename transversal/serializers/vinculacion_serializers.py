from rest_framework import serializers
from django.contrib import auth
from seguridad.models import HistoricoCargosUndOrgPersona, Personas

class VinculacionColaboradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personas
        fields = ['id_persona', 'id_cargo', 'id_unidad_organizacional_actual','observaciones_vinculacion_cargo_actual','fecha_a_finalizar_cargo_actual','fecha_inicio_cargo_actual']

class ConsultaVinculacionColaboradorSerializer(serializers.ModelSerializer):
    cargo_actual = serializers.ReadOnlyField(source='id_cargo.nombre', default=None)
    unidad_organizacional_actual = serializers.ReadOnlyField(source='id_unidad_organizacional_actual.nombre', default=None)
    fecha_vencida = serializers.BooleanField(read_only=True)

    class Meta:
        model = Personas
        fields = ('cargo_actual','unidad_organizacional_actual',"es_unidad_organizacional_actual",'fecha_inicio_cargo_actual', 'fecha_asignacion_unidad', 'fecha_a_finalizar_cargo_actual', 'observaciones_vinculacion_cargo_actual','fecha_vencida')

class UpdateVinculacionColaboradorSerializer(serializers.ModelSerializer):
    justificacion_cambio_und_org = serializers.CharField()

    class Meta:
        model = Personas
        fields = ['id_cargo', 'id_unidad_organizacional_actual', 'fecha_a_finalizar_cargo_actual','fecha_inicio_cargo_actual','observaciones_vinculacion_cargo_actual','justificacion_cambio_und_org']

class GetDesvinculacion_persona(serializers.ModelSerializer):
       
    class Meta:
        fields = '__all__'
        model = Personas
        
class BusquedaHistoricoCargoUndSerializer(serializers.ModelSerializer):
    nombre_cargo = serializers.CharField(source='id_cargo.nombre', read_only=True)
    nombre_unidad_organizacional = serializers.CharField(source='id_unidad_organizacional.nombre', read_only=True)

    class Meta:
        model = HistoricoCargosUndOrgPersona
        fields = ['nombre_cargo', 'nombre_unidad_organizacional', 'fecha_inicial_historico', 'fecha_final_historico', 'observaciones_vinculni_cargo', 'justificacion_cambio_und_org','desvinculado','fecha_desvinculacion','observaciones_desvinculacion']