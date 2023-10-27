import secrets
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max, F
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.depositos_models import CarpetaCaja 
from gestion_documental.models.expedientes_models import ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TablaRetencionDocumental, TipologiasDoc
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from datetime import datetime
from django.conf import settings
import os
import operator, itertools
import json


######################### SERIALIZERS EXPEDIENTE #########################

class SerieSubserieUnidadTRDGetSerializer(serializers.ModelSerializer):
    id_serie_doc = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_serie_doc', default=None)
    nombre_serie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre', default=None)
    codigo_serie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo', default=None)
    id_subserie_doc = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.id_subserie_doc', default=None)
    nombre_subserie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre', default=None)
    codigo_subserie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo', default=None)
    id_unidad_org_actual_admin_series = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.id_unidad_org_actual_admin_series.id_unidad_organizacional', default=None)
    nombre_unidad_org_actual_admin_series = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.id_unidad_org_actual_admin_series.nombre', default=None)
    codigo_unidad_org_actual_admin_series = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.id_unidad_org_actual_admin_series.codigo', default=None)
    id_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.id_unidad_organizacional', default=None)
    nombre_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.nombre', default=None)
    codigo_unidad_organizacional = serializers.ReadOnlyField(source='id_cat_serie_und.id_unidad_organizacional.codigo', default=None)
    id_catalogo_serie = serializers.ReadOnlyField(source='id_cat_serie_und.id_catalogo_serie.id_catalogo_serie', default=None)
    
    class Meta:
        model = CatSeriesUnidadOrgCCDTRD
        fields = [
            'id_catserie_unidadorg',
            'id_unidad_organizacional',
            'nombre_unidad_organizacional',
            'codigo_unidad_organizacional',
            'id_catalogo_serie',
            'id_serie_doc',
            'nombre_serie',
            'codigo_serie',
            'id_subserie_doc',
            'nombre_subserie',
            'codigo_subserie',
            'id_unidad_org_actual_admin_series',
            'nombre_unidad_org_actual_admin_series',
            'codigo_unidad_org_actual_admin_series'
        ]

class CarpetaCajaAperturaSerializer(serializers.ModelSerializer):
    carpeta = serializers.SerializerMethodField()
    caja = serializers.ReadOnlyField(source='id_caja_bandeja.identificacion_por_bandeja', default=None)
    bandeja = serializers.ReadOnlyField(source='id_caja_bandeja.id_bandeja_estante.identificacion_por_estante', default=None)
    estante = serializers.ReadOnlyField(source='id_caja_bandeja.id_bandeja_estante.id_estante_deposito.identificacion_por_deposito', default=None)
    deposito = serializers.ReadOnlyField(source='id_caja_bandeja.id_bandeja_estante.id_estante_deposito.id_deposito.identificacion_por_entidad', default=None)
    
    def get_carpeta(self, obj):
        carpeta = 'Carpeta ' + str(obj.orden_ubicacion_por_caja) + ' - ' + obj.identificacion_por_caja
        return carpeta
    
    class Meta:
        model =  CarpetaCaja
        fields = [
            'id_carpeta_caja',
            'carpeta',
            'caja',
            'bandeja',
            'estante',
            'deposito'
        ]

