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
from datetime import datetime  
from django.db import transaction
from datetime import datetime,date,timedelta
from gestion_documental.models.depositos_models import  CarpetaCaja, Deposito, EstanteDeposito, BandejaEstante, CajaBandeja
from gestion_documental.serializers.depositos_serializers import CarpetaCajaGetOrdenSerializer, CarpetaCajaRotuloSerializer,BandejaEstanteCreateSerializer, BandejaEstanteDeleteSerializer, BandejaEstanteGetOrdenSerializer, BandejaEstanteMoveSerializer, BandejaEstanteSearchSerializer, BandejaEstanteUpDateSerializer, BandejaListCarpetaInfoSerializer, BandejasByEstanteListSerializer, CajaBandejaCreateSerializer, CajaBandejaGetOrdenSerializer, CajaListBandejaInfoSerializer, CajaBandejaMoveSerializer, CajaBandejaUpDateSerializer, CajaEstanteDeleteSerializer, CajaEstanteSearchAdvancedSerializer, CajaEstanteSearchSerializer, CajaListDepositoInfoSerializer, CajaListEstanteInfoSerializer, CajaRotuloSerializer, CajasByBandejaListSerializer, CarpetaCajaCreateSerializer, CarpetaCajaDeleteSerializer, CarpetaCajaMoveSerializer, CarpetaCajaSearchAdvancedSerializer, CarpetaCajaSearchSerializer, CarpetaCajaUpDateSerializer, CarpetaListCajaInfoSerializer, CarpetasByCajaListSerializer, DepositoCreateSerializer, DepositoDeleteSerializer, DepositoGetAllSerializer, DepositoListCarpetaInfoSerializer, DepositoSearchSerializer, DepositoUpdateSerializer, EstanteDepositoCreateSerializer,DepositoGetSerializer, EstanteDepositoDeleteSerializer, EstanteDepositoSearchSerializer, EstanteDepositoGetOrdenSerializer, EstanteDepositoUpDateSerializer, EstanteGetByDepositoSerializer, EstanteListCarpetaInfoSerializer, MoveEstanteSerializer
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
            orden_siguiente = DepositoGetOrdenActual()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')
            print(maximo_orden)
            data_in['orden_ubicacion_por_entidad']=  maximo_orden + 1
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
            raise ValidationError("No se puede Eliminar deposito, si tiene estantes asignadas.")
        
        
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
        return Response({'success':True,'detail':'Se elimino el deposito seleccionado.'},status=status.HTTP_200_OK)


#ACTUALIZAR_DEPOSITO
class DepositoUpdate(generics.UpdateAPIView):
    serializer_class = DepositoUpdateSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        instance_previous = copy.copy(instance)  # Guarda una copia del estado previo
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Obtener los depósitos y ordenarlos por orden_ubicacion_por_entidad
        depositos = Deposito.objects.all()
        depositos_ordenados = sorted(depositos, key=lambda dep: dep.orden_ubicacion_por_entidad)

        # Serializar y retornar los depósitos ordenados
        serializer_ordenados = self.get_serializer(depositos_ordenados, many=True)

        #AUDITORIA ACTUALIZAR 
        usuario = request.user.id_usuario
        direccion = Util.get_client_ip(request)
        descripcion = {"IdDeposito": instance.id_deposito, "NombreDeposito": instance.nombre_deposito}
        valores_actualizados = {'current': instance, 'previous': instance_previous}
        auditoria_data = {
            "id_usuario": usuario,
            "id_modulo": 121,
            "cod_permiso": "AC",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion, 
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data) 

        return Response(serializer_ordenados.data)
    


#LISTAR_TODOS_LOS_DEPOSITOS
class DepositoGet(generics.ListAPIView):
    serializer_class = DepositoGetSerializer
    queryset = Deposito.objects.all().order_by('orden_ubicacion_por_entidad')
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de depósitos registrados.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes depósitos ordenados por orden_ubicacion_por_entidad.',
            'data': serializer.data
        })
    

#LISTAR_DEPOSITOS_POR_ID
class DepositoGetById(generics.ListAPIView):
    serializer_class = DepositoGetSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        deposito = Deposito.objects.filter(id_deposito=pk).order_by('orden_ubicacion_por_entidad')
        serializer = self.serializer_class(deposito, many=True)
        
        if not deposito:
            raise NotFound("El registro del deposito que busca, no se encuentra registrado")

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializer.data}, status=status.HTTP_200_OK)
        
#ORDEN_DEPOSITO_SIGUIENTE    
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
       

