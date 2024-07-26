from rest_framework import serializers
from recaudo.models.base_models import TipoRenta
from recaudo.models.liquidaciones_models import (
    HistEstadosLiq,
    OpcionesLiquidacionBase,
    Deudores,
    LiquidacionesBase,
    DetalleLiquidacionBase,
    Expedientes,
    CalculosLiquidacionBase
)
from recaudo.models.cobros_models import (
    Cartera,
    ConceptoContable
)

class OpcionesLiquidacionBaseSerializer(serializers.ModelSerializer):
    usada = serializers.SerializerMethodField()
    tipo_renta = serializers.ReadOnlyField(source='tipo_renta.nombre_tipo_renta', default=None)
    tipo_cobro = serializers.ReadOnlyField(source='tipo_cobro.nombre_tipo_cobro', default=None)

    def get_usada(self, obj):
        detalles_liquidacion = DetalleLiquidacionBase.objects.filter(id_opcion_liq=obj.id)
        if detalles_liquidacion.exists():
            return True
        else:
            return False
        
    # def get_tipo_renta(self, obj):
    #     id_tipo_renta = int(obj.tipo_renta)
    #     tipo_renta = TipoRenta.objects.filter(pk=id_tipo_renta).first()
    #     if tipo_renta:
    #         return tipo_renta.nombre_tipo_renta
    #     else:
    #         return None

    class Meta:
        model = OpcionesLiquidacionBase
        fields = '__all__'


class OpcionesLiquidacionBasePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionesLiquidacionBase
        fields = ('nombre', 'estado', 'version', 'funcion', 'variables', 'bloques','tipo_cobro','tipo_renta')


