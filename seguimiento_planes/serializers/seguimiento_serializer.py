from rest_framework import serializers
from seguimiento_planes.models.seguimiento_models import FuenteFinanciacionIndicadores, Sector, DetalleInversionCuentas, Modalidad, Ubicaciones, FuenteRecursosPaa, Intervalo, EstadoVF, CodigosUNSP

class FuenteFinanciacionIndicadoresSerializer(serializers.ModelSerializer):

    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
    nombre_cuenca = serializers.ReadOnlyField(source='id_cuenca.nombre', default=None)

    class Meta:
        model = FuenteFinanciacionIndicadores
        fields = '__all__'

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'

class SectorSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class DetalleInversionCuentasSerializer(serializers.ModelSerializer):

    nombre_sector = serializers.ReadOnlyField(source='id_sector.nombre_sector', default=None)
    nombre_rubro = serializers.ReadOnlyField(source='id_rubro.nombre_rubro', default=None)
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
    nombre_subprograma = serializers.ReadOnlyField(source='id_subprograma.nombre_subprograma', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)

    class Meta:
        model = DetalleInversionCuentas
        fields = '__all__'

class ModalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modalidad
        fields = '__all__'

class ModalidadSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Modalidad
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class UbicacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ubicaciones
        fields = '__all__'

class UbicacionesSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Ubicaciones
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)
        
class FuenteRecursosPaaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuenteRecursosPaa
        fields = '__all__'

class FuenteRecursosPaaSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = FuenteRecursosPaa
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class IntervaloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervalo
        fields = '__all__'

class IntervaloSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Intervalo
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class EstadoVFSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoVF
        fields = '__all__'

class EstadoVFSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = EstadoVF
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class CodigosUNSPSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigosUNSP
        fields = '__all__'

class CodigosUNSPSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = CodigosUNSP
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)