#ORDEN_ACTUAL
class DepositoGetOrdenActual(generics.ListAPIView):
    serializer_class = DepositoGetSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = Deposito.objects.aggregate(max_orden=Max('orden_ubicacion_por_entidad'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden'] 
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)
        
#FILTRO_DEPOSITOS_POR_IDENTIFICACION_&_NOMBRE
class DepositoSearch(generics.ListAPIView):
    serializer_class = DepositoSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        nombre_deposito = self.request.query_params.get('nombre_deposito', '').strip()
        identificacion_por_entidad = self.request.query_params.get('identificacion_por_entidad', '').strip()
        id_deposito = self.request.query_params.get('id_deposito', '').strip()

        # Filtrar por nombre_deposito, identificacion_por_entidad y ordenar por orden_ubicacion_por_entidad
        queryset = Deposito.objects.all()

        if nombre_deposito:
            queryset = queryset.filter(nombre_deposito__icontains=nombre_deposito)

        if identificacion_por_entidad:
            queryset = queryset.filter(identificacion_por_entidad__icontains=identificacion_por_entidad)

        if id_deposito:
            queryset = queryset.filter(id_deposito=id_deposito)    

        queryset = queryset.order_by('orden_ubicacion_por_entidad')  # Ordenar de forma ascendente

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

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
            orden_siguiente = EstanteDepositoGetOrdenActual()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')

            print(maximo_orden)
            data_in['orden_ubicacion_por_deposito']=  maximo_orden + 1
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            estante =serializer.save()


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
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = EstanteDepositoSearchSerializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    


#ORDEN_SIGUIENTE_ESTANTE 
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


#ORDEN_ACTUAL_ESTANTE
class EstanteDepositoGetOrdenActual(generics.ListAPIView):
    serializer_class = EstanteDepositoGetOrdenSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = EstanteDeposito.objects.aggregate(max_orden=Max('orden_ubicacion_por_deposito'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden']
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)
    

#EDITAR_ESTANTE
class EstanteDepositoUpDate(generics.UpdateAPIView):
    serializer_class = EstanteDepositoUpDateSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Obtener los estantes y ordenarlos por orden_ubicacion_por_deposito
        estantes = EstanteDeposito.objects.all()
        estantes_ordenados = sorted(estantes, key=lambda estante: estante.orden_ubicacion_por_deposito)

        # Serializar y retornar los estantes ordenados
        serializer_ordenados = self.get_serializer(estantes_ordenados, many=True)
        return Response(serializer_ordenados.data)

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
        estantes = EstanteDeposito.objects.filter(id_deposito=pk).order_by('orden_ubicacion_por_deposito')
        
        if not estantes.exists():
            raise NotFound("El registro del depósito que busca no se encuentra registrado.")
        
        serializer = self.serializer_class(estantes, many=True)
        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

#LISTAR_TODOS_ESTANTES
class EstanteGetAll(generics.ListAPIView):
    serializer_class = EstanteGetByDepositoSerializer
    queryset = EstanteDeposito.objects.all().order_by('orden_ubicacion_por_deposito')
    permission_classes = []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de estantes registrados.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes depósitos ordenados por orden_ubicacion_por_deposito.',
            'data': serializer.data
        }) 
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

# #LISTAR_BANDEJAS_POR_ESTANTE
# class BandejasByEstanteList(generics.ListAPIView):
#     serializer_class = BandejasByEstanteListSerializer
#     queryset = BandejaEstante.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def get(self,request,pk):
#         bandeja = BandejaEstante.objects.filter(id_estante_deposito=pk)
#         serializer = self.serializer_class(bandeja,many=True)
        
#         if not Deposito:
#             raise NotFound("El registro del estante que busca, no se encuentra registrado")

#         return Response({'success':True,
#                          'detail':'Se encontraron los siguientes registros.',
#                          'data':serializer.data},status=status.HTTP_200_OK)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

########################## CRUD BANDEJAS ##########################


#CREAR_BANDEJA
class BandejaEstanteCreate(generics.CreateAPIView):

    serializer_class = BandejaEstanteCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = BandejaEstante.objects.all()
    
    def post(self,request):
        
        try:
            data_in = request.data
            orden_siguiente = BandejaEstanteGetOrdenActual()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')

            print(maximo_orden)
            data_in['orden_ubicacion_por_estante']=  maximo_orden +1
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            bandeja =serializer.save()


            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)

#ORDEN_BANDEJAS_SIGUIENTE
class BandejaEstanteGetOrden(generics.ListAPIView):
     
    serializer_class = BandejaEstanteGetOrdenSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = BandejaEstante.objects.aggregate(max_orden=Max('orden_ubicacion_por_estante'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden'] + 1
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)

    
#ORDEN_BANDEJAS_ACTUAL
class BandejaEstanteGetOrdenActual(generics.ListAPIView):
     
    serializer_class = BandejaEstanteGetOrdenSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        maximo_orden = BandejaEstante.objects.aggregate(max_orden=Max('orden_ubicacion_por_estante'))
        
        if not maximo_orden:
            raise NotFound("El registro del depósito que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden'] 
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)

    
#EDITAR_BANDEJA
class BandejaEstanteUpDate(generics.UpdateAPIView):
    serializer_class = BandejaEstanteUpDateSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Obtener los estantes y ordenarlos por orden_ubicacion_por_deposito
        bandejas = BandejaEstante.objects.all()
        bandejas_ordenadas = sorted(bandejas, key=lambda bandeja: bandeja.orden_ubicacion_por_estante)

        # Serializar y retornar los estantes ordenados
        serializer_ordenados = self.get_serializer(bandejas_ordenadas, many=True)
        return Response(serializer_ordenados.data)
    

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

        estantes = estantes.order_by('orden_ubicacion_por_deposito')  # Ordenar aquí

        return estantes

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

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
        bandeja = BandejaEstante.objects.filter(id_estante_deposito=pk).order_by('orden_ubicacion_por_estante')
        serializer = self.serializer_class(bandeja,many=True)
        
        if not Deposito:
            raise NotFound("El registro del estante que busca, no se encuentra registrado")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)
    

 #LISTAR_TODAS_BANDEJAS
class BandejaEstanteAll(generics.ListAPIView):
    serializer_class = BandejasByEstanteListSerializer
    queryset = BandejaEstante.objects.all().order_by('orden_ubicacion_por_estante')
    permission_classes = []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de estantes registrados.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes bandejas ordenados por orden_ubicacion_por_estante.',
            'data': serializer.data
        })    
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
            orden_siguiente = CajaBandejaGetOrdenActual()
            response_orden = orden_siguiente.get(request)

            if response_orden.status_code != status.HTTP_200_OK:
                return response_orden
            maximo_orden = response_orden.data.get('orden_siguiente')

            print(maximo_orden)
            data_in['orden_ubicacion_por_bandeja']=  maximo_orden +1
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            caja =serializer.save()


            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)
        
