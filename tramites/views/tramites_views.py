from rest_framework import status
from rest_framework import generics, views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from tramites.models.tramites_models import PermisosAmbSolicitudesTramite, PermisosAmbientales, SolicitudesTramites
from tramites.serializers.tramites_serializers import InicioTramiteCreateSerializer, ListTramitesGetSerializer, PersonaTitularInfoGetSerializer, TramiteListGetSerializer
from transversal.models.personas_models import Personas

class ListTramitesGetView(generics.ListAPIView):
    serializer_class = ListTramitesGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, cod_tipo_permiso_ambiental):
        cod_tipo_permiso_ambiental_correctos = ['L', 'P', 'D', 'O']
        if cod_tipo_permiso_ambiental not in cod_tipo_permiso_ambiental_correctos:
            raise ValidationError('El código del tipo de permiso ambiental es incorrecto')
        
        permisos_ambientales = PermisosAmbientales.objects.filter(cod_tipo_permiso_ambiental=cod_tipo_permiso_ambiental)
        
        serializer = self.serializer_class(permisos_ambientales, many=True)
        
        return Response({'success': True, 'detail':'Se encontraron los siguientes resultados', 'data': serializer.data}, status=status.HTTP_200_OK)   

class PersonaTitularInfoGetView(generics.ListAPIView):
    serializer_class = PersonaTitularInfoGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_persona):
        persona = Personas.objects.filter(id_persona=id_persona).first()
        if not persona:
            raise NotFound('No se encontró la persona')
        
        serializer = self.serializer_class(persona, many=False)
        
        return Response({'success': True, 'detail':'Se encontró la siguiente información', 'data': serializer.data}, status=status.HTTP_200_OK)   

class TramiteListGetView(generics.ListAPIView):
    serializer_class = TramiteListGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_persona_titular):
        tramites_opas = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite__id_medio_solicitud=2, id_solicitud_tramite__id_persona_titular=id_persona_titular, id_permiso_ambiental__cod_tipo_permiso_ambiental = 'O')

        serializer = self.serializer_class(tramites_opas, many=True)
        
        return Response({'success': True, 'detail':'Se encontró la siguiente información', 'data': serializer.data}, status=status.HTTP_200_OK)   

class InicioTramiteCreateView(generics.CreateAPIView):
    serializer_class = InicioTramiteCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        data = request.data
        
        # direccion = request.data.get('direccion', '')
        descripcion_direccion = request.data.get('descripcion_direccion', '')
        coordenada_x = data.get('coordenada_x')
        coordenada_y = data.get('coordenada_y')
        # if direccion == '':
        #     raise ValidationError('La dirección es obligatoria')
        if descripcion_direccion == '':
            raise ValidationError('La descripción de la dirección es obligatoria')
        
        id_permiso_ambiental = data.get('id_permiso_ambiental')
        if not id_permiso_ambiental:
            raise ValidationError('El trámite o servicio es obligatorio')
        
        permiso_ambiental = PermisosAmbientales.objects.filter(id_permiso_ambiental=id_permiso_ambiental).first()
        if not permiso_ambiental:
            raise ValidationError('No se encontró el trámite elegido')
        
        id_persona_titular = data.get('id_persona_titular')
        id_persona_interpone = data.get('id_persona_interpone')
        
        if id_persona_titular == id_persona_interpone:
            data['cod_relacion_con_el_titular'] = 'MP'
        else:
            data['cod_relacion_con_el_titular'] = 'RL' # VALIDAR PARA CASO DE APODERADOS
        
        data['cod_tipo_operacion_tramite'] = 'N'
        data['nombre_proyecto'] = permiso_ambiental.nombre
        data['costo_proyecto'] = 0
        data['fecha_inicio_tramite'] = datetime.now()
        # data['id_medio_solicitud'] = 2 # QUE LO MANDE FRONTEND
        data['id_persona_registra'] = request.user.persona.id_persona
        data['id_estado_actual_solicitud'] = 1
        data['fecha_ini_estado_actual'] = datetime.now()
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        tramite_creado = serializer.save()
        
        # CREAR EN T280
        PermisosAmbSolicitudesTramite.objects.create(
            id_permiso_ambiental = permiso_ambiental,
            id_solicitud_tramite = tramite_creado,
            descripcion_direccion = descripcion_direccion,
            coordenada_x = coordenada_x,
            coordenada_y = coordenada_y
        )
        
        data_serializada = serializer.data
        data_serializada['id_permiso_ambiental'] = id_permiso_ambiental
        data_serializada['descripcion_direccion'] = descripcion_direccion
        data_serializada['coordenada_x'] = coordenada_x
        data_serializada['coordenada_y'] = coordenada_y
        
        return Response({'success': True, 'detail':'Se realizó la creación del inicio del trámite correctamente', 'data': data_serializada}, status=status.HTTP_201_CREATED)   

class InicioTramiteUpdateView(generics.UpdateAPIView):
    serializer_class = InicioTramiteCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, id_solicitud_tramite):
        data = request.data
        
        solicitud = SolicitudesTramites.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        if not solicitud:
            raise NotFound('No se encontró la solicitud')
        
        permiso_amb_solicitud = PermisosAmbSolicitudesTramite.objects.filter(id_solicitud_tramite=id_solicitud_tramite).first()
        
        id_permiso_ambiental = data.get('id_permiso_ambiental')
        # direccion = request.data.get('direccion', '')
        descripcion_direccion = request.data.get('descripcion_direccion', '')
        coordenada_x = data.get('coordenada_x')
        coordenada_y = data.get('coordenada_y')
        
        # ACTUALIZAR PERMISO AMBIENTAL SOLICITUD
        if id_permiso_ambiental != permiso_amb_solicitud.id_permiso_ambiental.id_permiso_ambiental:
            permiso_ambiental = PermisosAmbientales.objects.filter(id_permiso_ambiental=id_permiso_ambiental).first()
            if not permiso_ambiental:
                raise ValidationError('No se encontró el trámite elegido')
            
            permiso_amb_solicitud.id_permiso_ambiental = permiso_ambiental
            solicitud.nombre_proyecto = permiso_ambiental.nombre
            solicitud.save()
        # if direccion != '' and direccion != permiso_amb_solicitud.direccion:
        #     permiso_amb_solicitud.direccion = direccion
        if descripcion_direccion != '' and descripcion_direccion != permiso_amb_solicitud.descripcion_direccion:
            permiso_amb_solicitud.descripcion_direccion = descripcion_direccion
        if coordenada_x != '' and coordenada_x != permiso_amb_solicitud.coordenada_x:
            permiso_amb_solicitud.coordenada_x = coordenada_x
        if coordenada_y != '' and coordenada_y != permiso_amb_solicitud.coordenada_y:
            permiso_amb_solicitud.coordenada_y = coordenada_y
        
        permiso_amb_solicitud.save()
        
        serializer = self.serializer_class(solicitud)
        
        data_serializada = serializer.data
        data_serializada['id_permiso_ambiental'] = id_permiso_ambiental
        # data_serializada['direccion'] = direccion
        data_serializada['descripcion_direccion'] = descripcion_direccion
        data_serializada['coordenada_x'] = coordenada_x
        data_serializada['coordenada_y'] = coordenada_y
        
        return Response({'success': True, 'detail':'Se realizó la actualización del inicio del trámite correctamente', 'data': data_serializada}, status=status.HTTP_201_CREATED)   
