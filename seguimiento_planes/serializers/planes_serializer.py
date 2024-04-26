from rest_framework import serializers
from seguimiento_planes.models.planes_models import SeguimientoPGAR, ArmonizarPAIPGAR, LineasBasePGAR, ObjetivoDesarrolloSostenible, Planes, EjeEstractegico, Objetivo, Programa, Proyecto, Productos, Actividad, Entidad, Medicion, Tipo, Rubro, Indicador, Metas, TipoEje, Subprograma, MetasEjePGAR

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
    #nombre_tipo_indicador = serializers.CharField(source='get_tipo_indicador_display', default=None)
    #nombre_medida = serializers.CharField(source='get_medida_display', default=None)
    nombre_unidad_org = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    nombre_eje_estrategico = serializers.ReadOnlyField(source='id_eje_estrategico.nombre', default=None)
    nombre_meta = serializers.ReadOnlyField(source='id_meta_eje.nombre_meta_eje', default=None)
    nombre_linea_base = serializers.ReadOnlyField(source='id_linea_base.nombre_linea_base', default=None)
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
    nombre_objetivo = serializers.ReadOnlyField(source='id_objetivo.nombre_objetivo', default=None)
    nombre_plan = serializers.ReadOnlyField(source='id_objetivo.id_plan.nombre_plan', default=None)

    class Meta:
        model = Actividad
        fields = '__all__'

class IndicadoresPGARSerializer(serializers.ModelSerializer):
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    numero_actividad = serializers.ReadOnlyField(source='id_actividad.numero_actividad', default=None)
    #nombre_tipo_indicador = serializers.CharField(source='get_tipo_indicador_display', default=None)
    #nombre_medida = serializers.CharField(source='get_medida_display', default=None)
    nombre_unidad_org = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    nombre_eje_estrategico = serializers.ReadOnlyField(source='id_eje_estrategico.nombre', default=None)
    nombre_meta = serializers.ReadOnlyField(source='id_meta_eje.nombre_meta_eje', default=None)
    nombre_linea_base = serializers.ReadOnlyField(source='id_linea_base.nombre_linea_base', default=None)

    class Meta:
        model = Indicador
        fields = '__all__'

class ArmonizarPAIPGARSerializer(serializers.ModelSerializer):
    nombre_planPGAR = serializers.ReadOnlyField(source='id_planPGAR.nombre_plan', default=None)
    nombre_planPAI = serializers.ReadOnlyField(source='id_planPAI.nombre_plan', default=None)
    objetivoPGAR = serializers.SerializerMethodField()
    ejesEstrategicosPAI = serializers.SerializerMethodField()

    class Meta:
        model = ArmonizarPAIPGAR
        fields = '__all__'

    def get_objetivoPGAR(self, obj):
        #ObjetivoSerializer
        objetivos = Objetivo.objects.filter(id_plan=obj.id_planPGAR)
        serializer = ObjetivoSerializer(objetivos, many=True)
        return serializer.data
    
    def get_ejesEstrategicosPAI(self, obj):
        #EjeEstractegicoSerializer
        ejes_estractegicos = EjeEstractegico.objects.filter(id_plan=obj.id_planPAI)
        serializer = EjeEstractegicoSerializer(ejes_estractegicos, many=True)
        return serializer.data
    
