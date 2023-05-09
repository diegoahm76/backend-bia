from rest_framework import serializers
from recaudo.models.garantias_models import Garantias, RolesGarantias
from recaudo.models.base_models import TiposBien
from recaudo.models.procesos_models import Bienes


class RolesGarantiasSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesGarantias
        fields = '__all__'


class GarantiasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garantias
        fields = '__all__'


class TipoBienSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposBien
        fields = '__all__'


class BienSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bienes
        fields = '__all__'


class BienesDeudorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bienes
        fields = ('id_tipo_bien','descripcion','documento_soporte')
