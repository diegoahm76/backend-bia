import secrets
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max, F
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.depositos_models import CarpetaCaja 
from gestion_documental.models.expedientes_models import ConcesionesAccesoAExpsYDocs, EliminacionDocumental, ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TablaRetencionDocumental, TipologiasDoc
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from datetime import datetime, timedelta
from django.conf import settings
import os
import operator, itertools
import json
from transversal.models.personas_models import Personas

from transversal.serializers.personas_serializers import PersonasFilterSerializer


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
    nombre_serie_origen = serializers.ReadOnlyField(source='id_serie_origen.nombre', default=None)
    nombre_subserie_origen = serializers.ReadOnlyField(source='id_subserie_origen.nombre', default=None)
    nombre_trd_origen = serializers.ReadOnlyField(source='id_trd_origen.nombre', default=None)
    tipo_expediente = serializers.CharField(source='get_cod_tipo_expediente_display', read_only=True)
    etapa_de_archivo_actual_exped = serializers.CharField(source='get_cod_etapa_de_archivo_actual_exped_display', read_only=True)
    fecha_folio_inicial = serializers.DateTimeField(format="%d/%m/%Y")
    fecha_folio_final = serializers.DateTimeField(format="%d/%m/%Y")
    nombre_unidad_org_oficina_respon_original = serializers.ReadOnlyField(source='id_unidad_org_oficina_respon_original.nombre', default=None)
    desc_estado = serializers.CharField(source='get_estado_display', read_only=True)
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
            'id_serie_origen',
            'nombre_serie_origen',
            'id_subserie_origen',
            'nombre_subserie_origen',
            'id_trd_origen',
            'nombre_trd_origen',
            'cod_tipo_expediente',
            'tipo_expediente',
            'cod_etapa_de_archivo_actual_exped',
            'etapa_de_archivo_actual_exped',
            'fecha_folio_inicial',
            'fecha_folio_final',
            'id_unidad_org_oficina_respon_original',
            'nombre_unidad_org_oficina_respon_original',
            'estado',
            'desc_estado',
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
        # cod_unidad = obj.id_cat_serie_undorg_ccd.id_cat_serie_und.id_unidad_organizacional.codigo
        # cod_serie = obj.id_cat_serie_undorg_ccd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo
        # cod_subserie = obj.id_cat_serie_undorg_ccd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo if obj.id_cat_serie_undorg_ccd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc else None
        
        # codigo_exp_und_serie_subserie = cod_unidad + '.' + cod_serie + '.' + cod_subserie if cod_subserie else cod_unidad + '.' + cod_serie
        
        # expediente = ExpedientesDocumentales.objects.filter(codigo_exp_und_serie_subserie=codigo_exp_und_serie_subserie, codigo_exp_Agno=obj.agno_expediente)
        expediente = ExpedientesDocumentales.objects.filter(id_cat_serie_und_org_ccd_trd_prop=obj.id_cat_serie_undorg_ccd, codigo_exp_Agno=obj.agno_expediente)
        
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
        
        request_data = self.initial_data
        
        if request_data['cod_tipo_expediente'] == 'C':
            ultimo_expediente = ExpedientesDocumentales.objects.filter(codigo_exp_und_serie_subserie = request_data['codigo_exp_und_serie_subserie']).order_by('fecha_apertura_expediente').last()
            if ultimo_expediente and fecha_apertura < ultimo_expediente.fecha_apertura_expediente:
                raise ValidationError(f'La fecha tiene que ser posterior a la fecha de apertura del último expediente ({str(ultimo_expediente.fecha_apertura_expediente)})')
            
        return fecha_apertura
            
    def validate_palabras_clave_expediente(self, palabras):
        palabras_split = palabras.split('|')
        
        if len(palabras_split) > 5:
            raise ValidationError('No debe enviar más de 5 palabras clave')
        
        return palabras
        
    class Meta:
        model =  ExpedientesDocumentales
        fields = [
            'id_expediente_documental',
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
            'id_expediente_documental': {'read_only':True},
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
    desc_estado = serializers.CharField(source='get_estado_display', read_only=True)
    
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
            'codigo_exp_Agno',
            'codigo_exp_consec_por_agno',
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
            'nombre_persona_titular',
            'estado',
            'desc_estado',
            'fecha_cierre_reapertura_actual',
            'ubicacion_fisica_esta_actualizada',
            'descripcion_expediente'
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

class ListExpedientesComplejosSerializer(serializers.ModelSerializer):
    tipo_expediente = serializers.CharField(source='get_cod_tipo_expediente_display', default=None)
    carpetas_caja = serializers.SerializerMethodField()
    documentos_agregados = serializers.SerializerMethodField()
    
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
    
    def get_documentos_agregados(self, obj):
        documentos = obj.documentosdearchivoexpediente_set.all().order_by('orden_en_expediente')
        
        documentos = documentos.values(
            "id_documento_de_archivo_exped",
            "orden_en_expediente",
            "nombre_asignado_documento",
            tipologia = F("id_tipologia_documental__nombre")
        ) if documentos else []
        
        return documentos
    
    class Meta:
        model =  ExpedientesDocumentales
        fields = [
            'id_expediente_documental',
            'codigo_exp_und_serie_subserie',
            'codigo_exp_Agno',
            'codigo_exp_consec_por_agno',
            'titulo_expediente',
            'descripcion_expediente',
            'fecha_apertura_expediente',
            'cod_tipo_expediente',
            'tipo_expediente',
            'carpetas_caja',
            'documentos_agregados'
        ]
        
class IndexarDocumentosCreateSerializer(serializers.ModelSerializer):
    
    def validate_fecha_incorporacion_doc_a_Exp(self, fecha_incorp):
        request_data = self.initial_data
        ultimo_doc_expediente = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=request_data['id_expediente_documental']).order_by('orden_en_expediente').last()
        
        if ultimo_doc_expediente and fecha_incorp < ultimo_doc_expediente.fecha_incorporacion_doc_a_Exp:
            raise ValidationError(f'La fecha de incorporación de los documentos deben ser mayor al último documento ya ingresado del expediente elegido ({str(ultimo_doc_expediente.fecha_incorporacion_doc_a_Exp)})')
        
        return fecha_incorp
    
    def validate_fecha_creacion_doc(self, fecha_creacion):
        request_data = self.initial_data
        fecha_incorp = datetime.strptime(request_data['fecha_incorporacion_doc_a_Exp'], '%Y-%m-%d')
        
        if fecha_creacion > fecha_incorp:
            raise ValidationError('La Fecha de Creación del Documento tiene que ser igual o anterior a la Fecha de Incorporación al Expediente')
        
        return fecha_creacion
    
    def validate_codigo_radicado_consecutivo(self, codigo_radicado_consecutivo):
        request_data = self.initial_data
        if codigo_radicado_consecutivo and not request_data.get('codigo_radicado_agno'):
            raise ValidationError('Debe llenar mínimo el Consecutivo y el Año o los 3 campos')
            
        return codigo_radicado_consecutivo
    
    def validate_codigo_radicado_agno(self, codigo_radicado_agno):
        request_data = self.initial_data
        if codigo_radicado_agno and not request_data.get('codigo_radicado_consecutivo'):
            raise ValidationError('Debe llenar mínimo el Consecutivo y el Año o los 3 campos')
            
        return codigo_radicado_agno
    
    def validate_codigo_radicado_prefijo(self, codigo_radicado_prefijo):
        request_data = self.initial_data
        if codigo_radicado_prefijo and not request_data.get('codigo_radicado_agno') and not request_data.get('codigo_radicado_consecutivo'):
            raise ValidationError('Debe llenar mínimo el Consecutivo y el Año o los 3 campos')
            
        return codigo_radicado_prefijo
    
    def validate_palabras_clave_documento(self, palabras):
        palabras_split = palabras.split('|')
        
        if len(palabras_split) > 5:
            raise ValidationError('No debe enviar más de 5 palabras clave')
        
        return palabras
    
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = [
            'id_documento_de_archivo_exped',
            'id_expediente_documental',
            'identificacion_doc_en_expediente',
            'nombre_asignado_documento',
            'nombre_original_del_archivo',
            'fecha_creacion_doc',
            'fecha_incorporacion_doc_a_Exp',
            'descripcion',
            'asunto',
            'cod_categoria_archivo',
            'es_version_original',
            'tiene_replica_fisica',
            'nro_folios_del_doc',
            'cod_origen_archivo',
            'orden_en_expediente',
            'id_tipologia_documental',
            'codigo_radicado_prefijo',
            'codigo_radicado_agno',
            'codigo_radicado_consecutivo',
            'es_un_archivo_anexo',
            'id_doc_de_arch_del_cual_es_anexo',
            'anexo_corresp_a_lista_chequeo',
            'id_archivo_sistema',
            'palabras_clave_documento',
            'documento_requiere_rta',
            'creado_automaticamente',
            'fecha_indexacion_manual_sistema',
            'id_und_org_oficina_creadora',
            'id_persona_que_crea',
            'id_und_org_oficina_respon_actual'
        ]
        extra_kwargs = {
            'id_documento_de_archivo_exped': {'read_only': True},
            'fecha_incorporacion_doc_a_Exp': {'required': True, 'allow_null':False},
            'fecha_creacion_doc': {'required': True, 'allow_null':False},
            'id_tipologia_documental': {'required': True, 'allow_null':False},
            'nro_folios_del_doc': {'required': True, 'allow_null':False},
            'cod_origen_archivo': {'required': True, 'allow_blank':False, 'allow_null':False},
            'cod_categoria_archivo': {'required': True, 'allow_blank':False, 'allow_null':False},
            'tiene_replica_fisica': {'required': True, 'allow_null':False},
            'nombre_asignado_documento': {'required': True, 'allow_blank':False, 'allow_null':False},
            'descripcion': {'required': True, 'allow_blank':False, 'allow_null':False},
        }

