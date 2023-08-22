from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max 

from gestion_documental.models.depositos_models import  CarpetaCaja, Deposito, EstanteDeposito, BandejaEstante, CajaBandeja


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
        fields = ['id_deposito','nombre_deposito','identificacion_por_entidad','orden_ubicacion_por_entidad','direccion_deposito','cod_municipio_nal','cod_pais_exterior','id_sucursal_entidad','nombre_sucursal','municipio','activo']

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
        fields = ['id_deposito','orden_ubicacion_por_entidad','nombre_deposito','identificacion_por_entidad','nombre_sucursal']


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
        fields = ['id_estante_deposito','identificacion_por_deposito','orden_ubicacion_por_deposito']

#Eliminar_Estante
class EstanteDepositoDeleteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'

#Listar_estantes_por_deposito
class EstanteGetByDepositoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = ['id_estante_deposito','orden_ubicacion_por_deposito','identificacion_por_deposito']

#Mover_estante
class MoveEstanteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'


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
    nombre_deposito = serializers.CharField(source='id_deposito.nombre_deposito', read_only=True)
    identificacion_deposito = serializers.CharField(source='id_deposito.identificacion_por_entidad', read_only=True)

    class Meta:
        model = EstanteDeposito
        fields = [ 'orden_ubicacion_por_deposito','identificacion_por_deposito', 'nombre_deposito', 'identificacion_deposito']
 

#Mover_bandeja
class BandejaEstanteMoveSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  BandejaEstante
        fields = '__all__'

#Listar_Bandejas_por_estante
class BandejasByEstanteListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  BandejaEstante
        fields = ['id_estante_deposito','orden_ubicacion_por_estante','identificacion_por_estante']

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

#Listar_cajas_por_bandeja
class  CajasByBandejaListSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CajaBandeja
        fields = '__all__'


#Buscar_estante(Cajas)
class CajaEstanteSearchSerializer(serializers.ModelSerializer):
    nombre_deposito = serializers.CharField(source='id_deposito.nombre_deposito', read_only=True)
    identificacion_deposito = serializers.CharField(source='id_deposito.identificacion_por_entidad', read_only=True)

    class Meta:
        model = EstanteDeposito
        fields = [ 'orden_ubicacion_por_deposito','identificacion_por_deposito', 'nombre_deposito', 'identificacion_deposito','identificacion_por_estante']

#Editar_cajas
class CajaBandejaUpDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CajaBandeja
        fields = ['identificacion_por_bandeja', 'orden_ubicacion_por_bandeja']

    def validate_orden_ubicacion_por_bandeja(self, nuevo_orden):
        orden_actual = self.instance.orden_ubicacion_por_bandeja

        if nuevo_orden != orden_actual:
            # Obtener el número máximo de orden actual en las cajas
            maximo_orden = CajaBandeja.objects.aggregate(max_orden=Max('orden_ubicacion_por_bandeja')).get('max_orden')
            self.instance.orden_ubicacion_por_bandeja = maximo_orden + 1
            self.instance.save()

            if nuevo_orden > orden_actual:
                # Desplazar las cajas siguientes hacia abajo
                cajas = CajaBandeja.objects.filter(id_bandeja_estante=self.instance.id_bandeja_estante, orden_ubicacion_por_bandeja__gt=orden_actual, orden_ubicacion_por_bandeja__lte=nuevo_orden).order_by('orden_ubicacion_por_bandeja')

                for caja in cajas:
                    caja.orden_ubicacion_por_bandeja = caja.orden_ubicacion_por_bandeja - 1
                    caja.save()

            elif nuevo_orden < orden_actual:
                # Desplazar las cajas hacia arriba
                cajas = CajaBandeja.objects.filter(id_bandeja_estante=self.instance.id_bandeja_estante, orden_ubicacion_por_bandeja__lt=orden_actual, orden_ubicacion_por_bandeja__gte=nuevo_orden).order_by('-orden_ubicacion_por_bandeja')

                for caja in cajas:
                    caja.orden_ubicacion_por_bandeja = caja.orden_ubicacion_por_bandeja + 1
                    caja.save()

        return nuevo_orden
    
#Mover_caja_a_otra_bandeja
class  CajaBandejaMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CajaBandeja
        fields = '__all__'

#Busqueda_avanzada_de_cajas
class  CajaEstanteSearchAdvancedSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CajaBandeja
        fields = '__all__'

#Eliminar_caja
class  CajaEstanteDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CajaBandeja
        fields = '__all__'


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

######################## SERIALIZERS CARPETA ########################

#Crear_carpeta
class CarpetaCajaCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  CarpetaCaja
        fields = '__all__'

#Listar_orden_siguiente_carpeta
class  CarpetaCajaGetOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CarpetaCaja
        fields = '__all__'

#Buscar_caja(carpeta)
class  CarpetaCajaSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CajaBandeja
        fields = '__all__'

#Eliminar_carpeta
class  CarpetaCajaDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CarpetaCaja
        fields = '__all__'

#Listar_carpetas_por caja
class  CarpetasByCajaListSerializer(serializers.ModelSerializer):
    class Meta:
        model =  CarpetaCaja
        fields = ['id_carpeta_caja','orden_ubicacion_por_caja','identificacion_por_caja']

#Editar_carpetas
class CarpetaCajaUpDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarpetaCaja
        fields = ['identificacion_por_caja', 'orden_ubicacion_por_caja']

    def validate_orden_ubicacion_por_caja(self, nuevo_orden):
        orden_actual = self.instance.orden_ubicacion_por_caja

        if nuevo_orden != orden_actual:
            # Obtener el número máximo de orden actual en las carpeta
            maximo_orden = CarpetaCaja.objects.aggregate(max_orden=Max('orden_ubicacion_por_caja')).get('max_orden')
            self.instance.orden_ubicacion_por_caja = maximo_orden + 1
            self.instance.save()

            if nuevo_orden > orden_actual:
                # Desplazar las carpeta siguientes hacia abajo
                carpetas = CarpetaCaja.objects.filter(id_bandeja_estante=self.instance.id_caja_bandeja, orden_ubicacion_por_caja__gt=orden_actual, orden_ubicacion_por_caja__lte=nuevo_orden).order_by('orden_ubicacion_por_caja')

                for carpeta in carpetas:
                    carpeta.orden_ubicacion_por_caja = carpeta.orden_ubicacion_por_caja - 1
                    carpeta.save()

            elif nuevo_orden < orden_actual:
                # Desplazar las carpetas hacia arriba
                carpetas = CarpetaCaja.objects.filter(id_caja_bandeja=self.instance.id_caja_bandeja, orden_ubicacion_por_caja__lt=orden_actual, orden_ubicacion_por_caja__gte=nuevo_orden).order_by('-orden_ubicacion_por_caja')

                for carpeta in carpetas:
                    carpeta.orden_ubicacion_por_caja = carpeta.orden_ubicacion_por_caja + 1
                    carpeta.save()

        return nuevo_orden