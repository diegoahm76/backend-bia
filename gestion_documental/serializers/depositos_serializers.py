from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max 

from gestion_documental.models.depositos_models import  CarpetaCaja, Deposito, EstanteDeposito, BandejaEstante, CajaBandeja


######################### SERIALIZERS DEPOSITO #########################

#Crear_Deposito
class DepositoCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Deposito
        fields = '__all__'
    def validate_identificacion_por_entidad(self, value):
        if Deposito.objects.filter(identificacion_por_entidad=value).exists():
            raise serializers.ValidationError("Ya existe un depósito con esta identificación por entidad.")
        return value




#Borrar_Deposito
class DepositoDeleteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Deposito
        fields = '__all__'

#Actualizar_Deposito
class DepositoUpdateSerializer(serializers.ModelSerializer):

    def validate_identificacion_por_entidad(self, value):
        if self.instance:  # Si estamos actualizando un objeto existente
            queryset = Deposito.objects.exclude(pk=self.instance.pk)
        else:
            queryset = Deposito.objects.all()

        if queryset.filter(identificacion_por_entidad=value).exists():
            raise serializers.ValidationError("Esta identificación ya está en uso en otro deposito.")

        return value

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
        

#LISTAR_DEPOSITOS_POR_ID
class DepositoGetSerializer(serializers.ModelSerializer):
    nombre_sucursal = serializers.ReadOnlyField(source='id_sucursal_entidad.descripcion_sucursal', default=None)
    municipio=serializers.ReadOnlyField(source='id_sucursal_entidad.municipio', default=None)
    class Meta:
        model =  Deposito
        fields = ['id_deposito','nombre_deposito','identificacion_por_entidad','orden_ubicacion_por_entidad','direccion_deposito','cod_municipio_nal','cod_pais_exterior','id_sucursal_entidad','nombre_sucursal','municipio','activo']


#Filtro_deposito
class  DepositoSearchSerializer(serializers.ModelSerializer):
    nombre_sucursal = serializers.ReadOnlyField(source='id_sucursal_entidad.descripcion_sucursal', default=None)
    
    class Meta:
        model =  Deposito
        fields = '__all__'

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


######################### SERIALIZERS ESTANTE #########################

#Crear_estante
class EstanteDepositoCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'

    def validate_orden_ubicacion_por_deposito(self, value):
        if EstanteDeposito.objects.filter(orden_ubicacion_por_deposito=value).exists():
            raise serializers.ValidationError("Ya existe un estante con esta identificación.")
        return value

 
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


#Actualizar_estante
class EstanteDepositoUpDateSerializer(serializers.ModelSerializer):

    def validate_identificacion_por_deposito(self, value):
        if self.instance:  # Si estamos actualizando un objeto existente
            queryset = EstanteDeposito.objects.exclude(pk=self.instance.pk)
        else:
            queryset = EstanteDeposito.objects.all()

        if queryset.filter(identificacion_por_deposito=value).exists():
            raise serializers.ValidationError("Esta identificación ya está en uso en otro estante.")

        return value

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
        fields = ['id_estante_deposito','orden_ubicacion_por_deposito','identificacion_por_deposito','id_deposito']



#Mover_estante
class MoveEstanteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  EstanteDeposito
        fields = '__all__'


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

######################### SERIALIZERS BANDEJA #########################


#Crear_bandeja
class BandejaEstanteCreateSerializer(serializers.ModelSerializer):

    def validate_orden_identificacion_por_estante(self, value):
        if BandejaEstante.objects.filter(identificacion_por_estante=value).exists():
            raise serializers.ValidationError("Ya existe un bandeja con esta identificación.")
        return value

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
        fields = ['id_bandeja_estante','identificacion_por_estante','orden_ubicacion_por_estante'] 	   

    def validate_identificacion_por_estante(self, value):
        if self.instance:  # Si estamos actualizando un objeto existente
            queryset = BandejaEstante.objects.exclude(pk=self.instance.pk)
        else:
            queryset = BandejaEstante.objects.all()

        if queryset.filter(identificacion_por_estante=value).exists():
            raise serializers.ValidationError("Esta identificación ya está en uso en otro deposito.")

        return value
    
    def validate_orden_ubicacion_por_estante(self, nuevo_orden):
        # Obtener el orden actual de las bandejas
        orden_actual = self.instance.orden_ubicacion_por_estante

        if nuevo_orden != orden_actual:

            maximo_orden = BandejaEstante.objects.aggregate(max_orden=Max('orden_ubicacion_por_estante')).get('max_orden')
            self.instance.orden_ubicacion_por_estante = maximo_orden + 1
            self.instance.save()
         

            if nuevo_orden > orden_actual:
                
                # Desplazar las bandejas siguientes hacia abajo
                bandejas = BandejaEstante.objects.filter(orden_ubicacion_por_estante__gt=orden_actual, orden_ubicacion_por_estante__lte=nuevo_orden).order_by('orden_ubicacion_por_estante')  
                
                for bandeja in bandejas:
                    bandeja.orden_ubicacion_por_estante = bandeja.orden_ubicacion_por_estante - 1
                    bandeja.save()

            elif nuevo_orden < orden_actual:
        
                # Desplazar las bandejas hacia arriba
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
        fields = [ 'orden_ubicacion_por_deposito','identificacion_por_deposito', 'nombre_deposito', 'identificacion_deposito','id_estante_deposito','id_deposito']
 

