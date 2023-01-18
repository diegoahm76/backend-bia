from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from datetime import timezone
import copy

from seguridad.models import Personas
from conservacion.models.viveros_models import (
    Vivero,
    HistorialAperturaViveros,
    HistorialCuarentenaViveros
)
from almacen.models.bienes_models import (
    CatalogoBienes,
)
from almacen.serializers.bienes_serializers import (
    CatalogoBienesSerializer,
)
from conservacion.serializers.viveros_serializers import (
    ViveroSerializer,
    AbrirViveroSerializer,
    CerrarViveroSerializer,
    ViveroPostSerializer,
    ViveroSerializerDesactivoSerializer,
    ActivarDesactivarSerializer,
    ViveroPostSerializer,
    ViveroPutSerializer,
    TipificacionBienViveroSerializer
)

class DeleteVivero(generics.RetrieveDestroyAPIView):
    serializer_class = ViveroSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_vivero):
        data = request.data
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success': False, 'detail': 'No se encontró ningún vivero con el id_vivero enviado'}, status=status.HTTP_404_NOT_FOUND)
        if vivero.en_funcionamiento != None:
            return Response({'success': False, 'detail': 'No se puede eliminar un vivero que ha tenido una apertura'}, status=status.HTTP_403_FORBIDDEN)
        vivero.delete()
        # AUDITORIA DE CREATE DE VIVEROS
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        descripcion = {'nombre': vivero.nombre}
        auditoria_data = {
            'id_usuario': user_logeado,
            'id_modulo': 41,
            'cod_permiso': 'BO',
            'subsistema': 'CONS',
            'dirip': dirip,
            'descripcion': descripcion
        }
        Util.save_auditoria(auditoria_data)
        return Response({'success': True, 'detail': 'Se ha eliminado correctamente este vivero'}, status=status.HTTP_204_NO_CONTENT)

