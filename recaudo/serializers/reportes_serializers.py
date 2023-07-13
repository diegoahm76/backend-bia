from rest_framework import serializers
from recaudo.models.cobros_models import Cartera
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.pagos_models import DetallesFacilidadPago, FacilidadesPago
from django.core.exceptions import ObjectDoesNotExist

class CarteraGeneralSerializer(serializers.ModelSerializer):
    valor_sancion = serializers.DecimalField(max_digits=30, decimal_places=2, source='calcular_valor_total')
    concepto_deuda = serializers.SerializerMethodField()
    
    def get_concepto_deuda(self, obj):
        return obj.codigo_contable.descripcion

    class Meta:
        model = Cartera
        fields = ('codigo_contable', 'concepto_deuda', 'valor_sancion')

class CarteraGeneralDetalleSerializer(serializers.ModelSerializer):
    valor_sancion = serializers.DecimalField(max_digits=30, decimal_places=2, source='calcular_valor_total')
    nombre_deudor = serializers.SerializerMethodField()
    identificacion = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    resolucion = serializers.SerializerMethodField()
    concepto_deuda = serializers.SerializerMethodField()

    def get_nombre_deudor(self, obj):
        try:
            deudor = Deudores.objects.get(codigo=obj.id_obligacion.id_expediente.id_deudor.id)
            return f"{deudor.nombres} {deudor.apellidos}"
        except ObjectDoesNotExist:
            return None
        
    def get_identificacion(self, obj):
        try:
            deudor = Deudores.objects.get(codigo=obj.id_obligacion.id_expediente.id_deudor.id)
            return f"{deudor.identificacion}"
        except ObjectDoesNotExist:
            return None
    
    def get_expediente(self, obj):
        expediente = obj.id_obligacion.id_expediente
        return expediente.codigo_expediente if expediente else None

    def get_resolucion(self, obj):
        resolucion = obj.id_obligacion.id_expediente.numero_resolucion
        return resolucion if resolucion else None

    def get_concepto_deuda(self, obj):
        return obj.codigo_contable.descripcion
    
    class Meta:
        model = Cartera
        fields = ('codigo_contable','concepto_deuda','nombre_deudor','identificacion','expediente','resolucion','numero_factura','valor_sancion')

class CarteraEdadesSerializer(serializers.ModelSerializer):
    valor_sancion = serializers.DecimalField(max_digits=30, decimal_places=2, source='calcular_valor_total')
    nombre_deudor = serializers.ReadOnlyField()
    identificacion = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    resolucion = serializers.SerializerMethodField()

    def get_identificacion(self, obj):
        try:
            deudor = Deudores.objects.get(codigo=obj.id_obligacion.id_expediente.id_deudor.id)
            return f"{deudor.identificacion}"
        except ObjectDoesNotExist:
            return None
        
    def get_expediente(self, obj):
        expediente = obj.id_obligacion.id_expediente
        return expediente.codigo_expediente if expediente else None

    def get_resolucion(self, obj):
        resolucion = obj.id_obligacion.id_expediente.numero_resolucion
        return resolucion if resolucion else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            deudor = Deudores.objects.get(codigo=instance.id_obligacion.id_expediente.id_deudor.id)
            representation['nombre_deudor'] = f"{deudor.nombres} {deudor.apellidos}"
        except ObjectDoesNotExist:
            representation['nombre_deudor'] = None
        return representation

    class Meta:
        model = Cartera
        fields = ('identificacion', 'nombre_deudor', 'expediente', 'resolucion', 'id_rango', 'valor_sancion')

class ReporteFacilidadesPagosSerializer(serializers.ModelSerializer):
    total_sanciones_coactivo = serializers.DecimalField(max_digits=30, decimal_places=2)
    total_sanciones_persuasivo = serializers.DecimalField(max_digits=30, decimal_places=2)
    total_general = serializers.DecimalField(max_digits=30, decimal_places=2)

    class Meta:
        model = DetallesFacilidadPago
        fields = ('total_sanciones_coactivo','total_sanciones_persuasivo','total_general')

class ReporteFacilidadesPagosDetalleSerializer(serializers.ModelSerializer):
    tipo_cobro = serializers.CharField()
    identificacion = serializers.CharField()
    nombre_deudor = serializers.CharField()
    codigo_expediente = serializers.CharField()
    numero_resolucion = serializers.CharField()
    numero_factura = serializers.CharField()
    valor_sancion = serializers.DecimalField(max_digits=30, decimal_places=2)
    concepto_deuda = serializers.CharField()

    class Meta:
        model = DetallesFacilidadPago
        fields = ('tipo_cobro', 'identificacion', 'nombre_deudor', 'concepto_deuda','codigo_expediente', 'numero_resolucion',
                  'numero_factura', 'valor_sancion')

