from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.serializers.expedientes_serializers import ArchivosDigitalesSerializer
from recurso_hidrico.models.bibliotecas_models import Instrumentos
from recurso_hidrico.models.programas_models import ActividadesProyectos, AvancesProyecto, EvidenciasAvance, ProgramasPORH, ProyectosPORH

class RegistroProgramaPORHSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramasPORH
        fields = '__all__'

class ProyectosPORHSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProyectosPORH
        fields = '__all__'
class GenerardorMensajeProyectosPORHGetSerializer(serializers.ModelSerializer):
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre',default=None)
    id_programa=serializers.ReadOnlyField(source='id_programa.id_programa',default=None)
    nombre_porh = serializers.ReadOnlyField(source='id_programa.id_instrumento.nombre',default=None)
    id_porh=serializers.ReadOnlyField(source='id_programa.id_instrumento.id_instrumento',default=None)
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
        validators = [
            UniqueTogetherValidator(
                queryset=ProgramasPORH.objects.all(),
                fields= ['id_instrumento','nombre'],
                message='Ya existe un programa con este nombre.'
            )
        ]       
        

class ProgramasporPORHUpdateSerializers(serializers.ModelSerializer):
    id_instrumento=serializers.ReadOnlyField()
    class Meta:
        model = ProgramasPORH
        fields = ['id_instrumento','id_programa','nombre','fecha_inicio','fecha_fin']
        validators = [
            UniqueTogetherValidator(
                queryset=ProgramasPORH.objects.all(),
                fields= ['id_instrumento','nombre'],
                message='Ya existe un programa con este nombre.'
            )
        ]   
class GetProyectosPORHSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProyectosPORH
        fields = '__all__'

class ActualizarProyectosSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProyectosPORH
        fields = ['nombre','vigencia_inicial','vigencia_final','inversion']
        #fields = '__all__'
class GetActividadesporProyectosSerializers(serializers.ModelSerializer):
    class Meta:
        model = ActividadesProyectos
        #fields = ['id_proyecto','nombre','fecha_registro']
        fields = '__all__'

class GetAvancesporProyectosSerializers(serializers.ModelSerializer):
    evidencias = serializers.SerializerMethodField()
    class Meta:
        model = AvancesProyecto
        fields = ['id_avance','id_proyecto','fecha_reporte','accion','descripcion','id_persona_registra','fecha_registro','evidencias' ]
        #fields = '__all__'
        
    def get_evidencias(self, avance):
        evidencias = avance.evidenciasavance_set.all()
        return EvidenciaAvanceSerializer(evidencias, many=True).data

class BusquedaAvanzadaSerializers(serializers.ModelSerializer):
    
    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre',default=None)
    fecha_inicio = serializers.ReadOnlyField(source='id_programa.fecha_inicio',default=None)
    fecha_fin = serializers.ReadOnlyField(source='id_programa.fecha_fin',default=None)
    nombre_PORH = serializers.ReadOnlyField(source='id_programa.id_instrumento.nombre',default=None)
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
        model=AvancesProyecto
        fields='__all__'

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



###

class AvanceConEvidenciasSerializer(serializers.ModelSerializer):
    evidencias = serializers.SerializerMethodField()
    nombre_programa = serializers.ReadOnlyField(source='id_proyecto.id_programa.nombre', default=None)
    nombre_proyecto = serializers.ReadOnlyField(source='id_proyecto.nombre', default=None)
    nombre_PORH = serializers.ReadOnlyField(source='id_proyecto.id_programa.id_instrumento.nombre', default=None)
    class Meta:
        model = AvancesProyecto
        fields = ['nombre_PORH', 'nombre_programa', 'nombre_proyecto', 'descripcion', 'id_avance', 'id_proyecto', 'accion', 'id_persona_registra', 'fecha_registro','evidencias']


    def get_evidencias(self, avance):
        evidencias = avance.evidenciasavance_set.all()
        return EvidenciaAvanceSerializer(evidencias, many=True).data


class EvidenciaAvanceSerializer(serializers.ModelSerializer):
    ruta_archivo = serializers.SerializerMethodField()

    def get_ruta_archivo(self, obj):
        archivo = obj.id_archivo
        serializador = ArchivosDigitalesSerializer(archivo)
        ruta = serializador.data['ruta_archivo']
        return ruta
    class Meta:
        model = EvidenciasAvance
        fields = ('id_evidencia_avance', 'nombre_archivo','ruta_archivo')



# class GetAvanzadaProgramasporPORHSerializers(serializers.ModelSerializer):
#     nombre_PORH = serializers.ReadOnlyField(source='id_instrumento.nombre', default=None)
#     class Meta:
#         model = ProgramasPORH
#         fields = ['id_instrumento','id_programa','nombre','fecha_inicio','fecha_fin','nombre_PORH']

class GetAvanzadaProgramasporPORHSerializers(serializers.ModelSerializer):
    #nombre_PORH = serializers.ReadOnlyField(source='nombre', default=None)
    class Meta:
        model = Instrumentos
        fields = ('__all__')

