from rest_framework import serializers
from recaudo.models.procesos_models import (
    EtapasProceso,
    AtributosEtapas,
    TiposAtributos,
    FlujoProceso
)


class EtapasProcesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtapasProceso
        fields = '__all__'


class TiposAtributosSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposAtributos
        fields = '__all__'


class AtributosEtapasSerializer(serializers.ModelSerializer):
    id_tipo = TiposAtributosSerializer(many=False)

    class Meta:
        model = AtributosEtapas
        fields = ('id', 'descripcion', 'obligatorio', 'id_tipo')


class FlujoProcesoSerializer(serializers.ModelSerializer):
    id_etapa_origen = EtapasProcesoSerializer(many=False)
    id_etapa_destino = EtapasProcesoSerializer(many=False)

    class Meta:
        model = FlujoProceso
        fields = '__all__'
