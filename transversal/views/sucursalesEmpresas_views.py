import copy

from django.forms import ValidationError
from django.db.models import Max
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from seguridad.utils import Util

from transversal.serializers.entidades_serializers import SucursalesEmpresasSerializer, SucursalesEmpresasPostSerializer

from transversal.models.entidades_models import SucursalesEmpresas

from seguridad.models import Personas



class getSucursalesEmpresas(generics.ListAPIView):
    serializer_class = SucursalesEmpresasSerializer
    queryset = SucursalesEmpresas.objects.all()


class getSucursalEmpresaById(generics.RetrieveAPIView):
    serializer_class = SucursalesEmpresasSerializer
    queryset = SucursalesEmpresas.objects.all()


class deleteSucursalEmpresa(generics.DestroyAPIView):
    serializer_class = SucursalesEmpresasSerializer
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        sucursal=SucursalesEmpresas.objects.filter(id_sucursal_empresa=pk).first()

        if sucursal:
            persona_empresa=sucursal.id_persona_empresa
            sucursal.delete()
            persona=Personas.objects.get(id_persona=persona_empresa.id_persona)
            usuario = request.user.id_usuario
            dirip = Util.get_client_ip(request)
            descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(sucursal.sucursal)}
            auditoria_data = {
                'id_usuario': usuario,
                'id_modulo': 1,
                'cod_permiso': 'BO',
                'subsistema': 'TRSV',
                'dirip': dirip,
                'descripcion': descripcion,
            }
            
            Util.save_auditoria(auditoria_data)

            return Response({'success':True, 'detail':'La sucursal empresa fue eliminada'}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('No existe sucursal')
            
class updateSucursalEmpresa(generics.RetrieveUpdateAPIView):
    serializer_class = SucursalesEmpresasPostSerializer
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request,pk=None):
        sucursal = SucursalesEmpresas.objects.filter(id_sucursal_empresa= pk).first()
        previous_sucursal = copy.copy(sucursal)
        if sucursal:
            sucursal_serializer = self.serializer_class(sucursal, data=request.data)
            sucursal_serializer.is_valid(raise_exception=True)
            sucursal_serializer.save()
            
            usuario = request.user.id_usuario
            persona=Personas.objects.get(id_persona=request.data['id_persona_empresa'])
            dirip = Util.get_client_ip(request)
            descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(sucursal.sucursal)}
            valores_actualizados={'current':sucursal, 'previous':previous_sucursal}

            auditoria_data = {
                'id_usuario': usuario,
                'id_modulo': 1,
                'cod_permiso': 'AC',
                'subsistema': 'TRSV',
                'dirip': dirip,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }
            
            Util.save_auditoria(auditoria_data)
            return Response({'success':True, 'detail':'la sucursal empresa actualizada'}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError('No existe sucursal')

class registerSucursalEmpresa(generics.CreateAPIView):
    serializer_class = SucursalesEmpresasPostSerializer 
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializador=serializer.save()
        usuario = request.user.id_usuario

        persona=Personas.objects.get(id_persona=request.data['id_persona_empresa'])
        dirip = Util.get_client_ip(request)
        descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(serializador.sucursal)}

        auditoria_data = {
            'id_usuario': usuario,
            'id_modulo': 1,
            'cod_permiso': 'CR',
            'subsistema': 'TRSV',
            'dirip': dirip,
            'descripcion': descripcion,
        }
        
        Util.save_auditoria(auditoria_data)
        headers = self.get_success_headers(serializer.data)
        return Response({'success':True},serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

class GetEntidadById(generics.ListAPIView):
    d = 0