class ExpedienteAperturaSerializer(serializers.ModelSerializer):
    tipo_documento_persona_titular_exp_complejo = serializers.ReadOnlyField(source='id_persona_titular_exp_complejo.tipo_documento.cod_tipo_documento', default=None)
    nro_documento_persona_titular_exp_complejo = serializers.ReadOnlyField(source='id_persona_titular_exp_complejo.numero_documento', default=None)
    nombre_persona_titular_exp_complejo = serializers.SerializerMethodField()
    tipo_documento_persona_responsable_actual = serializers.ReadOnlyField(source='id_persona_responsable_actual.tipo_documento.cod_tipo_documento', default=None)
    nro_documento_persona_responsable_actual = serializers.ReadOnlyField(source='id_persona_responsable_actual.numero_documento', default=None)
    nombre_persona_responsable_actual = serializers.SerializerMethodField()
    nombre_und_org_oficina_respon_actual = serializers.ReadOnlyField(source='id_und_org_oficina_respon_actual.nombre', default=None)
    carpetas_caja = serializers.SerializerMethodField()
    nombre_persona_anula = serializers.SerializerMethodField()

    def get_nombre_persona_titular_exp_complejo(self, obj):
        nombre_persona_titular_exp_complejo = None
        if obj.id_persona_titular_exp_complejo:
            nombre_list = [obj.id_persona_titular_exp_complejo.primer_nombre, obj.id_persona_titular_exp_complejo.segundo_nombre,
                            obj.id_persona_titular_exp_complejo.primer_apellido, obj.id_persona_titular_exp_complejo.segundo_apellido]
            nombre_persona_titular_exp_complejo = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_titular_exp_complejo = nombre_persona_titular_exp_complejo if nombre_persona_titular_exp_complejo != "" else None
        return nombre_persona_titular_exp_complejo
    
    def get_nombre_persona_responsable_actual(self, obj):
        nombre_persona_responsable_actual = None
        if obj.id_persona_responsable_actual:
            nombre_list = [obj.id_persona_responsable_actual.primer_nombre, obj.id_persona_responsable_actual.segundo_nombre,
                            obj.id_persona_responsable_actual.primer_apellido, obj.id_persona_responsable_actual.segundo_apellido]
            nombre_persona_responsable_actual = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_responsable_actual = nombre_persona_responsable_actual if nombre_persona_responsable_actual != "" else None
        return nombre_persona_responsable_actual
    
    def get_carpetas_caja(self, obj):
        carpetas_caja = None
        carpetas_caja = obj.carpetacaja_set.all()
        serializer = CarpetaCajaAperturaSerializer(carpetas_caja, many=True)
        data_output = []
        
        if carpetas_caja:
            carpetas_caja_data = json.loads(json.dumps(serializer.data))
            
            carpetas_caja_data = sorted(carpetas_caja_data, key=operator.itemgetter("deposito"))
            
            for depositos, estantes in itertools.groupby(carpetas_caja_data, key=operator.itemgetter("deposito")):
                estantes_depositos = list(estantes)
                for estante in estantes_depositos:
                    del estante['deposito']
                
                estante_data = sorted(estantes_depositos, key=operator.itemgetter("estante"))
                data_estante = []
                
                for estantes, bandejas in itertools.groupby(estante_data, key=operator.itemgetter("estante")):
                    bandejas_estantes = list(bandejas)
                    for bandeja in bandejas_estantes:
                        del bandeja['estante']
                    
                    bandeja_data = sorted(bandejas_estantes, key=operator.itemgetter("bandeja"))
                    data_bandeja = []
                    
                    for bandejas, cajas in itertools.groupby(bandeja_data, key=operator.itemgetter("bandeja")):
                        cajas_bandejas = list(cajas)
                        for caja in cajas_bandejas:
                            del caja['bandeja']
                        
                        caja_data = sorted(cajas_bandejas, key=operator.itemgetter("caja"))
                        data_caja = []
                        
                        for cajas, carpetas in itertools.groupby(caja_data, key=operator.itemgetter("caja")):
                            carpetas_cajas = list(carpetas)
                            for carpeta in carpetas_cajas:
                                del carpeta['caja']
                            
                            items_data = {
                                "caja": cajas,
                                "carpetas": carpetas_cajas
                            }
                            
                            data_caja.append(items_data)
                        
                        items_data = {
                            "bandeja": bandejas,
                            "cajas": data_caja
                        }
                        
                        data_bandeja.append(items_data)
                    
                    items_data = {
                        "estante": estantes,
                        "bandejas": data_bandeja
                    }
                    
                    data_estante.append(items_data)
                
                items_data = {
                    "deposito": depositos,
                    "estantes": data_estante
                }
                
                data_output.append(items_data)
        
        return data_output
    
    def get_nombre_persona_anula(self, obj):
        nombre_persona_anula = None
        if obj.id_persona_anula:
            nombre_list = [obj.id_persona_anula.primer_nombre, obj.id_persona_anula.segundo_nombre,
                            obj.id_persona_anula.primer_apellido, obj.id_persona_anula.segundo_apellido]
            nombre_persona_anula = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_anula = nombre_persona_anula if nombre_persona_anula != "" else None
        return nombre_persona_anula

    class Meta:
        model =  ExpedientesDocumentales
        fields = [
            'id_expediente_documental',
            'codigo_exp_und_serie_subserie',
            'codigo_exp_Agno',
            'codigo_exp_consec_por_agno',
            'titulo_expediente',
            'descripcion_expediente',
            'id_persona_titular_exp_complejo',
            'tipo_documento_persona_titular_exp_complejo',
            'nro_documento_persona_titular_exp_complejo',
            'nombre_persona_titular_exp_complejo',
            'id_und_org_oficina_respon_actual',
            'nombre_und_org_oficina_respon_actual',
            'id_persona_responsable_actual',
            'tipo_documento_persona_responsable_actual',
            'nro_documento_persona_responsable_actual',
            'nombre_persona_responsable_actual',
            'fecha_apertura_expediente',
            'fecha_creacion_manual',
            'palabras_clave_expediente',
            'creado_automaticamente',
            'anulado',
            'observacion_anulacion',
            'fecha_anulacion',
            'id_persona_anula',
            'nombre_persona_anula',
            'carpetas_caja'
        ]

