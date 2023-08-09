from django.db.models import F
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# IMPORT LISTS
from seguridad.lists.tipo_persona_list import tipo_persona_LIST
from seguridad.lists.tipo_usuario_list import tipo_usuario_LIST
from seguridad.lists.clase_tercero_list import clase_tercero_LIST
from seguridad.lists.cod_permiso_list import cod_permiso_LIST
from seguridad.lists.opciones_usuario_list import opciones_usuario_LIST
from seguridad.lists.perfiles_sistema_list import perfiles_LIST
from seguridad.lists.subsistemas_list import subsistemas_LIST
from seguridad.lists.tipo_direccion_list import tipo_direccion_LIST
from seguridad.lists.cod_naturaleza_empresa_list import cod_naturaleza_empresa_LIST

class GetListTipoPersona(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los tipos de persona son los siguientes', 'data': tipo_persona_LIST}, status=status.HTTP_200_OK)
    
class GetListTipoUsuario(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los tipos de usuarios son los siguientes', 'data': tipo_usuario_LIST}, status=status.HTTP_200_OK)

class GetLisClaseTercero(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los tipos de clase tercero son los siguientes', 'data': clase_tercero_LIST}, status=status.HTTP_200_OK)
    
class GetLisCodPermiso(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los tipos de codigo permiso son los siguientes', 'data': cod_permiso_LIST}, status=status.HTTP_200_OK)

class GetLisOpcUsuario(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los tipos de opciones de usuario son los siguientes', 'data': opciones_usuario_LIST}, status=status.HTTP_200_OK) 

class GetLisPerfilesSistema(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los perfiles del sistema son los siguientes', 'data': perfiles_LIST}, status=status.HTTP_200_OK) 

class GetLisSubsistema(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los tipos de subsistema son los siguientes', 'data': subsistemas_LIST}, status=status.HTTP_200_OK)
    
class GetLisTipoDireccion(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los tipos de direccion son las siguientes', 'data': tipo_direccion_LIST}, status=status.HTTP_200_OK)

class GetLisCodNaturalezEmpresa(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los códigos de la naturaleza de una empresa son los siguientes', 'data': cod_naturaleza_empresa_LIST}, status=status.HTTP_200_OK)