from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator

from recurso_hidrico.models.programas_models import ActividadesProyectos, AvancesProyecto, EvidenciasAvance, ProgramasPORH, ProyectosPORH

class RegistroProgramaPORHSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramasPORH
        fields = '__all__'

class ProyectosPORHSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProyectosPORH
        fields = '__all__'

class ActividadesProyectosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActividadesProyectos
        fields = '__all__'


class GetProgramasporPORHSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProgramasPORH
        fields = ['id_programa','nombre','fecha_inicio','fecha_fin']
        
class GetProyectosPORHSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProyectosPORH
        fields = ['id_programa','nombre','vigencia_inicial','vigencia_final']

class ActualizarProyectosSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProyectosPORH
        #fields = ['nombre','vigencia_inicial','vigencia_final','inversion']
        fields = '__all__'
class GetActividadesporProyectosSerializers(serializers.ModelSerializer):
    class Meta:
        model = ActividadesProyectos
        #fields = ['id_proyecto','nombre','fecha_registro']
        fields = '__all__'
class BusquedaAvanzadaSerializers(serializers.ModelSerializer):
    
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre',default=None)
    fecha_inicio = serializers.ReadOnlyField(source='id_programa.fecha_inicio',default=None)
    fecha_fin = serializers.ReadOnlyField(source='id_programa.fecha_fin',default=None)
    nombre_PORH = serializers.ReadOnlyField(source='id_instrumento.nombre',default=None)
    fecha_inicio = serializers.ReadOnlyField(source='id_instrumento.fecha_inicio',default=None)
    fecha_fin = serializers.ReadOnlyField(source='id_instrumento.fecha_fin',default=None)
    
    class Meta:
        model = ProyectosPORH
        fields = '__all__'

class EliminarProyectoSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProyectosPORH
        fields = '__all__'

class ActualizarActividadesSerializers(serializers.ModelSerializer):
    class Meta:
        model = ActividadesProyectos
        fields = ['nombre']

class EliminarActividadesSerializers(serializers.ModelSerializer):
    class Meta:
        model = ActividadesProyectos
        fields = '__all__'
        
class RegistrarAvanceSerializers(serializers.ModelSerializer):
    class Meta:
        model: AvancesProyecto

class BusquedaAvanzadaAvancesSerializers(serializers.ModelSerializer):
    nombre_programa = serializers.ReadOnlyField(source='id_proyecto.id_programa.nombre', default=None)
    nombre_PORH = serializers.ReadOnlyField(source='id_proyecto.nombre', default=None)
    nombre = serializers.ReadOnlyField(source='id_proyecto.nombre', default=None)
    nombre_avance = serializers.ReadOnlyField(source='descripcion', default=None)  # Agregado: nombre del avance

    class Meta:
        model = AvancesProyecto
        fields = ['nombre_PORH', 'nombre_programa', 'nombre', 'nombre_avance', 'id_avance', 'id_proyecto', 'accion', 'id_persona_registra', 'fecha_registro']
        model= AvancesProyecto
        fields = '__all__'

class RegistroEvidenciaSerializers(serializers.ModelSerializer):
    class Meta:
        model = EvidenciasAvance
        fields = '__all__'
        
class ActualizarAvanceEvidenciaSerializers(serializers.ModelSerializer):
    class Meta:
        model = AvancesProyecto
        fields = ['accion','descripcion']

# class RegistrarAvanceSerializers(serializers.ModelSerializer):
#     class Meta:
#         model: AvancesProyecto
#         fields = ['fecha_reporte','accion','descripcion']