class IndexarDocumentosGetSerializer(serializers.ModelSerializer):
    tiene_consecutivo_documento = serializers.SerializerMethodField()
    nombre_tipologia = serializers.CharField(source='id_tipologia_documental.nombre', read_only=True)
    categoria_archivo = serializers.CharField(source='get_cod_categoria_archivo_display', read_only=True)
    origen_archivo = serializers.CharField(source='get_cod_origen_archivo_display', read_only=True)
    nombre_persona_anula = serializers.SerializerMethodField()
    
    def get_tiene_consecutivo_documento(self, obj):
        tiene_consecutivo_documento = False
        if obj.codigo_radicado_consecutivo:
            tiene_consecutivo_documento = True
            
        return tiene_consecutivo_documento
    
    def get_nombre_persona_anula(self, obj):
        nombre_persona_anula = None
        if obj.id_persona_anula:
            nombre_list = [obj.id_persona_anula.primer_nombre, obj.id_persona_anula.segundo_nombre,
                            obj.id_persona_anula.primer_apellido, obj.id_persona_anula.segundo_apellido]
            nombre_persona_anula = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_anula = nombre_persona_anula if nombre_persona_anula != "" else None
        return nombre_persona_anula
    
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = [
            'id_documento_de_archivo_exped',
            'id_expediente_documental',
            'identificacion_doc_en_expediente',
            'nombre_asignado_documento',
            'nombre_original_del_archivo',
            'fecha_creacion_doc',
            'fecha_incorporacion_doc_a_Exp',
            'descripcion',
            'asunto',
            'cod_categoria_archivo',
            'categoria_archivo',
            'es_version_original',
            'tiene_replica_fisica',
            'nro_folios_del_doc',
            'cod_origen_archivo',
            'origen_archivo',
            'orden_en_expediente',
            'id_tipologia_documental',
            'nombre_tipologia',
            'tiene_consecutivo_documento',
            'codigo_radicado_prefijo',
            'codigo_radicado_agno',
            'codigo_radicado_consecutivo',
            'es_un_archivo_anexo',
            'id_doc_de_arch_del_cual_es_anexo',
            'anexo_corresp_a_lista_chequeo',
            'id_archivo_sistema',
            'palabras_clave_documento',
            'documento_requiere_rta',
            'creado_automaticamente',
            'fecha_indexacion_manual_sistema',
            'id_und_org_oficina_creadora',
            'id_persona_que_crea',
            'id_und_org_oficina_respon_actual',
            'anulado',
            'observacion_anulacion',
            'fecha_anulacion',
            'id_persona_anula',
            'nombre_persona_anula'
        ]