#ORDEN_SIGUIENTE_CAJAS
class CajaBandejaGetOrden(generics.ListAPIView):
    serializer_class = CajaBandejaGetOrdenSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]
     
    def get(self, request):
        maximo_orden = CajaBandeja.objects.aggregate(max_orden=Max('orden_ubicacion_por_bandeja'))
        
        if not maximo_orden:
            raise NotFound("El registro de la caja que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden'] + 1
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)

    
#ORDEN_ACTUAL_CAJAS
class CajaBandejaGetOrdenActual(generics.ListAPIView):
    serializer_class = CajaBandejaGetOrdenSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]
     
    def get(self, request):
        maximo_orden = CajaBandeja.objects.aggregate(max_orden=Max('orden_ubicacion_por_bandeja'))
        
        if not maximo_orden:
            raise NotFound("El registro de la caja que busca no se encuentra registrado")
        
        orden_siguiente = maximo_orden['max_orden']
        
        return Response({'success': True, 'orden_siguiente': orden_siguiente}, status=status.HTTP_200_OK)
    
#LISTAR_CAJAS_POR_BANDEJA
class CajasByBandejaList(generics.ListAPIView):
    serializer_class = CajasByBandejaListSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        caja = CajaBandeja.objects.filter(id_bandeja_estante=pk).order_by('orden_ubicacion_por_bandeja')
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
            estantes = estantes.filter(orden_ubicacion_por_deposito=orden_estante)
            
        estantes = estantes.order_by('orden_ubicacion_por_deposito')  # Ordenar aquí

        return estantes

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


#EDITAR_CAJAS
class cajaBandejaUpDate(generics.UpdateAPIView):
    serializer_class = CajaBandejaUpDateSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Obtener las cajas y ordenarlos por orden_ubicacion_por_bandeja
        cajas = CajaBandeja.objects.all()
        cajas_ordenadas = sorted(cajas, key=lambda caja: caja.orden_ubicacion_por_bandeja)

        # Serializar y retornar las cajas ordenadas
        serializer_ordenados = self.get_serializer(cajas_ordenadas, many=True)
        return Response(serializer_ordenados.data)
    
    

