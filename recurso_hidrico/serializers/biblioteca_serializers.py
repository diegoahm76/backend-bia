from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno, AsignacionTramites
from gestion_documental.serializers.expedientes_serializers import ArchivosDigitalesSerializer
from recurso_hidrico.models.bibliotecas_models import AccionesCorrectivas, ArchivosInstrumento, CarteraAforos, Cuencas, CuencasInstrumento, DatosCarteraAforos, DatosRegistroLaboratorio, DatosSesionPruebaBombeo, Instrumentos, ParametrosLaboratorio, Pozos, PruebasBombeo, ResultadosLaboratorio, Secciones, SesionesPruebaBombeo,Subsecciones
from transversal.models.personas_models import Personas
from tramites.models.tramites_models import PermisosAmbSolicitudesTramite, SolicitudesTramites


class SeccionesSerializer(serializers.ModelSerializer):

    id_persona = serializers.IntegerField(source='id_persona_creada.id_persona', required=False, allow_null=True)
    nombre_completo = serializers.SerializerMethodField()
    nombre_comercial = serializers.CharField(source='id_persona_creada.nombre_comercial', required=False, allow_null=True)

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
    id_persona = serializers.IntegerField(source='id_persona_creada.id_persona', required=False, allow_null=True)
    nombre_comercial = serializers.CharField(source='id_persona_creada.nombre_comercial', required=False, allow_null=True)
    nombre_completo = serializers.SerializerMethodField()
    instrumentos_count = serializers.SerializerMethodField()

    class Meta:
        model = Subsecciones
        fields = ['id_subseccion', 'id_seccion', 'nombre', 'descripcion', 'fechaCreacion', 'id_persona','instrumentos_count',
                   'nombre_comercial','nombre_completo']
        
    def get_nombre_completo(self, obj):
        primer_nombre = obj.id_persona_creada.primer_nombre
        primer_apellido = obj.id_persona_creada.primer_apellido
        return f'{primer_nombre} {primer_apellido}'
    
    def get_instrumentos_count(self, obj):
        return obj.instrumentos.count()

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
        #fields = ['id_instrumento', 'nombre', 'id_seccion', 'id_subseccion', 'id_resolucion', 'id_persona_registra', 'fecha_registro', 'fecha_creacion_instrumento', 'fecha_fin_vigencia']
        fields = '__all__'

class SubseccionContarInstrumentosSerializer(serializers.ModelSerializer):
    instrumentos_count = serializers.SerializerMethodField()

    def get_instrumentos_count(self, obj):
        return obj.instrumentos.count()

    class Meta:
        model = Subsecciones
        fields = ['id_subseccion', 'id_seccion', 'nombre', 'descripcion', 'fechaCreacion', 'id_persona_creada', 'instrumentos_count']




class InstrumentoCuencasGetSerializer(serializers.ModelSerializer):
    id_instrumento=serializers.IntegerField(source='id_instrumento.id_instrumento', required=False, allow_null=True)
    instrumento = serializers.CharField(source='id_instrumento.nombre', required=False, allow_null=True)
    id_cuenca=serializers.IntegerField(source='id_cuenca.id_cuenca', required=False, allow_null=True)
    cuenca = serializers.CharField(source='id_cuenca.nombre', required=False, allow_null=True)
    class Meta:
        model=CuencasInstrumento
        fields=['id_instrumento','instrumento','id_cuenca','cuenca']


class CuencasGetSerializer(serializers.ModelSerializer):
    id_instrumento=serializers.IntegerField(source='id_instrumento.id_instrumento', required=False, allow_null=True)
    
    id_cuenca=serializers.IntegerField(source='id_cuenca.id_cuenca', required=False, allow_null=True)
    cuenca = serializers.CharField(source='id_cuenca.nombre', required=False, allow_null=True)
    class Meta:
        model=CuencasInstrumento
        fields=['id_instrumento','id_cuenca','cuenca']