class ConfiguracionTipoExpedienteAperturaGetSerializer(serializers.ModelSerializer):
    tipo_expediente = serializers.CharField(source='get_cod_tipo_expediente_display', read_only=True)
    expediente = serializers.SerializerMethodField()
    
    def get_expediente(self, obj):
        cod_unidad = obj.id_cat_serie_undorg_ccd.id_cat_serie_und.id_unidad_organizacional.codigo
        cod_serie = obj.id_cat_serie_undorg_ccd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo
        cod_subserie = obj.id_cat_serie_undorg_ccd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo if obj.id_cat_serie_undorg_ccd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc else None
        
        codigo_exp_und_serie_subserie = cod_unidad + '.' + cod_serie + '.' + cod_subserie if cod_subserie else cod_unidad + '.' + cod_serie
        
        expediente = ExpedientesDocumentales.objects.filter(codigo_exp_und_serie_subserie=codigo_exp_und_serie_subserie, codigo_exp_Agno=obj.agno_expediente)
        
        if expediente:
            serializer = ExpedienteAperturaSerializer(expediente, many=True)
            expediente = serializer.data
        
        expediente = expediente if expediente else []
        return expediente
    
    class Meta:
        model = ConfiguracionTipoExpedienteAgno
        fields = [
            'id_config_tipo_expediente_agno',
            'id_cat_serie_undorg_ccd',
            'cod_tipo_expediente',
            'tipo_expediente',
            'expediente'
        ]

