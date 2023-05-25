from rest_framework import serializers
from recaudo.models.cobros_models import Cartera
from recaudo.models.liquidaciones_models import Deudores

class CarteraGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartera
        fields = ('codigo_contable', 'valor_sancion')

class CarteraGeneralDetalleSerializer(serializers.ModelSerializer):
    nombre_deudor = serializers.SerializerMethodField()
    identificacion = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    resolucion = serializers.SerializerMethodField()

    def get_nombre_deudor(self, obj):
        deudor = Deudores.objects.get(codigo=obj.id_obligacion.cod_factura)
        return f"{deudor.nombres} {deudor.apellidos}"
        
    def get_identificacion(self, obj):
        deudor = Deudores.objects.get(codigo=obj.id_obligacion.cod_factura)
        return f"{deudor.identificacion}"
    
    def get_expediente(self, obj):
        expediente = obj.id_obligacion.id_expediente
        return expediente.codigo_expediente if expediente else None

    def get_resolucion(self, obj):
        resolucion = obj.id_obligacion.id_expediente.numero_resolucion
        return resolucion if resolucion else None

    class Meta:
        model = Cartera
        fields = ('codigo_contable','nombre_deudor','identificacion','expediente','resolucion','numero_factura','valor_sancion')

class CarteraEdadesSerializer(serializers.ModelSerializer):
    nombre_deudor = serializers.SerializerMethodField()
    identificacion = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    resolucion = serializers.SerializerMethodField()

    def get_nombre_deudor(self, obj):
        deudor = Deudores.objects.get(codigo=obj.id_obligacion.cod_factura)
        return f"{deudor.nombres} {deudor.apellidos}"
    
    def get_identificacion(self, obj):
        deudor = Deudores.objects.get(codigo=obj.id_obligacion.cod_factura)
        return f"{deudor.identificacion}"
    
    def get_expediente(self, obj):
        expediente = obj.id_obligacion.id_expediente
        return expediente.codigo_expediente if expediente else None

    def get_resolucion(self, obj):
        resolucion = obj.id_obligacion.id_expediente.numero_resolucion
        return resolucion if resolucion else None

    class Meta:
        model = Cartera
        fields = ('identificacion','nombre_deudor','expediente','resolucion','id_rango','valor_sancion')