class CuencasGetByInstrumentoSerializer(serializers.ModelSerializer):
    id_instrumento=serializers.IntegerField(source='id_instrumento.id_instrumento')
    
    id_cuenca=serializers.IntegerField(source='id_cuenca.id_cuenca', required=False, allow_null=True)
    cuenca = serializers.CharField(source='id_cuenca.nombre', required=False, allow_null=True)
    class Meta:
        model=CuencasInstrumento
        fields=['id_instrumento','id_cuenca','cuenca']



class ArchivosInstrumentoBusquedaAvanzadaSerializer(serializers.ModelSerializer):
    nombre_instrumento=serializers.CharField(source='id_instrumento.nombre', required=False, allow_null=True)
    id_seccion=serializers.IntegerField(source='id_instrumento.id_seccion.id_seccion', required=False, allow_null=True)
    nombre_seccion=serializers.CharField(source='id_instrumento.id_seccion.nombre', required=False, allow_null=True)
    id_subseccion=serializers.IntegerField(source='id_instrumento.id_subseccion.id_subseccion', required=False, allow_null=True)
    nombre_subseccion=serializers.CharField(source='id_instrumento.id_subseccion.nombre', required=False, allow_null=True)
    class Meta:
        model=ArchivosInstrumento
        fields=['id_seccion','nombre_seccion','id_subseccion','nombre_subseccion','id_archivo_instrumento','id_instrumento','nombre_instrumento','nombre_archivo','ruta_archivo']


class ArchivosInstrumentosGetSerializer(serializers.ModelSerializer):
        
    ruta_archivo = serializers.SerializerMethodField()
    class Meta:
        model=ArchivosInstrumento
        fields='__all__'
    def get_ruta_archivo(self, obj):
        
        data_serializador = ArchivosDigitalesSerializer(obj.ruta_archivo).data
        return data_serializador['ruta_archivo']

#Configuraciones basicas

class CuencasPostSerializer(serializers.ModelSerializer):
        class Meta:
            model=Cuencas
            fields='__all__'



class CuencasGetSerializer(serializers.ModelSerializer):
        class Meta:
            model=Cuencas
            fields='__all__'

class CuencasUpdateSerializer(serializers.ModelSerializer):
        
        item_ya_usado = serializers.ReadOnlyField()
        class Meta:
       
            model=Cuencas
            fields='__all__'
        def update(self, instance, validated_data):
            validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
            return super().update(instance, validated_data)
        

class PozosPostSerializer(serializers.ModelSerializer):
        class Meta:
            model=Pozos
            fields='__all__'

class PozosUpdateSerializer(serializers.ModelSerializer):
        
        item_ya_usado = serializers.ReadOnlyField()
        registro_precargado=serializers.ReadOnlyField()
        class Meta:
       
            model=Pozos
            fields='__all__'
        def update(self, instance, validated_data):
            validated_data.pop('item_ya_usado', None)  # Excluir el campo específico
            return super().update(instance, validated_data)


class PozosGetSerializer(serializers.ModelSerializer):
        class Meta:
            model=Pozos
            fields='__all__'


class ParametrosLaboratorioPostSerializer(serializers.ModelSerializer):
        class Meta:
            model=ParametrosLaboratorio
            fields='__all__'



class ParametrosLaboratorioUpdateSerializer(serializers.ModelSerializer):
        item_ya_usado = serializers.ReadOnlyField()
        registro_precargado=serializers.ReadOnlyField()
        
        class Meta:
       
            model=ParametrosLaboratorio
            fields='__all__'


class ParametrosLaboratorioGetSerializer(serializers.ModelSerializer):
        class Meta:
            model=ParametrosLaboratorio
            fields='__all__'


#Instrumentos

class InstrumentosPostSerializer(serializers.ModelSerializer):
        fecha_registro = serializers.ReadOnlyField()
        class Meta:
            model=Instrumentos
            fields='__all__'
            validators = [
                UniqueTogetherValidator(
                queryset=Instrumentos.objects.all(),
                fields= ['id_subseccion','nombre'],
                message='Ya existe un instrumento con este nombre.'
                )
                ]   
            