class SeguiemientoPGARSerializer(serializers.ModelSerializer):
    #nombre_plan = serializers.ReadOnlyField(source='id_plan.nombre_plan', default=None)
    id_planPGAR = serializers.ReadOnlyField(source='id_armonizar.id_planPGAR.id_plan', default=None)
    id_planPAI = serializers.ReadOnlyField(source='id_armonizar.id_planPAI.id_plan', default=None)
    nombre_armonizacion = serializers.ReadOnlyField(source='id_armonizar.nombre_relacion', default=None)
    nombre_planPGAR = serializers.ReadOnlyField(source='id_armonizar.id_planPGAR.nombre_plan', default=None)
    nombre_planPAI = serializers.ReadOnlyField(source='id_armonizar.id_planPAI.nombre_plan', default=None)
    id_objetivo = serializers.ReadOnlyField(source='id_eje_estrategico.id_objetivo.id_objetivo', default=None)
    nombre_objetivo = serializers.ReadOnlyField(source='id_eje_estrategico.id_objetivo.nombre_objetivo', default=None)
    nombre_eje_estrategico = serializers.ReadOnlyField(source='id_eje_estrategico.nombre', default=None)
    nombre_meta = serializers.ReadOnlyField(source='id_meta_eje.nombre_meta_eje', default=None)
    id_eje_estrategicoPAI = serializers.ReadOnlyField(source='id_programa.id_eje_estrategico.id_eje_estrategico', default=None)
    nombre_eje_estrategicoPAI = serializers.ReadOnlyField(source='id_programa.id_eje_estrategico.nombre', default=None)
    id_actividadPGAR = serializers.ReadOnlyField(source='id_indicador.id_actividad.id_actividad', default=None)
    nombre_actividadPGAR = serializers.ReadOnlyField(source='id_indicador.id_actividad.nombre_actividad', default=None)
    nombre_linea_base = serializers.ReadOnlyField(source='id_linea_base.nombre_linea_base', default=None)
    nombre_actividad = serializers.ReadOnlyField(source='id_actividad.nombre_actividad', default=None)
    nombre_indicador = serializers.ReadOnlyField(source='id_indicador.nombre_indicador', default=None)
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre_proyecto', default=None)
    id_producto = serializers.ReadOnlyField(source='id_actividad.id_producto.id_producto', default=None)
    nombre_producto = serializers.ReadOnlyField(source='id_actividad.id_producto.nombre_producto', default=None)
    nombre_unidad_org = serializers.ReadOnlyField(source='id_unidad_organizacional.nombre', default=None)
    nombre_indicador_seg = serializers.ReadOnlyField(source='id_indicador_seg.nombre_indicador', default=None)
    objetivoPGAR = serializers.SerializerMethodField()
    ejesEstrategicosPAI = serializers.SerializerMethodField()
    #nombre_tipo_indicador = serializers.CharField(source='get_tipo_indicador_display', default=None)
    #nombre_medida = serializers.CharField(source='get_medida_display', default=None)

    class Meta:
        model = SeguimientoPGAR
        fields = '__all__'

    def get_objetivoPGAR(self, obj):
        #ObjetivoSerializer
        objetivos = Objetivo.objects.filter(id_plan=obj.id_armonizar.id_planPGAR)
        serializer = ObjetivoSerializer(objetivos, many=True)
        return serializer.data
    
    def get_ejesEstrategicosPAI(self, obj):
        #EjeEstractegicoSerializer
        ejes_estractegicos = EjeEstractegico.objects.filter(id_plan=obj.id_armonizar.id_planPAI)
        serializer = EjeEstractegicoSerializer(ejes_estractegicos, many=True)
        return serializer.data    
    

class TableroPGARByObjetivoSerializer(serializers.ModelSerializer):
    porcentajes = serializers.SerializerMethodField()

    class Meta:
        model = EjeEstractegico
        fields = '__all__'


    def get_porcentajes(self, obj):
        agno = self.context['agno']
        porcentajes = {
            "pvance_fisico": 0,
            "pavance_fisico_acomulado": 0,
            "pavance_financiero": 0,
            "pavance_recursos_obligados": 0
        }
        iterador = 0
        seguimientoPGAR = SeguimientoPGAR.objects.filter(id_eje_estrategico=obj.id_eje_estrategico, ano_PGAR=agno)
        for seguimiento in seguimientoPGAR:
            porcentajes['pvance_fisico'] = porcentajes['pvance_fisico'] + seguimiento.pavance_fisico
            porcentajes['pavance_fisico_acomulado'] = porcentajes['pavance_fisico_acomulado'] + seguimiento.pavance_fisico_acumulado
            porcentajes['pavance_financiero'] = porcentajes['pavance_financiero'] + seguimiento.pavance_financiero
            porcentajes['pavance_recursos_obligados'] = porcentajes['pavance_recursos_obligados'] + seguimiento.pavance_recurso_obligado
            iterador = iterador + 1
        if iterador == 0:
            return 0
        porcentajes['pvance_fisico'] = porcentajes['pvance_fisico'] / iterador
        porcentajes['pavance_fisico_acomulado'] = porcentajes['pavance_fisico_acomulado'] / iterador
        porcentajes['pavance_financiero'] = porcentajes['pavance_financiero'] / iterador
        porcentajes['pavance_recursos_obligados'] = porcentajes['pavance_recursos_obligados'] / iterador
        return porcentajes
    
