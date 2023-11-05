from rest_framework import serializers
from seguimiento_planes.models.pgar_models import PlanGestionAmbientalRegional, Objetivo, LineaEstrategica, MetaEstrategica, Entidades, PgarIndicador, Actividad

class PlanGestionAmbientalRegionalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PlanGestionAmbientalRegional
        fields = '__all__'

class ObjetivoSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Objetivo
        fields = '__all__'

class LineaEstrategicaSerializer(serializers.ModelSerializer):

    class Meta:
        model = LineaEstrategica
        fields = '__all__'

class MetaEstrategicaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MetaEstrategica
        fields = '__all__'

class EntidadesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Entidades
        fields = '__all__'

class PgarIndicadorSerializer(serializers.ModelSerializer):

    class Meta:
        model = PgarIndicador
        fields = '__all__'

class ActividadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actividad
        fields = '__all__'