class InstrumentosUpdateSerializer(serializers.ModelSerializer):
        fecha_registro = serializers.ReadOnlyField()
        id_seccion=serializers.ReadOnlyField()
        id_subseccion=serializers.ReadOnlyField()
        id_persona_registra=serializers.ReadOnlyField()
        fecha_registro=serializers.ReadOnlyField()
        nombre=serializers.ReadOnlyField()
        id_resolucion=serializers.ReadOnlyField()
        fecha_creacion_instrumento=serializers.ReadOnlyField()
        cod_tipo_agua=serializers.ReadOnlyField()
        class Meta:
            model=Instrumentos
            fields='__all__'
            validators = [
                UniqueTogetherValidator(
                queryset=Instrumentos.objects.all(),
                fields= ['id_subseccion','nombre'],
                message='Ya existe un instrumento con este nombre.'
                )
                ]   
            

class InstrumentoBusquedaAvanzadaSerializer(serializers.ModelSerializer):
   
    id_seccion=serializers.IntegerField(source='id_seccion.id_seccion')
    nombre_seccion=serializers.CharField(source='id_seccion.nombre')
    id_subseccion=serializers.IntegerField(source='id_subseccion.id_subseccion')
    nombre_subseccion=serializers.CharField(source='id_subseccion.nombre')
    class Meta:
        model=Instrumentos
        fields = ('__all__')
        #fields=['id_instrumento ','nombre ','id_seccion ','id_subseccion ','id_resolucion ','id_persona_registra ','fecha_registro ','fecha_creacion_instrumento ','fecha_fin_vigencia ','id_pozo ','cod_tipo_agua ','id_seccion','nombre_seccion','id_subseccion','nombre_subseccion']

class InstrumentosDeleteSerializer(serializers.ModelSerializer):
        #fecha_registro = serializers.ReadOnlyField()
        class Meta:
            model=Instrumentos
            fields='__all__'
 

class CuencasInstrumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuencasInstrumento
        fields = '__all__'
        validators = [
                UniqueTogetherValidator(
                queryset=CuencasInstrumento.objects.all(),
                fields= ['id_instrumento','id_cuenca'],
                message='Ya existe un instrumento con este nombre.'
                )
                ] 

class CuencasInstrumentoDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuencasInstrumento
        fields = '__all__'


class ArchivosInstrumentoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=ArchivosInstrumento
        fields=('__all__')
        validators = [
                UniqueTogetherValidator(
                queryset=ArchivosInstrumento.objects.all(),
                fields= ['id_instrumento','nombre_archivo'],
                message='Ya existe un archivo  con este nombre.'
                )
                ] 

class ArchivosInstrumentoUpdateSerializer(serializers.ModelSerializer):
    id_instrumento=serializers.ReadOnlyField()
    class Meta:
        model=ArchivosInstrumento
        fields = ['id_instrumento','nombre_archivo']
        validators = [
                UniqueTogetherValidator(
                queryset=ArchivosInstrumento.objects.all(),
                fields= ['id_instrumento','nombre_archivo'],
                message='Ya existe un archivo  con este nombre.'
                )
                ] 

class SubseccionBusquedaAvanzadaSerializer(serializers.ModelSerializer):
   
    id_seccion=serializers.IntegerField(source='id_seccion.id_seccion')
    nombre_seccion=serializers.CharField(source='id_seccion.nombre')

    class Meta:
        model=Subsecciones
        fields=['id_seccion','nombre_seccion','id_subseccion','nombre']


##
class CarteraAforosPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=CarteraAforos
        fields=('__all__')


class CarteraAforosUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=CarteraAforos
        fields=('__all__')

class CarteraAforosGetSerializer(serializers.ModelSerializer):
    #cod_clase=serializers.CharField(source='id_parametro.cod_tipo_parametro')
    nombre_cuenca=serializers.CharField(source='id_cuenca.nombre', required=False, allow_null=True)
    class Meta:
        model=CarteraAforos
        fields=['id_cartera_aforos','id_instrumento','id_cuenca','fecha_registro','ubicacion_aforo','descripcion','latitud','longitud','fecha_aforo','cod_tipo_aforo','numero_serie','molinete','numero_helice','nombre_cuenca']



class CarteraAforosDeleteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CarteraAforos
        fields=('__all__')

##Datos carteras de aforo

##

class DatosCarteraAforosPostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=DatosCarteraAforos        
        fields=('__all__')
class DatosCarteraAforosGetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=DatosCarteraAforos        
        fields=('__all__')

class DatosCarteraAforosUpdateSerializer(serializers.ModelSerializer):
    id_cartera_aforos = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=DatosCarteraAforos
        fields=('__all__')

class DatosCarteraAforosDeleteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=DatosCarteraAforos
        fields=('__all__')

#Resultados de laboratorio

class ResultadosLaboratorioPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=ResultadosLaboratorio
        fields=('__all__')

class ResultadosLaboratorioGetSerializer(serializers.ModelSerializer):
    #cod_clase=serializers.CharField(source='id_parametro.cod_tipo_parametro')
    nombre_cuenca=serializers.CharField(source='id_cuenca.nombre', required=False, allow_null=True)
    nombre_pozo=serializers.CharField(source='id_pozo.nombre', required=False, allow_null=True)
    class Meta:
        model=ResultadosLaboratorio
        fields=('__all__')
class ResultadosLaboratorioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=ResultadosLaboratorio
        fields=('__all__')

class ResultadosLaboratorioDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model=ResultadosLaboratorio
        fields=('__all__')


#Datos_Registro_laboratorio
class DatosRegistroLaboratorioPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=DatosRegistroLaboratorio
        fields=('__all__')


class DatosRegistroLaboratorioDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model=DatosRegistroLaboratorio
        fields=('__all__')

class DatosRegistroLaboratorioUpdateSerializer(serializers.ModelSerializer):
    id_dato_registro_laboratorio =serializers.ReadOnlyField()
    #id_registro_laboratorio =serializers.ReadOnlyField()
    class Meta:
        model=DatosRegistroLaboratorio
        fields=['id_dato_registro_laboratorio','id_parametro','metodo','resultado','fecha_analisis']
        #fields=('__all__')


class DatosRegistroLaboratorioGetSerializer(serializers.ModelSerializer):
        
        cod_clase=serializers.CharField(source='id_parametro.cod_tipo_parametro', required=False, allow_null=True)
        parametro=serializers.CharField(source='id_parametro.nombre', required=False, allow_null=True)
        unidad=serializers.CharField(source='id_parametro.unidad_de_medida', required=False, allow_null=True)
        class Meta:
            model=DatosRegistroLaboratorio
            fields = [
            'cod_clase',
            'parametro',
            'unidad',
            'id_dato_registro_laboratorio',
            'id_registro_laboratorio',
            'id_parametro',
            'metodo',
            'resultado',
            'fecha_analisis',
        ]
            
#PRUEBAS DE BOMBEO

class PruebasBombeoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=PruebasBombeo
        fields=('__all__')

class PruebasBombeoGetSerializer(serializers.ModelSerializer):
    nombre_pozo=serializers.CharField(source='id_pozo.nombre', required=False, allow_null=True)
    class Meta:
        model=PruebasBombeo
        fields=['id_prueba_bombeo','id_instrumento','id_pozo','nombre_pozo','descripcion','fecha_registro','fecha_prueba_bombeo','latitud','longitud','ubicacion_prueba']
class PruebasBombeoDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model=PruebasBombeo
        fields=('__all__')

class PruebasBombeoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=PruebasBombeo
        fields=('__all__')
##SECCIONES PRUEBA DE BOMBEO

class SesionesPruebaBombeoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=SesionesPruebaBombeo
        fields=('__all__')

class SesionesPruebaBombeoPutSerializer(serializers.ModelSerializer):
    class Meta:
        model=SesionesPruebaBombeo
        fields=('__all__')
class SesionesPruebaBombeoDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model=SesionesPruebaBombeo
        fields=('__all__')

class SesionesPruebaBombeoGetSerializer(serializers.ModelSerializer):
    datos = serializers.SerializerMethodField()
    hora_inicio = serializers.SerializerMethodField()
    class Meta:
        model=SesionesPruebaBombeo
        fields=[ 'id_sesion_prueba_bombeo',
                'id_prueba_bombeo',
                'consecutivo_sesion',
                'fecha_inicio',
                'cod_tipo_sesion','hora_inicio',
                'datos']


    def get_hora_inicio(self, sesion_prueba_bombeo):
        if sesion_prueba_bombeo.fecha_inicio:
            hora_inicio = sesion_prueba_bombeo.fecha_inicio.strftime('%H:%M:%S')
            return hora_inicio
        return None
    def get_datos(self, avance):
        datos = avance.datossesionpruebabombeo_set.all().order_by('hora')
        return DatosSesionPruebaBombeoGetSerializer(datos, many=True).data
