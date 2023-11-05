from seguimiento_planes.models.pnd_models import PlanNacionalDesarrollo, Sector, Programa, Producto, PndIndicador
from rest_framework import serializers


class PlanNacionalDesarrolloSerializer(serializers.ModelSerializer):

    # nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)

    class Meta:
        model = PlanNacionalDesarrollo
        fields = '__all__'

class SectorSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Sector
        fields = '__all__'

class ProgramaSerializer(serializers.ModelSerializer):
            
    class Meta:
        model = Programa
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
                
    class Meta:
        model = Producto
        fields = '__all__'

class PndIndicadorSerializer(serializers.ModelSerializer):
                        
    class Meta:
        model = PndIndicador
        fields = '__all__'


# class DatosSerializerNombre(serializers.ModelSerializer):

#     nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)

#     class Meta:
#         model = PlanNacionalDesarrollo
#         fields = '__all__'
