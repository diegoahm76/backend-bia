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
from django.db import transaction
from datetime import datetime,date,timedelta
from gestion_documental.models.depositos_models import  CarpetaCaja, Deposito, EstanteDeposito, BandejaEstante, CajaBandeja
from gestion_documental.serializers.depositos_serializers import BandejaEstanteCreateSerializer, BandejaEstanteDeleteSerializer, BandejaEstanteMoveSerializer, BandejaEstanteSearchSerializer, BandejaEstanteUpDateSerializer, BandejasByEstanteListSerializer, CajaBandejaCreateSerializer, CajaBandejaMoveSerializer, CajaBandejaUpDateSerializer, CajaEstanteDeleteSerializer, CajaEstanteSearchAdvancedSerializer, CajaEstanteSearchSerializer, CajasByBandejaListSerializer, CarpetaCajaCreateSerializer, CarpetaCajaDeleteSerializer, CarpetaCajaSearchSerializer, CarpetaCajaUpDateSerializer, CarpetasByCajaListSerializer, DepositoCreateSerializer, DepositoDeleteSerializer, DepositoSearchSerializer, DepositoUpdateSerializer, EstanteDepositoCreateSerializer,DepositoGetSerializer, EstanteDepositoDeleteSerializer, EstanteDepositoSearchSerializer, EstanteDepositoGetOrdenSerializer, EstanteDepositoUpDateSerializer, EstanteGetByDepositoSerializer, MoveEstanteSerializer
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
    
    def get(self, request):
        maximo_orden = Deposito.objects.aggregate(max_orden=Max('orden_ubicacion_por_entidad'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden'] + 1
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)
       
#FILTRO_DEPOSITOS_POR_IDENTIFICACION_&_NOMBRE
class DepositoSearch(generics.ListAPIView):
    serializer_class = DepositoSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        nombre_deposito = self.request.query_params.get('nombre_deposito', '').strip()
        identificacion_por_entidad = self.request.query_params.get('identificacion_por_entidad', '').strip()

        # Filtrar por nombre_deposito, identificacion_por_entidad y ordenar por orden_ubicacion_por_entidad
        queryset = Deposito.objects.all()

        if nombre_deposito:
            queryset = queryset.filter(nombre_deposito__icontains=nombre_deposito)

        if identificacion_por_entidad:
            queryset = queryset.filter(identificacion_por_entidad__icontains=identificacion_por_entidad)

        queryset = queryset.order_by('orden_ubicacion_por_entidad')  # Ordenar de forma ascendente

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_200_OK)

        serializer = DepositoSearchSerializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


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

        queryset = queryset.order_by('orden_ubicacion_por_entidad')  # Ordenar de forma ascendente

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
    
    def get(self, request):
        maximo_orden = EstanteDeposito.objects.aggregate(max_orden=Max('orden_ubicacion_por_deposito'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden'] + 1
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)
        
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
            max_orden = maximo_orden['max_orden'] + 1

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

#LISTAR_BANDEJAS_POR ESTANTE
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
            max_orden = maximo_orden['max_orden'] + 1

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
    

#BUSCAR_ESTANTE(CAJAS)
class CajaEstanteSearch(generics.ListAPIView):
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
            estantes = estantes.filter(orden_ubicacion_por_entante=orden_estante)

        return estantes

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_200_OK)

        serialized_data = []
        for estante in queryset:
            # Obtener la bandeja correspondiente
            bandeja = BandejaEstante.objects.filter(id_estante_deposito=estante.id_estante_deposito).first()
            if bandeja:
                serialized_data.append({
                    'orden_ubicacion_por_estante': bandeja.orden_ubicacion_por_estante,
                    'nombre_deposito': estante.id_deposito.nombre_deposito,
                    'identificacion_deposito': estante.id_deposito.identificacion_por_entidad,
                    'identificacion_por_estante': bandeja.identificacion_por_estante,
                })

        # Ordenar los datos por orden_ubicacion_por_estante de forma ascendente
        serialized_data.sort(key=lambda x: x['orden_ubicacion_por_estante'])

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serialized_data
        }, status=status.HTTP_200_OK)

