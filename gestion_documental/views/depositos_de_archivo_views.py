import copy
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max 
from django.db.models import Q
from datetime import datetime,date,timedelta
from gestion_documental.models.depositos_models import  Deposito, EstanteDeposito, BandejaEstante, CajaBandeja
from gestion_documental.serializers.depositos_serializers import BandejaEstanteCreateSerializer, BandejaEstanteDeleteSerializer, BandejaEstanteMoveSerializer, BandejaEstanteSearchSerializer, BandejaEstanteUpDateSerializer, BandejasByEstanteListSerializer, CajaBandejaCreateSerializer, CajasByBandejaListSerializer, DepositoCreateSerializer, DepositoDeleteSerializer, DepositoUpdateSerializer, EstanteDepositoCreateSerializer,DepositoGetSerializer, EstanteDepositoDeleteSerializer, EstanteDepositoSearchSerializer, EstanteDepositoGetOrdenSerializer, EstanteDepositoUpDateSerializer, EstanteGetByDepositoSerializer, MoveEstanteSerializer
from seguridad.utils import Util


########################## CRUD DE DEPOSITO ##########################

#CREAR_DEPOSITO
class DepositoCreate(generics.CreateAPIView):
    serializer_class = DepositoCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Deposito.objects.all()
    
    def post(self,request):
        
        try:
            data_in = request.data
            #data_in['activo']=True
            orden_siguiente = DepositoGetOrden()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')
            print(maximo_orden)
            data_in['orden_ubicacion_por_entidad']=maximo_orden+1
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            deposito =serializer.save()


            #AUDITORIA 
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"IdDeposito":deposito.id_deposito,"NombreDeposito":deposito.nombre_deposito}
            #valores_actualizados = {'current': instance, 'previous': instance_previous}
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 121,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
                #"valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data)

            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)

#BORRAR_DEPOSITO       
class DepositoDelete(generics.DestroyAPIView):
    serializer_class = DepositoDeleteSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        deposito = Deposito.objects.filter(id_deposito=pk).first()
        estantes = EstanteDeposito.objects.filter(id_deposito=pk).first()
       
        
        if not deposito:
            raise ValidationError("No existe la deposito a eliminar")
        
        if estantes:
            raise ValidationError("No se puede Eliminar una deposito, si tiene estantes asignadas.")
        
        
        tiene_bandejas = BandejaEstante.objects.filter(id_estante_deposito__id_deposito=pk).exists()

        if tiene_bandejas:
            return Response({'success': False, 'detail': 'No se puede eliminar el depósito porque tiene bandejas asociadas a él.'},
                            status=status.HTTP_400_BAD_REQUEST)

        tiene_cajas = CajaBandeja.objects.filter(id_bandeja_estante__id_estante_deposito__id_deposito=pk).exists()

        if tiene_cajas:
            return Response({'success': False, 'detail': 'No se puede eliminar el depósito porque tiene una o más cajas asociadas a él.'},
                            status=status.HTTP_400_BAD_REQUEST)
        #reordenar
        depositos = Deposito.objects.filter(orden_ubicacion_por_entidad__gt=deposito.orden_ubicacion_por_entidad).order_by('orden_ubicacion_por_entidad') 
        deposito.delete()
        
        for deposito in depositos:
            deposito.orden_ubicacion_por_entidad = deposito.orden_ubicacion_por_entidad - 1
            deposito.save()
        
      


        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        descripcion = {"IdDeposito":deposito.id_deposito,"NombreDeposito":deposito.nombre_deposito}
        auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 121,
                "cod_permiso": "BO",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
                
            }
        Util.save_auditoria(auditoria_data) 
        return Response({'success':True,'detail':'Se elimino el deposito seleccionada.'},status=status.HTTP_200_OK)


