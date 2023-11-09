from rest_framework import serializers
from seguimiento_planes.models.planes_models import ObjetivoDesarrolloSostenible, Planes, EjeEstractegico, Objetivo, Programa, Proyecto, Productos, Actividad, Entidad, Medicion, Tipo, Rublo, Indicador, Metas

class ObjetivoDesarrolloSostenibleSerializer(serializers.ModelSerializer):
        
        class Meta:
            model = ObjetivoDesarrolloSostenible
            fields = '__all__'

class ObjetivoDesarrolloSostenibleSerializerUpdate(serializers.ModelSerializer):
        
        class Meta:
            model = ObjetivoDesarrolloSostenible
            fields = '__all__'
            def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)


class PlanesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Planes
        fields = '__all__'

class EjeEstractegicoSerializer(serializers.ModelSerializer):
         
    nombre_plan = serializers.ReadOnlyField(source='id_plan_desarrollo.nombre_plan', default=None)
            
    class Meta:
        model = EjeEstractegico
        fields = '__all__'

class ObjetivoSerializer(serializers.ModelSerializer):
         
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
            
    class Meta:
        model = Objetivo
        fields = '__all__'

class ProgramaSerializer(serializers.ModelSerializer):
         
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
            
    class Meta:
        model = Programa
        fields = '__all__'

class ProyectoSerializer(serializers.ModelSerializer):
         
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
            
    class Meta:
        model = Proyecto
        fields = '__all__'

class ProductosSerializer(serializers.ModelSerializer):
         
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
            
    class Meta:
        model = Productos
        fields = '__all__'

class ActividadSerializer(serializers.ModelSerializer):
             
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
                
    class Meta:
        model = Actividad
        fields = '__all__'

class EntidadSerializer(serializers.ModelSerializer):
                
    class Meta:
        model = Entidad
        fields = '__all__'

class MedicionSerializer(serializers.ModelSerializer):
                
    class Meta:
        model = Medicion
        fields = '__all__'

class TipoSerializer(serializers.ModelSerializer):
                
    class Meta:
        model = Tipo
        fields = '__all__'

class RubloSerializer(serializers.ModelSerializer):
                
    class Meta:
        model = Rublo
        fields = '__all__'

class IndicadorSerializer(serializers.ModelSerializer):

    nombre_medicion = serializers.ReadOnlyField(source='id_medicion.nombre_medicion', default=None)
    nombre_tipo = serializers.ReadOnlyField(source='id_tipo.nombre_tipo', default=None)
    nombre_rublo = serializers.ReadOnlyField(source='id_rublo.nombre_rublo', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
                
    class Meta:
        model = Indicador
        fields = '__all__'

class MetasSerializer(serializers.ModelSerializer):

    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
                
    class Meta:
        model = Metas
        fields = '__all__'