class IndexarDocumentosUpdateSerializer(serializers.ModelSerializer):
    def validate_fecha_incorporacion_doc_a_Exp(self, fecha_incorp):
        doc_siguiente_expediente = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=self.instance.id_expediente_documental, orden_en_expediente__gte=self.instance.orden_en_expediente).order_by('orden_en_expediente').first()
        doc_anterior_expediente = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=self.instance.id_expediente_documental, orden_en_expediente__lte=self.instance.orden_en_expediente).order_by('orden_en_expediente').last()
        
        if doc_anterior_expediente and fecha_incorp < doc_anterior_expediente.fecha_incorporacion_doc_a_Exp:
            raise ValidationError(f'La fecha de incorporación del documento elegido no puede ser menor a la fecha de incorporación del anterior documento ({str(doc_anterior_expediente.fecha_incorporacion_doc_a_Exp)})')
        
        if doc_siguiente_expediente and fecha_incorp > doc_siguiente_expediente.fecha_incorporacion_doc_a_Exp:
            raise ValidationError(f'La fecha de incorporación del documento elegido no puede ser mayor a la fecha de incorporación del siguiente documento ({str(doc_siguiente_expediente.fecha_incorporacion_doc_a_Exp)})')
        
        return fecha_incorp
    
    def validate_fecha_creacion_doc(self, fecha_creacion):
        request_data = self.initial_data
        if request_data.get('fecha_incorporacion_doc_a_Exp'):
            fecha_incorp = datetime.strptime(request_data['fecha_incorporacion_doc_a_Exp'], '%Y-%m-%d')
        else:
            fecha_incorp = self.instance.fecha_incorporacion_doc_a_Exp
        
        if fecha_creacion > fecha_incorp:
            raise ValidationError('La Fecha de Creación del Documento tiene que ser igual o anterior a la Fecha de Incorporación al Expediente')
        
        return fecha_creacion
    
    def validate_palabras_clave_documento(self, palabras):
        palabras_split = palabras.split('|')
        
        if len(palabras_split) > 5:
            raise ValidationError('No debe enviar más de 5 palabras clave')
        
        return palabras
    
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = [
            'fecha_creacion_doc',
            'fecha_incorporacion_doc_a_Exp',
            'descripcion',
            'asunto',
            'nombre_asignado_documento',
            'id_persona_titular',
            'cod_categoria_archivo',
            'tiene_replica_fisica',
            'nro_folios_del_doc',
            'cod_origen_archivo',
            'palabras_clave_documento'
        ]

class IndexarDocumentosUpdateAutSerializer(serializers.ModelSerializer):
    def validate_palabras_clave_documento(self, palabras):
        palabras_split = palabras.split('|')
        
        if len(palabras_split) > 5:
            raise ValidationError('No debe enviar más de 5 palabras clave')
        
        return palabras
    
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = ['palabras_clave_documento']
        
class IndexarDocumentosAnularSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = [
            'anulado',
            'observacion_anulacion',
            'fecha_anulacion',
            'id_persona_anula'
        ]
        extra_kwargs = {
            'observacion_anulacion': {'required': True, 'allow_blank':False, 'allow_null':False}
        }
        
class DocsIndiceElectronicoExpSerializer(serializers.ModelSerializer):
    nombre_tipologia = serializers.CharField(source='id_tipologia_documental.nombre', read_only=True)
    origen_archivo = serializers.CharField(source='get_cod_origen_archivo_display', read_only=True)
    documento_principal = serializers.ReadOnlyField(source='id_doc_indice_Anexo.identificación_doc_exped', default=None)
    
    class Meta:
        model =  Docs_IndiceElectronicoExp
        fields = [
            'id_doc_indice_electronico_exp',
            'id_doc_archivo_exp',
            'identificación_doc_exped',
            'nombre_documento',
            'id_tipologia_documental',
            'nombre_tipologia',
            'fecha_creacion_doc',
            'fecha_incorporacion_exp',
            'valor_huella',
            'funcion_resumen',
            'orden_doc_expediente',
            'pagina_inicio',
            'pagina_fin',
            'formato',
            'tamagno_kb',
            'cod_origen_archivo',
            'origen_archivo',
            'es_un_archivo_anexo',
            'id_doc_indice_Anexo',
            'documento_principal',
            'tipologia_no_creada_trd'
        ]

class InformacionIndiceGetSerializer(serializers.ModelSerializer):
    docs_indice_electronico_exp = serializers.SerializerMethodField()
    
    def get_docs_indice_electronico_exp(self, obj):
        docs_indice = Docs_IndiceElectronicoExp.objects.filter(id_indice_electronico_exp=obj.id_indice_electronico_exp)
        serializer_docs_indice = DocsIndiceElectronicoExpSerializer(docs_indice, many=True)
        return serializer_docs_indice.data

    class Meta:
        model =  IndicesElectronicosExp
        fields = [
            'id_indice_electronico_exp',
            'abierto',
            'fecha_indice_electronico',
            'fecha_cierre',
            'docs_indice_electronico_exp'
        ]
        
class EnvioCodigoSerializer(serializers.ModelSerializer):

    class Meta:
        model =  IndicesElectronicosExp
        fields = [
            'id_indice_electronico_exp',
            'abierto',
            'fecha_indice_electronico',
            'fecha_cierre',
            'docs_indice_electronico_exp'
        ]
        
class FirmaCierreGetSerializer(serializers.ModelSerializer):
    nombre_persona_firma_cierre = serializers.SerializerMethodField()
    telefono_celular = serializers.ReadOnlyField(source='id_persona_firma_cierre.telefono_celular', default=None)
    email = serializers.ReadOnlyField(source='id_persona_firma_cierre.email', default=None)
    
    def get_nombre_persona_firma_cierre(self, obj):
        nombre_persona_firma_cierre = None
        if obj.id_persona_firma_cierre:
            nombre_list = [obj.id_persona_firma_cierre.primer_nombre, obj.id_persona_firma_cierre.segundo_nombre,
                            obj.id_persona_firma_cierre.primer_apellido, obj.id_persona_firma_cierre.segundo_apellido]
            nombre_persona_firma_cierre = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_firma_cierre = nombre_persona_firma_cierre if nombre_persona_firma_cierre != "" else None
        return nombre_persona_firma_cierre

    class Meta:
        model =  IndicesElectronicosExp
        fields = [
            'id_indice_electronico_exp',
            'id_persona_firma_cierre',
            'nombre_persona_firma_cierre',
            'fecha_cierre',
            'telefono_celular',
            'email',
            'observacion_firme_cierre'
        ]
      
class ConcesionAccesoPersonasFilterSerializer(PersonasFilterSerializer):
    nombre_unidad_organizacional_actual = serializers.ReadOnlyField(source='id_unidad_organizacional_actual.nombre', default=None)
    
    class Meta:
        model =  Personas
        fields = PersonasFilterSerializer.Meta.fields + [
            'id_unidad_organizacional_actual',
            'es_unidad_organizacional_actual',
            'nombre_unidad_organizacional_actual',
        ]

class ConcesionAccesoExpedientesCreateSerializer(serializers.ModelSerializer):
        
    class Meta:
        model =  ConcesionesAccesoAExpsYDocs
        fields = [
            'id_concesion_acc',
            'id_persona_concede_acceso',
            'id_persona_recibe_acceso',
            'id_unidad_org_destinatario_conceder',
            'id_expediente',
            'con_acceso_tipologias_reservadas',
            'fecha_acceso_inicia',
            'fecha_acceso_termina',
            'observacion'
        ]
        extra_kwargs = {
            'id_concesion_acc': {'read_only':True},
            'id_persona_recibe_acceso': {'required': True, 'allow_null':False},
            'id_unidad_org_destinatario_conceder': {'required': True, 'allow_null':False},
            'con_acceso_tipologias_reservadas': {'required': True, 'allow_null':False},
            'fecha_acceso_inicia': {'required': True, 'allow_null':False},
            'fecha_acceso_termina': {'required': True, 'allow_null':False},
            'observacion': {'required': True, 'allow_blank':False, 'allow_null':False},
        }
        