#MOVER CAJA
class CajaEstanteBandejaMove(generics.UpdateAPIView):
    serializer_class = CajaBandejaMoveSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, id_caja_bandeja):
        # Obtener la caja actual
        caja = get_object_or_404(CajaBandeja, id_caja_bandeja=id_caja_bandeja)

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
            'id_caja':id_caja_bandeja,
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


        
        return queryset.order_by('orden_ubicacion_por_bandeja')


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron cajas que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serialized_data = []
        for caja in queryset:
            serialized_data.append({

                'identificacion_deposito': caja.id_bandeja_estante.id_estante_deposito.id_deposito.identificacion_por_entidad,
                'id_deposito': caja.id_bandeja_estante.id_estante_deposito.id_deposito.id_deposito,
                'identificacion_estante': caja.id_bandeja_estante.id_estante_deposito.identificacion_por_deposito,
                'id_estante': caja.id_bandeja_estante.id_estante_deposito.id_estante_deposito,
                'identificacion_bandeja': caja.id_bandeja_estante.identificacion_por_estante,
                'id_bandeja' :caja.id_bandeja_estante.id_bandeja_estante,
                'identificacion_caja': caja.identificacion_por_bandeja,
                'id_caja':caja.id_caja_bandeja,
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
        
        caja = CajaBandeja.objects.filter(id_caja_bandeja=pk).first()

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


#FILTRO_BANDEJAS_POR_CAJA
#Este permite filtrar todas la bandejas, menos la bandeja a la cual pertenece una caja
class CajaListBandejaInfo(generics.ListAPIView):
    serializer_class = CajaListBandejaInfoSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_caja = self.kwargs.get('id_caja')  # Obtener el valor del id_caja de la URL
        
        # Verificar si la caja existe
        caja = get_object_or_404(CajaBandeja, id_caja_bandeja=id_caja)
        
        bandejas_relacionadas = CajaBandeja.objects.filter(id_caja_bandeja=id_caja).values_list('id_bandeja_estante', flat=True)
        queryset = BandejaEstante.objects.exclude(id_bandeja_estante__in=bandejas_relacionadas)
        
        return queryset.order_by('orden_ubicacion_por_estante')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        id_caja = self.kwargs.get('id_caja')
        data = {
            "id_caja": id_caja,
            "bandejas": self.serializer_class(queryset, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)



#FILTRO_ESTANTE_POR_CAJA
#Este permite filtrar todos los estante, menos el estante a la cual pertenece una caja
class CajaListEstanteInfo(generics.ListAPIView):
    serializer_class = CajaListEstanteInfoSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_caja = self.kwargs.get('id_caja')  # Obtener el valor del id_caja de la URL}

        # Verificar si la caja existe
        caja = CajaBandeja.objects.filter(id_caja_bandeja=id_caja).get()
            
        # Obtener los IDs de las bandejas relacionadas con la caja
        bandejas_relacionadas = CajaBandeja.objects.filter(id_caja_bandeja=id_caja).values_list('id_bandeja_estante', flat=True)
        
        # Obtener los IDs de los estantes a través de las bandejas relacionadas
        estantes_relacionados = BandejaEstante.objects.filter(id_bandeja_estante__in=bandejas_relacionadas).values_list('id_estante_deposito', flat=True)
        
        # Obtener todos los estantes que NO están en los IDs relacionados
        queryset = EstanteDeposito.objects.exclude(id_estante_deposito__in=estantes_relacionados)
        
        return queryset.order_by('orden_ubicacion_por_deposito')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        id_caja = self.kwargs.get('id_caja')
        data = {
            "id_caja": id_caja,
            "estante": self.serializer_class(queryset, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)
    


#FILTRO_DEPOSITO_POR_CAJA
#Este permite filtrar todos los depositos, menos el deposito a la cual pertenece una caja
class CajaListDepositoInfo(generics.ListAPIView):
    serializer_class = CajaListDepositoInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_caja = self.kwargs.get('id_caja')  # Obtener el valor del id_caja de la URL

        # Verificar si la caja existe
        caja = get_object_or_404(CajaBandeja, id_caja_bandeja=id_caja)

        # Obtener los IDs de las bandejas relacionadas con la caja
        bandejas_relacionadas = CajaBandeja.objects.filter(id_caja_bandeja=id_caja).values_list('id_bandeja_estante', flat=True)

        # Obtener los IDs de los estantes a través de las bandejas relacionadas
        estantes_relacionados = BandejaEstante.objects.filter(id_bandeja_estante__in=bandejas_relacionadas).values_list('id_estante_deposito', flat=True)

        # Obtener los IDs de los depósitos relacionados con los estantes
        depositos_relacionados = EstanteDeposito.objects.filter(id_estante_deposito__in=estantes_relacionados).values_list('id_deposito', flat=True)

        # Obtener los objetos de los depósitos que NO están en los IDs relacionados
        queryset = Deposito.objects.exclude(id_deposito__in=depositos_relacionados).order_by('orden_ubicacion_por_entidad')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        id_caja = self.kwargs.get('id_caja')
        data = {
            "id_caja": id_caja,
            "depósitos": self.serializer_class(queryset, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)
    

#LISTAR_TODAS_CAJAS
class CajaBandejaAll(generics.ListAPIView):
    serializer_class = CajasByBandejaListSerializer
    queryset = CajaBandeja.objects.all().order_by('orden_ubicacion_por_bandeja')
    permission_classes = []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de estantes registrados.',
                'data': []
            }, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes bandejas ordenados por orden_ubicacion_por_estante.',
            'data': serializer.data
        })    
    

#ROTULO_CAJA
class CajaRotulo(generics.ListAPIView):
    serializer_class = CajaRotuloSerializer
    queryset = CajaBandeja.objects.all().order_by('orden_ubicacion_por_bandeja')
    permission_classes = []

    def get_queryset(self):
        queryset = CajaBandeja.objects.all().order_by('orden_ubicacion_por_bandeja')
        
        # Obtener el valor del parámetro de la URL
        id_caja_bandeja = self.kwargs.get('id_caja_bandeja')

        if id_caja_bandeja is not None:
            queryset = queryset.filter(id_caja_bandeja=id_caja_bandeja)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de cajas registrados.',
                'data': []
            }, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)

        # Agrega la fecha actual al diccionario de respuesta
        response_data = {
            'success': True,
            'detail': 'Se encontraron las siguientes cajas.',
            'data': serializer.data,
            'fecha_actual': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return Response(response_data)

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
            orden_siguiente = CarpetaCajaGetOrdenActual()
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
        

#ORDEN_SIGUIENTE_CARPETAS
class CarpetaCajaGetOrden(generics.ListAPIView):
    serializer_class = CarpetasByCajaListSerializer    
    queryset = CarpetaCaja.objects.all()
    permission_classes = [IsAuthenticated]
     
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

#ORDEN_ACTUAL_CARPETAS
class CarpetaCajaGetOrdenActual(generics.ListAPIView):
    serializer_class = CarpetasByCajaListSerializer 
    queryset = CarpetaCaja.objects.all()
    permission_classes = [IsAuthenticated]
     
    def get(self, request):
        maximo_orden = CarpetaCaja.objects.aggregate(max_orden=Max('orden_ubicacion_por_caja'))

        # Verificar si el valor del orden es nulo
        if not maximo_orden['max_orden']:
            max_orden = 0
        else:
            max_orden = maximo_orden['max_orden']

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
            }, status=status.HTTP_404_NOT_FOUND)

        serialized_data = []
        for caja in queryset:
            serialized_data.append({
                'nombre_deposito': caja.id_bandeja_estante.id_estante_deposito.id_deposito.nombre_deposito,
                'identificacion_deposito': caja.id_bandeja_estante.id_estante_deposito.id_deposito.identificacion_por_entidad,
                'id_deposito': caja.id_bandeja_estante.id_estante_deposito.id_deposito.id_deposito,
                'identificacion_estante': caja.id_bandeja_estante.id_estante_deposito.identificacion_por_deposito,
                'id_estante': caja.id_bandeja_estante.id_estante_deposito.id_estante_deposito,
                'identificacion_bandeja': caja.id_bandeja_estante.identificacion_por_estante,
                'id_bandeja' :caja.id_bandeja_estante.id_bandeja_estante,
                'identificacion_caja': caja.identificacion_por_bandeja,
                'id_caja':caja.id_caja_bandeja,
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
        carpeta = CarpetaCaja.objects.filter(id_caja_bandeja=pk).order_by('orden_ubicacion_por_caja')
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Obtener las cajas y ordenarlos por orden_ubicacion_por_caja
        carpetas = CarpetaCaja.objects.all()
        carpetas_ordenadas = sorted(carpetas, key=lambda caja: caja.orden_ubicacion_por_caja)

        # Serializar y retornar las cajas ordenadas
        serializer_ordenados = self.get_serializer(carpetas_ordenadas, many=True)
        return Response(serializer_ordenados.data)
    
#LISTAR_TODAS_CARPETAS
class CarpetaCajaAll(generics.ListAPIView):
    serializer_class = CarpetasByCajaListSerializer
    queryset = CarpetaCaja.objects.all().order_by('orden_ubicacion_por_caja')
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de estantes registrados.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes bandejas ordenados por orden_ubicacion_por_estante.',
            'data': serializer.data
        })    
    

