from rest_framework import serializers
from recaudo.models.cobros_models import Cartera, ConceptoContable, VistaCarteraTua
from recaudo.models.liquidaciones_models import (
    Deudores
)
from recaudo.models.base_models import (
    RangosEdad,
    TipoRenta
)
from recaudo.models.procesos_models import (
    CategoriaAtributo,
    EtapasProceso,
    Procesos,
    TiposAtributos
)


class CarteraSerializer(serializers.ModelSerializer):
    identificacion = serializers.SerializerMethodField()
    nombres = serializers.SerializerMethodField()
    class Meta:
        model = Cartera
        fields = '__all__'

    def get_nombres(self, obj):    
        if obj.id_deudor.id_persona_deudor:
            if obj.id_deudor.id_persona_deudor.razon_social:
                nombre_completo = obj.id_deudor.id_persona_deudor.razon_social
            else:
                nombre_completo = ' '.join(filter(None, [obj.id_deudor.id_persona_deudor.primer_nombre, obj.id_deudor.id_persona_deudor.segundo_nombre, obj.id_deudor.id_persona_deudor.primer_apellido, obj.id_deudor.id_persona_deudor.segundo_apellido]))
            return nombre_completo
        elif obj.id_deudor.id_persona_deudor_pymisis:
            return f"{obj.id_deudor.id_persona_deudor_pymisis.t03nombre}"
        else:
            return None
    
    def get_identificacion(self, obj):
        if obj.id_deudor.id_persona_deudor:
            return obj.id_deudor.id_persona_deudor.numero_documento
        elif obj.id_deudor.id_persona_deudor_pymisis:
            return obj.id_deudor.id_persona_deudor_pymisis.t03nit
        else:
            return None


class DeudorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deudores
        fields = '__all__'


class RangosEdadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RangosEdad
        fields = '__all__'


class ProcesosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procesos
        fields = '__all__'


class TipoRentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRenta
        fields = '__all__'


class CarteraGeneralSerializer(serializers.ModelSerializer):
    id_deudor = DeudorSerializer(many=False)
    id_rango = RangosEdadSerializer(many=False)
    proceso_cartera = serializers.SerializerMethodField()
    fecha_facturacion = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, allow_null=True)
    fecha_notificacion = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, allow_null=True)
    fecha_ejecutoriado = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, allow_null=True)
    concepto_contable = serializers.ReadOnlyField(source='concepto_contable.codigo_contable', default=None)
    inicio = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, allow_null=True)
    expediente = serializers.SerializerMethodField()
    fin = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, allow_null=True)
    nombre_deudor = serializers.SerializerMethodField()
    identificacion = serializers.SerializerMethodField()

    class Meta:
        model = Cartera
        fields = ('__all__')#('id', 'nombre', 'dias_mora', 'valor_intereses', 'valor_sancion', 'inicio', 'fin', 'id_rango', 'codigo_contable', 'fecha_facturacion', 'fecha_notificacion',
                  #'fecha_ejecutoriado', 'numero_factura', 'monto_inicial', 'tipo_cobro', 'id_deudor', 'proceso_cartera', 'tipo_renta','nombre_deudor','identificacion')

    def get_proceso_cartera(self, obj):
        procesos_cartera = obj.proceso_cartera.filter(fin__isnull=True)
        serializer = ProcesosSerializer(instance=procesos_cartera, many=True)
        return serializer.data
    
    def get_nombre_deudor(self, obj):
        if obj.id_deudor.id_persona_deudor:
            if obj.id_deudor.id_persona_deudor.razon_social:
                nombre_completo = obj.id_deudor.id_persona_deudor.razon_social
            else:
                nombre_completo = ' '.join(filter(None, [obj.id_deudor.id_persona_deudor.primer_nombre, obj.id_deudor.id_persona_deudor.segundo_nombre, obj.id_deudor.id_persona_deudor.primer_apellido, obj.id_deudor.id_persona_deudor.segundo_apellido]))
            return nombre_completo
        elif obj.id_deudor.id_persona_deudor_pymisis:
            return f"{obj.id_deudor.id_persona_deudor_pymisis.t03nombre}"
        else:
            return None
        
    def get_identificacion(self, obj):
        if obj.id_deudor.id_persona_deudor:
            return obj.id_deudor.id_persona_deudor.numero_documento
        elif obj.id_deudor.id_persona_deudor_pymisis:
            return obj.id_deudor.id_persona_deudor_pymisis.t03nit
        else:
            return None
        
    def get_expediente(self, obj):
        if obj.id_expediente:
            if obj.id_expediente.id_expediente_pimisys:
                return obj.id_expediente.id_expediente_pimisys.t920codexpediente
            elif obj.id_expediente.id_expediente_doc:
                return f"{obj.id_expediente.id_expediente_doc.codigo_exp_und_serie_subserie}-{obj.id_expediente.id_expediente_doc.codigo_exp_Agno}-{obj.id_expediente.id_expediente_doc.codigo_exp_consec_por_agno}"
            else:
                return None
        else:
            return None
    
class CarteraCompararSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartera
        fields = ['numero_factura']

class CarteraPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartera
        fields = ('__all__')
    
class VistaCarteraTuaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VistaCarteraTua
        fields = '__all__' #['fecha', 'cod_cia', 'tipo_renta', 'cuenta_contable', 'nit', 'nombre_deudor', 'fecha_fac', 'fecha_notificacion', 'fecha_en_firme', 'corte_desde', 'corte_hasta', 'num_factura', 'num_liquidacion', 'periodo', 'agno', 'expediente', 'num_resolucion', 'recurso', 'doc_auto', 'saldo_capital', 'saldo_intereses', 'dias_mora']


class RangosSerializer(serializers.ModelSerializer):
    class Meta:
        model = RangosEdad
        fields = '__all__'

class ConceptoContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptoContable
        fields = '__all__'

class EtapasSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtapasProceso
        fields = '__all__'

class SubEtapasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaAtributo
        fields = '__all__'
    
class TiposAtributosSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposAtributos
        fields = '__all__'