class AbrirCerrarVivero(generics.RetrieveUpdateAPIView):
    serializer_class = AbrirViveroSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_vivero):
        data = request.data
        accion = data['accion']
        persona = request.user.persona.id_persona
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success': False, 'detail': 'No se encontró ningún vivero con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
       
        match accion:
            case 'Abrir':
                if vivero.en_funcionamiento == None:
                    if vivero.id_viverista_actual == None:
                        return Response({'success': False, 'detail': 'No se puede abrir un vivero sin un viverista'}, status=status.HTTP_403_FORBIDDEN)
                    data['fecha_ultima_apertura'] = datetime.now()
                    data['en_funcionamiento'] = True
                    data['item_ya_usado'] = True
                    data['id_persona_abre'] = persona
                    serializer = self.serializer_class(vivero, data=data, many=False)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

                    # AUDITORIA
                    user_logeado = request.user.id_usuario
                    dirip = Util.get_client_ip(request)
                    descripcion = {'nombre': vivero.nombre}
                    auditoria_data = {
                        'id_usuario': user_logeado,
                        'id_modulo': 43,
                        'cod_permiso': 'CR',
                        'subsistema': 'CONS',
                        'dirip': dirip,
                        'descripcion': descripcion
                    }
                    Util.save_auditoria(auditoria_data)
                    return Response({'success': True, 'detail': 'Acción realizada correctamente'}, status=status.HTTP_201_CREATED)
                else:
                    if not vivero.fecha_cierre_actual:
                        return Response({'success': False, 'detail': 'No se puede abrir un vivero si no se encuentra actualmente cerrado'}, status=status.HTTP_400_BAD_REQUEST)
                    data['fecha_ultima_apertura'] = datetime.now()
                    data['en_funcionamiento'] = True
                    data['item_ya_usado'] = True
                    serializer = self.serializer_class(vivero, data=data, many=False)
                    serializer.is_valid(raise_exception=True)
                    
                    historial = HistorialAperturaViveros.objects.create(
                        id_vivero = vivero,
                        fecha_apertura_anterior = vivero.fecha_ultima_apertura,
                        fecha_cierre_correspondiente = vivero.fecha_cierre_actual,
                        id_persona_apertura_anterior = vivero.id_persona_abre,
                        id_persona_cierre_correspondiente = vivero.id_persona_cierra,
                        justificacion_apertura_anterior = vivero.justificacion_apertura,
                        justificacion_cierre_correspondiente = vivero.justificacion_cierre
                    )

                    serializer.save()

                    vivero.fecha_cierre_actual = None
                    vivero.id_persona_cierra = None
                    vivero.justificacion_cierre = None
                    vivero.save()

                    # AUDITORIA
                    user_logeado = request.user.id_usuario
                    dirip = Util.get_client_ip(request)
                    descripcion = {'nombre': vivero.nombre}
                    auditoria_data = {
                        'id_usuario': user_logeado,
                        'id_modulo': 43,
                        'cod_permiso': 'CR',
                        'subsistema': 'CONS',
                        'dirip': dirip,
                        'descripcion': descripcion
                    }
                    Util.save_auditoria(auditoria_data)
                    return Response({'success': True, 'detail': 'Acción realizada correctamente'}, status=status.HTTP_201_CREATED)
            
            case 'Cerrar':
                if not vivero.fecha_ultima_apertura:
                    return Response({'success': False, 'detail': 'No se puede cerrar un vivero si no se encuentra actualmente abierto'}, status=status.HTTP_400_BAD_REQUEST)
                data['fecha_cierre_actual'] = datetime.now()
                data['en_funcionamiento'] = False
                data['item_ya_usado'] = True
                data['id_persona_cierra'] = persona
                serializer = CerrarViveroSerializer(vivero, data=data, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                # AUDITORIA
                user_logeado = request.user.id_usuario
                dirip = Util.get_client_ip(request)
                descripcion = {'nombre': vivero.nombre}
                auditoria_data = {
                    'id_usuario': user_logeado,
                    'id_modulo': 43,
                    'cod_permiso': 'CR',
                    'subsistema': 'CONS',
                    'dirip': dirip,
                    'descripcion': descripcion
                }
                Util.save_auditoria(auditoria_data)
                return Response({'success': True, 'detail': 'Acción realizada correctamente'}, status=status.HTTP_201_CREATED)
            case _:
                return Response({'success': False, 'detail': 'Debe enviar una acción válida'}, status=status.HTTP_400_BAD_REQUEST)

class CreateViveros(generics.CreateAPIView):
    serializer_class = ViveroPostSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        persona = request.user.persona.id_persona
        data['id_persona_crea'] = persona
        
        # VALIDAR ASIGNACIÓN VIVERISTA
        viverista = data.get('id_viverista_actual')
        if viverista:
            viverista_existe = Personas.objects.filter(id_persona=viverista)
            if not viverista_existe:
                return Response({'status':False, 'detail':'Debe elegir un viverista que exista'}, status=status.HTTP_400_BAD_REQUEST)
            
            viveristas_actuales = Vivero.objects.filter(id_viverista_actual = viverista)
            
            if viveristas_actuales:
                return Response({'status':False, 'detail':'Debe elegir un viverista que no tenga ningún vivero asignado'}, status=status.HTTP_403_FORBIDDEN)
            
            data['fecha_inicio_viverista_actual'] = datetime.now()
        
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        
        # AUDITORIA DE CREATE DE VIVEROS
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        descripcion = {'nombre':data['nombre']}
        auditoria_data = {
            'id_usuario': user_logeado,
            'id_modulo': 41,
            'cod_permiso': 'CR',
            'subsistema': 'CONS',
            'dirip': dirip,
            'descripcion': descripcion
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success':True, 'detail':'Se ha creado el vivero', 'data':serializador.data}, status=status.HTTP_201_CREATED)

class GetViveroByPk(generics.RetrieveAPIView):
    serializer_class=ViveroSerializer
    queryset=Vivero.objects.all()

class UpdateViveroCuarentena(generics.ListAPIView):
    serializer_class=ViveroSerializer
    queryset=Vivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,id_vivero):
        vivero=Vivero.objects.filter(id_vivero=id_vivero).first()
        if vivero:
            if not request.data.get('justificacion_cuarentena') or  not len(request.data.get('justificacion_cuarentena')):
                return Response({'success':False,'detail':'Envía la justificación'},status=status.HTTP_400_BAD_REQUEST)
            if vivero.en_funcionamiento == True and (vivero.vivero_en_cuarentena == False or vivero.vivero_en_cuarentena == None): 
                vivero.en_funcionamiento = False
                vivero.vivero_en_cuarentena = True
                vivero.id_persona_cuarentena = request.user.persona
                vivero.fecha_inicio_cuarentena = datetime.now()
                vivero.justificacion_cuarentena = request.data['justificacion_cuarentena']
                vivero.save()
                
                # AUDITORIA DE ABRIR CUARENTENA
                user_logeado = request.user.id_usuario
                dirip = Util.get_client_ip(request)
                descripcion = {'nombre':vivero.nombre,'Cuarentena ':vivero.vivero_en_cuarentena}
                auditoria_data = {
                    'id_usuario': user_logeado,
                    'id_modulo': 42,
                    'cod_permiso': 'CR',
                    'subsistema': 'CONS',
                    'dirip': dirip,
                    'descripcion': descripcion
                }
                Util.save_auditoria(auditoria_data)
                return Response({'success':True,'detail':'Vivero ingreso en cuarentena'},status=status.HTTP_200_OK)
            #
            if vivero.en_funcionamiento == False and vivero.vivero_en_cuarentena == True:    
                print("JUSTIFICACION",vivero.justificacion_cuarentena)
                #Historial de cierre de cuarentena
                creacion_historial=HistorialCuarentenaViveros.objects.create(
                        id_vivero=vivero,
                        fecha_inicio_cuarentena=vivero.fecha_inicio_cuarentena,
                        id_persona_inicia_cuarentena=vivero.id_persona_cuarentena,
                        justificacion_inicio_cuarentena= vivero.justificacion_cuarentena,
                        fecha_fin_cuarentena=datetime.now(),
                        id_persona_finaliza_cuarentena= request.user.persona,
                        justifiacion_fin_cuarentena=request.data.get('justificacion_cuarentena')
                )
                vivero.en_funcionamiento = True
                vivero.vivero_en_cuarentena = False
                vivero.id_persona_cuarentena = None
                vivero.fecha_inicio_cuarentena = None
                vivero.justificacion_cuarentena = None
                vivero.save()
                
                # AUDITORIA DE CERRAR CUARENTENA
                user_logeado = request.user.id_usuario
                dirip = Util.get_client_ip(request)
                descripcion = {'nombre':vivero.nombre,'Cuarentena ':vivero.vivero_en_cuarentena}
                auditoria_data = {
                    'id_usuario': user_logeado,
                    'id_modulo': 42,
                    'cod_permiso': 'CR',
                    'subsistema': 'CONS',
                    'dirip': dirip,
                    'descripcion': descripcion
                }
                Util.save_auditoria(auditoria_data)
                return Response({'success ':True,'detail':'Vivero fuera de cuarentena '},status=status.HTTP_200_OK)
            return Response({'success ':False,'detail':'El vivero no se encuentra en funcionamiento '},status=status.HTTP_200_OK)
        else : 
            return Response({'success ':False,'detail':'El vivero seleccionado no existe'},status=status.HTTP_404_NOT_FOUND)
    
class FilterViverosByNombreAndMunicipioForCuarentena(generics.ListAPIView):
    serializer_class=ViveroSerializer
    queryset=Vivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','cod_municipio']:
                if key != 'cod_municipio':
                    filter[key+'__icontains']=value
                else: 
                    filter[key]=value
        vivero=Vivero.objects.filter(**filter).filter(Q(en_funcionamiento=True) | Q(vivero_en_cuarentena=True))
        serializer=self.serializer_class(vivero,many=True)
        if vivero:
            return Response({'success':True,'detail':'Se encontraron viveros','data':serializer.data},status=status.HTTP_200_OK)
        else: 
            return Response({'success':False,'detail':'No se encontraron viveros'},status=status.HTTP_404_NOT_FOUND)
        
class FilterViverosByNombreAndMunicipioForAperturaCierres(generics.ListAPIView):
    serializer_class=ViveroSerializer
    queryset=Vivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','cod_municipio']:
                if key != 'cod_municipio':
                    filter[key+'__icontains']=value
                else:
                    filter[key]=value
        vivero=Vivero.objects.filter(**filter).filter( Q(activo=True) & (Q(vivero_en_cuarentena=False) | Q(vivero_en_cuarentena= None)))
        if vivero:
            serializer=self.serializer_class(vivero,many=True)
            return Response({'success':True,'detail':'Se encontraron viveros','data':serializer.data},status=status.HTTP_200_OK)
        else: 
            return Response({'success':False,'detail':'No se encontraron viveros'},status=status.HTTP_404_NOT_FOUND)

class FilterViverosByNombreAndMunicipio(generics.ListAPIView):
    serializer_class=ViveroSerializer
    queryset=Vivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','cod_municipio']:
                if key != 'cod_municipio':
                    filter[key+'__icontains']=value
                else:
                    filter[key]=value
        vivero=Vivero.objects.filter(**filter)
        if vivero:
            serializer=self.serializer_class(vivero,many=True)
            return Response({'success':True,'detail':'Se encontraron viveros','data':serializer.data},status=status.HTTP_200_OK)
        else: 
            return Response({'success':False,'detail':'No se encontraron viveros'},status=status.HTTP_404_NOT_FOUND)

class UpdateViveros(generics.UpdateAPIView):
    serializer_class = ViveroPutSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id_vivero_ingresado):
        request.data._mutable=True
        data = request.data
        persona = request.user.persona.id_persona
        data['id_persona_crea'] = persona
        vivero_actualizar = Vivero.objects.filter(id_vivero=id_vivero_ingresado).first()
        if not vivero_actualizar:
            return Response({'status':False, 'detail':'No se encontró ningun vivero'}, status=status.HTTP_400_BAD_REQUEST)
        previous = copy.copy(vivero_actualizar)
        # VALIDAR ASIGNACIÓN VIVERISTA
        viverista = data.get('id_viverista_actual')
        if viverista:
            viverista_existe = Personas.objects.filter(id_persona=viverista).first()
            if not viverista_existe:
                return Response({'status':False, 'detail':'Debe elegir un viverista que exista'}, status=status.HTTP_400_BAD_REQUEST)
            if int(viverista) != int(vivero_actualizar.id_viverista_actual.id_persona):
                data['fecha_inicio_viverista_actual'] = datetime.now()
            aux_vivero = Vivero.objects.filter(Q(id_viverista_actual=viverista_existe.id_persona)&~Q(id_vivero=vivero_actualizar.id_vivero))
            if aux_vivero:
                return Response({'status':False, 'detail':'Este viverista ya está asignado a otro vivero'}, status=status.HTTP_400_BAD_REQUEST)
        serializador = self.serializer_class(vivero_actualizar,data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        
        # AUDITORIA DE CREATE DE VIVEROS
        valores_actualizados = {'previous':previous, 'current':vivero_actualizar}
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        descripcion = {'nombre':vivero_actualizar.nombre}
        auditoria_data = {
            'id_usuario': user_logeado,
            'id_modulo': 41,
            'cod_permiso': 'AC',
            'subsistema': 'CONS',
            'dirip': dirip,
            'descripcion': descripcion,
            'valores_actualizados' : valores_actualizados
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success':True, 'detail':'Vivero actualizado con éxito', 'data':serializador.data}, status=status.HTTP_201_CREATED)

class DesactivarActivarViveroView(generics.RetrieveUpdateAPIView):
    serializer_class = ViveroSerializerDesactivoSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_vivero):
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        previous_vivero = copy.copy(vivero)
        if not vivero:
            return Response({'success':False, 'detail':'No existe ningun vivero con el id proporcionado'}, status=status.HTTP_404_NOT_FOUND)
        if vivero.activo == False:
            request.data['activo'] = True
            serializer = self.serializer_class(vivero, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializador = serializer.save()

            # AUDITORÍA ACTIVACIÓN VIVERO
            usuario = request.user.id_usuario
            descripcion = {"nombre": str(previous_vivero.nombre)}
            direccion=Util.get_client_ip(request)
            valores_actualizados = {'previous':previous_vivero, 'current':vivero}
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 41,
                "cod_permiso": "AC",
                "subsistema": 'CONS',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_actualizados": valores_actualizados,
            }
            Util.save_auditoria(auditoria_data)
            return Response({'success': True, 'detail': 'Se ha activado el vivero exitosamente'}, status=status.HTTP_201_CREATED)
        else:
            request.data['activo'] = False
            serializer = self.serializer_class(vivero, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializador = serializer.save()

            # AUDITORÍA DESACTIVACIÓN VIVERO
            usuario = request.user.id_usuario
            descripcion = {"nombre": str(previous_vivero.nombre)}
            direccion=Util.get_client_ip(request)
            valores_actualizados = {'previous':previous_vivero, 'current':vivero}
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 41,
                "cod_permiso": "AC",
                "subsistema": 'CONS',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_actualizados": valores_actualizados,
            }
            Util.save_auditoria(auditoria_data)
            return Response({'success': True, 'detail': 'Vivero desactivado exitosamente'}, status=status.HTTP_201_CREATED)

class TipificacionBienConsumoVivero(generics.UpdateAPIView):
    serializer_class = TipificacionBienViveroSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id_bien):
        data = request.data
        bien = CatalogoBienes.objects.filter(id_bien=id_bien).first()
        
        if bien:
            previous_bien = copy.copy(bien)
            if bien.cod_tipo_bien == 'C' and bien.nivel_jerarquico == 5 and bien.solicitable_vivero:
                serializador = self.serializer_class(bien,data=data)
                serializador.is_valid(raise_exception=True)
                serializador.save()
                
                # AUDITORÍA TIPIFICACIÓN
                usuario = request.user.id_usuario
                descripcion = {"codigo_bien": str(previous_bien.codigo_bien), "nombre": str(previous_bien.nombre)}
                direccion=Util.get_client_ip(request)
                valores_actualizados = {'previous':previous_bien, 'current':bien}
                auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : 44,
                    "cod_permiso": "AC",
                    "subsistema": 'CONS',
                    "dirip": direccion,
                    "descripcion": descripcion,
                    "valores_actualizados": valores_actualizados,
                }
                Util.save_auditoria(auditoria_data)
            else:
                return Response({'success':False, 'detail':'No puede tipificar el bien ingresado'})
            
            return Response({'success':True, 'detail':'Bien tipificado con éxito', 'data':serializador.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success':False, 'detail':'No existe el bien ingresado'}, status=status.HTTP_404_NOT_FOUND)
