from almacen.models.generics_models import UnidadesMedida
from almacen.models.hoja_de_vida_models import HojaDeVidaVehiculos
from transversal.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from rest_framework import serializers
from datetime import datetime
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.mantenimientos_models import (
    ProgramacionMantenimientos,
    RegistroMantenimientos
)
        
class SerializerProgramacionMantenimientos(serializers.ModelSerializer):
    id_persona_solicita = PersonasSerializer(read_only=True)
    id_persona_anula = PersonasSerializer(read_only=True)
    placa = serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_articulo.codigo_bien', default=None)
    consecutivo = serializers.ReadOnlyField(source='id_articulo.nro_elemento_bien', default=None)

    class Meta:
        model=ProgramacionMantenimientos
        fields='__all__'
        
class SerializerProgramacionMantenimientosGet(serializers.ModelSerializer):
    id_programacion_mantenimiento = serializers.ReadOnlyField(source='id_programacion_mtto', default=None)
    tipo = serializers.ReadOnlyField(source='cod_tipo_mantenimiento', default=None)
    tipo_descripcion = serializers.CharField(source='get_cod_tipo_mantenimiento_display', default=None)
    fecha = serializers.ReadOnlyField(source='fecha_programada', default=None)
    articulo = serializers.ReadOnlyField(source='id_articulo.id_bien', default=None)
    placa = serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro', default=None)
    marca = serializers.ReadOnlyField(source='id_articulo.id_marca.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_articulo.codigo_bien', default=None)
    consecutivo = serializers.ReadOnlyField(source='id_articulo.nro_elemento_bien', default=None)
    motivo = serializers.ReadOnlyField(source='motivo_mantenimiento', default=None)
    observacion = serializers.ReadOnlyField(source='observaciones', default=None)
    responsable = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    fecha_ejecutado = serializers.SerializerMethodField()
    persona_realiza = serializers.SerializerMethodField()
    persona_diligencia = serializers.SerializerMethodField()

    def get_fecha_ejecutado(self, obj):
        registro_mantenimiento = RegistroMantenimientos.objects.filter(id_programacion_mtto=obj.id_programacion_mtto).first()
        if registro_mantenimiento:
            return registro_mantenimiento.fecha_ejecutado
        return None
    
    def get_persona_realiza(self, obj):
        registro_mantenimiento = RegistroMantenimientos.objects.filter(id_programacion_mtto=obj.id_programacion_mtto).first()
        if registro_mantenimiento:
            return registro_mantenimiento.id_persona_realiza.__str__()
        return None
    
    def get_persona_diligencia(self, obj):
        registro_mantenimiento = RegistroMantenimientos.objects.filter(id_programacion_mtto=obj.id_programacion_mtto).first()
        if registro_mantenimiento:
            return registro_mantenimiento.id_persona_diligencia.__str__()
        return None

    def get_responsable(self, obj):
        nombre_completo_reponsable = None
        if obj.id_persona_solicita:
            if obj.id_persona_solicita.tipo_persona == 'J':
                nombre_completo_reponsable = obj.id_persona_solicita.razon_social
            else:
                nombre_list = [obj.id_persona_solicita.primer_nombre, obj.id_persona_solicita.segundo_nombre,
                                obj.id_persona_solicita.primer_apellido, obj.id_persona_solicita.segundo_apellido]
                nombre_completo_reponsable = ' '.join(item for item in nombre_list if item is not None)
                nombre_completo_reponsable = nombre_completo_reponsable if nombre_completo_reponsable != "" else None
        return nombre_completo_reponsable

    def get_estado(self, obj):
        estado = None
        if obj.fecha_programada:
            estado = 'Vencido' if obj.fecha_programada < datetime.now().date() else 'Programado'
        else:
            hdv_vehiculo = HojaDeVidaVehiculos.objects.filter(id_articulo=obj.id_articulo).first()
            if hdv_vehiculo and hdv_vehiculo.ultimo_kilometraje:
                estado = 'Vencido' if obj.kilometraje_programado < hdv_vehiculo.ultimo_kilometraje else 'Programado'
            else:
                estado = 'Programado'
        return estado

    class Meta:
        model=ProgramacionMantenimientos
        fields= '__all__'

class AnularMantenimientoProgramadoSerializer(serializers.ModelSerializer):
    justificacion_anulacion = serializers.CharField(max_length=255, min_length=10)
    class Meta:
        model=ProgramacionMantenimientos
        fields=['justificacion_anulacion']

class UpdateMantenimientoProgramadoSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProgramacionMantenimientos
        fields=['cod_tipo_mantenimiento', 'observaciones']
        
class SerializerRegistroMantenimientos(serializers.ModelSerializer):
    id_persona_realiza = PersonasSerializer(read_only=True)
    id_persona_diligencia = PersonasSerializer(read_only=True)
    ruta_documentos_soporte = serializers.ReadOnlyField(source='ruta_documentos_soporte.ruta_archivo.url', default=None)
    class Meta:
        model=RegistroMantenimientos
        fields=('__all__')
        