class AperturaExpedienteSimpleSerializer(serializers.ModelSerializer):
    def validate_fecha_apertura_expediente(self, fecha_apertura):
        current_date = datetime.now()
        
        if fecha_apertura > current_date:
            raise ValidationError('No debe enviar una fecha posterior al día de hoy')
        
        if current_date.year != fecha_apertura.year:
            raise ValidationError('No debe enviar una fecha con año distinto al actual')
        
        request_data = self.context["request"].data
        
        if request_data['cod_tipo_expediente'] == 'C':
            ultimo_expediente = ExpedientesDocumentales.objects.filter(codigo_exp_und_serie_subserie = request_data['codigo_exp_und_serie_subserie']).order_by('fecha_apertura_expediente').last()
            if fecha_apertura > ultimo_expediente.fecha_apertura_expediente:
                raise ValidationError('La fecha tiene que ser posterior a la fecha de apertura del último expediente')
            
        return fecha_apertura
            
    def validate_palabras_clave_expediente(self, palabras):
        palabras_split = palabras.split('|')
        
        if len(palabras_split) > 5:
            raise ValidationError('No debe enviar más de 5 palabras clave')
        
        return palabras
        
    class Meta:
        model =  ExpedientesDocumentales
        fields = [
            'titulo_expediente',
            'descripcion_expediente',
            'id_unidad_org_oficina_respon_original',
            'id_und_org_oficina_respon_actual',
            'id_persona_responsable_actual',
            'fecha_apertura_expediente',
            'palabras_clave_expediente',
            'codigo_exp_und_serie_subserie',
            'codigo_exp_Agno',
            'codigo_exp_consec_por_agno',
            'id_cat_serie_und_org_ccd_trd_prop',
            'id_trd_origen',
            'id_und_seccion_propietaria_serie',
            'id_serie_origen',
            'id_subserie_origen',
            'cod_tipo_expediente',
            'estado',
            'fecha_folio_inicial',
            'cod_etapa_de_archivo_actual_exped',
            'tiene_carpeta_fisica',
            'ubicacion_fisica_esta_actualizada',
            'creado_automaticamente',
            'fecha_creacion_manual',
            'id_persona_crea_manual'
        ]
        extra_kwargs = {
            'titulo_expediente': {'required': True, 'allow_blank':False, 'allow_null':False},
            'descripcion_expediente': {'required': False, 'allow_blank':True, 'allow_null':True},
            'id_unidad_org_oficina_respon_original': {'required': True, 'allow_null':False},
            'id_und_org_oficina_respon_actual': {'required': True, 'allow_null':False},
            'id_persona_responsable_actual': {'required': False, 'allow_null':True},
            'fecha_apertura_expediente': {'required': True, 'allow_null':False},
            'palabras_clave_expediente': {'required': True, 'allow_null':False},
            'id_cat_serie_und_org_ccd_trd_prop': {'required': True, 'allow_null':False},
            'id_trd_origen': {'required': True, 'allow_null':False},
            'id_und_seccion_propietaria_serie': {'required': True, 'allow_null':False},
            'id_serie_origen': {'required': True, 'allow_null':False},
            'id_subserie_origen': {'required': False, 'allow_null':True}
        }
        
class AperturaExpedienteComplejoSerializer(AperturaExpedienteSimpleSerializer):
    
    class Meta:
        model =  ExpedientesDocumentales
        fields = AperturaExpedienteSimpleSerializer.Meta.fields + ['id_persona_titular_exp_complejo']
        extra_kwargs = AperturaExpedienteSimpleSerializer.Meta.extra_kwargs | {'id_persona_titular_exp_complejo': {'required': False,'allow_null':True}}

class AperturaExpedienteUpdateAutSerializer(serializers.ModelSerializer):
        
    def validate_palabras_clave_expediente(self, palabras):
        palabras_split = palabras.split('|')
        
        if len(palabras_split) > 5:
            raise ValidationError('No debe enviar más de 5 palabras clave')
        
        return palabras
        
    class Meta:
        model =  ExpedientesDocumentales
        fields = [
            'palabras_clave_expediente'
        ]

class AperturaExpedienteUpdateNoAutSerializer(AperturaExpedienteUpdateAutSerializer):
    
    def validate_fecha_apertura_expediente(self, fecha_apertura):
        documentos = self.instance.documentosdearchivoexpediente_set.all()
        
        for documento in documentos:
            if documento.fecha_incorporacion_doc_a_Exp < fecha_apertura:
                raise PermissionDenied('No puede actualizar la fecha de apertura a una menor a la fecha de incorporación de un documento del expediente elegido')
        
        return fecha_apertura
    
    class Meta:
        model =  ExpedientesDocumentales
        fields = AperturaExpedienteSimpleSerializer.Meta.fields + ['descripcion_expediente', 'fecha_apertura_expediente']

