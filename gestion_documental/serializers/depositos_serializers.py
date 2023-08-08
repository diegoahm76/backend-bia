from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max 

from gestion_documental.models.depositos_models import  Deposito, EstanteDeposito, BandejaEstante, CajaBandeja


######################### SERIALIZERS DEPOSITO #########################

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


######################### SERIALIZERS ESTANTE #########################

#Crear_estante
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
class EstanteDepositoUpDateSerializer(serializers.ModelSerializer):

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
        fields = ['identificacion_por_deposito','orden_ubicacion_por_deposito']

#Eliminar_Estante
class EstanteDepositoDeleteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'

#Listar_estantes_por_deposito
class EstanteGetByDepositoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = ['orden_ubicacion_por_deposito','identificacion_por_deposito']

#Mover_estante
class MoveEstanteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'

#Listar_Bandejas_por_estante
class BandejasByEstanteListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  BandejaEstante
        fields = ['orden_ubicacion_por_estante','identificacion_por_estante']

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

######################### SERIALIZERS BANDEJA #########################


#Crear_bandeja
class BandejaEstanteCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  BandejaEstante
        fields = '__all__'

#Listar_orden_siguiente_bandeja
class  BandejaEstanteGetOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model =  BandejaEstante
        fields = '__all__'

 #Editar_bandejas       
class  BandejaEstanteUpDateSerializer(serializers.ModelSerializer):
   class Meta:
        model =  BandejaEstante
        fields = ['identificacion_por_estante','orden_ubicacion_por_estante'] 	   
    
   def validate_orden_ubicacion_por_estante(self, nuevo_orden):

        # Obtener el orden actual del depósito
        orden_actual = self.instance.orden_ubicacion_por_estante

        if nuevo_orden != orden_actual:

            maximo_orden = BandejaEstante.objects.aggregate(max_orden=Max('orden_ubicacion_por_estante')).get('max_orden')
            self.instance.orden_ubicacion_por_estante = maximo_orden + 1
            self.instance.save()
         

            if nuevo_orden > orden_actual:
                
                # Desplazar los depósitos siguientes hacia abajo
                bandejas = BandejaEstante.objects.filter(orden_ubicacion_por_estante__gt=orden_actual, orden_ubicacion_por_estante__lte=nuevo_orden).order_by('orden_ubicacion_por_estante')  
                
                for bandeja in bandejas:
                    bandeja.orden_ubicacion_por_estante = bandeja.orden_ubicacion_por_estante - 1
                    bandeja.save()

            elif nuevo_orden < orden_actual:
        
                # Desplazar los depósitos hacia arriba
                bandejas = BandejaEstante.objects.filter(orden_ubicacion_por_estante__lt=orden_actual, orden_ubicacion_por_estante__gte=nuevo_orden).order_by('-orden_ubicacion_por_estante')  
                
                for bandeja in bandejas:
                    bandeja.orden_ubicacion_por_estante = bandeja.orden_ubicacion_por_estante + 1
                    bandeja.save()		  	                  

        
        return nuevo_orden		 
                  
#Eliminar_bandeja
class BandejaEstanteDeleteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  BandejaEstante
        fields = '__all__'

#Buscar_estante(mover_bandejas)
class BandejaEstanteSearchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = ['orden_ubicacion_por_deposito','identificacion_por_deposito','id_deposito']


#Mover_bandeja
class BandejaEstanteMoveSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  BandejaEstante
        fields = '__all__'

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

######################## SERIALIZERS CAJA ########################

class CajaBandejaCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  CajaBandeja
        fields = '__all__'

#Listar_orden_siguiente_bandeja
class  CajaBandejaGetOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CajaBandeja
        fields = '__all__'