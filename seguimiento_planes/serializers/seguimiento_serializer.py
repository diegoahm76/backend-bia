from rest_framework import serializers
from seguimiento_planes.models.planes_models import Sector
from seguimiento_planes.models.seguimiento_models import (FuenteFinanciacionIndicadores, 
                                                          DetalleInversionCuentas, 
                                                          Modalidad, 
                                                          Ubicaciones, 
                                                          FuenteRecursosPaa, 
                                                          Intervalo, 
                                                          EstadoVF, 
                                                          CodigosUNSP, 
                                                          ConceptoPOAI, 
                                                          FuenteFinanciacion, 
                                                          BancoProyecto, 
                                                          PlanAnualAdquisiciones, 
                                                          PAACodgigoUNSP, 
                                                          SeguimientoPAI,
                                                          SeguimientoPAIDocumentos,
                                                          SeguimientoPOAI)
class FuenteFinanciacionIndicadoresSerializer(serializers.ModelSerializer):

    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
    nombre_cuenca = serializers.ReadOnlyField(source='id_cuenca.nombre', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    nombre_meta = serializers.ReadOnlyField(source='id_meta.nombre_meta', default=None)

    class Meta:
        model = FuenteFinanciacionIndicadores
        fields = '__all__'

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'

class SectorSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class DetalleInversionCuentasSerializer(serializers.ModelSerializer):

    nombre_sector = serializers.ReadOnlyField(source='id_sector.nombre_sector', default=None)
    rubro = serializers.ReadOnlyField(source='id_rubro.cuenta', default=None)
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
    nombre_subprograma = serializers.ReadOnlyField(source='id_subprograma.nombre_subprograma', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
    nombre_meta = serializers.ReadOnlyField(source='id_meta.nombre_meta', default=None)

    class Meta:
        model = DetalleInversionCuentas
        fields = '__all__'

class ModalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modalidad
        fields = '__all__'

class ModalidadSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Modalidad
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class UbicacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ubicaciones
        fields = '__all__'

class UbicacionesSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Ubicaciones
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)
        
class FuenteRecursosPaaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuenteRecursosPaa
        fields = '__all__'

class FuenteRecursosPaaSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = FuenteRecursosPaa
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class IntervaloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervalo
        fields = '__all__'

class IntervaloSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Intervalo
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class EstadoVFSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoVF
        fields = '__all__'

class EstadoVFSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = EstadoVF
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class CodigosUNSPSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigosUNSP
        fields = '__all__'

class CodigosUNSPSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = CodigosUNSP
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)

class ConceptoPOAISerializer(serializers.ModelSerializer):
    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
    nombre = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    rubro = serializers.ReadOnlyField(source='id_rubro.cuenta', default=None)

    class Meta:
        model = ConceptoPOAI
        fields = '__all__'

class ConceptoPOAISerializerGet(serializers.ModelSerializer):
    nombre_responsable = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    nombre_modalidad = serializers.ReadOnlyField(source='id_modalidad.nombre_modalidad', default=None)

    class Meta:
        model = ConceptoPOAI
        fields = ['id_concepto', 'nombre_concepto', 'valor_inicial', 'nombre_responsable', 'nombre_modalidad']

class FuenteFinanciacionSerializer(serializers.ModelSerializer):

    concepto = serializers.ReadOnlyField(source='id_concepto.concepto', default=None)
    class Meta:
        model = FuenteFinanciacion
        fields = '__all__'

class BancoProyectoSerializer(serializers.ModelSerializer):
    
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
    nombre_meta = serializers.ReadOnlyField(source='id_meta.nombre_meta', default=None)
    rubro = serializers.ReadOnlyField(source='id_rubro.cuenta', default=None)
    nombre_fuente = serializers.ReadOnlyField(source='id_fuente.nombre_fuente', default=None)
    
    class Meta:
        model = BancoProyecto
        fields = '__all__'

