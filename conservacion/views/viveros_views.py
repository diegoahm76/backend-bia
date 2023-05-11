from conservacion.serializers.viveros_serializers import PersonasAsignacionViveroSerializer
from conservacion.serializers.viveros_serializers import ViveristaActualSerializers
from conservacion.models.viveros_models import HistoricoResponsableVivero
from conservacion.serializers.viveros_serializers import HistorialViveristaByViveroSerializers
from rest_framework import generics, status
from seguridad.serializers.personas_serializers import PersonasFilterSerializer
from seguridad.utils import Util  
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from datetime import timezone
from django.db.models.functions import Concat
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
from conservacion.models.inventario_models import (
    InventarioViveros
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

class DeleteVivero(generics.DestroyAPIView):
    serializer_class = ViveroSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_vivero):
        
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        vivero_eliminar = vivero
        
        if not vivero:
            raise NotFound('No se encontró ningún vivero con el id_vivero enviado')
        
        if vivero.en_funcionamiento != None:
            raise PermissionDenied('No se puede eliminar un vivero que ha tenido una apertura')
        
        vivero.delete()
        
        # AUDITORIA DE CREATE DE VIVEROS
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        descripcion = {'nombre': str(vivero_eliminar.nombre)}
        auditoria_data = {
            'id_usuario': user_logeado,
            'id_modulo': 41,
            'cod_permiso': 'BO',
            'subsistema': 'CONS',
            'dirip': dirip,
            'descripcion': descripcion
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success': True, 'detail': 'Se ha eliminado correctamente este vivero'}, status=status.HTTP_200_OK)

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
            raise NotFound('No se encontró ningún vivero con el parámetro ingresado')
       
        match accion:
            case 'Abrir':
                if vivero.en_funcionamiento == None:
                    if vivero.id_viverista_actual == None:
                        raise PermissionDenied('No se puede abrir un vivero sin un viverista')
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
                        raise ValidationError('El vivero ya se encuentra abierto')
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
                    raise ValidationError('No se puede cerrar un vivero si no se encuentra actualmente abierto')
                data['fecha_cierre_actual'] = datetime.now()
                data['en_funcionamiento'] = False
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
                raise ValidationError('Debe enviar una acción válida')

class CreateViveros(generics.CreateAPIView):
    serializer_class = ViveroPostSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        persona = request.user.persona.id_persona
        data['id_persona_crea'] = persona
    
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
                return Response({'success':True,'detail':'El Vivero ingresó en cuarentena'},status=status.HTTP_200_OK)
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
            raise PermissionDenied ('El vivero se encuentra en funcionamiento ')
        else : 
            raise NotFound('El vivero seleccionado no existe')
    
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
        serializer=self.serializer_class(vivero,many=True, context = {'request':request})
        if vivero:
            return Response({'success':True,'detail':'Se encontraron viveros','data':serializer.data},status=status.HTTP_200_OK)
        else: 
            raise NotFound('No se encontraron viveros')
        
        
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
            serializer=self.serializer_class(vivero,many=True, context = {'request':request})
            return Response({'success':True,'detail':'Se encontraron viveros','data':serializer.data},status=status.HTTP_200_OK)
        else: 
            raise NotFound('No se encontraron viveros')
        

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
            serializer=self.serializer_class(vivero,many=True, context = {'request':request})
            return Response({'success':True,'detail':'Se encontraron viveros','data':serializer.data},status=status.HTTP_200_OK)
        else: 
            raise NotFound('No se encontraron viveros')
        

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
            raise ValidationError('No se encontró ningun vivero')
        previous = copy.copy(vivero_actualizar)
        
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
            raise NotFound('No existe ningun vivero con el id proporcionado')
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
            # VALIDAR QUE EL BIEN NO EXISTA EN INVENTARIO VIVERO
            inventario_vivero = InventarioViveros.objects.filter(id_bien=bien.id_bien)
            
            if inventario_vivero:
                raise PermissionDenied('No puede realizar la tipificación porque este bien ya fue distribuido')
            
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
                raise PermissionDenied('No puede tipificar el bien ingresado')
            
            return Response({'success':True, 'detail':'Bien tipificado con éxito', 'data':serializador.data}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe el bien ingresado')
        
class HistorialViveristaByVivero (generics.ListAPIView):

    serializer_class = HistorialViveristaByViveroSerializers
    queryset = HistoricoResponsableVivero.objects.all()
    
    def get(self,request,id_vivero):
        
        vivero = Vivero.objects.filter(id_vivero=id_vivero,activo=True).first()
        
        if not vivero:
            raise NotFound('No existe el vivero o está desactivado')
        
        viveristas = self.queryset.all().filter(id_vivero=vivero.id_vivero)
        
        if viveristas:
            
            serializador = self.serializer_class(viveristas,many=True)
            
            return Response ({'success':True,'detail':'Se encontraron registros','data':serializador.data},status=status.HTTP_200_OK)
        else:
            return Response ({'success':False,'detail':'No se encontraron registros'},status=status.HTTP_200_OK)
        
    
class GetViveristaActual(generics.ListAPIView):
    
    serializer_class = ViveristaActualSerializers
    queryset = Vivero.objects.all()
    
    def get (self,request,id_vivero):
        
        vivero = self.queryset.all().filter(id_vivero = id_vivero,activo=True).first()
        if vivero:
            
            if vivero.id_viverista_actual:
                        
                serializador = self.serializer_class(vivero,many=False)
                
                return Response ({'success':True,'detail':'El vivero ingresado tiene viverista actualmente','data':serializador.data},status=status.HTTP_200_OK)
            else:
                return Response ({'success':True,'detail':'El vivero ingresado no tiene viverista actual'},status=status.HTTP_200_OK)
        
        else:
            raise NotFound('El vivero no existe o no está activo')

        
class GetPersonaFiltro (generics.ListAPIView):
    
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()
    
    def get(self,request):
        
        filter={}
            
        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento','primer_nombre','segundo_nombre','primer_apellido','segundo_apellido']:
                if key == 'numero_documento':
                    if value != '':
                        filter[key+'__startswith']=value
                elif key == 'tipo_documento':
                    if value != '':
                        filter[key]=value
                else:
                    if value != '':
                        filter[key+'__icontains']=value
                
        persona = self.queryset.all().filter(**filter).filter(~Q(id_cargo=None) & ~Q(id_unidad_organizacional_actual=None) & Q(es_unidad_organizacional_actual=True))

        print('PERSONA',persona)
        if persona: 
            
            serializador = self.serializer_class(persona,many=True)
            
            return Response ({'success':True,'detail':'Se encontraron personas: ','data':serializador.data},status=status.HTTP_200_OK) 
        
        else:
            return Response ({'success':True,'detail':'No se encontraron personas','data':[]},status=status.HTTP_200_OK) 
            

class GetPersonaByNumeroDocumento(generics.ListAPIView):
    
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()
    
    def get(self,request):
        filter = {}
        numero_documento = request.query_params.get('numero_documento')
        tipo_documento = request.query_params.get('tipo_documento')
        
        if not numero_documento or not tipo_documento:
            raise PermissionDenied('Debe de seleccionar el tipo de documento y digitar el número de documento')

        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento']:
                filter[key]=value
        
        persona = Personas.objects.filter(**filter).filter(~Q(id_cargo=None) and ~Q(id_unidad_organizacional_actual=None) and Q(es_unidad_organizacional_actual=True))

        if persona: 
            
            serializador = self.serializer_class(persona,many=True)
            
            return Response ({'success':True,'detail':'Se encontraron personas: ','data':serializador.data},status=status.HTTP_200_OK) 
        
        else:
            return Response ({'success':True,'detail':'No existe la persona, o no está en una unidad organizacional actual','data':[]},status=status.HTTP_200_OK) 
        

class GuardarAsignacionViverista(generics.CreateAPIView):
    
    serializer_class = ViveroSerializer
    queryset = Vivero.objects.all()
    
    def post(self,request,id_vivero):
        
        data = request.data
        
        vivero = Vivero.objects.filter(id_vivero = id_vivero).first()
        persona = Personas.objects.filter(id_persona = data['id_persona']).filter(~Q(id_cargo=None) and ~Q(id_unidad_organizacional_actual=None) and Q(es_unidad_organizacional_actual=True)).first()

        if vivero:
            
            if vivero.id_viverista_actual == persona:
                raise PermissionDenied('La persona seleccionada ya es el viverista de este vivero')
            
            if vivero.id_viverista_actual == None and vivero.fecha_inicio_viverista_actual == None:
                
                vivero.id_viverista_actual = persona
                vivero.fecha_inicio_viverista_actual = datetime.now()
            
            else:
                
                historico = HistoricoResponsableVivero.objects.filter(id_vivero=vivero.id_vivero, id_persona=vivero.id_viverista_actual).last()
                
                consecutivo = 1
                
                if historico:
                    consecutivo = historico.consec_asignacion + 1
                
                HistoricoResponsableVivero.objects.create(
                    id_vivero = vivero,
                    id_persona = vivero.id_viverista_actual,
                    consec_asignacion = consecutivo,
                    fecha_inicio_periodo = vivero.fecha_inicio_viverista_actual,
                    fecha_fin_periodo = datetime.now(),
                    observaciones = data['observaciones'],
                    id_persona_cambia = request.user.persona,
                    )

                vivero.id_viverista_actual = persona
                vivero.fecha_inicio_viverista_actual = datetime.now()
            
            vivero.save()
            
            return Response({'success':True,'detail':'La asignación del viverista fue exitosa'},status=status.HTTP_200_OK)
        else:
            raise NotFound('El vivero no existe')      
                    
        

class GetBienesConsumoFiltro (generics.ListAPIView):
    
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    
    def get (self,request):
        
        filter={}
        
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre_cientifico','nombre','cod_tipo_elemento_vivero']:
                if key == 'codigo_bien':
                    if value != "":
                        filter[key+'__startswith']=value
                elif key == 'nombre_cientifico' or key == 'nombre':
                    if value != "":
                        filter[key+'__icontains']=value
                else:
                    if value != "":
                        filter[key]=value
                    
        filter['solicitable_vivero'] = True
        filter['nivel_jerarquico'] = 5
        filter['cod_tipo_bien'] = "C"
        
        bienes = self.queryset.all().filter(**filter)
        
        if bienes:
            serializador = self.serializer_class(bienes,many = True)
            
            return Response({'success':True,'detail':'Se encontraron bienes','data':serializador.data},status=status.HTTP_200_OK)
        
        else: return Response({'success':True,'detail':'No se encontraron bienes'},status=status.HTTP_200_OK)

class GetBienesConsumoByCodigoBien(generics.ListAPIView):
    
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    
    def get (self,request):
        
        filter={}
        
        codigo_bien = request.query_params.get('codigo_bien')
                    
        filter['solicitable_vivero'] = True
        filter['nivel_jerarquico'] = 5
        filter['cod_tipo_bien'] = "C"
        filter['codigo_bien'] = codigo_bien
        
        bien = self.queryset.all().filter(**filter).first()
        
        if bien:
            serializador = self.serializer_class(bien)
            
            return Response({'success':True,'detail':'Se encontró el bien','data':serializador.data},status=status.HTTP_200_OK)
        
        else: return Response({'success':True,'detail':'No se encontró el bien'},status=status.HTTP_200_OK)
            
        
        