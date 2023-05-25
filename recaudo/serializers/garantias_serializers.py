from rest_framework import serializers
from recaudo.models.garantias_models import Garantias, RolesGarantias
from recaudo.models.base_models import TiposBien
from recaudo.models.procesos_models import Bienes, Avaluos
from recaudo.models.pagos_models import GarantiasFacilidad


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
    ubicacion = serializers.ReadOnlyField(source='id_ubicacion.nombre', default=None)
    nombre_tipo_bien = serializers.ReadOnlyField(source='id_tipo_bien.descripcion', default=None)
    valor = serializers.SerializerMethodField()
    
    def get_valor(self, obj):
        valor_avaluo = Avaluos.objects.filter(id_bien=obj.id).first()
        valora = valor_avaluo.valor
        return valora


    class Meta:
        model = Bienes
        fields = ('nombre_tipo_bien','descripcion','valor','direccion','ubicacion','documento_soporte')


class GarantiasFacilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GarantiasFacilidad
        fields = '__all__'