class PlanAnualAdquisicionesSerializer(serializers.ModelSerializer):
    
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    nombre_intervalo = serializers.ReadOnlyField(source='id_intervalo.nombre_intervalo', default=None)
    nombre_modalidad = serializers.ReadOnlyField(source='id_modalidad.nombre_modalidad', default=None)
    codigo_modalidad = serializers.ReadOnlyField(source='id_modalidad.codigo_modalidad', default=None)
    nombre_fuente = serializers.ReadOnlyField(source='id_recurso_paa.nombre_fuente', default=None)
    nombre_estado = serializers.ReadOnlyField(source='id_estado_vf.nombre_estado', default=None)
    nombre_unidad = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    nombre_ubicacion = serializers.ReadOnlyField(source='id_ubicaion.nombre_ubicacion', default=None)
    email_persona_responsable = serializers.ReadOnlyField(source='id_persona_responsable.email', default=None)
    telefono_persona_responsable = serializers.ReadOnlyField(source='id_persona_responsable.telefono_celular', default=None)
    persona_responsable = serializers.SerializerMethodField()
    
    def get_persona_responsable(self, obj):
        persona_responsable = None
        nombre_list = [obj.id_persona_responsable.primer_nombre, obj.id_persona_responsable.segundo_nombre, obj.id_persona_responsable.primer_apellido, obj.id_persona_responsable.segundo_apellido]
        persona_responsable = ' '.join(item for item in nombre_list if item is not None)
        return persona_responsable.upper()
    
    class Meta:
        model = PlanAnualAdquisiciones
        fields = '__all__'

class PAACodgigoUNSPSerializer(serializers.ModelSerializer):
        
    nombre_paa = serializers.ReadOnlyField(source='id_plan.descripcion', default=None)
    nombre_producto_unsp = serializers.ReadOnlyField(source='id_codigo.codigo_unsp', default=None)
    codigo_unsp = serializers.ReadOnlyField(source='id_codigo.codigo_unsp', default=None)
        
    class Meta:
        model = PAACodgigoUNSP
        fields = '__all__'

class SeguimientoPAISerializer(serializers.ModelSerializer):
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    nombre_unidad = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
    nombre_meta = serializers.ReadOnlyField(source='id_meta.nombre_meta', default=None)

    class Meta:
            model = SeguimientoPAI
            fields = '__all__'

class SeguimientoPAIDocumentosSerializer(serializers.ModelSerializer):
    class Meta:
            model = SeguimientoPAIDocumentos
            fields = '__all__'

# class SeguimientoPOAISerializer(serializers.ModelSerializer):
#     nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
#     nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
#     nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
#     nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
#     nombre_unidad = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
#     nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
#     nombre_meta = serializers.ReadOnlyField(source='id_meta.nombre_meta', default=None)
#     codigo_modalidad = serializers.ReadOnlyField(source='id_modalidad.codigo_modalidad', default=None)
#     concepto = serializers.ReadOnlyField(source='id_concepto.concepto', default=None)
#     sector = serializers.ReadOnlyField(source='id_sector.nombre_sector', default=None)
#     nombre_fuente = serializers.ReadOnlyField(source='id_fuente.nombre_fuente', default=None)
#     cuenta = serializers.ReadOnlyField(source='id_detalle_inversion.cuenta', default=None)
#     objeto_contrato = serializers.ReadOnlyField(source='id_banco_proyecto.objeto_contrato', default=None)
#     ubicacion = serializers.ReadOnlyField(source='id_ubicacion.nombre_ubicacion', default=None)
#     clase_tercero = serializers.ReadOnlyField(source='id_tercero.nombre', default=None)

#     class Meta:
#             model = SeguimientoPOAI
#             fields = '__all__'

class SeguimientoPOAISerializer(serializers.ModelSerializer):
    class Meta:
            model = SeguimientoPOAI
            fields = '__all__'