#ACTUALIZAR_DEPOSITO
class DepositoUpdate(generics.UpdateAPIView):
    serializer_class = DepositoUpdateSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
        try:
            data = request.data
            deposito = Deposito.objects.filter(id_deposito=pk).first()
            
            if not deposito:
                raise NotFound("No se existe el deposito que trata de Actualizar.")
            
            instance_previous=copy.copy(deposito)
            serializer = self.serializer_class(deposito,data=data)
            serializer.is_valid(raise_exception=True)

            serializer.save()

            #AUDITORIA ACTUALIZAR 
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"IdDeposito":deposito.id_deposito,"NombreDeposito":deposito.nombre_deposito}
            valores_actualizados = {'current': deposito, 'previous': instance_previous}
            auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : 121,
                    "cod_permiso": "AC",
                    "subsistema": 'GEST',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                    "valores_actualizados": valores_actualizados
                }
            Util.save_auditoria(auditoria_data) 

            return Response({'success':True,'detail':"Se actualizo el deposito Correctamente."},status=status.HTTP_200_OK)
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)


#LISTAR_TODOS_LOS_DEPOSITOS
class DepositoGet(generics.ListAPIView):
    serializer_class = DepositoGetSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

#LISTAR_DEPOSITOS_POR_ID
class DepositoGetById(generics.ListAPIView):
    serializer_class = DepositoGetSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        deposito = Deposito.objects.filter(id_deposito=pk)
        serializer = self.serializer_class(deposito,many=True)
        
        if not Deposito:
            raise NotFound("El registro del deposito que busca, no se encuentra registrado")

        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)
    
#ORDEN_DEPOSITO    
class DepositoGetOrden(generics.ListAPIView):
    serializer_class = DepositoGetSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        maximo_orden = Deposito.objects.aggregate(max_orden=Max('orden_ubicacion_por_entidad'))
        #serializer = self.serializer_class(deposito,many=True)
        
        if not maximo_orden:
            raise NotFound("El registro del deposito que busca, no se encuentra registrado")
        return Response({'success':True,'orden_siguiente':maximo_orden['max_orden']},status=status.HTTP_200_OK)
        #return JsonResponse({'maximo_orden': maximo_orden['max_orden']+1},status=status.HTTP_200_OK)
        #return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



########################## CRUD ESTANTE DEPOSITO ##########################

#CREAR_ESTANTE
class EstanteDepositoCreate(generics.CreateAPIView):

    serializer_class = EstanteDepositoCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = EstanteDeposito.objects.all()
    
    def post(self,request):
        
        try:
            data_in = request.data
            #data_in['activo']=True
            orden_siguiente = EstanteDepositoGetOrden()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')
            print(maximo_orden)
            data_in['orden_ubicacion_por_deposito']=maximo_orden+1
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()


            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)
        

#BUSCAR DEPOSITO POR NOMBRE, IDENTIFICACION, SUCURSAL EN ESTANTE
class EstanteDepositoSearch(generics.ListAPIView):
    serializer_class = EstanteDepositoSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        nombre_deposito = self.request.query_params.get('nombre_deposito', '').strip()
        identificacion_por_entidad = self.request.query_params.get('identificacion_por_entidad', '').strip()
        nombre_sucursal = self.request.query_params.get('nombre_sucursal', '').strip()

        # Filtrar por nombre_deposito, identificacion_por_entidad y nombre_sucursal (unión de parámetros)
        queryset = Deposito.objects.all()

        if nombre_deposito:
            queryset = queryset.filter(nombre_deposito__icontains=nombre_deposito)

        if identificacion_por_entidad:
            queryset = queryset.filter(identificacion_por_entidad__icontains=identificacion_por_entidad)

        if nombre_sucursal:
            queryset = queryset.filter(id_sucursal_entidad__descripcion_sucursal__icontains=nombre_sucursal)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_200_OK)

        serializer = EstanteDepositoSearchSerializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    


#ORDEN ESTANTE 
class EstanteDepositoGetOrden(generics.ListAPIView):
     
    serializer_class = EstanteDepositoGetOrdenSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        maximo_orden = EstanteDeposito.objects.aggregate(max_orden=Max('orden_ubicacion_por_deposito'))
        #serializer = self.serializer_class(deposito,many=True)
        
        if not maximo_orden or 0:
            raise NotFound("El registro del deposito que busca, no se encuentra registrado")
        return Response({
            'success':True,
            'orden_siguiente':maximo_orden['max_orden']},
            status=status.HTTP_200_OK)
        