class SerializerUpdateRegistroMantenimientos(serializers.ModelSerializer):
    # ruta_documentos_soporte = serializers.ReadOnlyField(source='ruta_documentos_soporte.url', default=None)
    # id_persona_diligencia = PersonasSerializer(read_only=True)
    class Meta:
        model=RegistroMantenimientos
        fields=('cod_tipo_mantenimiento','acciones_realizadas','dias_empleados','observaciones','cod_estado_final','valor_mantenimiento','contrato_mantenimiento','id_persona_realiza','id_persona_diligencia','ruta_documentos_soporte')


class SerializerProgramacionMantenimientosPost(serializers.ModelSerializer):
    class Meta:
        model=ProgramacionMantenimientos
        fields=('__all__')
        extra_kwargs = {
            'id_articulo': {'required': True},
            'cod_tipo_mantenimiento': {'required': True},
            'fecha_generada': {'required': True},
            'fecha_programada': {'required': True},
            'motivo_mantenimiento': {'required': True},
            'ejecutado': {'required': True}
        }

class SerializerRegistroMantenimientosPost(serializers.ModelSerializer):
    class Meta:
        model=RegistroMantenimientos
        fields=('__all__')

class ControlMantenimientosProgramadosGetListSerializer(serializers.ModelSerializer):
    nombre_bien = serializers.ReadOnlyField(source='id_articulo.nombre', default=None)
    codigo_bien = serializers.ReadOnlyField(source='id_articulo.codigo_bien', default=None)
    cod_tipo_activo = serializers.ReadOnlyField(source='id_articulo.cod_tipo_activo.cod_tipo_activo', default=None)
    tipo_activo = serializers.ReadOnlyField(source='id_articulo.cod_tipo_activo.nombre', default=None)
    serial_placa = serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro', default=None)
    tipo_mantenimiento = serializers.CharField(source='get_cod_tipo_mantenimiento_display')
    kilometraje_actual = serializers.SerializerMethodField()
    dias_kilometros_vencidos = serializers.SerializerMethodField()
    persona_solicita = serializers.SerializerMethodField()
    persona_anula = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()

    def get_kilometraje_actual(self, obj):
        kilometraje_actual = None
        hoja_vida = HojaDeVidaVehiculos.objects.filter(id_articulo = obj.id_articulo).first()
        if hoja_vida:
            kilometraje_actual = hoja_vida.ultimo_kilometraje
        return kilometraje_actual
    
    def get_dias_kilometros_vencidos(self, obj):
        dias_kilometros_vencidos = None
        current_date = datetime.now().date()
        
        kilometraje_actual = 0
        hoja_vida = HojaDeVidaVehiculos.objects.filter(id_articulo = obj.id_articulo).first()
        if hoja_vida:
            kilometraje_actual = hoja_vida.ultimo_kilometraje
            
        if obj.fecha_programada:
            if current_date > obj.fecha_programada and not obj.ejecutado:
                dias_kilometros_vencidos = abs((current_date - obj.fecha_programada).days)
        elif obj.kilometraje_programado and kilometraje_actual:
            if kilometraje_actual > obj.kilometraje_programado and not obj.ejecutado:
                dias_kilometros_vencidos = kilometraje_actual - obj.kilometraje_programado 
            
        return dias_kilometros_vencidos
    
    def get_persona_solicita(self, obj):
        nombre_completo_persona_solicita = None
        if obj.id_persona_solicita:
            if obj.id_persona_solicita.tipo_persona == 'J':
                nombre_completo_persona_solicita = obj.id_persona_solicita.razon_social
            else:
                nombre_list = [obj.id_persona_solicita.primer_nombre, obj.id_persona_solicita.segundo_nombre,
                                obj.id_persona_solicita.primer_apellido, obj.id_persona_solicita.segundo_apellido]
                nombre_completo_persona_solicita = ' '.join(item for item in nombre_list if item is not None)
                nombre_completo_persona_solicita = nombre_completo_persona_solicita if nombre_completo_persona_solicita != "" else None
        return nombre_completo_persona_solicita
    
    def get_persona_anula(self, obj):
        nombre_completo_persona_anula = None
        if obj.id_persona_anula:
            if obj.id_persona_anula.tipo_persona == 'J':
                nombre_completo_persona_anula = obj.id_persona_anula.razon_social
            else:
                nombre_list = [obj.id_persona_anula.primer_nombre, obj.id_persona_anula.segundo_nombre,
                                obj.id_persona_anula.primer_apellido, obj.id_persona_anula.segundo_apellido]
                nombre_completo_persona_anula = ' '.join(item for item in nombre_list if item is not None)
                nombre_completo_persona_anula = nombre_completo_persona_anula if nombre_completo_persona_anula != "" else None
        return nombre_completo_persona_anula
    
    def get_estado(self, obj):
        estado = None
        if obj.fecha_programada:
            estado = 'Vencido' if obj.fecha_programada < datetime.now().date() else 'Programado'
        else:
            hdv_vehiculo = HojaDeVidaVehiculos.objects.filter(id_articulo=obj.id_articulo).first()
            if hdv_vehiculo and hdv_vehiculo.ultimo_kilometraje:
                estado = 'Vencido' if obj.kilometraje_programado < hdv_vehiculo.ultimo_kilometraje else 'Programado'
            else:
                estado = 'Programado'
        return estado
    
    class Meta:
        fields= '__all__'
        model = ProgramacionMantenimientos