class TableroPGARByEjeSerializer(serializers.ModelSerializer):
    porcentajes = serializers.SerializerMethodField()

    class Meta:
        model = EjeEstractegico
        fields = '__all__'


    def get_porcentajes(self, obj):
        agno_inicio = self.context['agno_inicio']
        agno_fin = self.context['agno_fin']
        agnos = []
        
        for agno in range(agno_inicio, agno_fin + 1):
            porcenjates_año = {
                "año": 0,
                "pvance_fisico": 0,
                "pavance_fisico_acomulado": 0,
                "pavance_financiero": 0,
                "pavance_recursos_obligados": 0
            }
            iterador = 0
            seguimientoPGAR = SeguimientoPGAR.objects.filter(id_eje_estrategico=obj.id_eje_estrategico, ano_PGAR=agno)
            for seguimiento in seguimientoPGAR:
                porcenjates_año['pvance_fisico'] = porcenjates_año['pvance_fisico'] + seguimiento.pavance_fisico
                porcenjates_año['pavance_fisico_acomulado'] = porcenjates_año['pavance_fisico_acomulado'] + seguimiento.pavance_fisico_acumulado
                porcenjates_año['pavance_financiero'] = porcenjates_año['pavance_financiero'] + seguimiento.pavance_financiero
                porcenjates_año['pavance_recursos_obligados'] = porcenjates_año['pavance_recursos_obligados'] + seguimiento.pavance_recurso_obligado
                iterador = iterador + 1
            if iterador != 0:
                porcenjates_año['pvance_fisico'] = porcenjates_año['pvance_fisico'] / iterador
                porcenjates_año['pavance_fisico_acomulado'] = porcenjates_año['pavance_fisico_acomulado'] / iterador
                porcenjates_año['pavance_financiero'] = porcenjates_año['pavance_financiero'] / iterador
                porcenjates_año['pavance_recursos_obligados'] = porcenjates_año['pavance_recursos_obligados'] / iterador
                porcenjates_año['año'] = agno - (agno_inicio - 1)
                agnos.append(porcenjates_año)
            else:
                porcenjates_año['pvance_fisico'] = 0
                porcenjates_año['pavance_fisico_acomulado'] = 0
                porcenjates_año['pavance_financiero'] = 0
                porcenjates_año['pavance_recursos_obligados'] = 0
                porcenjates_año['año'] = agno - (agno_inicio - 1)
                agnos.append(porcenjates_año)

        return agnos
    

class TableroPGARObjetivoEjeSerializer(serializers.ModelSerializer):
    porcentajes = serializers.SerializerMethodField()

    class Meta:
        model = EjeEstractegico
        fields = '__all__'


    def get_porcentajes(self, obj):
        agno_inicio = self.context['agno_inicio']
        agno_fin = self.context['agno_fin']
        agnos = []
        
        for agno in range(agno_inicio, agno_fin + 1):
            porcenjates_año = {
                "año": 0,
                "pvance_fisico": 0,
                "pavance_fisico_acomulado": 0,
                "pavance_financiero": 0,
                "pavance_recursos_obligados": 0
            }
            iterador = 0
            seguimientoPGAR = SeguimientoPGAR.objects.filter(id_eje_estrategico=obj.id_eje_estrategico, ano_PGAR=agno)
            for seguimiento in seguimientoPGAR:
                porcenjates_año['pvance_fisico'] = porcenjates_año['pvance_fisico'] + seguimiento.pavance_fisico
                porcenjates_año['pavance_fisico_acomulado'] = porcenjates_año['pavance_fisico_acomulado'] + seguimiento.pavance_fisico_acumulado
                porcenjates_año['pavance_financiero'] = porcenjates_año['pavance_financiero'] + seguimiento.pavance_financiero
                porcenjates_año['pavance_recursos_obligados'] = porcenjates_año['pavance_recursos_obligados'] + seguimiento.pavance_recurso_obligado
                iterador = iterador + 1
            if iterador != 0:
                porcenjates_año['pvance_fisico'] = porcenjates_año['pvance_fisico'] / iterador
                porcenjates_año['pavance_fisico_acomulado'] = porcenjates_año['pavance_fisico_acomulado'] / iterador
                porcenjates_año['pavance_financiero'] = porcenjates_año['pavance_financiero'] / iterador
                porcenjates_año['pavance_recursos_obligados'] = porcenjates_año['pavance_recursos_obligados'] / iterador
                porcenjates_año['año'] = agno - (agno_inicio - 1)
                agnos.append(porcenjates_año)

        return agnos