class AnularExpedienteSerializer(serializers.ModelSerializer):
        
    class Meta:
        model =  ExpedientesDocumentales
        fields = [
            'anulado',
            'observacion_anulacion',
            'fecha_anulacion',
            'id_persona_anula'
        ]
        extra_kwargs = {
            'observacion_anulacion': {'required': True, 'allow_blank':False, 'allow_null':False}
        }
        
class BorrarExpedienteSerializer(serializers.ModelSerializer):
        
    class Meta:
        model =  ExpedientesDocumentales
        fields = [
            'anulado',
            'observacion_anulacion',
            'fecha_anulacion',
            'id_persona_anula'
        ]
        extra_kwargs = {
            'observacion_anulacion': {'required': True, 'allow_blank':False, 'allow_null':False}
        }

#Buscar-Expediente
class ExpedienteSearchSerializer(serializers.ModelSerializer):

    nombre_serie_origen = serializers.ReadOnlyField(source='id_serie_origen.nombre', default=None)
    nombre_subserie_origen = serializers.ReadOnlyField(source='id_subserie_origen.nombre', default=None)
    nombre_unidad_org = serializers.ReadOnlyField(source='id_und_seccion_propietaria_serie.nombre', default=None)
    nombre_trd_origen = serializers.ReadOnlyField(source='id_trd_origen.nombre', default=None)
    nombre_persona_titular = serializers.SerializerMethodField()
    
    def get_nombre_persona_titular(self, obj):
        nombre_persona_titular = None
        if obj.id_persona_titular_exp_complejo:
            nombre_list = [obj.id_persona_titular_exp_complejo.primer_nombre, obj.id_persona_titular_exp_complejo.segundo_nombre,
                            obj.id_persona_titular_exp_complejo.primer_apellido, obj.id_persona_titular_exp_complejo.segundo_apellido]
            nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        return nombre_persona_titular

    class Meta:
        model =  ExpedientesDocumentales
        fields = [
            'codigo_exp_und_serie_subserie',
            'id_expediente_documental',
            'titulo_expediente',
            'id_und_seccion_propietaria_serie',
            'nombre_unidad_org',
            'id_serie_origen',
            'nombre_serie_origen',
            'id_subserie_origen',
            'nombre_subserie_origen',
            'nombre_subserie_origen',
            'id_trd_origen',
            'nombre_trd_origen',
            'fecha_apertura_expediente',
            'id_persona_titular_exp_complejo',
            'nombre_persona_titular'
        ]


class ListarTRDSerializer(serializers.ModelSerializer):
    nombre_tdr_origen = serializers.ReadOnlyField(source='id_trd_origen.nombre', default=None)
    actual_tdr_origen = serializers.ReadOnlyField(source='id_trd_origen.actual', default=None)
    fecha_retiro_produccion_tdr_origen = serializers.ReadOnlyField(source='id_trd_origen.fecha_retiro_produccion', default=None)
    estado_actual = serializers.SerializerMethodField()  # Nuevo campo para el estado actual

    class Meta:
        model = ExpedientesDocumentales
        fields = ['id_trd_origen', 'nombre_tdr_origen', 'actual_tdr_origen', 'fecha_retiro_produccion_tdr_origen', 'estado_actual']

    def get_estado_actual(self, obj):
        return "ACTUAL" if obj.id_trd_origen.actual else "NO ACTUAL"

#Listar_Expedientes    
class ExpedientesDocumentalesGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpedientesDocumentales
        fields = '__all__'



#Orden_Siguiente_Expediente
class ExpedienteGetOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = '__all__'
 


#Cierre_Expediente  
class CierreExpedienteSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # Aquí puedes realizar la lógica de conversión de campos vacíos a None (null)
        # Por ejemplo:
        for field_name, field_value in validated_data.items():
            if field_value == "":
                validated_data[field_name] = None
    
    class Meta:
        model =  CierresReaperturasExpediente
        fields = '__all__'




#ArchivosSoporte_CierreReapertura
class ArchivosSoporteCierreReaperturaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  ArchivosSoporte_CierreReapertura
        fields = '__all__'