class ConcesionAccesoUpdateSerializer(serializers.ModelSerializer):
        
    class Meta:
        model =  ConcesionesAccesoAExpsYDocs
        fields = [
            'con_acceso_tipologias_reservadas',
            'fecha_acceso_inicia',
            'fecha_acceso_termina',
            'observacion'
        ]
        
class ConcesionAccesoDocumentosCreateSerializer(serializers.ModelSerializer):
        
    class Meta:
        model =  ConcesionesAccesoAExpsYDocs
        fields = [
            'id_concesion_acc',
            'id_persona_concede_acceso',
            'id_persona_recibe_acceso',
            'id_unidad_org_destinatario_conceder',
            'id_documento_exp',
            'fecha_acceso_inicia',
            'fecha_acceso_termina',
            'observacion'
        ]
        extra_kwargs = {
            'id_concesion_acc': {'read_only':True},
            'id_persona_recibe_acceso': {'required': True, 'allow_null':False},
            'id_unidad_org_destinatario_conceder': {'required': True, 'allow_null':False},
            'fecha_acceso_inicia': {'required': True, 'allow_null':False},
            'fecha_acceso_termina': {'required': True, 'allow_null':False},
            'observacion': {'required': True, 'allow_blank':False, 'allow_null':False},
        }
        
class ConcesionAccesoExpedientesGetSerializer(serializers.ModelSerializer):
    nombre_persona_recibe_acceso = serializers.SerializerMethodField()
    tipo_documento_persona_recibe_acceso = serializers.ReadOnlyField(source='id_persona_recibe_acceso.tipo_documento.cod_tipo_documento', default=None)
    numero_documento_persona_recibe_acceso = serializers.ReadOnlyField(source='id_persona_recibe_acceso.numero_documento', default=None)
    nombre_persona_concede_acceso = serializers.SerializerMethodField()
    nombre_unidad_org_destinatario_conceder = serializers.ReadOnlyField(source='id_unidad_org_destinatario_conceder.nombre', default=None)
    titulo_expediente = serializers.ReadOnlyField(source='id_expediente.titulo_expediente', default=None)
    codigo_exp_und_serie_subserie = serializers.ReadOnlyField(source='id_expediente.codigo_exp_und_serie_subserie', default=None)

    def get_nombre_persona_recibe_acceso(self, obj):
        nombre_persona_recibe_acceso = None
        if obj.id_persona_recibe_acceso:
            nombre_list = [obj.id_persona_recibe_acceso.primer_nombre, obj.id_persona_recibe_acceso.segundo_nombre,
                            obj.id_persona_recibe_acceso.primer_apellido, obj.id_persona_recibe_acceso.segundo_apellido]
            nombre_persona_recibe_acceso = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_recibe_acceso = nombre_persona_recibe_acceso if nombre_persona_recibe_acceso != "" else None
        return nombre_persona_recibe_acceso
    
    def get_nombre_persona_concede_acceso(self, obj):
        nombre_persona_concede_acceso = None
        if obj.id_persona_concede_acceso:
            nombre_list = [obj.id_persona_concede_acceso.primer_nombre, obj.id_persona_concede_acceso.segundo_nombre,
                            obj.id_persona_concede_acceso.primer_apellido, obj.id_persona_concede_acceso.segundo_apellido]
            nombre_persona_concede_acceso = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_concede_acceso = nombre_persona_concede_acceso if nombre_persona_concede_acceso != "" else None
        return nombre_persona_concede_acceso
        
    class Meta:
        model =  ConcesionesAccesoAExpsYDocs
        fields = [
            'id_concesion_acc',
            'id_persona_concede_acceso',
            'nombre_persona_concede_acceso',
            'id_persona_recibe_acceso',
            'tipo_documento_persona_recibe_acceso',
            'numero_documento_persona_recibe_acceso',
            'nombre_persona_recibe_acceso',
            'id_unidad_org_destinatario_conceder',
            'nombre_unidad_org_destinatario_conceder',
            'id_expediente',
            'titulo_expediente',
            'codigo_exp_und_serie_subserie',
            'con_acceso_tipologias_reservadas',
            'fecha_acceso_inicia',
            'fecha_acceso_termina',
            'observacion'
        ]
        
