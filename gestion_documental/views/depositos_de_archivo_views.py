import copy
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max 
from datetime import datetime,date,timedelta
from gestion_documental.models.depositos_models import Deposito, EstanteDeposito
from gestion_documental.serializers.depositos_serializers import DepositoCreateSerializer, DepositoDeleteSerializer, DepositoUpdateSerializer, EstanteDepositoCreateSerializer,DepositoGetSerializer
from seguridad.utils import Util


##CRUD DE DEPOSITO
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
        
class DepositoDelete(generics.DestroyAPIView):
    serializer_class = DepositoDeleteSerializer
    queryset = Deposito.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        deposito = Deposito.objects.filter(id_deposito=pk).first()
        estantes = EstanteDeposito.objects.filter(id_deposito=pk).first()
       
        
        if not deposito:
            raise ValidationError("No existe la deposito a eliminar")
        

        #pendiente validacion de cajas bandeja

        if estantes:
            raise ValidationError("No se puede Eliminar una deposito, si tiene estantes asignadas.")
        
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


#CRUD ESTANTE DEPOSITO
class EstanteDepositoCreate(generics.CreateAPIView):
    serializer_class = EstanteDepositoCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = EstanteDeposito.objects.all()
    
    def post(self,request):
        
        try:
            data_in = request.data
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)

