from rest_framework import serializers
from recaudo.models.procesos_models import (
    Avaluos, 
    Bienes
)

from recaudo.models.pagos_models import (
    FacilidadesPago,
    GarantiasFacilidad,
    DetallesBienFacilidadPago,
    CumplimientoRequisitos
)

from recaudo.models.base_models import TiposBien


class TipoBienSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposBien
        fields = '__all__'


class BienSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bienes
        fields = '__all__'


class AvaluosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaluos
        fields = '__all__'


class GarantiasFacilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = GarantiasFacilidad
        fields = '__all__'    


class DetallesBienFacilidadPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallesBienFacilidadPago
        fields = '__all__'


class CumplimientoRequisitosSerializer (serializers.ModelSerializer):
    class Meta:
        model = CumplimientoRequisitos
        fields = '__all__'


class FacilidadesPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilidadesPago
        fields = '__all__'
        extra_kwargs = {
            'id_deudor': {'required': True},
            'id_tipo_actuacion': {'required': True},
            'id_tasas_interes': {'required': True},
            'documento_soporte': {'required': True},
            'consignacion_soporte': {'required':True}
        }


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