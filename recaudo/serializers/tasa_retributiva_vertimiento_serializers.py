from gestion_documental.serializers.pqr_serializers import ArchivosSerializer
from gestion_documental.models.expedientes_models import ArchivosDigitales
from recaudo.models.tasa_retributiva_vertimiento_models import documento_formulario_recuado
from rest_framework import serializers



class documento_formulario_recuados_serializer(serializers.ModelSerializer):
    class Meta:
        model = documento_formulario_recuado
        fields = '__all__'


class documento_formulario_recuados_Getserializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    ruta_archivo = serializers.SerializerMethodField()
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
    
    def get_ruta_archivo(self, obj):
    
        archivo = ArchivosDigitales.objects.filter(id_archivo_digital = obj.id_archivo_sistema.id_archivo_digital).first()
        data = ArchivosSerializer(archivo).data
        return data