from rest_framework import serializers

from gestion_documental.models.plantillas_models import PlantillasDoc
from gestion_documental.models.trd_models import TipologiasDoc



class  PlantillasDocCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  PlantillasDoc
        fields = '__all__'

class  TipologiasDocSerializerGetSerializer(serializers.ModelSerializer):
    class Meta:
        model =  TipologiasDoc
        fields = '__all__'