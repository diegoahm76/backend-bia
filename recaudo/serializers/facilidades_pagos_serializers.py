from rest_framework import serializers
from recaudo.models.procesos_models import (
    Avaluos, 
    Bienes
)

from recaudo.models.pagos_models import (
    FacilidadesPago,
    GarantiasFacilidad,
    DetallesBienFacilidadPago,
    CumplimientoRequisitos, 
    RequisitosActuacion
)

from recaudo.models.base_models import TiposBien, TipoActuacion

from seguridad.models import Personas, Municipio


class TipoBienSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposBien
        fields = '__all__'


class TipoActuacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActuacion
        fields = '__all__'


class BienSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bienes
        fields = '__all__'


class AvaluosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaluos
        fields = '__all__'


class RequisitosActuacionSerializer (serializers.ModelSerializer):
    class Meta:
        model = RequisitosActuacion
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


class DatosContactoDeudorSerializer(serializers.ModelSerializer):
    ciudad = serializers.SerializerMethodField()

    def get_ciudad(self, obj):
        ubicacion = Municipio.objects.filter(cod_municipio=obj.municipio_residencia).first()
        ubicacion = ubicacion.nombre
        return ubicacion
        
    class Meta:
        model = Personas
        fields = ('direccion_notificaciones', 'ciudad', 'telefono_celular')


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


class ListadoFacilidadesPagoSerializer(serializers.ModelSerializer):
    identificacion = serializers.ReadOnlyField(source='id_deudor.identificacion',default=None)
    nombre_de_usuario = serializers.SerializerMethodField()
    nombre_funcionario = serializers.SerializerMethodField()
    id_facilidad = serializers.ReadOnlyField(source='id', default=None)

    def get_nombre_de_usuario(self, obj):
        return f"{obj.id_deudor.nombres} {obj.id_deudor.apellidos}"

    def get_nombre_funcionario(self, obj):
        funcionario = Personas.objects.filter(id_persona=obj.id_funcionario).first()
        return f"{funcionario.primer_nombre} {funcionario.primer_apellido}"
    
    class Meta:
        model = FacilidadesPago
        fields = ('id_facilidad','nombre_de_usuario','identificacion','numero_radicacion','fecha_generacion','nombre_funcionario')


class FacilidadesPagoFuncionarioPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilidadesPago
        fields = ('id','id_funcionario')


class FuncionariosSerializer(serializers.ModelSerializer):
    nombre_funcionario = serializers.SerializerMethodField()
    
    def get_nombre_funcionario(self, obj):
        nombre_funcionario = None
        nombre_list = [obj.primer_nombre, obj.primer_apellido]
        nombre_funcionario = ' '.join(item for item in nombre_list if item is not None)
        return nombre_funcionario
    
    class Meta:
        model = Personas
        fields = ('id_persona', 'nombre_funcionario')


class FacilidadPagoGetByIdSerializer(serializers.ModelSerializer):
    tipo_actuacion = serializers.ReadOnlyField(source='id_tipo_actuacion.descripcion',default=None)

    class Meta:
        model = FacilidadesPago
        fields = ('id', 'id_deudor', 'id_tipo_actuacion', 'tipo_actuacion', 'fecha_generacion',
                  'observaciones', 'periodicidad', 'cuotas', 'documento_soporte', 'consignacion_soporte',
                  'documento_no_enajenacion', 'id_funcionario','notificaciones', 'numero_radicacion'
                  )

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