#EDITAR_CAJAS(CAJAS)
class cajaBandejaUpDate(generics.UpdateAPIView):
    serializer_class = CajaBandejaUpDateSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]

    def put (self,request, pk):
        try:
            caja = CajaBandeja.objects.filter(id_caja_estante=pk).first()
        except CajaBandeja.DoesNotExist:
            return Response({'error': 'La bandeja no existe.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CajaBandejaUpDateSerializer(caja, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True, 'detail': 'La bandeja se ha actualizado correctamente.'},
                         status=status.HTTP_200_OK)
    

#MOVER CAJA
class CajaEstanteBandejaMove(generics.UpdateAPIView):
    serializer_class = CajaBandejaMoveSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, id_caja_estante):
        # Obtener la caja actual
        caja = get_object_or_404(CajaBandeja, id_caja_estante=id_caja_estante)

        # Obtener los datos de destino desde la solicitud
        identificacion_bandeja_destino = request.data.get('identificacion_bandeja_destino')
        identificacion_estante_destino = request.data.get('identificacion_estante_destino')
        identificacion_deposito_destino = request.data.get('identificacion_deposito_destino')

        
        # Validar si la bandeja de destino existe
        bandeja_destino = BandejaEstante.objects.filter(identificacion_por_estante=identificacion_bandeja_destino).first()
        if not bandeja_destino:
            return Response({'success': False, 'detail': 'No se encontró la bandeja de destino especificada.'}, status=status.HTTP_404_NOT_FOUND)

        # Validar si el estante de destino existe
        estante_destino = EstanteDeposito.objects.filter(identificacion_por_deposito=identificacion_estante_destino).first()
        if not estante_destino:
            return Response({'success': False, 'detail': 'No se encontró el estante de destino especificado.'}, status=status.HTTP_404_NOT_FOUND)

        # Validar si el depósito de destino existe
        deposito_destino = Deposito.objects.filter(identificacion_por_entidad=identificacion_deposito_destino).first()
        if not deposito_destino:
            return Response({'success': False, 'detail': 'No se encontró el depósito de destino especificado.'}, status=status.HTTP_404_NOT_FOUND)

       
        # Verificar si la caja tiene un expediente asociado
        if CarpetaCaja.id_expediente is not None:
            # Validar si el depósito de destino existe y está activo
            deposito_destino = Deposito.objects.filter(identificacion_por_entidad=identificacion_deposito_destino, activo=True).first()
            if not deposito_destino:
                return Response({'success': False, 'detail': 'La caja tiene un expediente asociado y no puede ser movida a un depósito inactivo.'}, status=status.HTTP_400_BAD_REQUEST)

            
        # Retener los datos actuales de la caja (sin cambios)
        caja_actual_data = {
            'identificacion_bandeja': caja.id_bandeja_estante.identificacion_por_estante,
            'identificacion_estante': caja.id_bandeja_estante.id_estante_deposito.identificacion_por_deposito,
            'identificacion_deposito': caja.id_bandeja_estante.id_estante_deposito.id_deposito.identificacion_por_entidad,
        }

        # Realizar el cambio de la caja a la bandeja de destino
        caja.id_bandeja_estante = bandeja_destino
        caja.save()

        # Retornar los datos de caja actual y caja destino
        return Response({
            'success': True,
            'detail': 'Caja movida exitosamente.',
            'id_caja':id_caja_estante,
            'caja_actual': caja_actual_data,
            'caja_destino': {
                'identificacion_bandeja': identificacion_bandeja_destino,
                'identificacion_estante': identificacion_estante_destino,
                'identificacion_deposito': identificacion_deposito_destino,
            },
        }, status=status.HTTP_200_OK)