#EDITAR ESTANTE
class EstanteDepositoUpDate(generics.UpdateAPIView):
    serializer_class = EstanteDepositoGetOrdenSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]

    def put (self,request, pk):
        try:
            estante = EstanteDeposito.objects.filter(id_estante_deposito=pk).first()
        except EstanteDeposito.DoesNotExist:
            return Response({'error': 'El estante no existe.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EstanteDepositoUpDateSerializer(estante, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True, 'detail': 'Orden del estante cambiado correctamente.'},
                         status=status.HTTP_200_OK)

#BORRAR_ESTANTE
class EstanteDepositoDelete(generics.DestroyAPIView):
        
    serializer_class = EstanteDepositoDeleteSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        
        estante = EstanteDeposito.objects.filter(id_estante_deposito=pk).first()

        if not estante:
            raise ValidationError("No existe el estante que desea eliminar")

        # Verificar si el estante tiene bandejas
        tiene_bandejas = BandejaEstante.objects.filter(id_estante_deposito=pk).exists()

        if tiene_bandejas:
            # Verificar si alguna bandeja tiene cajas asociadas
            tiene_cajas = CajaBandeja.objects.filter(id_bandeja_estante__id_estante_deposito=pk).exists()

            if tiene_cajas:
                return Response({'success': False, 'detail': 'No se puede eliminar el estante porque tiene cajas asociadas a una o más bandejas.'},
                                status=status.HTTP_400_BAD_REQUEST)

        # Reordenar
        estantes = EstanteDeposito.objects.filter(orden_ubicacion_por_deposito__gt=estante.orden_ubicacion_por_deposito).order_by('orden_ubicacion_por_deposito') 
        estante.delete()

        for estante in estantes:
            estante.orden_ubicacion_por_deposito = estante.orden_ubicacion_por_deposito - 1
            estante.save()

        return Response({'success': True, 'detail': 'Se eliminó el estante seleccionado.'}, status=status.HTTP_200_OK)    

#LISTADO_DE_ESTANTES_POR_DEPOSITO
class EstanteGetByDeposito(generics.ListAPIView):
    serializer_class = EstanteGetByDepositoSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        estantes = EstanteDeposito.objects.filter(id_deposito=pk)
        
        if not estantes.exists():
            raise NotFound("El registro del depósito que busca no se encuentra registrado.")
        
        serializer = self.serializer_class(estantes, many=True)
        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    
#MOVER_ESTANTE
class MoveEstante(generics.UpdateAPIView):
    serializer_class = MoveEstanteSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, identificacion_por_deposito):
        # Paso 1: Obtener el estante a mover
        estante = get_object_or_404(EstanteDeposito, identificacion_por_deposito=identificacion_por_deposito)

        # Paso 2: Verificar si el estante tiene bandejas
        tiene_bandejas = BandejaEstante.objects.filter(id_estante_deposito=estante.id_estante_deposito).exists()
        
        if tiene_bandejas:
            return Response({'success': False, 'detail': 'No se puede cambiar de depósito porque el estante tiene bandejas asociadas.'}, status=status.HTTP_400_BAD_REQUEST)

        # Paso 3: Obtener el depósito actual
        deposito_actual = f"{estante.id_deposito.identificacion_por_entidad}, {estante.id_deposito.nombre_deposito}"

        # Paso 4: Obtener el depósito de destino del cuerpo de la solicitud
        identificacion_por_entidad_destino = request.data.get('identificacion_por_entidad_destino')
        nombre_deposito_destino = request.data.get('nombre_deposito_destino')
        deposito_destino = f"{identificacion_por_entidad_destino}, {nombre_deposito_destino}"

        # Paso 5: Verificar si el depósito de destino existe
        try:
            deposito_destino_obj = Deposito.objects.get(identificacion_por_entidad=identificacion_por_entidad_destino, nombre_deposito=nombre_deposito_destino)
        except Deposito.DoesNotExist:
            return Response({'success': False, 'detail': 'El depósito de destino no existe.'}, status=status.HTTP_400_BAD_REQUEST)

        # Paso 6: Actualizar el depósito del estante
        estante.id_deposito = deposito_destino_obj
        estante.save()

        return Response({'success': True, 
                        'detail': 'El estante se ha cambiado de depósito exitosamente.',
                        'identificacion_del_estante': estante.identificacion_por_deposito,
                        'deposito_actual': deposito_actual, 
                        'deposito_destino': deposito_destino},
                          status=status.HTTP_200_OK)

