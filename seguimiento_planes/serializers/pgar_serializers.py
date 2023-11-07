from rest_framework import serializers
from seguimiento_planes.models.pgar_models import PlanGestionAmbientalRegional, Objetivo, LineaEstrategica, MetaEstrategica, Entidades, PgarIndicador, Actividad

class PlanGestionAmbientalRegionalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PlanGestionAmbientalRegional
        fields = '__all__'

class ObjetivoSerializer(serializers.ModelSerializer):

    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
        
    class Meta:
        model = Objetivo
        fields = '__all__'

class LineaEstrategicaSerializer(serializers.ModelSerializer):

    descripcion_objetivo = serializers.ReadOnlyField(source='id_objetivo.descripcion_objetivo', default=None)

    class Meta:
        model = LineaEstrategica
        fields = '__all__'

class MetaEstrategicaSerializer(serializers.ModelSerializer):
    
    descripcion_linea_estrategica = serializers.ReadOnlyField(source='id_linea_estrategica.descripcion_linea_estrategica', default=None)
    class Meta:
        model = MetaEstrategica
        fields = '__all__'

class EntidadesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Entidades
        fields = '__all__'

class PgarIndicadorSerializer(serializers.ModelSerializer):

    nombre_entidad = serializers.ReadOnlyField(source='id_entidad.nombre_entidad', default=None)

    class Meta:
        model = PgarIndicador
        fields = '__all__'

class ActividadSerializer(serializers.ModelSerializer):

    descripcion_indicador = serializers.ReadOnlyField(source='id_indicador.descripcion_indicador', default=None)
    descripcion_meta_estrategica = serializers.ReadOnlyField(source='id_meta_estrategica.descripcion_meta_estrategica', default=None)

    class Meta:
        model = Actividad
        fields = '__all__'