#BUSQUEDA_AVANZADA_DE_CAJAS
class CajaEstanteSearchAdvanced(generics.ListAPIView):
    serializer_class = CajaEstanteSearchAdvancedSerializer
    permission_classes = [IsAuthenticated]
    
    def clean_search_param(self, param):
        # Convertir a minúsculas y eliminar espacios en blanco
        return param.lower().strip() if param else None

    def get_queryset(self):
        identificacion_deposito = self.clean_search_param(self.request.query_params.get('identificacion_deposito'))
        identificacion_estante = self.clean_search_param(self.request.query_params.get('identificacion_estante'))
        identificacion_bandeja = self.clean_search_param(self.request.query_params.get('identificacion_bandeja'))
        identificacion_caja = self.clean_search_param(self.request.query_params.get('identificacion_caja'))
        orden_caja = self.clean_search_param(self.request.query_params.get('orden_caja'))

        queryset = CajaBandeja.objects.all()

        if identificacion_deposito:
            queryset = queryset.filter(id_bandeja_estante__id_estante_deposito__id_deposito__identificacion_por_entidad__icontains=identificacion_deposito)

        if identificacion_estante:
            queryset = queryset.filter(id_bandeja_estante__id_estante_deposito__identificacion_por_deposito__icontains=identificacion_estante)

        if identificacion_bandeja:
            queryset = queryset.filter(id_bandeja_estante__identificacion_por_estante__icontains=identificacion_bandeja)

        if identificacion_caja:
            queryset = queryset.filter(identificacion_por_bandeja__icontains=identificacion_caja)

        if orden_caja:
            queryset = queryset.filter(orden_ubicacion_por_bandeja=orden_caja)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron cajas que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_200_OK)

        serialized_data = []
        for caja in queryset:
            serialized_data.append({
                'identificacion_deposito': caja.id_bandeja_estante.id_estante_deposito.id_deposito.identificacion_por_entidad,
                'identificacion_estante': caja.id_bandeja_estante.id_estante_deposito.identificacion_por_deposito,
                'identificacion_bandeja': caja.id_bandeja_estante.identificacion_por_estante,
                'identificacion_caja': caja.identificacion_por_bandeja,
                'orden_caja': caja.orden_ubicacion_por_bandeja,
            })

        return Response({
            'success': True,
            'detail': 'Se encontraron las siguientes cajas.',
            'data': serialized_data
        }, status=status.HTTP_200_OK)
    
#ELIMINAR_CAJA
class CajaEstanteDelete(generics.DestroyAPIView):
        
    serializer_class = CajaEstanteDeleteSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        
        caja = CajaBandeja.objects.filter(id_caja_estante=pk).first()

        if not caja:
            raise ValidationError("No existe la caja que desea eliminar")

        tiene_carpetas = CarpetaCaja.objects.filter(id_carpeta_caja=pk).exists()

        if tiene_carpetas:
                return Response({'success': False, 'detail': 'No se puede eliminar la caja porque tiene una o mas carpetas asociadas a esta caja.'},
                                status=status.HTTP_400_BAD_REQUEST)

        #Reordenar
        cajas = CajaBandeja.objects.filter(orden_ubicacion_por_bandeja__gt=caja.orden_ubicacion_por_bandeja).order_by('orden_ubicacion_por_bandeja') 
        caja.delete()

        for caja in cajas:
            caja.orden_ubicacion_por_bandeja = caja.orden_ubicacion_por_bandeja - 1
            caja.save()

        return Response({'success': True, 'detail': 'Se eliminó correctamente la caja seleccionada.'}, status=status.HTTP_200_OK)  

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



########################## CRUD CARPETAS ##########################


#CREAR_CARPETAS
class CarpetaCajaCreate(generics.CreateAPIView):

    serializer_class = CarpetaCajaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = CarpetaCaja.objects.all()
    
    def post(self,request):
        
        try:
            data_in = request.data
            orden_siguiente = CarpetaCajaGetOrden()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')
            print(maximo_orden)
            data_in['orden_ubicacion_por_caja']=maximo_orden+1
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
        

#ORDEN CARPETAS
class CarpetaCajaGetOrden(generics.ListAPIView):
     
     def get(self, request):
        maximo_orden = CarpetaCaja.objects.aggregate(max_orden=Max('orden_ubicacion_por_caja'))

        # Verificar si el valor del orden es nulo
        if not maximo_orden['max_orden']:
            max_orden = 0
        else:
            max_orden = maximo_orden['max_orden'] + 1

        return Response({
            'success': True,
            'orden_siguiente': max_orden
        }, status=status.HTTP_200_OK)         
    
