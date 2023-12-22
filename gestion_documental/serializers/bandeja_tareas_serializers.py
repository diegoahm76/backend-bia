
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.bandeja_tareas_models import TareasAsignadas

from gestion_documental.models.radicados_models import BandejaTareasPersona, TareaBandejaTareasPersona



class BandejaTareasPersonaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandejaTareasPersona
        fields = '__all__'

#TareasAsignadas crear
        

class TareaBandejaTareasPersonaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaBandejaTareasPersona
        fields = '__all__'
        
class TareasAsignadasCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = '__all__'