#Mover_bandeja
class BandejaEstanteMoveSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  BandejaEstante
        fields = '__all__'

#Listar_Bandejas_por_estante
class BandejasByEstanteListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  BandejaEstante
        fields = ['id_bandeja_estante','orden_ubicacion_por_estante','identificacion_por_estante']

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

######################## SERIALIZERS CAJA ########################

class CajaBandejaCreateSerializer(serializers.ModelSerializer):
    def validate_identificacion_por_bandeja(self, value):
        if CajaBandeja.objects.filter(identificacion_por_bandeja=value).exists():
            raise serializers.ValidationError("Ya existe un caja con esta identificación.")
        return value
    
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
        fields = ['id_caja_bandeja','identificacion_por_bandeja', 'orden_ubicacion_por_bandeja']

    def validate_identificacion_por_bandeja(self, value):
        if self.instance:  # Si estamos actualizando un objeto existente
            queryset = CajaBandeja.objects.exclude(pk=self.instance.pk)
        else:
            queryset = CajaBandeja.objects.all()

        if queryset.filter(identificacion_por_bandeja=value).exists():
            raise serializers.ValidationError("Esta identificación ya está en uso en otra caja.")

        return value    

    def validate_orden_ubicacion_por_bandeja(self, nuevo_orden):

        # Obtener el orden actual del depósito
        orden_actual = self.instance.orden_ubicacion_por_bandeja

        if nuevo_orden != orden_actual:

            maximo_orden = CajaBandeja.objects.aggregate(max_orden=Max('orden_ubicacion_por_bandeja')).get('max_orden')
            self.instance.orden_ubicacion_por_bandeja = maximo_orden + 1
            self.instance.save()
         

            if nuevo_orden > orden_actual:
                
                # Desplazar las cajas siguientes hacia abajo
                cajas = CajaBandeja.objects.filter(orden_ubicacion_por_bandeja__gt=orden_actual, orden_ubicacion_por_bandeja__lte=nuevo_orden).order_by('orden_ubicacion_por_bandeja')  
                
                for caja in cajas:
                    caja.orden_ubicacion_por_bandeja = caja.orden_ubicacion_por_bandeja - 1
                    caja.save()

            elif nuevo_orden < orden_actual:
        
                # Desplazar las cajas hacia arriba
                cajas = CajaBandeja.objects.filter(orden_ubicacion_por_bandeja__lt=orden_actual, orden_ubicacion_por_bandeja__gte=nuevo_orden).order_by('-orden_ubicacion_por_bandeja')  
                
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



#Filtro_bandejas_por_caja
class  CajaListBandejaInfoSerializer(serializers.ModelSerializer):
       
    class Meta:
        model = BandejaEstante
        fields = '__all__'


#Filtro_estante_por_caja
class  CajaListEstanteInfoSerializer(serializers.ModelSerializer):
       
    class Meta:
        model = EstanteDeposito
        fields = '__all__'

#Filtro_deposito_por_caja
class  CajaListDepositoInfoSerializer(serializers.ModelSerializer):
       
    class Meta:
        model = Deposito
        fields = '__all__'
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

######################## SERIALIZERS CARPETA ########################

#Crear_carpeta
class CarpetaCajaCreateSerializer(serializers.ModelSerializer):

    def validate_identificacion_por_caja(self, value):
        if CarpetaCaja.objects.filter(identificacion_por_caja=value).exists():
            raise serializers.ValidationError("Ya existe un carpeta con esta identificación.")
        return value
    
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
        fields = ['id_carpeta_caja','identificacion_por_caja', 'orden_ubicacion_por_caja']
    
    def validate_identificacion_por_caja(self, value):
        if self.instance:  # Si estamos actualizando un objeto existente
            queryset = CarpetaCaja.objects.exclude(pk=self.instance.pk)
        else:
            queryset = CarpetaCaja.objects.all()

        if queryset.filter(identificacion_por_caja=value).exists():
            raise serializers.ValidationError("Esta identificación ya está en uso en otra carpeta.")

        return value

    def validate_orden_ubicacion_por_caja(self, nuevo_orden):

        # Obtener el orden actual del depósito
        orden_actual = self.instance.orden_ubicacion_por_caja

        if nuevo_orden != orden_actual:

            maximo_orden = CarpetaCaja.objects.aggregate(max_orden=Max('orden_ubicacion_por_caja')).get('max_orden')
            self.instance.orden_ubicacion_por_caja = maximo_orden + 1
            self.instance.save()
         

            if nuevo_orden > orden_actual:
                
                # Desplazar las cajas siguientes hacia abajo
                carpetas = CarpetaCaja.objects.filter(orden_ubicacion_por_caja__gt=orden_actual,orden_ubicacion_por_caja__lte=nuevo_orden).order_by('orden_ubicacion_por_caja')  
                
                for carpeta in carpetas:
                    carpeta.orden_ubicacion_por_caja = carpeta.orden_ubicacion_por_caja - 1
                    carpeta.save()

            elif nuevo_orden < orden_actual:
        
                # Desplazar las cajas hacia arriba
                carpetas = CarpetaCaja.objects.filter(orden_ubicacion_por_caja__lt=orden_actual,orden_ubicacion_por_caja__gte=nuevo_orden).order_by('-orden_ubicacion_por_caja')  
                
                for carpeta in carpetas:
                    carpeta.orden_ubicacion_por_caja = carpeta.orden_ubicacion_por_caja + 1
                    carpeta.save()		  	                 
        
        return nuevo_orden		