#DATOS SECCION PRUEBAS BOMBEO

class DatosSesionPruebaBombeoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=DatosSesionPruebaBombeo
        fields=('__all__')

class DatosSesionPruebaBombeoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model=DatosSesionPruebaBombeo
        fields=('__all__')

class DatosSesionPruebaBombeoPutSerializer(serializers.ModelSerializer):
    class Meta:
        model=DatosSesionPruebaBombeo
        fields=('__all__')


class DatosSesionPruebaBombeoDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model=DatosSesionPruebaBombeo
        fields=('__all__')


class DatosSesionPruebaBombeoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model=DatosSesionPruebaBombeo
        fields=('__all__')

class AccionesCorrectivasSerializer(serializers.ModelSerializer):
    nombre_tramite = serializers.ReadOnlyField(source ='id_tramite.nombre_proyecto', default=None)
    tipo_tramite = serializers.SerializerMethodField()
    class Meta:
        model=AccionesCorrectivas
        fields=('__all__')

    def get_tipo_tramite(self, obj):
        permisosAmbSolicitudesTramite = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=obj.id_tramite).first()
        return permisosAmbSolicitudesTramite.id_permiso_ambiental.get_cod_tipo_permiso_ambiental_display()
    
class TramiteSerializer(serializers.ModelSerializer):
    numero_auto_inicio = serializers.ReadOnlyField(source='id_auto_inicio.numero_acto_administrativo', default=None)
    numero_expediente = serializers.SerializerMethodField()
    tipo_tramite = serializers.SerializerMethodField() 
    numero_documento = serializers.ReadOnlyField(source='id_persona_titular.numero_documento', default=None)
    radicado = serializers.SerializerMethodField()
    nombre_solicitante = serializers.SerializerMethodField()
    grupo_funcional = serializers.SerializerMethodField()

    class Meta:
        model=SolicitudesTramites
        fields=('__all__')

    def get_nombre_solicitante(self, obj):
        if obj.id_persona_titular.tipo_persona == 'N':
            return f'{obj.id_persona_titular.primer_nombre} {obj.id_persona_titular.segundo_nombre} {obj.id_persona_titular.primer_apellido} {obj.id_persona_titular.segundo_apellido}'
        else:
            return obj.id_persona_titular.razon_social
        
    def get_radicado(self, obj):
        cadena = ""
        radicado = obj
        if radicado.id_radicado:
            agno_radicado = radicado.fecha_radicado.year
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=agno_radicado ,cod_tipo_radicado=radicado.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(radicado.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
            return cadena
        else: 
            return 'SIN RADICAR'
        
    def get_grupo_funcional(self, obj):
        asignacion = AsignacionTramites.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite).first()
        if asignacion:  
            if asignacion.id_und_org_seccion_asignada:
                return asignacion.id_und_org_seccion_asignada.nombre
            elif asignacion.id_und_org_oficina_asignada:
                return asignacion.id_und_org_oficina_asignada.nombre
        else:
            return "Sin asignar"
        
    def get_tipo_tramite(self, obj):
        permisosAmbSolicitudesTramite = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=obj.id_solicitud_tramite).first()
        if permisosAmbSolicitudesTramite:
            return permisosAmbSolicitudesTramite.id_permiso_ambiental.get_cod_tipo_permiso_ambiental_display()
        else:
            return "Sin tipo de trámite"
    
    def get_numero_expediente(self, obj):
        if obj.id_expediente:
            return f'{obj.id_expediente.codigo_exp_und_serie_subserie}-{obj.id_expediente.codigo_exp_Agno}-{obj.id_expediente.codigo_exp_consec_por_agno}'
        else:
            return "Sin expediente"
    