class ConcesionAccesoDocumentosGetSerializer(serializers.ModelSerializer):
    nombre_persona_recibe_acceso = serializers.SerializerMethodField()
    tipo_documento_persona_recibe_acceso = serializers.ReadOnlyField(source='id_persona_recibe_acceso.tipo_documento.cod_tipo_documento', default=None)
    numero_documento_persona_recibe_acceso = serializers.ReadOnlyField(source='id_persona_recibe_acceso.numero_documento', default=None)
    nombre_persona_concede_acceso = serializers.SerializerMethodField()
    nombre_unidad_org_destinatario_conceder = serializers.ReadOnlyField(source='id_unidad_org_destinatario_conceder.nombre', default=None)
    identificacion_doc_en_expediente = serializers.ReadOnlyField(source='id_documento_exp.identificacion_doc_en_expediente', default=None)
    nombre_asignado_documento = serializers.ReadOnlyField(source='id_documento_exp.nombre_asignado_documento', default=None)

    def get_nombre_persona_recibe_acceso(self, obj):
        nombre_persona_recibe_acceso = None
        if obj.id_persona_recibe_acceso:
            nombre_list = [obj.id_persona_recibe_acceso.primer_nombre, obj.id_persona_recibe_acceso.segundo_nombre,
                            obj.id_persona_recibe_acceso.primer_apellido, obj.id_persona_recibe_acceso.segundo_apellido]
            nombre_persona_recibe_acceso = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_recibe_acceso = nombre_persona_recibe_acceso if nombre_persona_recibe_acceso != "" else None
        return nombre_persona_recibe_acceso
    
    def get_nombre_persona_concede_acceso(self, obj):
        nombre_persona_concede_acceso = None
        if obj.id_persona_concede_acceso:
            nombre_list = [obj.id_persona_concede_acceso.primer_nombre, obj.id_persona_concede_acceso.segundo_nombre,
                            obj.id_persona_concede_acceso.primer_apellido, obj.id_persona_concede_acceso.segundo_apellido]
            nombre_persona_concede_acceso = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_concede_acceso = nombre_persona_concede_acceso if nombre_persona_concede_acceso != "" else None
        return nombre_persona_concede_acceso
        
    class Meta:
        model =  ConcesionesAccesoAExpsYDocs
        fields = [
            'id_concesion_acc',
            'id_persona_concede_acceso',
            'nombre_persona_concede_acceso',
            'id_persona_recibe_acceso',
            'tipo_documento_persona_recibe_acceso',
            'numero_documento_persona_recibe_acceso',
            'nombre_persona_recibe_acceso',
            'id_unidad_org_destinatario_conceder',
            'nombre_unidad_org_destinatario_conceder',
            'id_documento_exp',
            'identificacion_doc_en_expediente',
            'nombre_asignado_documento',
            'fecha_acceso_inicia',
            'fecha_acceso_termina',
            'observacion'
        ]


class ReubicacionFisicaExpedienteSerializer(serializers.ModelSerializer):
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
        serializer = CarpetaCajaReubicacionSerializer(carpetas_caja, many=True)
        data_output = []
        
        if carpetas_caja:
            carpetas_caja_data = json.loads(json.dumps(serializer.data))
            
            carpetas_caja_data = sorted(carpetas_caja_data, key=operator.itemgetter("deposito","id_deposito"))
            
            for depositos, estantes in itertools.groupby(carpetas_caja_data, key=operator.itemgetter("deposito","id_deposito")):
                estantes_depositos = list(estantes)
                for estante in estantes_depositos:
                    del estante['deposito']
                    del estante['id_deposito']
                
                estante_data = sorted(estantes_depositos, key=operator.itemgetter("estante","id_estante"))
                data_estante = []
                
                for estantes, bandejas in itertools.groupby(estante_data, key=operator.itemgetter("estante","id_estante")):
                    bandejas_estantes = list(bandejas)
                    for bandeja in bandejas_estantes:
                        del bandeja['estante']
                        del bandeja['id_estante']
                    
                    bandeja_data = sorted(bandejas_estantes, key=operator.itemgetter("bandeja","id_bandeja"))
                    data_bandeja = []
                    
                    for bandejas, cajas in itertools.groupby(bandeja_data, key=operator.itemgetter("bandeja","id_bandeja")):
                        cajas_bandejas = list(cajas)
                        for caja in cajas_bandejas:
                            del caja['bandeja']
                            del caja['id_bandeja']
                        
                        caja_data = sorted(cajas_bandejas, key=operator.itemgetter("caja","id_caja"))
                        data_caja = []
                        
                        for cajas, carpetas in itertools.groupby(caja_data, key=operator.itemgetter("caja","id_caja")):
                            carpetas_cajas = list(carpetas)
                            for carpeta in carpetas_cajas:
                                del carpeta['caja']
                            
                            items_data = {
                                "caja": cajas[0],
                                "id_caja": cajas[1],
                                "carpetas": carpetas_cajas
                            }
                            
                            data_caja.append(items_data)
                        
                        items_data = {
                            "bandeja": bandejas[0],
                            "id_bandeja": bandejas[1],
                            "cajas": data_caja
                        }
                        
                        data_bandeja.append(items_data)
                    
                    items_data = {
                        "estante": estantes[0],
                        "id_estante": estantes[1],
                        "bandejas": data_bandeja
                    }
                    
                    data_estante.append(items_data)
                
                items_data = {
                    "deposito": depositos[0],
                    "id_deposito": depositos[1],
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
    
class CarpetaCajaReubicacionSerializer(serializers.ModelSerializer):
    carpeta = serializers.SerializerMethodField()
    caja = serializers.ReadOnlyField(source='id_caja_bandeja.identificacion_por_bandeja', default=None)
    id_caja = serializers.ReadOnlyField(source='id_caja_bandeja.id_caja_bandeja', default=None)
    bandeja = serializers.ReadOnlyField(source='id_caja_bandeja.id_bandeja_estante.identificacion_por_estante', default=None)
    id_bandeja = serializers.ReadOnlyField(source='id_caja_bandeja.id_bandeja_estante.id_bandeja_estante', default=None)
    estante = serializers.ReadOnlyField(source='id_caja_bandeja.id_bandeja_estante.id_estante_deposito.identificacion_por_deposito', default=None)
    id_estante = serializers.ReadOnlyField(source='id_caja_bandeja.id_bandeja_estante.id_estante_deposito.id_estante_deposito', default=None)
    deposito = serializers.ReadOnlyField(source='id_caja_bandeja.id_bandeja_estante.id_estante_deposito.id_deposito.identificacion_por_entidad', default=None)
    id_deposito = serializers.ReadOnlyField(source='id_caja_bandeja.id_bandeja_estante.id_estante_deposito.id_deposito.id_deposito', default=None)
    
    def get_carpeta(self, obj):
        carpeta = 'Carpeta ' + str(obj.orden_ubicacion_por_caja) + ' - ' + obj.identificacion_por_caja
        return carpeta
    
    class Meta:
        model =  CarpetaCaja
        fields = [
            
            'id_carpeta_caja',
            'carpeta',
            'caja',
            'id_caja',
            'id_bandeja',
            'bandeja',
            'estante',
            'id_estante',
            'deposito',
            'id_deposito'
        ]
        
class ConsultaExpedientesGetSerializer(serializers.ModelSerializer):
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
            'id_expediente_documental',
            'id_cat_serie_und_org_ccd_trd_prop',
            'codigo_exp_und_serie_subserie',
            'id_trd_origen',
            'nombre_trd_origen',
            'titulo_expediente',
            'id_und_seccion_propietaria_serie',
            'nombre_unidad_org',
            'id_serie_origen',
            'nombre_serie_origen',
            'id_subserie_origen',
            'nombre_subserie_origen',
            'codigo_exp_Agno',
            'codigo_exp_consec_por_agno',
            'id_persona_titular_exp_complejo',
            'nombre_persona_titular'
        ]
        
