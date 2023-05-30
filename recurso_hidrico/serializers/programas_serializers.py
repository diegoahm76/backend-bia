from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator

from recurso_hidrico.models.programas_models import ActividadesProyectos, AvancesProyecto, ProgramasPORH, ProyectosPORH

class RegistroProgramaPORHSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramasPORH
        fields = '__all__'

class GetProgramasporPORHSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProgramasPORH
        fields = ['nombre','fecha_inicio','fecha_fin']
        
class GetProyectosPORHSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProyectosPORH
        fields = ['id_programa','nombre','vigencia_inicial','vigencia_final']

class ActualizarProyectosSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProyectosPORH
        fields = ['nombre','vigencia_inicial','vigencia_final','inversion']
        
class GetActividadesporProyectosSerializers(serializers.ModelSerializer):
    class Meta:
        model = ActividadesProyectos
        fields = ['id_proyecto','nombre','fecha_registro']
        
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
        fields = '__all__'