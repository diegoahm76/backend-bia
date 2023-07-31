from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max 

from gestion_documental.models.depositos_models import Deposito, EstanteDeposito


#DEPOSITOS

class DepositoCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Deposito
        fields = '__all__'

class DepositoDeleteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Deposito
        fields = '__all__'

class DepositoUpdateSerializer(serializers.ModelSerializer):
    
    def validate_orden_ubicacion_por_entidad(self, nuevo_orden):

        # Obtener el orden actual del depósito
        orden_actual = self.instance.orden_ubicacion_por_entidad

        if nuevo_orden != orden_actual:

            maximo_orden = Deposito.objects.aggregate(max_orden=Max('orden_ubicacion_por_entidad')).get('max_orden')
            self.instance.orden_ubicacion_por_entidad = maximo_orden + 1
            self.instance.save()
         

            if nuevo_orden > orden_actual:
                
                # Desplazar los depósitos siguientes hacia abajo
                depositos = Deposito.objects.filter(orden_ubicacion_por_entidad__gt=orden_actual, orden_ubicacion_por_entidad__lte=nuevo_orden).order_by('orden_ubicacion_por_entidad')  
                
                for deposito in depositos:
                    deposito.orden_ubicacion_por_entidad = deposito.orden_ubicacion_por_entidad - 1
                    deposito.save()

            elif nuevo_orden < orden_actual:
        
                # Desplazar los depósitos hacia arriba
                depositos = Deposito.objects.filter(orden_ubicacion_por_entidad__lt=orden_actual, orden_ubicacion_por_entidad__gte=nuevo_orden).order_by('-orden_ubicacion_por_entidad')  
                
                for deposito in depositos:
                    deposito.orden_ubicacion_por_entidad = deposito.orden_ubicacion_por_entidad + 1
                    deposito.save()		  	                  

        return nuevo_orden
        
    class Meta:
        model =  Deposito
        fields = '__all__'



class DepositoGetSerializer(serializers.ModelSerializer):
    nombre_sucursal = serializers.ReadOnlyField(source='id_sucursal_entidad.descripcion_sucursal', default=None)
    municipio=serializers.ReadOnlyField(source='id_sucursal_entidad.municipio', default=None)
    class Meta:
        model =  Deposito
        fields = ['nombre_deposito','identificacion_por_entidad','orden_ubicacion_por_entidad','direccion_deposito','cod_municipio_nal','cod_pais_exterior','id_sucursal_entidad','nombre_sucursal','municipio','activo']

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#ESTANTES

#Crear estante
class EstanteDepositoCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'
 
#Buscar_deposito
class  EstanteDepositoSearchSerializer(serializers.ModelSerializer):
    nombre_sucursal = serializers.ReadOnlyField(source='id_sucursal_entidad.descripcion_sucursal', default=None)
    
    class Meta:
        model =  Deposito
        fields = ['orden_ubicacion_por_entidad','nombre_deposito','identificacion_por_entidad','nombre_sucursal']


#Listar_orden_siguiente_estante
class  EstanteDepositoGetOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'


#Cambiar_orden_estante
class EstanteDepositoChangeOrdenSerializer(serializers.ModelSerializer):

    def validate_orden_ubicacion_por_deposito(self, nuevo_orden):

        # Obtener el orden actual del depósito
        orden_actual = self.instance.orden_ubicacion_por_deposito

        if nuevo_orden != orden_actual:

            maximo_orden = EstanteDeposito.objects.aggregate(max_orden=Max('orden_ubicacion_por_deposito')).get('max_orden')
            self.instance.orden_ubicacion_por_deposito = maximo_orden + 1
            self.instance.save()
         

            if nuevo_orden > orden_actual:
                
                # Desplazar los depósitos siguientes hacia abajo
                estantes = EstanteDeposito.objects.filter(orden_ubicacion_por_deposito__gt=orden_actual, orden_ubicacion_por_deposito__lte=nuevo_orden).order_by('orden_ubicacion_por_deposito')  
                
                for estante in estantes:
                    estante.orden_ubicacion_por_deposito = estante.orden_ubicacion_por_deposito - 1
                    estante.save()

            elif nuevo_orden < orden_actual:
        
                # Desplazar los depósitos hacia arriba
                estantes = EstanteDeposito.objects.filter(orden_ubicacion_por_deposito__lt=orden_actual, orden_ubicacion_por_deposito__gte=nuevo_orden).order_by('-orden_ubicacion_por_deposito')  
                
                for estante in estantes:
                    estante.orden_ubicacion_por_deposito = estante.orden_ubicacion_por_deposito + 1
                    estante.save()		  	                  

        return nuevo_orden
        
    class Meta:
        model =  EstanteDeposito
        fields = ['orden_ubicacion_por_deposito']

        