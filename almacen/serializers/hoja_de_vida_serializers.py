from almacen.models.generics_models import UnidadesMedida
from transversal.serializers.personas_serializers import PersonasSerializer
from almacen.models.generics_models import Magnitudes
from rest_framework import serializers
from almacen.models.bienes_models import CatalogoBienes
from almacen.models.hoja_de_vida_models import HojaDeVidaComputadores, HojaDeVidaOtrosActivos, HojaDeVidaVehiculos, DocumentosVehiculo
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class SerializersHojaDeVidaComputadores(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_articulo.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_articulo.nombre',default=None)
    doc_identificador_nro=serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro',default=None)
    id_marca=serializers.ReadOnlyField(source='id_articulo.id_marca.id_marca',default=None)
    marca=serializers.ReadOnlyField(source='id_articulo.id_marca.nombre',default=None)
    
    class Meta:
        model=HojaDeVidaComputadores
        fields=('__all__')

class SerializersHojaDeVidaComputadoresGet(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_articulo.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_articulo.nombre',default=None)
    doc_identificador_nro=serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro',default=None)
    id_marca=serializers.ReadOnlyField(source='id_articulo.id_marca.id_marca',default=None)
    marca=serializers.ReadOnlyField(source='id_articulo.id_marca.nombre',default=None)
    ruta_imagen_foto=serializers.ReadOnlyField(source='ruta_imagen_foto.ruta_archivo.url', default=None)
    
    class Meta:
        model=HojaDeVidaComputadores
        fields=('__all__')
        
class SerializersPutHojaDeVidaComputadores(serializers.ModelSerializer):
    class Meta:
        model=HojaDeVidaComputadores
        exclude=('id_articulo',)
        
class SerializersPutHojaDeVidaVehiculos(serializers.ModelSerializer):
    class Meta:
        model=HojaDeVidaVehiculos
        exclude=('id_articulo',)
        
class SerializersPutHojaDeVidaOtrosActivos(serializers.ModelSerializer):
    class Meta:
        model=HojaDeVidaOtrosActivos
        exclude=('id_articulo',)
        
class SerializersHojaDeVidaVehiculos(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_articulo.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_articulo.nombre',default=None)
    doc_identificador_nro=serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro',default=None)
    id_marca=serializers.ReadOnlyField(source='id_articulo.id_marca.id_marca',default=None)
    marca=serializers.ReadOnlyField(source='id_articulo.id_marca.nombre',default=None)
    
    class Meta:
        model=HojaDeVidaVehiculos
        fields='__all__'
        
class SerializersHojaDeVidaVehiculosGet(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_articulo.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_articulo.nombre',default=None)
    doc_identificador_nro=serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro',default=None)
    id_marca=serializers.ReadOnlyField(source='id_articulo.id_marca.id_marca',default=None)
    marca=serializers.ReadOnlyField(source='id_articulo.id_marca.nombre',default=None)
    ruta_imagen_foto=serializers.ReadOnlyField(source='ruta_imagen_foto.ruta_archivo.url', default=None)
    
    class Meta:
        model=HojaDeVidaVehiculos
        fields='__all__'

class SerializersHojaDeVidaOtrosActivos(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_articulo.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_articulo.nombre',default=None)
    doc_identificador_nro=serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro',default=None)
    id_marca=serializers.ReadOnlyField(source='id_articulo.id_marca.id_marca',default=None)
    marca=serializers.ReadOnlyField(source='id_articulo.id_marca.nombre',default=None)
    
    class Meta:
        model=HojaDeVidaOtrosActivos
        fields=('__all__')

class SerializersHojaDeVidaOtrosActivosGet(serializers.ModelSerializer):
    codigo_bien=serializers.ReadOnlyField(source='id_articulo.codigo_bien',default=None)
    nombre=serializers.ReadOnlyField(source='id_articulo.nombre',default=None)
    doc_identificador_nro=serializers.ReadOnlyField(source='id_articulo.doc_identificador_nro',default=None)
    id_marca=serializers.ReadOnlyField(source='id_articulo.id_marca.id_marca',default=None)
    marca=serializers.ReadOnlyField(source='id_articulo.id_marca.nombre',default=None)
    ruta_imagen_foto=serializers.ReadOnlyField(source='ruta_imagen_foto.ruta_archivo.url', default=None)
    
    class Meta:
        model=HojaDeVidaOtrosActivos
        fields=('__all__')