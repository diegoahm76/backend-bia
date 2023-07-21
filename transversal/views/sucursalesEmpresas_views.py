import copy

from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from seguridad.utils import Util

from transversal.serializers.entidades_serializers import SucursalesEmpresasSerializer, SucursalesEmpresasPostSerializer, SucursalesEmpresasPutSerializer

from transversal.models.entidades_models import SucursalesEmpresas

from seguridad.models import Personas


class GetSucursalesEmpresasView(generics.ListAPIView):
    serializer_class = SucursalesEmpresasSerializer
    def get(self, request, id):
        queryset = SucursalesEmpresas.objects.all().filter(id_persona_empresa=id)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail':'Se muestra los datos la facilidad de pago', 'data': serializer.data}, status=status.HTTP_200_OK)   


class getSucursalEmpresaById(generics.RetrieveAPIView):
    serializer_class = SucursalesEmpresasSerializer
    queryset = SucursalesEmpresas.objects.all()


class CrearSucursalEmpresaView(generics.CreateAPIView):
    serializer_class = SucursalesEmpresasPostSerializer 
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        data = request.data

        data['numero_sucursal'] = 0

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        id_persona_empresa = serializer.validated_data.get('id_persona_empresa')

        # VALIDACION PRINCIPAL
        principal_existe = SucursalesEmpresas.objects.filter(id_persona_empresa=id_persona_empresa).filter(es_principal=True).first()
        es_principal = serializer.validated_data.get('es_principal')
        
        if principal_existe != None:
            if es_principal == True:
                raise ValidationError('Ya existe una sucursal principal')
        else:
            data['es_principal'] = True
            
        # AGREGAR NUMERO SUCURSAL
        num_max = SucursalesEmpresas.objects.filter(id_persona_empresa=id_persona_empresa).last()
        consecutivo = 1
        if num_max:
            consecutivo = num_max.numero_sucursal + 1

        data['numero_sucursal'] = consecutivo

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializador=serializer.save()

        usuario = request.user.id_usuario
        persona=Personas.objects.get(id_persona=request.data['id_persona_empresa'])
        dirip = Util.get_client_ip(request)
        descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(serializador.descripcion_sucursal)}

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
        return Response({'success':True, 'detail':'la sucursal empresa ha sido creada','data':serializer.data}, status=status.HTTP_201_CREATED)

            
class PutSucursalEmpresa(generics.RetrieveUpdateAPIView):
    serializer_class = SucursalesEmpresasPutSerializer
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id):
        sucursal = SucursalesEmpresas.objects.filter(id_sucursal_empresa=id).first()
        previous_sucursal = copy.copy(sucursal)
        if sucursal:

            sucursal_serializer = self.serializer_class(sucursal, data=request.data)
            sucursal_serializer.is_valid(raise_exception=True)
            descripcion_sucursal = sucursal_serializer.validated_data.get('descripcion_sucursal')

            aprobado = False
            print("SUCURSAL", sucursal.descripcion_sucursal)
            if sucursal.descripcion_sucursal == descripcion_sucursal:
                aprobado = True
            else:
                if sucursal.item_ya_usado == False:
                    aprobado = True
                else:
                    raise ValidationError('No se puede modificar la descripcion de la sucursal por motivo de que se encuentra en uso')   
            
            if aprobado == True:
                sucursal_serializer.save()
                usuario = request.user.id_usuario
                print("ID SUCURSAL", sucursal.direccion)
                persona=Personas.objects.get(id_persona=request.data['id_persona_empresa'])
                dirip = Util.get_client_ip(request)
                descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(sucursal.descripcion_sucursal)}
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
                return Response({'success':True, 'detail':'la sucursal empresa actualizada'}, status=status.HTTP_200_OK)
        
        else:
            raise NotFound('No existe sucursal')


class DeleteSucursalEmpresa(generics.DestroyAPIView):
    serializer_class = SucursalesEmpresasSerializer
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,id):
        sucursal=SucursalesEmpresas.objects.filter(id_sucursal_empresa=id).first()

        if sucursal:
            if sucursal.item_ya_usado == False:
                persona_empresa=sucursal.id_persona_empresa
                sucursal.delete()

                persona=Personas.objects.get(id_persona=persona_empresa.id_persona)
                usuario = request.user.id_usuario
                dirip = Util.get_client_ip(request)
                descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(sucursal.descripcion_sucursal)}
                auditoria_data = {
                    'id_usuario': usuario,
                    'id_modulo': 1,
                    'cod_permiso': 'BO',
                    'subsistema': 'TRSV',
                    'dirip': dirip,
                    'descripcion': descripcion,
                }
                
                Util.save_auditoria(auditoria_data)

                return Response({'success':True, 'detail':'La sucursal fue eliminada'}, status=status.HTTP_204_NO_CONTENT)
            
            else:
                raise ValidationError('No se puede eliminar la sucursal por motivo de que se encuentra en uso')
        else:
            raise NotFound('No existe sucursal')


class BusquedaSucursalView(generics.ListAPIView):
    serializer_class = SucursalesEmpresasSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):

        sucursal = SucursalesEmpresas.objects.all()
        descripcion_sucursal = self.request.query_params.get('descripcion_sucursal', '')
        direccion = self.request.query_params.get('direccion', '')
        
        descripcion = descripcion_sucursal.split()
        for x in range(len(descripcion)):
            sucursal = sucursal.filter(descripcion_sucursal__icontains=descripcion[x])
        
        direccion_sucursal = direccion.split()
        for x in range(len(direccion_sucursal)):
            sucursal = sucursal.filter(direccion__icontains=direccion_sucursal[x])    
        
        if not sucursal.exists():
            raise NotFound("La sucursal consultada no existe")

        serializer = SucursalesEmpresasSerializer(sucursal, many=True)
        return Response({'success':True, 'detail':'Se muestra las sucursales', 'data':serializer.data},status=status.HTTP_200_OK)
