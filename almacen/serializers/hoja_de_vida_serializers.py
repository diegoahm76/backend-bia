from almacen.models.generics_models import UnidadesMedida
from almacen.models.vehiculos_models import VehiculosArrendados
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


class CatalogoBienesGetVehSerializer(serializers.ModelSerializer):
    marca=serializers.ReadOnlyField(source='id_marca.nombre',default=None)
    nombre_padre=serializers.ReadOnlyField(source='id_bien_padre.nombre',default=None)
    unidad_medida=serializers.ReadOnlyField(source='id_unidad_medida.abreviatura',default=None)
    unidad_medida_vida_util=serializers.ReadOnlyField(source='id_unidad_medida_vida_util.abreviatura',default=None)
    porcentaje_iva=serializers.ReadOnlyField(source='id_porcentaje_iva.porcentaje',default=None)
    tipo_bien = serializers.CharField(source='get_cod_tipo_bien_display',read_only=True,default=None)
    placa=serializers.ReadOnlyField(source='doc_identificador_nro',default=None)
    id_vehiculo_arrendado = serializers.SerializerMethodField()
    empresa_contratista = serializers.SerializerMethodField()

    def get_id_vehiculo_arrendado(self, obj):
        return None

    def get_empresa_contratista(self, obj):
        return None

    class Meta:
        model= CatalogoBienes
        fields='__all__'

class VehiculosArrendadosSerializer(serializers.ModelSerializer):
    id_bien = serializers.SerializerMethodField()
    id_bien_padre = serializers.SerializerMethodField()
    marca=serializers.ReadOnlyField(source='id_marca.nombre', default=None)
    tiene_hoja_vida=serializers.ReadOnlyField(source='tiene_hoja_de_vida', default=None)
    codigo_bien = serializers.SerializerMethodField()
    nro_elemento_bien = serializers.SerializerMethodField()
    nombre_padre=serializers.SerializerMethodField()
    id_unidad_medida=serializers.SerializerMethodField()
    unidad_medida=serializers.SerializerMethodField()
    id_unidad_medida_vida_util=serializers.SerializerMethodField()
    unidad_medida_vida_util=serializers.SerializerMethodField()
    id_porcentaje_iva=serializers.SerializerMethodField()
    porcentaje_iva=serializers.SerializerMethodField()
    cod_tipo_bien = serializers.SerializerMethodField()
    cod_tipo_activo = serializers.SerializerMethodField()
    tipo_bien = serializers.SerializerMethodField()
    nivel_jerarquico = serializers.SerializerMethodField()
    nombre_cientifico = serializers.SerializerMethodField()
    doc_identificador_nro = serializers.SerializerMethodField()
    cod_metodo_valoracion = serializers.SerializerMethodField()
    cod_tipo_depreciacion = serializers.SerializerMethodField()
    cantidad_vida_util = serializers.SerializerMethodField()
    valor_residual = serializers.SerializerMethodField()
    stock_minimo = serializers.SerializerMethodField()
    stock_maximo = serializers.SerializerMethodField()
    solicitable_vivero = serializers.SerializerMethodField()
    maneja_hoja_vida = serializers.SerializerMethodField()
    visible_solicitudes = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    es_semilla_vivero = serializers.SerializerMethodField()
    cod_tipo_elemento_vivero = serializers.SerializerMethodField()

    def get_id_bien(self, obj):
        return None

    def get_id_bien_padre(self, obj):
        return None

    def get_codigo_bien(self, obj):
        return None

    def get_nro_elemento_bien(self, obj):
        return None

    def get_nombre_padre(self, obj):
        return None

    def get_id_unidad_medida(self, obj):
        return None

    def get_unidad_medida(self, obj):
        return None

    def get_id_unidad_medida_vida_util(self, obj):
        return None

    def get_unidad_medida_vida_util(self, obj):
        return None

    def get_id_porcentaje_iva(self, obj):
        return None

    def get_porcentaje_iva(self, obj):
        return None

    def get_cod_tipo_bien(self, obj):
        return 'A'

    def get_nivel_jerarquico(self, obj):
        return None

    def get_nombre_cientifico(self, obj):
        return None

    def get_cod_tipo_activo(self, obj):
        return 'Veh'

    def get_tipo_bien(self, obj):
        return 'Activo Fijo'

    def get_doc_identificador_nro(self, obj):
        return obj.placa

    def get_cod_metodo_valoracion(self, obj):
        return None

    def get_cod_tipo_depreciacion(self, obj):
        return None

    def get_cantidad_vida_util(self, obj):
        return None

    def get_valor_residual(self, obj):
        return None

    def get_stock_minimo(self, obj):
        return None

    def get_stock_maximo(self, obj):
        return None

    def get_solicitable_vivero(self, obj):
        return None

    def get_maneja_hoja_vida(self, obj):
        return True

    def get_visible_solicitudes(self, obj):
        return False

    def get_estado(self, obj):
        return None

    def get_es_semilla_vivero(self, obj):
        return None

    def get_cod_tipo_elemento_vivero(self, obj):
        return None

    class Meta:
        model= VehiculosArrendados
        exclude=('tiene_hoja_de_vida',)