class DeudoresSerializer(serializers.ModelSerializer):
    identificacion = serializers.SerializerMethodField()
    nombres = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    direccion = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    fecha_nacimiento = serializers.SerializerMethodField()
    # genero = serializers.SerializerMethodField()
    # carteras = serializers.SerializerMethodField()
    # liquidaciones = serializers.SerializerMethodField()

    class Meta:
        model = Deudores
        fields = ('id', 'identificacion', 'nombres', 'telefono', 'direccion', 'email','fecha_nacimiento')

    def get_nombres(self, obj):
        if obj.id_persona_deudor:
            if obj.id_persona_deudor.razon_social:
                nombre_completo = obj.id_persona_deudor.razon_social
            else:
                nombre_completo = ' '.join(filter(None, [obj.id_persona_deudor.primer_nombre, obj.id_persona_deudor.segundo_nombre, obj.id_persona_deudor.primer_apellido, obj.id_persona_deudor.segundo_apellido]))
            return nombre_completo
        elif obj.id_persona_deudor_pymisis:
            return f"{obj.id_persona_deudor_pymisis.t03nombre}"
        else:
            return None

    def get_identificacion(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.numero_documento
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03nit
        else:
            return None
        
    def get_telefono(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.telefono_celular
        elif obj.id_persona_deudor:
            return obj.id_persona_deudor.telefono_empresa
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03telefono
        else:
            return None
        
    def get_direccion(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.direccion_residencia
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03direccion
        else:
            return None
        
    def get_fecha_nacimiento(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.fecha_nacimiento
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03fechanacimiento
        else:
            return None
        
    # def get_genero(self, obj):
    #     if obj.id_persona_deudor:
    #         return obj.id_persona_deudor.sexo
    #     elif obj.id_persona_deudor_pymisis:
    #         return obj.id_persona_deudor_pymisis.t03genero
    #     else:
    #         return None
        
    def get_email(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.email
        elif obj.id_persona_deudor:
            return obj.id_persona_deudor.email_empresarial
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03email
        else:
            return None


    # def get_carteras(self, obj):
    #     carteras = Cartera.objects.filter(id_deudor=obj.id)
    #     cartera_data = []

    #     for cartera in carteras:
    #         cartera_data.append({
    #             'tipo_renta': cartera.tipo_renta,
    #             'tipo_cobro': cartera.tipo_cobro,
    #             'dias_mora': cartera.dias_mora,
    #             'fecha_facturacion': cartera.fecha_facturacion,
    #             'resolucion': cartera.num_resolucion,
    #         })

    #     return cartera_data
    
    # def get_liquidaciones(self, obj):
    #     liquidaciones = LiquidacionesBase.objects.filter(id_deudor=obj.id)
    #     liquidacion_data = []

    #     for liquidacion in liquidaciones:
    #         liquidacion_data.append({
    #             'estado': liquidacion.estado
    #         })

    #     return liquidacion_data
    
    


class DetallesLiquidacionBaseSerializer(serializers.ModelSerializer):
    id_opcion_liq = OpcionesLiquidacionBaseSerializer(many=False)

    class Meta:
        model = DetalleLiquidacionBase
        fields = '__all__'


class ExpedientesSerializer(serializers.ModelSerializer):
    expediente = serializers.SerializerMethodField()

    class Meta:
        model = Expedientes
        fields = '__all__'

    def get_expediente(self, obj):
        expediente_doc = obj.id_expediente_doc
        if expediente_doc:
            codigo_exp = f"{expediente_doc.codigo_exp_und_serie_subserie}{expediente_doc.codigo_exp_Agno}{expediente_doc.codigo_exp_consec_por_agno}"
            return codigo_exp
        else:
            expediente_pimisys = obj.id_expediente_pimisys
            if expediente_pimisys:
                return expediente_pimisys.t920codexpediente
            else:
                return None


class LiquidacionesBaseSerializer(serializers.ModelSerializer):
    id_deudor = DeudoresSerializer(many=False)
    id_expediente = ExpedientesSerializer(many=False)
    detalles = DetallesLiquidacionBaseSerializer(many=True)

    class Meta:
        model = LiquidacionesBase
        fields = ('id', 'id_deudor', 'id_expediente', 'fecha_liquidacion', 'vencimiento', 'periodo_liquidacion', 'valor', 'estado', 'detalles', 'ciclo_liquidacion')


class LiquidacionesBasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidacionesBase
        fields = '__all__'

class LiquidacionesTramitePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidacionesBase
        fields = '__all__'
        extra_kwargs = {
            'fecha_liquidacion': {'required': True, 'allow_null': False},
            'vencimiento': {'required': True, 'allow_null': False},
            'periodo_liquidacion': {'required': True, 'allow_null': False},
            'valor': {'required': True, 'allow_null': False},
            'estado': {'required': True, 'allow_null': False},
            'id_solicitud_tramite': {'required': True, 'allow_null': False}
        }


class LiquidacionesExpedientePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidacionesBase
        fields = '__all__'
        extra_kwargs = {
            'fecha_liquidacion': {'required': True, 'allow_null': False},
            'vencimiento': {'required': True, 'allow_null': False},
            'periodo_liquidacion': {'required': True, 'allow_null': False},
            'valor': {'required': True, 'allow_null': False},
            'estado': {'required': True, 'allow_null': False},
            'id_expediente': {'required': True, 'allow_null': False}
        }

class LiquidacionesTramiteGetSerializer(serializers.ModelSerializer):
    id_archivo_ruta = serializers.ReadOnlyField(source='id_archivo.ruta_archivo.url', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_solicitud_tramite.nombre_proyecto', default=None)
    detalles = serializers.SerializerMethodField()
    persona_liquida = serializers.SerializerMethodField()

    def get_detalles(self, obj):
        detalles = DetalleLiquidacionBase.objects.filter(id_liquidacion=obj.id)
        serializer_detalles = DetallesLiquidacionBasePostSerializer(detalles, many=True)
        return serializer_detalles.data

    def get_persona_liquida(self, obj):
        nombre_persona_liquida = None
        if obj.id_persona_liquida:
            if obj.id_persona_liquida.tipo_persona == 'J':
                nombre_persona_liquida = obj.id_persona_liquida.razon_social
            else:
                nombre_list = [obj.id_persona_liquida.primer_nombre, obj.id_persona_liquida.segundo_nombre,
                                obj.id_persona_liquida.primer_apellido, obj.id_persona_liquida.segundo_apellido]
                nombre_persona_liquida = ' '.join(item for item in nombre_list if item is not None)
                nombre_persona_liquida = nombre_persona_liquida if nombre_persona_liquida != "" else None
        return nombre_persona_liquida

    class Meta:
        model = LiquidacionesBase
        fields = '__all__'

class LiquidacionesTramiteAnularSerializer(serializers.ModelSerializer):

    class Meta:
        model = LiquidacionesBase
        fields = ['estado','anulado','observacion']

class HistEstadosLiqPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistEstadosLiq
        fields = '__all__'

class HistEstadosLiqGetSerializer(serializers.ModelSerializer):
    num_liquidacion = serializers.ReadOnlyField(source='id_liquidacion_base.num_liquidacion', default=None)
    valor_liquidacion = serializers.ReadOnlyField(source='id_liquidacion_base.valor', default=None)
    fecha_liquidacion = serializers.ReadOnlyField(source='id_liquidacion_base.fecha_liquidacion', default=None)
    fecha_vencimiento_liquidacion = serializers.ReadOnlyField(source='id_liquidacion_base.vencimiento', default=None)
    id_solicitud_tramite = serializers.ReadOnlyField(source='id_liquidacion_base.id_solicitud_tramite.id_solicitud_tramite', default=None)
    nombre_proyecto_tramite = serializers.ReadOnlyField(source='id_liquidacion_base.id_solicitud_tramite.nombre_proyecto', default=None)
    
    class Meta:
        model = HistEstadosLiq
        fields = '__all__'

class LiquidacionesBasePostMasivoSerializer(serializers.ModelSerializer):
    id_expediente = serializers.ListField(child=serializers.IntegerField(), write_only=True)  

    class Meta:
        model = LiquidacionesBase
        fields = ( 'id_expediente','id', 'id_deudor', 'fecha_liquidacion', 'vencimiento', 'periodo_liquidacion', 'estado', 'ciclo_liquidacion', 'valor')

    def create(self, validated_data):
        id_expedientes = validated_data.pop('id_expediente', [])
        instances = []
        for id_expediente in id_expedientes:
            expediente_instance = Expedientes.objects.get(pk=id_expediente)
            validated_data['id_expediente'] = expediente_instance  # Reemplazamos la lista de IDs con la instancia del expediente
            instance = LiquidacionesBase.objects.create(**validated_data)
            expediente_instance.estado = 'guardado'
            expediente_instance.save()
            instances.append(instance)
        return instances


class DetallesLiquidacionBasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleLiquidacionBase
        fields = '__all__'


class CalculosLiquidacionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculosLiquidacionBase
        fields = '__all__'