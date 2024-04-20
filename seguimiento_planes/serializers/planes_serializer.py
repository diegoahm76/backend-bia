from rest_framework import serializers
from seguimiento_planes.models.planes_models import ArmonizarPAIPGAR, LineasBasePGAR, ObjetivoDesarrolloSostenible, Planes, EjeEstractegico, Objetivo, Programa, Proyecto, Productos, Actividad, Entidad, Medicion, Tipo, Rubro, Indicador, Metas, TipoEje, Subprograma, MetasEjePGAR

class ObjetivoDesarrolloSostenibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoDesarrolloSostenible
        fields = '__all__'

class ObjetivoDesarrolloSostenibleSerializerUpdate(serializers.ModelSerializer):
        
    class Meta:
        model = ObjetivoDesarrolloSostenible
        fields = '__all__'
        def update(self, instance, validated_data):
                validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
                return super().update(instance, validated_data)


class PlanesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Planes
        fields = '__all__'

class EjeEstractegicoSerializer(serializers.ModelSerializer):
         
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    sigla_plan = serializers.ReadOnlyField(source='id_plan.sigla_plan', default=None)
    nombre_tipo_eje = serializers.ReadOnlyField(source='id_tipo_eje.nombre_tipo_eje', default=None)
    #nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
    nombre_objetivo = serializers.ReadOnlyField(source='id_objetivo.nombre_objetivo', default=None)
    nombre_plan_objetivo = serializers.ReadOnlyField(source='id_objetivo.id_plan.nombre_plan', default=None)
    sigla_plan_objetivo = serializers.ReadOnlyField(source='id_objetivo.id_plan.sigla_plan', default=None)
            
    class Meta:
        model = EjeEstractegico
        fields = '__all__'

class ObjetivoSerializer(serializers.ModelSerializer):
         
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
            
    class Meta:
        model = Objetivo
        fields = '__all__'

class ProgramaSerializer(serializers.ModelSerializer):
         
    nombre_eje_estrategico = serializers.ReadOnlyField(source='id_eje_estrategico.nombre', default=None)
            
    class Meta:
        model = Programa
        fields = '__all__'

class ProyectoSerializer(serializers.ModelSerializer):
         
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)

    class Meta:
        model = Proyecto
        fields = '__all__'

class ProductosSerializer(serializers.ModelSerializer):
         
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)     
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)     
    class Meta:
        model = Productos
        fields = '__all__'

class ActividadSerializer(serializers.ModelSerializer):
             
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)     
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    numero_producto = serializers.ReadOnlyField(source='id_producto.numero_producto', default=None)
    indicadores = serializers.SerializerMethodField()     
    class Meta:
        model = Actividad
        fields = '__all__'
    def get_indicadores (self, obj):
        instance = Indicador.objects.filter(id_actividad=obj.id_actividad)
        data = IndicadorSerializer(instance, many=True).data
        return data

class EntidadSerializer(serializers.ModelSerializer):
                
    class Meta:
        model = Entidad
        fields = '__all__'

class MedicionSerializer(serializers.ModelSerializer):
                
    class Meta:
        model = Medicion
        fields = '__all__'

class TipoSerializer(serializers.ModelSerializer):
                
    class Meta:
        model = Tipo
        fields = '__all__'

class RubroSerializer(serializers.ModelSerializer):

    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
                
    class Meta:
        model = Rubro
        fields = '__all__'

class IndicadorSerializer(serializers.ModelSerializer):

    nombre_medicion = serializers.ReadOnlyField(source='id_medicion.nombre_medicion', default=None)
    nombre_tipo = serializers.ReadOnlyField(source='id_tipo.nombre_tipo', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)     
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    metas = serializers.SerializerMethodField()     
    class Meta:
        model = Indicador
        fields = '__all__'

    def get_metas(self, obj):
        instance = Metas.objects.filter(id_indicador=obj.id_indicador)
        data = MetasSerializer(instance, many=True).data
        return data

class MetasSerializer(serializers.ModelSerializer):

    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)     
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
                
    class Meta:
        model = Metas
        fields = '__all__'

class TipoEjeSerializer(serializers.ModelSerializer):
                    
    class Meta:
        model = TipoEje
        fields = '__all__'

class SubprogramaSerializer(serializers.ModelSerializer):
             
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
                
    class Meta:
        model = Subprograma
        fields = '__all__'
class ProductosActividadesSerializer(serializers.ModelSerializer):
         
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    actividades = serializers.SerializerMethodField()
    class Meta:
        model = Productos
        fields = '__all__'
    def get_actividades(self, obj):
        #ActividadSerializer
        actividades = Actividad.objects.filter(id_producto=obj.id_producto)
        serializer = ActividadSerializer(actividades, many=True)
        return serializer.data
    