#FILTRO_CAJAS_POR_CARPETA
#Este permite filtrar todas las cajas, menos la caja a la cual pertenece una carpeta
class CarpetaListCajaInfo(generics.ListAPIView):
    serializer_class = CarpetaListCajaInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_carpeta = self.kwargs.get('id_carpeta')  # Obtener el valor del id_carpeta de la URL
        
        # Verificar si la carpeta existe
        carpeta = get_object_or_404(CarpetaCaja, id_carpeta_caja=id_carpeta)
        
        cajas_relacionadas = CarpetaCaja.objects.filter(id_carpeta_caja=id_carpeta).values_list('id_caja_bandeja', flat=True)
        queryset = CajaBandeja.objects.exclude(id_caja_bandeja__in=cajas_relacionadas)
        
        return queryset.order_by('orden_ubicacion_por_bandeja')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        id_carpeta = self.kwargs.get('id_carpeta')
        data = {
            "id_carpeta": id_carpeta,
            "cajas": self.serializer_class(queryset, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)
    
#FILTRO_BANDEJAS_POR_CARPETA
#Este permite filtrar todas las bandejas, menos la caja a la cual pertenece una carpeta
class CarpetaListBandejaInfo(generics.ListAPIView):
    serializer_class = BandejaListCarpetaInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_carpeta = self.kwargs.get('id_carpeta')  # Obtener el valor del id_carpeta de la URL
        
        # Verificar si la carpeta existe
        carpeta = get_object_or_404(CarpetaCaja, id_carpeta_caja=id_carpeta)
        
        # Obtener el ID de la caja que pertenece a la carpeta
        id_caja_perteneciente = carpeta.id_caja_bandeja.id_caja_bandeja
        
        # Obtener las bandejas relacionadas con la caja de la carpeta
        bandejas_relacionadas = CajaBandeja.objects.filter(id_caja_bandeja=id_caja_perteneciente).values_list('id_bandeja_estante', flat=True)
        
        # Obtener todas las bandejas excepto las relacionadas con la caja de la carpeta
        queryset = BandejaEstante.objects.exclude(id_bandeja_estante__in=bandejas_relacionadas)
        
        return queryset.order_by('orden_ubicacion_por_estante')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#FILTRO_ESTANTES_POR_CARPETA
#Este permite filtrar todas las estantes, menos la caja a la cual pertenece una carpeta
class EstanteListCarpetaInfo(generics.ListAPIView):
    serializer_class = EstanteListCarpetaInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_carpeta = self.kwargs.get('id_carpeta')  # Obtener el valor del id_carpeta de la URL

        # Verificar si la carpeta existe
        carpeta = get_object_or_404(CarpetaCaja, id_carpeta_caja=id_carpeta)

        # Obtener el ID de la caja que pertenece a la carpeta
        id_caja_perteneciente = carpeta.id_caja_bandeja.id_caja_bandeja

        # Obtener los IDs de las bandejas relacionadas con la caja de la carpeta
        bandejas_relacionadas = CajaBandeja.objects.filter(id_caja_bandeja=id_caja_perteneciente).values_list('id_bandeja_estante', flat=True)

        # Obtener los IDs de los estantes a través de las bandejas relacionadas
        estantes_relacionados = BandejaEstante.objects.filter(id_bandeja_estante__in=bandejas_relacionadas).values_list('id_estante_deposito', flat=True)

        # Obtener todos los estantes que NO están en los IDs relacionados
        queryset = EstanteDeposito.objects.exclude(id_estante_deposito__in=estantes_relacionados)

        return queryset.order_by('orden_ubicacion_por_deposito')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        id_carpeta = self.kwargs.get('id_carpeta')
        data = {
            "id_carpeta": id_carpeta,
            "estante": self.serializer_class(queryset, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)
    
#FILTRO_DEPOSITO_POR_CARPETA
#Este permite filtrar todos los depositos, menos el deposito a la cual pertenece una carpeta
class CarpetaListDepositoInfo(generics.ListAPIView):
    serializer_class = DepositoListCarpetaInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_carpeta = self.kwargs.get('id_carpeta')  # Obtener el valor del id_carpeta de la URL

        # Verificar si la carpeta existe
        carpeta = get_object_or_404(CarpetaCaja, id_carpeta_caja=id_carpeta)

        # Obtener el ID de la caja que pertenece a la carpeta
        id_caja_perteneciente = carpeta.id_caja_bandeja.id_caja_bandeja

        # Obtener el ID del depósito que pertenece a la caja de la carpeta
        id_deposito_perteneciente = CajaBandeja.objects.get(id_caja_bandeja=id_caja_perteneciente).id_bandeja_estante.id_estante_deposito.id_deposito.id_deposito

        # Obtener todos los depósitos excepto el que pertenece a la carpeta
        queryset = Deposito.objects.exclude(id_deposito=id_deposito_perteneciente)

        return queryset.order_by('orden_ubicacion_por_entidad')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        id_carpeta = self.kwargs.get('id_carpeta')
        data = {
            "id_carpeta": id_carpeta,
            "depositos": self.serializer_class(queryset, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)
    


#MOVER_CAJA 
class CarpetaCajaMove(generics.UpdateAPIView):
    serializer_class = CarpetaCajaMoveSerializer
    queryset = CarpetaCaja.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, id_carpeta_caja):
        # Obtener la caja actual
        carpeta = get_object_or_404(CarpetaCaja, id_carpeta_caja=id_carpeta_caja)

        # Obtener los datos de destino desde la solicitud
        identificacion_caja_destino = request.data.get('identificacion_caja_destino')
        identificacion_bandeja_destino = request.data.get('identificacion_bandeja_destino')
        identificacion_estante_destino = request.data.get('identificacion_estante_destino')
        identificacion_deposito_destino = request.data.get('identificacion_deposito_destino')

        # Validar si la caja de destino existe
        caja_destino = CajaBandeja.objects.filter(identificacion_por_bandeja=identificacion_caja_destino).first()
        if not caja_destino:
            return Response({'success': False, 'detail': 'No se encontró la caja de destino especificada.'}, status=status.HTTP_404_NOT_FOUND)
        
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
                return Response({'success': False, 'detail': 'La carpeta tiene un expediente asociado y no puede ser movida a un depósito inactivo.'}, status=status.HTTP_400_BAD_REQUEST)

            
        # Retener los datos actuales de la caja (sin cambios)
        carpeta_actual_data = {
            'identificacion_caja': carpeta.id_caja_bandeja.identificacion_por_bandeja,
            'identificacion_bandeja': carpeta.id_caja_bandeja.id_bandeja_estante.identificacion_por_estante,
            'identificacion_estante': carpeta.id_caja_bandeja.id_bandeja_estante.id_estante_deposito.identificacion_por_deposito,
            'identificacion_deposito': carpeta.id_caja_bandeja.id_bandeja_estante.id_estante_deposito.id_deposito.identificacion_por_entidad,
        }

        # Realizar el cambio de la caja a la bandeja de destino
        carpeta.id_caja_bandeja = caja_destino
        carpeta.save()

        # Retornar los datos de caja actual y caja destino
        return Response({
            'success': True,
            'detail': 'Carpeta movida exitosamente.',
            'id_caja':id_carpeta_caja,
            'caja_actual': carpeta_actual_data,
            'caja_destino': {
                'identificacion_caja': identificacion_caja_destino,
                'identificacion_bandeja': identificacion_bandeja_destino,
                'identificacion_estante': identificacion_estante_destino,
                'identificacion_deposito': identificacion_deposito_destino,
            },
        }, status=status.HTTP_200_OK)


#BUSQUEDA_CARPETAS

#BUSQUEDA_AVANZADA_DE_CARPETAS
class CarpetaCajaSearchAdvanced(generics.ListAPIView):
    serializer_class = CarpetaCajaSearchAdvancedSerializer
    permission_classes = [IsAuthenticated]
    
    def clean_search_param(self, param):
        # Convertir a minúsculas y eliminar espacios en blanco
        return param.lower().strip() if param else None

    def get_queryset(self):
        identificacion_deposito = self.clean_search_param(self.request.query_params.get('identificacion_deposito'))
        identificacion_estante = self.clean_search_param(self.request.query_params.get('identificacion_estante'))
        identificacion_bandeja = self.clean_search_param(self.request.query_params.get('identificacion_bandeja'))
        identificacion_caja = self.clean_search_param(self.request.query_params.get('identificacion_caja'))
        identificacion_carpeta = self.clean_search_param(self.request.query_params.get('identificacion_carpeta'))
        orden_carpeta= self.clean_search_param(self.request.query_params.get('orden_carpeta'))
        

        queryset = CarpetaCaja.objects.all()

        if identificacion_deposito:
            queryset = queryset.filter(id_caja_bandeja__id_bandeja_estante__id_estante_deposito__id_deposito__identificacion_por_entidad__icontains=identificacion_deposito)

        if identificacion_estante:
            queryset = queryset.filter(id_caja_bandeja__id_bandeja_estante__id_estante_deposito__identificacion_por_deposito__icontains=identificacion_estante)

        if identificacion_bandeja:
            queryset = queryset.filter(id_caja_bandeja__id_bandeja_estante__identificacion_por_estante__icontains=identificacion_bandeja)

        if identificacion_caja:
            queryset = queryset.filter(id_caja_bandeja__identificacion_por_bandeja__icontains=identificacion_caja)

        if identificacion_carpeta:
            queryset = queryset.filter(identificacion_por_caja__icontains=identificacion_carpeta)
    

        if orden_carpeta:
            queryset = queryset.filter(orden_ubicacion_por_caja=orden_carpeta)


        
        return queryset.order_by('orden_ubicacion_por_caja')


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron cajas que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serialized_data = []
        for carpeta in queryset:
            serialized_data.append({

                'identificacion_deposito': carpeta.id_caja_bandeja.id_bandeja_estante.id_estante_deposito.id_deposito.identificacion_por_entidad,
                'id_deposito': carpeta.id_caja_bandeja.id_bandeja_estante.id_estante_deposito.id_deposito.id_deposito,
             #--------------------------------------------------------------------------------------------------------------------------------   
                'identificacion_estante': carpeta.id_caja_bandeja.id_bandeja_estante.id_estante_deposito.identificacion_por_deposito,
                'id_estante': carpeta.id_caja_bandeja.id_bandeja_estante.id_estante_deposito.id_estante_deposito,
             #--------------------------------------------------------------------------------------------------------------------------------
                'identificacion_bandeja': carpeta.id_caja_bandeja.id_bandeja_estante.identificacion_por_estante,
                'id_bandeja' :carpeta.id_caja_bandeja.id_bandeja_estante.id_bandeja_estante,
             #--------------------------------------------------------------------------------------------------------------------------------
                'identificacion_caja': carpeta.id_caja_bandeja.identificacion_por_bandeja,
                'id_caja':carpeta.id_caja_bandeja.id_caja_bandeja,
             #--------------------------------------------------------------------------------------------------------------------------------
                'identificacion_carpeta':carpeta.identificacion_por_caja,
                'id_carpeta':carpeta.id_carpeta_caja,
                'orden_carpeta': carpeta.orden_ubicacion_por_caja,

            })

        return Response({
            'success': True,
            'detail': 'Se encontraron las siguientes cajas.',
            'data': serialized_data
        }, status=status.HTTP_200_OK)
    

#ROTULO_CARPETA
class CarpetaRotulo(generics.ListAPIView):
    serializer_class = CarpetaCajaRotuloSerializer
    queryset = CarpetaCaja.objects.all().order_by('orden_ubicacion_por_caja')
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CarpetaCaja.objects.all().order_by('orden_ubicacion_por_caja')
        
        # Obtener el valor del parámetro de la URL
        id_carpeta_caja = self.kwargs.get('id_carpeta_caja')

        if id_carpeta_caja is not None:
            queryset = queryset.filter(id_carpeta_caja=id_carpeta_caja)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de carpetas registrados.',
                'data': []
            }, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)

        # Agrega la fecha actual al diccionario de respuesta
        response_data = {
            'success': True,
            'detail': 'Se encontraron las siguientes carpetas.',
            'data': serializer.data,
            'fecha_actual': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return Response(response_data)
    
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



########################## CRUD ARCHIVO FISICO ##########################

#LISTAR_DEPOSITO_POR_ID
class DepositoGetById(generics.ListAPIView):
    serializer_class = DepositoGetSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        deposito = Deposito.objects.filter(id_deposito=pk).order_by('orden_ubicacion_por_entidad')
        serializer = self.serializer_class(deposito, many=True)
        
        if not deposito:
            raise NotFound("El registro del deposito que busca, no se encuentra registrado")

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
#LISTAR_ESTANTE_POR_ID
class EstanteGetById(generics.ListAPIView):
    serializer_class = EstanteDepositoGetOrdenSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        estante = EstanteDeposito.objects.filter(id_estante_deposito=pk).order_by('orden_ubicacion_por_deposito')
        serializer = self.serializer_class(estante, many=True)
        
        if not estante:
            raise NotFound("El registro del estante que busca, no se encuentra registrado")

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
#LISTAR_BANDEJA_POR_ID
class BandejaGetById(generics.ListAPIView):
    serializer_class = BandejaEstanteGetOrdenSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        bandeja = BandejaEstante.objects.filter(id_bandeja_estante=pk).order_by('orden_ubicacion_por_estante')
        serializer = self.serializer_class(bandeja, many=True)
        
        if not bandeja:
            raise NotFound("El registro de la bandeja que busca, no se encuentra registrado")

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
#LISTAR_CAJA_POR_ID
class CajaGetById(generics.ListAPIView):
    serializer_class = CajaBandejaGetOrdenSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        caja = CajaBandeja.objects.filter(id_caja_bandeja=pk).order_by('orden_ubicacion_por_bandeja')
        serializer = self.serializer_class(caja, many=True)
        
        if not caja:
            raise NotFound("El registro de la caja que busca, no se encuentra registrado")

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
#LISTAR_CARPETA_POR_ID
class CarpetaGetById(generics.ListAPIView):
    serializer_class = CarpetaCajaGetOrdenSerializer
    queryset = CarpetaCaja.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        carpeta = CarpetaCaja.objects.filter(id_carpeta_caja=pk).order_by('orden_ubicacion_por_caja')
        serializer = self.serializer_class(carpeta, many=True)
        
        if not carpeta:
            raise NotFound("El registro de la carpeta que busca, no se encuentra registrado")

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializer.data}, status=status.HTTP_200_OK)
    
