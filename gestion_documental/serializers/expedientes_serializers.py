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

    class Meta:
        model = DocumentosDeArchivoExpediente
        fields = '__all__'
        read_only_fields = ['fecha_incorporacion_doc_a_Exp']


   

class ListarTipologiasSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipologiasDoc
        fields = ['id_tipologia_documental', 'nombre']
  

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

    def save(self, subcarpeta='',**kwargs):
        try:
            archivo = self.validated_data['ruta_archivo']
            nombre_archivo = archivo.name
            Subcarpeta=subcarpeta
            # Utiliza la ruta de medios para guardar el archivo
            
            ruta_completa = os.path.join(settings.MEDIA_ROOT,Subcarpeta, nombre_archivo)
            
            if not os.path.relpath(ruta_completa, settings.MEDIA_ROOT):
                raise serializers.ValidationError(f"La subcarpeta '{subcarpeta}' no existe en la ruta especificada.")
            print("hola?")
            # Guarda el archivo
            with open(ruta_completa, 'wb') as destination:
                for chunk in archivo.chunks():
                    destination.write(chunk)


            self.validated_data['ruta_archivo'] = os.path.relpath(ruta_completa, settings.MEDIA_ROOT)

            return super().save(**kwargs)

        except FileNotFoundError as e:

             raise serializers.ValidationError('Error:No es posible guardar el archivo.')
