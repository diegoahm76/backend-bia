import secrets
from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max 
from gestion_documental.models.expedientes_models import ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura
from gestion_documental.models.trd_models import TablaRetencionDocumental, TipologiasDoc
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.conf import settings
import os


######################### SERIALIZERS EXPEDIENTE #########################

#Buscar-Expediente
class ExpedienteSearchSerializer(serializers.ModelSerializer):

    nombre_serie_origen = serializers.ReadOnlyField(source='id_serie_origen.nombre', default=None)
    nombre_subserie_origen = serializers.ReadOnlyField(source='id_subserie_origen.nombre', default=None)
    nombre_unidad_org = serializers.ReadOnlyField(source='id_und_seccion_propietaria_serie.nombre', default=None)
    nombre_trd_origen = serializers.ReadOnlyField(source='id_trd_origen.nombre', default=None)

    class Meta:
        model =  ExpedientesDocumentales
        fields = ['codigo_exp_und_serie_subserie','id_expediente_documental','titulo_expediente','id_und_seccion_propietaria_serie','nombre_unidad_org','id_serie_origen','nombre_serie_origen','id_subserie_origen','nombre_subserie_origen','nombre_subserie_origen','id_trd_origen','nombre_trd_origen','fecha_apertura_expediente']


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
        fields = ('orden_en_expediente','id_documento_de_archivo_exped', 'id_expediente_documental', 'nombre_asignado_documento', 'id_tipologia_documental',  'nombre_tipologia')

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