#LISTAR_TODOS_DEPOSITOS
class DepositoGetAll(generics.ListAPIView):
    serializer_class = DepositoGetAllSerializer
    queryset = Deposito.objects.all().order_by('orden_ubicacion_por_entidad')
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': False,
                'detail': 'No se encontraron datos de depósitos registrados.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes depósitos ordenados por orden_ubicacion_por_entidad.',
            'data': serializer.data
        })
    
#LISTAR_TODOS_ESTANTE
class EstanteGetAll(generics.ListAPIView):
    serializer_class = EstanteDepositoGetOrdenSerializer
    queryset = EstanteDeposito.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_deposito):
        try:
            # Filtrar las estantes por el ID del estante_deposito y ordenarlas por orden_ubicacion_por_deposito
            estantes = EstanteDeposito.objects.filter(id_deposito=id_deposito).order_by('orden_ubicacion_por_deposito')

            # Verificar si no se encontraron registros
            if not estantes:
                return Response({'success': False, 'detail': 'No se encontraron estantes relacionadas para el deposito especificado.'}, status=status.HTTP_404_NOT_FOUND)

            # Crear una lista de resultados formateados según tus especificaciones
            resultados = []
            for estante in estantes:
                # Construir el resultado formateado con los campos adicionales
                resultado_formateado = {
                    'id_estante': estante.id_estante_deposito,
                    'id_deposito': estante.id_deposito.id_deposito,  
                    'identificacion_estante': estante.identificacion_por_deposito,
                    'orden_ubicacion_estante': estante.orden_ubicacion_por_deposito,
                    'Informacion_Mostrar': f"{estante.orden_ubicacion_por_deposito} - Estante {estante.identificacion_por_deposito}"
                }
                resultados.append(resultado_formateado)

            # Devolver la lista de resultados en la respuesta
            return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': resultados}, status=status.HTTP_200_OK)

        except BandejaEstante.DoesNotExist:
            return Response({'success': False, 'detail': 'No se encontraron bandejas para el estante_deposito especificado.'}, status=status.HTTP_404_NOT_FOUND)


