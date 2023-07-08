from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator

from recurso_hidrico.models.bibliotecas_models import ArchivosInstrumento, Cuencas, CuencasInstrumento, Instrumentos, Secciones,Subsecciones
from seguridad.models import Personas


class SeccionesSerializer(serializers.ModelSerializer):

    id_persona = serializers.IntegerField(source='id_persona_creada.id_persona')
    nombre_completo = serializers.SerializerMethodField()
    nombre_comercial = serializers.CharField(source='id_persona_creada.nombre_comercial')

    class Meta:
        model = Secciones
        fields = ['id_seccion', 'nombre', 'descripcion', 'fecha_creacion', 'id_persona_creada',
                  'id_persona','nombre_completo','nombre_comercial']
    def get_nombre_completo(self, obj):
        primer_nombre = obj.id_persona_creada.primer_nombre
        primer_apellido = obj.id_persona_creada.primer_apellido
        return f'{primer_nombre} {primer_apellido}'
    
class GetSeccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secciones
        fields = '__all__'

class RegistrarSeccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secciones
        fields = '__all__'
class RegistrarSubSeccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subsecciones
        fields = '__all__'

# class GetSubseccionesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subsecciones
#         fields = '__all__'

class GetSubseccionesSerializer(serializers.ModelSerializer):
    id_persona = serializers.IntegerField(source='id_persona_creada.id_persona')
    nombre_comercial = serializers.CharField(source='id_persona_creada.nombre_comercial')
    nombre_completo = serializers.SerializerMethodField()
    class Meta:
        model = Subsecciones
        fields = ['id_subseccion', 'id_seccion', 'nombre', 'descripcion', 'fechaCreacion', 'id_persona',
                   'nombre_comercial','nombre_completo']
        
    def get_nombre_completo(self, obj):
        primer_nombre = obj.id_persona_creada.primer_nombre
        primer_apellido = obj.id_persona_creada.primer_apellido
        return f'{primer_nombre} {primer_apellido}'

class ActualizarSubseccionesSerializer(serializers.ModelSerializer):
    id_seccion = serializers.PrimaryKeyRelatedField(read_only=True)
    id_persona_creada = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Subsecciones
        fields = '__all__'

class ActualizarSeccionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secciones
        read_only_fields = ['registroPrecargado', 'id_persona_creada']
        fields = '__all__'

class SubseccionSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    class Meta:
        model = Subsecciones
        fields = ['id_subseccion', 'nombre', 'descripcion', 'fechaCreacion', 'id_persona_creada','nombre_completo']
    def get_nombre_completo(self, obj):
        primer_nombre = obj.id_persona_creada.primer_nombre
        primer_apellido = obj.id_persona_creada.primer_apellido
        return f'{primer_nombre} {primer_apellido}'

class SeccionSerializer(serializers.ModelSerializer):
    #subsecciones = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    class Meta:
        model = Secciones
        fields = ['id_seccion', 'nombre', 'descripcion', 'fecha_creacion', 'id_persona_creada','nombre_completo']

    # def get_subsecciones(self, subseccion):
    #     subsecciones = subseccion.subsecciones_set.all()
    #     return SubseccionSerializer(subsecciones, many=True).data
    
    def get_nombre_completo(self, obj):
        primer_nombre = obj.id_persona_creada.primer_nombre
        primer_apellido = obj.id_persona_creada.primer_apellido
        return f'{primer_nombre} {primer_apellido}'
    
class EliminarSubseccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subsecciones
        fields = '__all__'


class EliminarSeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secciones
        fields = '__all__'


#CONSULTA-BIBLIOTECA
class InstrumentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrumentos
        fields = ['id_instrumento', 'nombre', 'id_seccion', 'id_subseccion', 'id_resolucion', 'id_persona_registra', 'fecha_registro', 'fecha_creacion_instrumento', 'fecha_fin_vigencia']


class SubseccionContarInstrumentosSerializer(serializers.ModelSerializer):
    instrumentos_count = serializers.SerializerMethodField()

    def get_instrumentos_count(self, obj):
        return obj.instrumentos.count()

    class Meta:
        model = Subsecciones
        fields = ['id_subseccion', 'id_seccion', 'nombre', 'descripcion', 'fechaCreacion', 'id_persona_creada', 'instrumentos_count']




class InstrumentoCuencasGetSerializer(serializers.ModelSerializer):
    id_instrumento=serializers.IntegerField(source='id_instrumento.id_instrumento')
    instrumento = serializers.CharField(source='id_instrumento.nombre')
    id_cuenca=serializers.IntegerField(source='id_cuenca.id_cuenca')
    cuenca = serializers.CharField(source='id_cuenca.nombre')
    class Meta:
        model=CuencasInstrumento
        fields=['id_instrumento','instrumento','id_cuenca','cuenca']


class CuencasGetSerializer(serializers.ModelSerializer):
    id_instrumento=serializers.IntegerField(source='id_instrumento.id_instrumento')
    
    id_cuenca=serializers.IntegerField(source='id_cuenca.id_cuenca')
    cuenca = serializers.CharField(source='id_cuenca.nombre')
    class Meta:
        model=CuencasInstrumento
        fields=['id_instrumento','id_cuenca','cuenca']



class ArchivosInstrumentoBusquedaAvanzadaSerializer(serializers.ModelSerializer):
    nombre_instrumento=serializers.CharField(source='id_instrumento.nombre')
    id_seccion=serializers.IntegerField(source='id_instrumento.id_seccion.id_seccion')
    nombre_seccion=serializers.CharField(source='id_instrumento.id_seccion.nombre')
    id_subseccion=serializers.IntegerField(source='id_instrumento.id_subseccion.id_subseccion')
    nombre_subseccion=serializers.CharField(source='id_instrumento.id_subseccion.nombre')
    class Meta:
        model=ArchivosInstrumento
        fields=['id_seccion','nombre_seccion','id_subseccion','nombre_subseccion','id_archivo_instrumento','id_instrumento','nombre_instrumento','nombre_archivo','ruta_archivo']