class ProyectoSerializerProductos(serializers.ModelSerializer):
         
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
    productos = serializers.SerializerMethodField()
    class Meta:
        model = Proyecto
        fields = '__all__'
    def get_productos(self, obj):
        #ProductosSerializer
        productos = Productos.objects.filter(id_proyecto=obj.id_proyecto)
        serializer = ProductosActividadesSerializer(productos, many=True)
        return serializer.data

class ObjetivoSerializerGetAll(serializers.ModelSerializer):
         
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
            
    class Meta:
        model = Objetivo
        fields = '__all__'
class ProgramaSerializerGetProyectos(serializers.ModelSerializer):
         
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    proyectos = serializers.SerializerMethodField()
            
    class Meta:
        model = Programa
        fields = '__all__'
    def get_proyectos(self, obj):
        #ProyectoSerializer
        proyectos = Proyecto.objects.filter(id_programa=obj.id_programa)
        serializer = ProyectoSerializerProductos(proyectos, many=True)
        return serializer.data

class PlanesSerializerGet(serializers.ModelSerializer):
    objetivos = serializers.SerializerMethodField()
    ejes_estractegicos = serializers.SerializerMethodField()
    programas = serializers.SerializerMethodField()

    class Meta:
        model = Planes
        fields = '__all__'

    def get_objetivos(self, obj):
        #ObjetivoSerializer
        objetivos = Objetivo.objects.filter(id_plan=obj.id_plan)
        serializer = ObjetivoSerializerGetAll(objetivos, many=True)
        return serializer.data
    
    def get_ejes_estractegicos(self, obj):
        #EjeEstractegicoSerializer
        ejes_estractegicos = EjeEstractegico.objects.filter(id_plan=obj.id_plan)
        serializer = EjeEstractegicoSerializer(ejes_estractegicos, many=True)
        return serializer.data
    def get_programas(self, obj):
        #ProgramaSerializer
        programas = Programa.objects.filter(id_plan=obj.id_plan)
        serializer = ProgramaSerializerGetProyectos(programas, many=True)
        return serializer.data


#PGAR

class MetasPGARSerializer(serializers.ModelSerializer):
    nombre_eje_estrategico = serializers.ReadOnlyField(source='id_eje_estrategico.nombre', default=None)
    nombre_objetivo = serializers.ReadOnlyField(source='id_objetivo.nombre_objetivo', default=None)
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    tipo_eje_estrategico = serializers.ReadOnlyField(source='id_eje_estrategico.id_tipo_eje.nombre_tipo_eje', default=None)
    nombre_plan_objetivo = serializers.ReadOnlyField(source='id_objetivo.id_plan.nombre_plan', default=None)

    class Meta:
        model = MetasEjePGAR
        fields = '__all__'

class LineasBasePGARSerializer(serializers.ModelSerializer):
    nombre_eje_estrategico = serializers.ReadOnlyField(source='id_eje_estrategico.nombre', default=None)
    nombre_objetivo = serializers.ReadOnlyField(source='id_objetivo.nombre_objetivo', default=None)
    nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    nombre_meta = serializers.ReadOnlyField(source='id_meta_eje.nombre_meta_eje', default=None)
    tipo_eje_estrategico = serializers.ReadOnlyField(source='id_eje_estrategico.id_tipo_eje.nombre_tipo_eje', default=None)

    class Meta:
        model = LineasBasePGAR
        fields = '__all__'


class ActividadesPGARSerializer(serializers.ModelSerializer):
    nombre_eje_estrategico = serializers.ReadOnlyField(source='id_eje_estrategico.nombre', default=None)
    nombre_meta = serializers.ReadOnlyField(source='id_meta_eje.nombre_meta_eje', default=None)
    nombre_linea_base = serializers.ReadOnlyField(source='id_linea_base.nombre_linea_base', default=None)

    class Meta:
        model = Actividad
        fields = '__all__'

class IndicadoresPGARSerializer(serializers.ModelSerializer):
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    nombre_tipo_indicador = serializers.CharField(source='get_tipo_indicador_display', default=None)
    nombre_medida = serializers.CharField(source='get_medida_display', default=None)
    nombre_unidad_org = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)

    class Meta:
        model = Indicador
        fields = '__all__'

class ArmonizarPAIPGARSerializer(serializers.ModelSerializer):
    nombre_planPGAR = serializers.ReadOnlyField(source='id_planPGAR.nombre_plan', default=None)
    nombre_planPAI = serializers.ReadOnlyField(source='id_planPAI.nombre_plan', default=None)
    objetivoPGAR = serializers.SerializerMethodField()

    class Meta:
        model = ArmonizarPAIPGAR
        fields = '__all__'

    def get_objetivoPGAR(self, obj):
        #ObjetivoSerializer
        objetivos = Objetivo.objects.filter(id_plan=obj.id_planPGAR)
        serializer = ObjetivoSerializer(objetivos, many=True)
        return serializer.data