#LISTAR_TODAS_BANDEJAS
class BandejaGetAll(generics.ListAPIView):
    serializer_class = BandejaEstanteGetOrdenSerializer
    queryset = BandejaEstante.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_estante_deposito):
        try:
            # Filtrar las bandejas por el ID del estante_deposito y ordenarlas por T232ordenUbicacionPorEstante
            bandejas = BandejaEstante.objects.filter(id_estante_deposito=id_estante_deposito).order_by('orden_ubicacion_por_estante')

            # Verificar si no se encontraron registros
            if not bandejas:
                return Response({'success': False, 'detail': 'No se encontraron bandejas relacionadas para el estante especificado.'}, status=status.HTTP_404_NOT_FOUND)

            # Crear una lista de resultados formateados según tus especificaciones
            resultados = []
            for bandeja in bandejas:
                # Construir el resultado formateado con los campos adicionales
                resultado_formateado = {
                    'id_bandeja': bandeja.id_bandeja_estante,
                    'id_estante': bandeja.id_estante_deposito.id_estante_deposito,  
                    'identificacion_bandeja': bandeja.identificacion_por_estante,
                    'orden_ubicacion_bandeja': bandeja.orden_ubicacion_por_estante,
                    'Informacion_Mostrar': f"{bandeja.orden_ubicacion_por_estante} - Bandeja {bandeja.identificacion_por_estante}"
                }
                resultados.append(resultado_formateado)

            # Devolver la lista de resultados en la respuesta
            return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': resultados}, status=status.HTTP_200_OK)

        except BandejaEstante.DoesNotExist:
            return Response({'success': False, 'detail': 'No se encontraron bandejas para el estante_deposito especificado.'}, status=status.HTTP_404_NOT_FOUND)
        
