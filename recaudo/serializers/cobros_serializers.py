from rest_framework import serializers
from recaudo.models.cobros_models import (
    Cartera,
    Obligaciones
)
from recaudo.models.liquidaciones_models import (
    Deudores
)
from recaudo.models.base_models import (
    RangosEdad
)
from recaudo.models.procesos_models import (
    Procesos
)


class CarteraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartera
        fields = '__all__'


class DeudorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deudores
        fields = '__all__'


class RangosEdadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RangosEdad
        fields = '__all__'


class ObligacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obligaciones
        fields = '__all__'


class ProcesosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procesos
        fields = '__all__'


class CarteraGeneralSerializer(serializers.ModelSerializer):
    id_deudor = DeudorSerializer(many=False)
    id_rango = RangosEdadSerializer(many=False)
    id_obligacion = ObligacionesSerializer(many=False)
    proceso_cartera = serializers.SerializerMethodField()

    class Meta:
        model = Cartera
        fields = ('id', 'id_obligacion', 'dias_mora', 'valor_intereses', 'valor_sancion', 'inicio', 'fin', 'id_rango', 'codigo_contable', 'fecha_facturacion', 'fecha_notificacion',
                  'fecha_ejecutoriado', 'numero_factura', 'monto_inicial', 'tipo_cobro', 'id_deudor', 'proceso_cartera')

    def get_proceso_cartera(self, obj):
        procesos_cartera = obj.proceso_cartera.filter(fin__isnull=True)
        serializer = ProcesosSerializer(instance=procesos_cartera, many=True)
        return serializer.data