class ConsultaExpedientesDocumentosGetSerializer(serializers.ModelSerializer):
    pagina_inicio = serializers.SerializerMethodField()
    pagina_fin = serializers.SerializerMethodField()
    nombre_tipologia = serializers.ReadOnlyField(source='id_tipologia_documental.nombre', read_only=True, default=None)
    formato = serializers.ReadOnlyField(source='id_archivo_sistema.formato', default=None)
    tamagno_kb = serializers.ReadOnlyField(source='id_archivo_sistema.tamagno_kb', default=None)
    origen_archivo = serializers.CharField(source='get_cod_origen_archivo_display', read_only=True)
    
    def get_pagina_inicio(self, obj):
        pagina_inicio = None
        
        doc_indice_electronico = obj.docs_indiceelectronicoexp_set.first()
        if doc_indice_electronico:
            pagina_inicio = doc_indice_electronico.pagina_inicio
            
        return pagina_inicio
    
    def get_pagina_fin(self, obj):
        pagina_fin = None
        
        doc_indice_electronico = obj.docs_indiceelectronicoexp_set.first()
        if doc_indice_electronico:
            pagina_fin = doc_indice_electronico.pagina_fin
            
        return pagina_fin
    
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = [
            'id_documento_de_archivo_exped',
            'id_expediente_documental',
            'identificacion_doc_en_expediente',
            'nombre_asignado_documento',
            'id_tipologia_documental',
            'nombre_tipologia',
            'fecha_creacion_doc',
            'fecha_incorporacion_doc_a_Exp',
            'orden_en_expediente',
            'pagina_inicio',
            'pagina_fin',
            'formato',
            'tamagno_kb',
            'cod_origen_archivo',
            'origen_archivo',
            'es_un_archivo_anexo',
            'asunto',
            'palabras_clave_documento'
        ]

class ConsultaExpedientesDocumentosGetListSerializer(serializers.ModelSerializer):
    nombre_persona_titular = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    
    def get_nombre_persona_titular(self, obj):
        nombre_persona_titular = None
        if obj.id_persona_titular:
            nombre_list = [obj.id_persona_titular.primer_nombre, obj.id_persona_titular.segundo_nombre,
                            obj.id_persona_titular.primer_apellido, obj.id_persona_titular.segundo_apellido]
            nombre_persona_titular = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_titular = nombre_persona_titular if nombre_persona_titular != "" else None
        return nombre_persona_titular
    
    def get_label(self, obj):
        label = [obj.identificacion_doc_en_expediente, obj.nombre_asignado_documento]
        nombre_persona_titular = self.get_nombre_persona_titular(obj)
        
        if obj.codigo_tipologia_doc_prefijo:
            label.append(str(obj.codigo_tipologia_doc_prefijo))
        if obj.codigo_tipologia_doc_consecutivo:
            label.append(str(obj.codigo_tipologia_doc_consecutivo))
        if obj.codigo_tipologia_doc_agno:
            label.append(str(obj.codigo_tipologia_doc_agno))
        if nombre_persona_titular:
            label.append(str(nombre_persona_titular))
            
        label = '-'.join(item for item in label if item is not None)
        label = label if label != "" else None
        
        return label
    
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = [
            'id_documento_de_archivo_exped',
            'id_expediente_documental',
            'identificacion_doc_en_expediente',
            'nombre_asignado_documento',
            'codigo_tipologia_doc_prefijo',
            'codigo_tipologia_doc_consecutivo',
            'codigo_tipologia_doc_agno',
            'id_persona_titular',
            'nombre_persona_titular',
            'label',
            'orden_en_expediente',
            'es_un_archivo_anexo',
            'id_doc_de_arch_del_cual_es_anexo',
            'palabras_clave_documento'
        ]