#LISTAR_TODAS_CAJAS
class CajaGetAll(generics.ListAPIView):
    serializer_class = CajaBandejaGetOrdenSerializer
    queryset = CajaBandeja.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_bandeja_estante):
        try:
            # Filtrar las cajas por el ID del id_bandeja_estante y ordenarlas por orden_ubicacion_por_bandeja
            cajas = CajaBandeja.objects.filter(id_bandeja_estante=id_bandeja_estante).order_by('orden_ubicacion_por_bandeja')

            # Verificar si no se encontraron registros
            if not cajas:
                return Response({'success': False, 'detail': 'No se encontraron cajas relacionadas para la bandeja especificada.'}, status=status.HTTP_404_NOT_FOUND)

            # Crear una lista de resultados formateados según tus especificaciones
            resultados = []
            for caja in cajas:
                # Construir el resultado formateado con los campos adicionales
                resultado_formateado = {
                    'id_caja': caja.id_caja_bandeja,
                    'id_bandeja': caja.id_bandeja_estante.id_bandeja_estante,  
                    'identificacion_caja': caja.identificacion_por_bandeja,
                    'orden_ubicacion_caja': caja.orden_ubicacion_por_bandeja,
                    'Informacion_Mostrar': f"{caja.orden_ubicacion_por_bandeja} - Caja {caja.identificacion_por_bandeja}"
                }
                resultados.append(resultado_formateado)

            # Devolver la lista de resultados en la respuesta
            return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': resultados}, status=status.HTTP_200_OK)

        except BandejaEstante.DoesNotExist:
            return Response({'success': False, 'detail': 'No se encontraron cajas para el estante_deposito especificado.'}, status=status.HTTP_404_NOT_FOUND)
        

#LISTAR_TODAS_CARPETAS
class CarpetaGetAll(generics.ListAPIView):
    serializer_class = CarpetaCajaGetOrdenSerializer
    queryset = CarpetaCaja.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_caja_bandeja):
        try:
            # Filtrar las carpetas por el ID del id_bandeja_estante y ordenarlas por orden_ubicacion_por_caja
            carpetas = CarpetaCaja.objects.filter(id_caja_bandeja=id_caja_bandeja).order_by('orden_ubicacion_por_caja')

            # Verificar si no se encontraron registros
            if not carpetas:
                return Response({'success': False, 'detail': 'No se encontraron carpetas relacionadas para la caja especificada.'}, status=status.HTTP_404_NOT_FOUND)

            # Crear una lista de resultados formateados según tus especificaciones
            resultados = []
            for carpeta in carpetas:
                # Construir el resultado formateado con los campos adicionales
                resultado_formateado = {
                    'id_carpeta': carpeta.id_carpeta_caja,
                    'id_caja': carpeta.id_caja_bandeja.id_caja_bandeja,  
                    'identificacion_carpeta': carpeta.identificacion_por_caja,
                    'orden_ubicacion_carpeta': carpeta.orden_ubicacion_por_caja,
                    'Informacion_Mostrar': f"{carpeta.orden_ubicacion_por_caja} - Carpeta {carpeta.identificacion_por_caja}"
                }
                resultados.append(resultado_formateado)

            # Devolver la lista de resultados en la respuesta
            return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': resultados}, status=status.HTTP_200_OK)

        except BandejaEstante.DoesNotExist:
            return Response({'success': False, 'detail': 'No se encontraron carpetas para el estante_deposito especificado.'}, status=status.HTTP_404_NOT_FOUND)