#LISTAR_BANDEJAS_POR_ESTANTE
class BandejasByEstanteList(generics.ListAPIView):
    serializer_class = BandejasByEstanteListSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        bandeja = BandejaEstante.objects.filter(id_estante_deposito=pk)
        serializer = self.serializer_class(bandeja,many=True)
        
        if not Deposito:
            raise NotFound("El registro del estante que busca, no se encuentra registrado")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

########################## CRUD BANDEJAS ##########################


#CREAR_BANDEJA
class BandejaEstanteCreate(generics.CreateAPIView):

    serializer_class = BandejaEstanteCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = BandejaEstante.objects.all()
    
    def post(self, request):
        
        try:
            data_in = request.data
            orden_siguiente = BandejaEstanteGetOrden()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')

            # Verificar si maximo_orden es None y asignar 1 en ese caso
            if maximo_orden is None or 0:
                maximo_orden = 1
            else:
                maximo_orden += 1

            data_in['orden_ubicacion_por_estante'] = maximo_orden
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                'success': True,
                'detail': 'Se crearon los registros correctamente',
                'data': serializer.data},
                status=status.HTTP_201_CREATED)
        except ValidationError as e:
            error_message = {'error': e.detail}
            raise ValidationError(e.detail)

#ORDEN BANDEJAS
class BandejaEstanteGetOrden(generics.ListAPIView):
     
    def get(self, request):
        maximo_orden = BandejaEstante.objects.aggregate(max_orden=Max('orden_ubicacion_por_estante'))

        # Verificar si el valor del orden es nulo
        if not maximo_orden['max_orden']:
            max_orden = 0
        else:
            max_orden = maximo_orden['max_orden']

        return Response({
            'success': True,
            'orden_siguiente': max_orden
        }, status=status.HTTP_200_OK)
    