#BUSQUEDA_CAJAS(CARPETAS)
class CarpetaCajaSearch(generics.ListAPIView):
    serializer_class = CarpetaCajaSearchSerializer
    permission_classes = [IsAuthenticated]
    
    def clean_search_param(self, param):
        # Convertir a minúsculas y eliminar espacios en blanco
        return param.lower().strip() if param else None

    def get_queryset(self):
        identificacion_deposito = self.clean_search_param(self.request.query_params.get('identificacion_deposito'))
        identificacion_estante = self.clean_search_param(self.request.query_params.get('identificacion_estante'))
        identificacion_bandeja = self.clean_search_param(self.request.query_params.get('identificacion_bandeja'))
        identificacion_caja = self.clean_search_param(self.request.query_params.get('identificacion_caja'))
        orden_caja = self.clean_search_param(self.request.query_params.get('orden_caja'))

        queryset = CajaBandeja.objects.all()

        if identificacion_deposito:
            queryset = queryset.filter(id_bandeja_estante__id_estante_deposito__id_deposito__identificacion_por_entidad__icontains=identificacion_deposito)

        if identificacion_estante:
            queryset = queryset.filter(id_bandeja_estante__id_estante_deposito__identificacion_por_deposito__icontains=identificacion_estante)

        if identificacion_bandeja:
            queryset = queryset.filter(id_bandeja_estante__identificacion_por_estante__icontains=identificacion_bandeja)

        if identificacion_caja:
            queryset = queryset.filter(identificacion_por_bandeja__icontains=identificacion_caja)

        if orden_caja:
            queryset = queryset.filter(orden_ubicacion_por_bandeja=orden_caja)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron cajas que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_200_OK)

        serialized_data = []
        for caja in queryset:
            serialized_data.append({
                'identificacion_deposito': caja.id_bandeja_estante.id_estante_deposito.id_deposito.identificacion_por_entidad,
                'identificacion_estante': caja.id_bandeja_estante.id_estante_deposito.identificacion_por_deposito,
                'identificacion_bandeja': caja.id_bandeja_estante.identificacion_por_estante,
                'identificacion_caja': caja.identificacion_por_bandeja,
                'orden_caja': caja.orden_ubicacion_por_bandeja,
            })

        return Response({
            'success': True,
            'detail': 'Se encontraron las siguientes cajas.',
            'data': serialized_data
        }, status=status.HTTP_200_OK)
    
#ELIMINAR_CARPETA
class CarpetaCajaDelete(generics.DestroyAPIView):
        
    serializer_class = CarpetaCajaDeleteSerializer
    queryset = CarpetaCaja.objects.all()
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        carpeta = self.get_object()

        if not carpeta:
            return Response({'detail': 'La carpeta no existe.'}, status=status.HTTP_404_NOT_FOUND)

        # Verificar si la carpeta tiene un expediente asociado
        if carpeta.id_expediente is not None:
            return Response({'detail': 'No se puede eliminar la carpeta porque tiene uno o mas expedientes asociado.'}, status=status.HTTP_400_BAD_REQUEST)

        #Reordenar
        carpetas = CarpetaCaja.objects.filter(orden_ubicacion_por_caja__gt=carpeta.orden_ubicacion_por_caja).order_by('orden_ubicacion_por_caja') 
        carpeta.delete()

        for carpeta in carpetas:
            carpeta.orden_ubicacion_por_caja = carpeta.orden_ubicacion_por_caja - 1
            carpeta.save()

        return Response({'success': True, 'detail': 'Se eliminó correctamente la carpeta seleccionada.'}, status=status.HTTP_200_OK)


#LISTAR_CARPETAS_POR_CAJA
class CarpetasByCajaList(generics.ListAPIView):
    serializer_class = CarpetasByCajaListSerializer
    queryset = CarpetaCaja.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        carpeta = CarpetaCaja.objects.filter(id_caja_bandeja=pk)
        serializer = self.serializer_class(carpeta,many=True)
        
        if not Deposito:
            raise NotFound("El registro del estante que busca, no se encuentra registrado")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)
    
#EDITAR_CARPETAS
class CarpetaCajaUpDate(generics.UpdateAPIView):
    serializer_class = CarpetaCajaUpDateSerializer
    queryset = CarpetaCaja.objects.all()
    permission_classes = [IsAuthenticated]

    def put (self,request, pk):
        try:
            caja = CarpetaCaja.objects.filter(id_carpeta_caja=pk).first()
        except CarpetaCaja.DoesNotExist:
            return Response({'error': 'La bandeja no existe.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CarpetaCajaUpDateSerializer(caja, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success': True, 'detail': 'La carpeta se ha actualizado correctamente.'},
                         status=status.HTTP_200_OK)