from rest_framework import serializers

from gestion_documental.models.plantillas_models import AccesoUndsOrg_PlantillaDoc, PlantillasDoc
from gestion_documental.models.trd_models import TipologiasDoc



class  PlantillasDocCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  PlantillasDoc
        fields = '__all__'

class  TipologiasDocSerializerGetSerializer(serializers.ModelSerializer):
    class Meta:
        model =  TipologiasDoc
        fields = '__all__'

class AccesoUndsOrg_PlantillaDocCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  AccesoUndsOrg_PlantillaDoc
        fields = '__all__'