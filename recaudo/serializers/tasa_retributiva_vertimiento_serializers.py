from gestion_documental.serializers.pqr_serializers import ArchivosSerializer
from gestion_documental.models.expedientes_models import ArchivosDigitales
from recaudo.models.tasa_retributiva_vertimiento_models import CaptacionMensualAgua, FactoresUtilizacion, InformacionFuente, T0444Formulario, documento_formulario_recuado
from rest_framework import serializers



class documento_formulario_recuados_serializer(serializers.ModelSerializer):
    class Meta:
        model = documento_formulario_recuado
        fields = '__all__'




class documento_formulario_recuados_Getserializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    ruta_archivo = serializers.SerializerMethodField()
    formato = serializers.SerializerMethodField()
    fecha_creacion_doc = serializers.SerializerMethodField()
    class Meta:
        model = documento_formulario_recuado
        fields = '__all__'
    def get_nombre_completo(self, obj):
        nombre_completo = None
        nombre_list = [obj.id_persona.primer_nombre, obj.id_persona.segundo_nombre,
                        obj.id_persona.primer_apellido, obj.id_persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    
    def get_formato(self, obj):
    
        archivo = ArchivosDigitales.objects.filter(id_archivo_digital = obj.id_archivo_sistema.id_archivo_digital).first()
        data = ArchivosSerializer(archivo).data
        return data['formato']
    
    def get_fecha_creacion_doc(self, obj):
    
        archivo = ArchivosDigitales.objects.filter(id_archivo_digital = obj.id_archivo_sistema.id_archivo_digital).first()
        data = ArchivosSerializer(archivo).data
        return data['fecha_creacion_doc']    
    
    def get_ruta_archivo(self, obj):
    
        archivo = ArchivosDigitales.objects.filter(id_archivo_digital = obj.id_archivo_sistema.id_archivo_digital).first()
        data = ArchivosSerializer(archivo).data
        return data
    

#-----------------------------------------------------------------------------------
    


class InformacionFuenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacionFuente
        fields = '__all__'

# class CoordenadasSitioCaptacionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CoordenadasSitioCaptacion
#         fields = '__all__'

class FactoresUtilizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoresUtilizacion
        fields = '__all__'

class CaptacionMensualAguaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaptacionMensualAgua
        fields = '__all__'


class T0444FormularioSerializer(serializers.ModelSerializer):
    informacionFuentesAbastecimiento = InformacionFuenteSerializer(many=True)
    # coordenadasSitioCaptacion = CoordenadasSitioCaptacionSerializer()
    factoresUtilizacion = FactoresUtilizacionSerializer()
    captacionesMensualesAgua = CaptacionMensualAguaSerializer(many=True)

    class Meta:
        model = T0444Formulario
        fields = '__all__'

    def create(self, validated_data):
        informacion_fuentes_data = validated_data.pop('informacionFuentesAbastecimiento')
        # coordenadas_sitio_data = validated_data.pop('coordenadasSitioCaptacion')
        factores_utilizacion_data = validated_data.pop('factoresUtilizacion')
        captaciones_mensuales_data = validated_data.pop('captacionesMensualesAgua')

        informacion_fuentes = [InformacionFuente.objects.create(**item) for item in informacion_fuentes_data]
        # coordenadas_sitio = CoordenadasSitioCaptacion.objects.create(**coordenadas_sitio_data)
        factores_utilizacion = FactoresUtilizacion.objects.create(**factores_utilizacion_data)
        captaciones_mensuales = [CaptacionMensualAgua.objects.create(**item) for item in captaciones_mensuales_data]

        formulario = T0444Formulario.objects.create(
            # coordenadasSitioCaptacion=coordenadas_sitio,
            factoresUtilizacion=factores_utilizacion,
            **validated_data
        )

        formulario.informacionFuentesAbastecimiento.set(informacion_fuentes)
        formulario.captacionesMensualesAgua.set(captaciones_mensuales)

        return formulario