#EDITAR_BANDEJA
class BandejaEstanteUpDate(generics.UpdateAPIView):
    serializer_class = BandejaEstanteUpDateSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]

    def put (self,request, pk):
        try:
            bandeja = BandejaEstante.objects.filter(id_bandeja_estante=pk).first()
        except BandejaEstante.DoesNotExist:
            return Response({'error': 'La bandeja no existe.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BandejaEstanteUpDateSerializer(bandeja, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True, 'detail': 'La bandeja se ha actualizado correctamente.'},
                         status=status.HTTP_200_OK)

#ELIMINAR_BANDEJA

class BandejaEstanteDelete(generics.DestroyAPIView):
        
    serializer_class = BandejaEstanteDeleteSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        
        bandeja = BandejaEstante.objects.filter(id_bandeja_estante=pk).first()

        if not bandeja:
            raise ValidationError("No existe la bandeja que desea eliminar")

        tiene_cajas = CajaBandeja.objects.filter(id_bandeja_estante=pk).exists()

        if tiene_cajas:
                return Response({'success': False, 'detail': 'No se puede eliminar la bandeja porque tiene una o mas cajas asociadas a esta bandeja.'},
                                status=status.HTTP_400_BAD_REQUEST)

        #Reordenar
        bandejas = BandejaEstante.objects.filter(orden_ubicacion_por_estante__gt=bandeja.orden_ubicacion_por_estante).order_by('orden_ubicacion_por_estante') 
        bandeja.delete()

        for bandeja in bandejas:
            bandeja.orden_ubicacion_por_estante = bandeja.orden_ubicacion_por_estante - 1
            bandeja.save()

        return Response({'success': True, 'detail': 'Se eliminó correctamente la bandeja seleccionada.'}, status=status.HTTP_200_OK)  

#BUSCAR_ESTANTE(MOVER_BANDEJAS)
class BandejaEstanteSearch(generics.ListAPIView):
    serializer_class = BandejaEstanteSearchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        nombre_deposito = self.request.query_params.get('nombre_deposito', '').strip()
        identificacion_estante = self.request.query_params.get('identificacion_estante', '').strip()
        orden_estante = self.request.query_params.get('orden_estante', '').strip()

        estantes = EstanteDeposito.objects.all()

        if nombre_deposito:
            estantes = estantes.filter(id_deposito__nombre_deposito__icontains=nombre_deposito) | \
                       estantes.filter(id_deposito__identificacion_por_entidad__icontains=nombre_deposito)
        
        if identificacion_estante:
            estantes = estantes.filter(identificacion_por_deposito__icontains=identificacion_estante)

        if orden_estante:
            estantes = estantes.filter(orden_ubicacion_por_deposito=orden_estante)

        return estantes

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

#MOVER_BANDEJA
class BandejaEstanteMove(generics.UpdateAPIView):
    serializer_class = BandejaEstanteMoveSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_bandeja_estante):
        bandeja = get_object_or_404(BandejaEstante, id_bandeja_estante=id_bandeja_estante)

        id_deposito_destino = request.data.get('id_deposito_destino')
        id_estante_destino = request.data.get('id_estante_destino')

        try:
            deposito_destino = Deposito.objects.get(id_deposito=id_deposito_destino)
        except Deposito.DoesNotExist:
            return Response({'success': False, 'detail': 'El depósito de destino no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            estante_destino = EstanteDeposito.objects.get(id_estante_deposito=id_estante_destino)
        except EstanteDeposito.DoesNotExist:
            return Response({'success': False, 'detail': 'El estante de destino no existe.'}, status=status.HTTP_404_NOT_FOUND)

            
        # Verificar si la bandeja tiene cajas asociadas
        tiene_cajas = CajaBandeja.objects.filter(id_bandeja_estante=bandeja.id_bandeja_estante).exists()
        if tiene_cajas:
            return Response({'success': False, 'detail': 'No se puede mover la bandeja porque tiene cajas asociadas.'}, status=status.HTTP_400_BAD_REQUEST)

        id_deposito_destino = request.data.get('id_deposito_destino')
        id_estante_destino = request.data.get('id_estante_destino')

        # Obtener el depósito y estante de destino
        deposito_destino = get_object_or_404(Deposito, id_deposito=id_deposito_destino)
        estante_destino = get_object_or_404(EstanteDeposito, id_estante_deposito=id_estante_destino)

        # Realizar el cambio de depósito y estante
        bandeja.id_estante_deposito = estante_destino
        bandeja.save()

        return Response({
            'success': True,
            'detail': 'La Bandeja ha sido movida exitosamente.'
        }, status=status.HTTP_200_OK)

   
    
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

######################## CRUD CAJA ########################

#CREAR_CAJA
class CajaBandejaCreate(generics.CreateAPIView):

    serializer_class = CajaBandejaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = CajaBandeja.objects.all()
    
    def post(self,request):
        
        try:
            data_in = request.data
            #data_in['activo']=True
            orden_siguiente = CajaBandejaGetOrden()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')
            print(maximo_orden)
            data_in['orden_ubicacion_por_bandeja']=maximo_orden+1
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()


            return Response({'success':True,
                             'detail':'Se crearon los registros correctamente',
                             'data':serializer.data},
                             status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)
        
#ORDEN CAJAS
class CajaBandejaGetOrden(generics.ListAPIView):
     
    def get(self, request):
        maximo_orden = CajaBandeja.objects.aggregate(max_orden=Max('orden_ubicacion_por_bandeja'))

        # Verificar si el valor del orden es nulo
        if not maximo_orden['max_orden']:
            max_orden = 0
        else:
            max_orden = maximo_orden['max_orden']

        return Response({
            'success': True,
            'orden_siguiente': max_orden
        }, status=status.HTTP_200_OK)        
    
#LISTAR_CAJAS_POR_BANDEJA
class CajasByBandejaList(generics.ListAPIView):
    serializer_class = CajasByBandejaListSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        caja = CajaBandeja.objects.filter(id_bandeja_estante=pk)
        serializer = self.serializer_class(caja,many=True)
        
        if not Deposito:
            raise NotFound("El registro del estante que busca, no se encuentra registrado")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)