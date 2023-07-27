from rest_framework import serializers
from recaudo.models.procesos_models import (
    EtapasProceso,
    AtributosEtapas,
    TiposAtributos,
    FlujoProceso,
    ValoresProceso,
    Procesos,
    Avaluos,
    CategoriaAtributo
)
from recaudo.serializers.cobros_serializers import (
    CarteraSerializer
)


class EtapasProcesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtapasProceso
        fields = '__all__'


class TiposAtributosSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposAtributos
        fields = '__all__'


class CategoriaAtributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaAtributo
        fields = '__all__'


class AtributosEtapasSerializer(serializers.ModelSerializer):
    id_tipo = TiposAtributosSerializer(many=False)
    id_categoria = CategoriaAtributoSerializer(many=False)

    class Meta:
        model = AtributosEtapas
        fields = ('id', 'descripcion', 'obligatorio', 'id_tipo', 'id_categoria')


class AtributosEtapasPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtributosEtapas
        fields = '__all__'


class FlujoProcesoSerializer(serializers.ModelSerializer):
    id_etapa_origen = EtapasProcesoSerializer(many=False)
    id_etapa_destino = EtapasProcesoSerializer(many=False)

    class Meta:
        model = FlujoProceso
        fields = '__all__'


class FlujoProcesoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlujoProceso
        fields = '__all__'


class ValoresProcesoSerializer(serializers.ModelSerializer):
    id_atributo = AtributosEtapasSerializer(many=False)

    class Meta:
        model = ValoresProceso
        fields = ('id', 'id_atributo', 'valor', 'documento')


class ValoresProcesoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValoresProceso
        fields = '__all__'


class ValoresProcesoPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValoresProceso
        fields = ('valor', 'documento')


class ProcesosSerializer(serializers.ModelSerializer):
    id_cartera = CarteraSerializer(many=False)
    id_etapa = EtapasProcesoSerializer(many=False)
    id_categoria = CategoriaAtributoSerializer(many=False)

    class Meta:
        model = Procesos
        fields = '__all__'


class ProcesosPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procesos
        fields = '__all__'