class ConsultaExpedientesDocumentosGetByIdSerializer(serializers.ModelSerializer):
    fecha_creacion_doc = serializers.DateTimeField(format="%d/%m/%Y")
    fecha_incorporacion_doc_a_Exp = serializers.DateTimeField(format="%d/%m/%Y")
    numero_anexos = serializers.SerializerMethodField()
    origen_archivo = serializers.CharField(source='get_cod_origen_archivo_display', read_only=True, default=None)
    categoria_archivo = serializers.CharField(source='get_cod_categoria_archivo_display', read_only=True, default=None)
    nombre_tipologia = serializers.CharField(source='id_tipologia_documental.nombre', read_only=True, default=None)
    ruta_archivo = serializers.FileField(source='id_archivo_sistema.ruta_archivo', default=None)
    
    def get_numero_anexos(self, obj):
        numero_anexos = 0
        if not obj.es_un_archivo_anexo:
            numero_anexos = DocumentosDeArchivoExpediente.objects.filter(id_expediente_documental=obj.id_expediente_documental.id_expediente_documental, es_un_archivo_anexo=True)
            numero_anexos = numero_anexos.count()
            
        return numero_anexos
    
    class Meta:
        model =  DocumentosDeArchivoExpediente
        fields = [
            'id_documento_de_archivo_exped',
            'id_expediente_documental',
            'identificacion_doc_en_expediente',
            'fecha_creacion_doc',
            'fecha_incorporacion_doc_a_Exp',
            'numero_anexos',
            'cod_origen_archivo',
            'origen_archivo',
            'cod_categoria_archivo',
            'categoria_archivo',
            'id_tipologia_documental',
            'nombre_tipologia',
            'nro_folios_del_doc',
            'asunto',
            'descripcion',
            'ruta_archivo'
        ]




#IndiceElectronicoXML
class DocsIndiceElectronicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docs_IndiceElectronicoExp
        fields = '__all__'

class IndiceElectronicoXMLSerializer(serializers.ModelSerializer):
    documentos = DocsIndiceElectronicoSerializer(many=True, read_only=True)

    class Meta:
        model = IndicesElectronicosExp
        fields = '__all__'
        
class EliminacionHistorialGetSerializer(serializers.ModelSerializer):
    desc_estado = serializers.CharField(source='get_estado_display', read_only=True)
    dias_restantes = serializers.SerializerMethodField()
    
    def get_dias_restantes(self, obj):
        dias_restantes = 0
        if obj.id_estado == 'P':
            fecha_max_eliminacion = obj.fecha_publicacion + timedelta(days=obj.dias_publicacion)
            dias_restantes = (fecha_max_eliminacion - datetime.now()).days
            dias_restantes = dias_restantes if dias_restantes > 0 else 0
        return dias_restantes

    def get_nombre_persona_elimino(self, obj):
        nombre_persona_titular_exp_complejo = None
        if obj.id_persona_elimino:
            nombre_list = [obj.id_persona_elimino.primer_nombre, obj.id_persona_elimino.segundo_nombre,
                            obj.id_persona_elimino.primer_apellido, obj.id_persona_elimino.segundo_apellido]
            nombre_persona_titular_exp_complejo = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_titular_exp_complejo = nombre_persona_titular_exp_complejo if nombre_persona_titular_exp_complejo != "" else None
        return nombre_persona_titular_exp_complejo
    
    class Meta:
        model =  EliminacionDocumental
        fields = '__all__'
        
# class InventarioCreateSerializer(serializers.ModelSerializer):
#     desc_estado = serializers.CharField(source='get_estado_display', read_only=True)
#     dias_restantes = serializers.SerializerMethodField()
    
#     def get_dias_restantes(self, obj):
#         dias_restantes = 0
#         if obj.id_estado == 'P':
#             fecha_max_eliminacion = obj.fecha_publicacion + timedelta(days=obj.dias_publicacion)
#             dias_restantes = (fecha_max_eliminacion - datetime.now()).days
#             dias_restantes = dias_restantes if dias_restantes > 0 else 0
#         return dias_restantes

#     def get_nombre_persona_elimino(self, obj):
#         nombre_persona_titular_exp_complejo = None
#         if obj.id_persona_elimino:
#             nombre_list = [obj.id_persona_elimino.primer_nombre, obj.id_persona_elimino.segundo_nombre,
#                             obj.id_persona_elimino.primer_apellido, obj.id_persona_elimino.segundo_apellido]
#             nombre_persona_titular_exp_complejo = ' '.join(item for item in nombre_list if item is not None)
#             nombre_persona_titular_exp_complejo = nombre_persona_titular_exp_complejo if nombre_persona_titular_exp_complejo != "" else None
#         return nombre_persona_titular_exp_complejo
    
#     class Meta:
#         model =  InventarioDocume
#         fields = '__all__'