######################### SERIALIZERS DOCUMENTOS DE ARCHIVO DE EXPEDIENTE #########################


class AgregarArchivoSoporteCreateSerializer(serializers.ModelSerializer):

    def validate_palabras_clave_documento(self, value):
        # Separar las palabras clave ingresadas por el carácter "|"
        palabras_clave = value.split('|')

        # Limitar a un máximo de 5 palabras clave
        if len(palabras_clave) > 5:
            raise ValidationError("No se pueden ingresar más de 5 palabras clave.")

        # Eliminar espacios en blanco al principio y al final de cada palabra clave
        palabras_clave = [palabra.strip() for palabra in palabras_clave]

        # Unir las palabras clave formateadas de nuevo con "|"
        return '|'.join(palabras_clave)
    
    def create(self, validated_data):
        # Aquí puedes realizar la lógica de conversión de campos vacíos a None (null)
        # Por ejemplo:
        for field_name, field_value in validated_data.items():
            if field_value == "":
                validated_data[field_name] = None
        return super().create(validated_data)

    class Meta:
        model = DocumentosDeArchivoExpediente
        fields = '__all__'


class ArchivosSoporteGetAllSerializer(serializers.ModelSerializer):
    # Puedes incluir el nombre de la tipología documental a través de la relación
    nombre_tipologia = serializers.CharField(source='id_tipologia_documental.nombre', read_only=True)
    
    class Meta:
        model = DocumentosDeArchivoExpediente
        fields = '__all__'  # Esto ya incluye todos los campos del modelo


class ListarTipologiasSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipologiasDoc
        fields = ['id_tipologia_documental', 'nombre']


class ArchivoSoporteSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentosDeArchivoExpediente
        fields = '__all__'

  
class CierreExpedienteDetailSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # Aquí puedes realizar la lógica de conversión de campos vacíos a None (null)
        # Por ejemplo:
        for field_name, field_value in validated_data.items():
            if field_value == "":
                validated_data[field_name] = None
    
    class Meta:
        model =  CierresReaperturasExpediente
        fields = '__all__'


 ######################### SERIALIZERS ARCHIVOS DIGITALES #########################
class ArchivosDigitalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
        fields = '__all__'  

class ArchivosDigitalesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivosDigitales
        fields = '__all__'
        # extra_kwargs = {
        #     'ruta_archivo': {'write_only': True}
        # }

    def save(self, subcarpeta='',nombre_cifrado=True,**kwargs):
        try:
            archivo = self.validated_data['ruta_archivo']
            nombre_archivo = archivo.name
            Subcarpeta=subcarpeta
            unique_filename = secrets.token_hex(10)
            nombre_sin_extension, extension = os.path.splitext(nombre_archivo)
            extension_sin_punto = extension[1:] if extension.startswith('.') else extension
            if nombre_cifrado:
                nombre_nuevo=unique_filename+'.'+extension_sin_punto
            else:
                nombre_nuevo=self.validated_data['nombre_de_Guardado']+'.'+extension_sin_punto
                unique_filename=self.validated_data['nombre_de_Guardado']
            if not extension_sin_punto:
                raise ValidationError("No fue posible registrar el archivo")
                # Utiliza la ruta de medios para guardar el archivo
            
            ruta_completa = os.path.join(settings.MEDIA_ROOT,Subcarpeta, nombre_nuevo)
            
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, Subcarpeta)):
                os.makedirs(os.path.join(settings.MEDIA_ROOT, Subcarpeta))
            # Guarda el archivo
            with open(ruta_completa, 'wb') as destination:
                for chunk in archivo.chunks():
                    destination.write(chunk)


            self.validated_data['ruta_archivo'] = os.path.relpath(ruta_completa, settings.MEDIA_ROOT)
            self.validated_data['nombre_de_Guardado'] = unique_filename
            #print(self.validated_data)
            return super().save(**kwargs)

        except FileNotFoundError as e:

             raise serializers.ValidationError(str(e))
