
import copy
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.radicados_models import PQRSDF, MediosSolicitud, TiposPQR
from rest_framework.response import Response
from gestion_documental.serializers.pqr_serializers import MediosSolicitudCreateSerializer, MediosSolicitudDeleteSerializer, MediosSolicitudSearchSerializer, MediosSolicitudUpdateSerializer, PQRSDFSerializer, TiposPQRGetSerializer, TiposPQRUpdateSerializer
from seguridad.utils import Util

from django.db.models import Q
class TiposPQRGet(generics.ListAPIView):
    serializer_class = TiposPQRGetSerializer
    queryset = TiposPQR.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):

        instance=TiposPQR.objects.filter(cod_tipo_pqr=pk)
        if not instance:
            raise NotFound("No existen tipos de radicado")
        
        serializer = self.serializer_class(instance, many=True)

                         
        return Response({'succes':True, 'detail':'Se encontró los siguientes registross','data':serializer.data}, status=status.HTTP_200_OK)


class TiposPQRUpdate(generics.UpdateAPIView):
    serializer_class = TiposPQRUpdateSerializer
    queryset = TiposPQR.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
    
        try:    
            data = request.data
            instance = TiposPQR.objects.filter(cod_tipo_pqr=pk).first()
            
            if not instance:
                raise NotFound("No se existe un tipo de radicado con este codigo.")
            
            instance_previous=copy.copy(instance)
            serializer = self.serializer_class(instance,data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            serializer.save()

            #AUDITORIA 
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"Nombre":instance.nombre}
            valores_actualizados = {'current': instance, 'previous': instance_previous}
            auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : 153,
                    "cod_permiso": "AC",
                    "subsistema": 'GEST',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                    "valores_actualizados": valores_actualizados
                }
            Util.save_auditoria(auditoria_data) 

            return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data},status=status.HTTP_200_OK)
        
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)    

class GetPQRSDFForStatus(generics.ListAPIView):
    serializer_class = PQRSDFSerializer
    queryset = PQRSDF.objects.all()

    def get(self, request, id_persona_titular):
        pqrsdf = self.queryset.filter(Q(id_persona_titular = id_persona_titular) & 
                                      Q(Q(id_radicado = 0) | Q(id_radicado = None) | Q(~Q(id_radicado=0) & Q(requiere_rta = True) & Q(fecha_rta_final_gestion = None))))
        if pqrsdf:
            serializador = self.serializer_class(pqrsdf, many = True)
            return Response({'success':True, 'detail':'Se encontraron PQRSDF asociadas al titular','data':serializador.data},status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'No se encontraron PQRSDF asociadas al titular'},status=status.HTTP_200_OK) 



 ########################## MEDIOS DE SOLICITUD ##########################


#CREAR_MEDIOS_SOLICITUD
class MediosSolicitudCreate(generics.CreateAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MediosSolicitudCreateSerializer
    permission_classes = [IsAuthenticated]


#BUSCAR_MEDIOS_SOLICITUD
class MediosSolicitudSearch(generics.ListAPIView):
    serializer_class = MediosSolicitudSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        nombre_medio_solicitud = self.request.query_params.get('nombre_medio_solicitud', '').strip()
        aplica_para_pqrsdf = self.request.query_params.get('aplica_para_pqrsdf', '').strip()
        aplica_para_tramites = self.request.query_params.get('aplica_para_tramites', '').strip()
        aplica_para_otros = self.request.query_params.get('aplica_para_otros', '').strip()
        activo = self.request.query_params.get('activo', '').strip()

        medios_solicitud = MediosSolicitud.objects.all()

        if nombre_medio_solicitud:
            medios_solicitud = medios_solicitud.filter(nombre__icontains=nombre_medio_solicitud)

        
        if aplica_para_pqrsdf:
            medios_solicitud = medios_solicitud.filter(aplica_para_pqrsdf__icontains=aplica_para_pqrsdf)


        if aplica_para_tramites:
            medios_solicitud = medios_solicitud.filter(aplica_para_tramites__icontains=aplica_para_tramites)

        if aplica_para_otros:
            medios_solicitud = medios_solicitud.filter(descripcion__icontains=aplica_para_otros)

    
        if activo:
            medios_solicitud = medios_solicitud.filter(activo__icontains=activo)
            

        medios_solicitud = medios_solicitud.order_by('id_medio_solicitud')  # Ordenar aquí

        return medios_solicitud

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron medios de solicitud que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes medios de solicitud.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
#BORRAR_MEDIO_SOLICITUD
class MediosSolicitudDelete(generics.DestroyAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MediosSolicitudDeleteSerializer 
    lookup_field = 'id_medio_solicitud'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Verificar si T253registroPrecargado es TRUE
        if instance.registro_precargado:
            return Response({'success': False,"detail": "No puedes eliminar este medio de solicitud porque está precargado (Registro_Precargado=TRUE)."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si T253itemYaUsado es TRUE
        if instance.item_ya_usado:
            return Response({'success': False,"detail": "No puedes eliminar este medio de solicitud porque ya ha sido usado (ItemYaUsado=TRUE)."}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar el medio de solicitud
        instance.delete()

        return Response({'success': True,"detail": "El medio de solicitud se eliminó con éxito."}, status=status.HTTP_200_OK)
    
#ACTUALIZAR_MEDIO_SOLICITUD
class MediosSolicitudUpdate(generics.UpdateAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MediosSolicitudUpdateSerializer  
    lookup_field = 'id_medio_solicitud'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Verificar si T253registroPrecargado es TRUE
        if instance.registro_precargado:
            return Response({'success': False, "detail": "No puedes actualizar este medio de solicitud porque está precargado.", "data": MediosSolicitudUpdateSerializer(instance).data}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si T253itemYaUsado es TRUE
        if instance.item_ya_usado:
            # Comprobar si 'nombre' está presente en los datos de solicitud
            if 'nombre' in request.data:
                return Response({'success': False, "detail": "No puedes actualizar el campo 'nombre' en este medio de solicitud.", "data": MediosSolicitudUpdateSerializer(instance).data}, status=status.HTTP_400_BAD_REQUEST)

            # Permitir actualizar otros campos
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, "detail": "El medio de solicitud se actualizó con éxito.", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Si T253itemYaUsado es FALSE, permitir la actualización completa del medio de solicitud
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "detail": "El medio de solicitud se actualizó con éxito.", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)