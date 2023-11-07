from seguimiento_planes.models.pnd_models import PlanNacionalDesarrollo, Sector, Programa, Producto, PndIndicador
from rest_framework import serializers


class PlanNacionalDesarrolloSerializer(serializers.ModelSerializer):

    # nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)

    class Meta:
        model = PlanNacionalDesarrollo
        fields = '__all__'

class SectorSerializer(serializers.ModelSerializer):

    nombre_plan = serializers.ReadOnlyField(source='id_plan_desarrollo.nombre_plan', default=None)
        
    class Meta:
        model = Sector
        fields = '__all__'

class ProgramaSerializer(serializers.ModelSerializer):

    nombre_sector = serializers.ReadOnlyField(source='id_sector.nombre_sector', default=None)
            
    class Meta:
        model = Programa
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):

    nombre_programa = serializers.ReadOnlyField(source='id_programa.nombre_programa', default=None)
                
    class Meta:
        model = Producto
        fields = '__all__'

class PndIndicadorSerializer(serializers.ModelSerializer):

    nombre_producto = serializers.ReadOnlyField(source='id_producto.nombre_producto', default=None)
             
    class Meta:
        model = PndIndicador
        fields = '__all__'


# class DatosSerializerNombre(serializers.ModelSerializer):

#     nombre_estacion = serializers.ReadOnlyField(source='id_estacion.nombre_estacion', default=None)

#     class Meta:
#         model = PlanNacionalDesarrollo
#         fields = '__all__'
