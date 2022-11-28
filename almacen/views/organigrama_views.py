from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from itertools import groupby
from seguridad.utils import Util
from django.db.models import Q
from datetime import datetime
import copy
from django.db.models import Q
from operator import itemgetter
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from almacen.serializers.organigrama_serializers import ( 
    OrganigramaSerializer,
    OrganigramaPutSerializer, 
    UnidadesPutSerializer, 
    OrganigramaActivateSerializer, 
    NivelesUpdateSerializer, 
    NivelesGetSerializer,
    UnidadesGetSerializer,
    OrganigramaPostSerializer
    )
from almacen.models.organigrama_models import (
    Organigramas,
    UnidadesOrganizacionales,
    NivelesOrganigrama
    )
from rest_framework.permissions import IsAuthenticated

# VIEWS FOR NIVELES ORGANIGRAMA
class UpdateNiveles(generics.UpdateAPIView):
    serializer_class = NivelesUpdateSerializer
    queryset = NivelesOrganigrama.objects.all()

    def put(self, request, id_organigrama):
        data = request.data

        #VALIDACION DE ORGANIGRAMA
        try:
            organigrama = Organigramas.objects.get(id_organigrama=id_organigrama)
            pass
        except:
            return Response({'success': False, 'detail': 'No se pudo encontrar un organigrama con el parámetro ingresado'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDA SI NO HA CREADO NINGÚN NIVEL
        if not data:
            return Response({'success': False, 'detail': 'No se puede guardar sin crear al menos un nivel'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE ID_ORGANIGRAMA SEA EL MISMO
        niveles_list_id = [nivel['id_organigrama'] for nivel in data]
        if len(set(niveles_list_id)) != 1:
             return Response({'success':False, 'detail':'Debe validar que los niveles pertenezcan a un mismo Organigrama'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if niveles_list_id[0] != int(id_organigrama):
                return Response({'success':False, 'detail':'El id organigrama de la petición debe ser igual al enviado en url'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACION DE FECHA DE TERMINADO
        if organigrama.fecha_terminado != None:
            return Response({'success': False, 'detail': 'El organigrama ya está terminado, por lo cúal no es posible realizar acciones sobre los niveles'}, status=status.HTTP_403_FORBIDDEN)

        #CREACION DE NIVELES Y VALIDACION DEL ORDEN DE NIVEL
        contador = 1
        for nivel in data:
            orden_nivel = nivel.get('orden_nivel')
            
            if orden_nivel == contador:
                contador += 1
                pass
            else:
                return Response({'success': False, 'detail': 'No coincide el orden de los niveles'}, status=status.HTTP_400_BAD_REQUEST)
        
        #Creación de niveles
        niveles_create = list(filter(lambda nivel: nivel['id_nivel_organigrama'] == None, data))
        niveles_id_create = []
        if niveles_create:
            serializer = self.serializer_class(data=niveles_create, many=True)
            serializer.is_valid(raise_exception=True)
            serializador = serializer.save()
            niveles_id_create_dos = [nivel.id_nivel_organigrama for nivel in serializador]
            niveles_id_create.extend(niveles_id_create_dos)

        #Update de niveles
        niveles_update = list(filter(lambda nivel: nivel['id_nivel_organigrama'] != None, data))
        if niveles_update:
            for nivel in niveles_update:
                nivel_existe = NivelesOrganigrama.objects.filter(id_nivel_organigrama=nivel['id_nivel_organigrama']).first()
                if nivel_existe:
                    serializer = self.serializer_class(nivel_existe, data=nivel)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        
        #Delete de niveles
        lista_niveles_id = [nivel['id_nivel_organigrama'] for nivel in niveles_update]
        lista_niveles_id.extend(niveles_id_create)
        niveles_total = NivelesOrganigrama.objects.filter(id_organigrama=id_organigrama).exclude(id_nivel_organigrama__in=lista_niveles_id)
        
        #Validacion NO PODER ELIMINAR eliminar un nivel que ya está siendo usado
        niveles_eliminar_list = [nivel.id_nivel_organigrama for nivel in niveles_total]
        if UnidadesOrganizacionales.objects.filter(id_nivel_organigrama__in=niveles_eliminar_list).exists():
            return Response({'success': False, 'detail': 'El nivel que intenta eliminar ya se encuentra relacionado con una unidad organizacional'}, status=status.HTTP_400_BAD_REQUEST)
        niveles_total.delete()

        return Response({'success':True,'detail': 'Actualizacion exitosa de los niveles'}, status=status.HTTP_201_CREATED)

class GetNiveles(generics.ListAPIView):
    serializer_class = NivelesGetSerializer

    def get(self, request):
        consulta = request.query_params.get('pk')
        if consulta == None:
            niveles = NivelesOrganigrama.objects.all().values()
            if len(niveles) == 0:
                return Response({'success': False, 'detail' : 'Aún no hay niveles registrados'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'success': True, 'Niveles' : niveles}, status=status.HTTP_200_OK)
        else:
            nivel = NivelesOrganigrama.objects.filter(id_nivel_organigrama=int(consulta)).values()
            return Response({'success': True, 'Nivel': nivel}, status=status.HTTP_200_OK)


class GetNivelesByOrganigrama(generics.ListAPIView):
    serializer_class = NivelesGetSerializer
    queryset = NivelesOrganigrama.objects.all()
    lookup_field = 'id_organigrama'

    def get(self, request, id_organigrama):
        niveles = NivelesOrganigrama.objects.filter(id_organigrama=id_organigrama)
        if not niveles:
            return Response({'success': True, 'detail': 'No se encontraron niveles para el organigrama ingresado', 'data': niveles.values()}, status=status.HTTP_200_OK)
        serializer = self.serializer_class(niveles, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes niveles para el organigrama ingresado', 'data': serializer.data}, status=status.HTTP_200_OK)


#VIEWS FOR UNIDADES ORGANIZACIONALES 
class UpdateUnidades(generics.UpdateAPIView):
    serializer_class=UnidadesPutSerializer
    queryset=UnidadesOrganizacionales.objects.all()

    def put(self, request, pk):
        data = request.data
        organigrama=Organigramas.objects.filter(id_organigrama=pk).first()
        if organigrama:
            if not organigrama.fecha_terminado:
                if data:
                    nivel_unidades = sorted(data, key=itemgetter('id_nivel_organigrama'))
                    
                    # ELIMINACION DE UNIDADES
                    unidades_eliminar = UnidadesOrganizacionales.objects.filter(id_organigrama=pk)
                    unidades_eliminar.delete()
                    
                    # VALIDACIONES
                    
                    # VALIDACIÓN DE EXISTENCIA DE NIVELES
                    niveles_list = [unidad['id_nivel_organigrama'] for unidad in data]
                    niveles_existe = NivelesOrganigrama.objects.filter(id_nivel_organigrama__in=niveles_list)
                    if niveles_existe.count() != len(list(dict.fromkeys(niveles_list))):
                        return Response({'success':False, 'detail':'Uno o varios niveles que está asociando no existen'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDACIÓN DE UNA SOLA RAÍZ          
                    raiz_list = [unidad['unidad_raiz'] for unidad in data]
                    if raiz_list.count(True) > 1:
                        return Response({'success':False, 'detail':'No puede definir más de una unidad como raíz'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDACIÓN DE EXISTENCIA UNIDAD RAÍZ Y PERTENENCIA A NIVEL UNO
                    unidad_raiz = list(filter(lambda unidad: unidad['unidad_raiz'] == True, data))
                    if unidad_raiz:
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=unidad_raiz[0]['id_nivel_organigrama']).first()
                        if nivel_instance.orden_nivel != 1:
                            return Response({'success':False, 'detail':'La unidad raíz solo puede pertenecer al nivel uno'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'success':False, 'detail':'Debe enviar la unidad raíz'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDACIÓN QUE SECCIÓN SEA UNIDAD RAÍZ
                    seccion_raiz = list(filter(lambda unidad: unidad['cod_agrupacion_documental'] == 'SEC', data))
                    if seccion_raiz:
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=seccion_raiz[0]['id_nivel_organigrama']).first()
                        if nivel_instance.orden_nivel != 1:
                            return Response({'success':False, 'detail':'La sección solo puede pertenecer a la unidad raíz'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDACIÓN QUE UNIDADES STAFF SEAN DE NIVEL DOS
                    staff_unidades = list(filter(lambda unidad: unidad['cod_tipo_unidad'] != 'LI', data))
                    for unidad in staff_unidades:
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=unidad['id_nivel_organigrama']).first()
                        if nivel_instance.orden_nivel != 2:
                            return Response({'success':False, 'detail':'Las unidades de staff solo pueden pertenecer al nivel dos'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDACIÓN DE EXISTENCIA DE SECCIÓN Y UNA SOLA SECCIÓN
                    seccion_list = [unidad['cod_agrupacion_documental'] for unidad in data]
                    if seccion_list:
                        if seccion_list.count('SEC') > 1:
                            return Response({'success':False, 'detail':'No puede definir más de una unidad como sección'}, status=status.HTTP_400_BAD_REQUEST)
                        if ('SUB' in seccion_list) and ('SEC' not in seccion_list):
                            return Response({'success':False, 'detail':'Debe definir la sección para las subsecciones'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDACIÓN DE EXISTENCIA DE UNIDADES PADRE
                    unidades_codigo_list = [unidad['codigo'] for unidad in data]
                    unidades_padre_list = [unidad['cod_unidad_org_padre'] for unidad in data if unidad['cod_unidad_org_padre'] is not None]
                    if not set(unidades_padre_list).issubset(unidades_codigo_list):
                        return Response({'success':False, 'detail':'Debe asociar unidades padre que existan'}, status=status.HTTP_400_BAD_REQUEST)          
                            
                    # VALIDACIÓN DE UNA UNIDAD EN NIVEL UNO
                    current_cod_unidades = []
                    for nivel, unidades in groupby(nivel_unidades, itemgetter('id_nivel_organigrama')):
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=nivel).first()
                        unidades_list = list(unidades)
                        
                        # VALIDACIÓN DE UNIDAD PADRE QUE SEA DE  LÍNEA Y DE NIVEL SUPERIOR
                        unidades_codigo_list = [unidad['codigo'] for unidad in unidades_list if unidad['cod_tipo_unidad'] == 'LI']
                        current_cod_unidades.extend(unidades_codigo_list)
                        unidades_padre_list = [unidad['cod_unidad_org_padre'] for unidad in unidades_list if unidad['cod_unidad_org_padre'] is not None]
                        if not set(unidades_padre_list).issubset(current_cod_unidades):
                            return Response({'success':False, 'detail':'Debe asociar unidades padre de línea y superiores a unidades hijos'}, status=status.HTTP_400_BAD_REQUEST)   
                        
                        # VALIDACIÓN DE UNA UNIDAD EN NIVEL UNO
                        if nivel_instance.orden_nivel == 1 and (len(unidades_list) > 1):
                            return Response({'success':False, 'detail':'Solo debe establecer una unidad para el nivel uno'}, status=status.HTTP_400_BAD_REQUEST)
                        if nivel_instance.orden_nivel != 1:
                            
                            # VALIDACIÓN DEFINIR PADRES EN TODAS LOS NIVELES MENOS EL UNO
                            unidades_org = list(filter(lambda unidad: (unidad['cod_unidad_org_padre'] == None or unidad['cod_unidad_org_padre'] == '') and (unidad['cod_tipo_unidad'] == 'LI'), unidades_list))
                            if unidades_org:
                                return Response({'success':False, 'detail':'Debe definir el padre en todas las unidades de línea que no sea la raíz'}, status=status.HTTP_400_BAD_REQUEST)                
                            
                            # VALIDACIÓN QUE EL PADRE DE SUBSECCIÓN ESTÉ MARCADO COMO SUBSECCIÓN
                            unidades_sub = list(filter(lambda unidad: unidad['cod_agrupacion_documental'] == 'SUB', unidades_list))
                            if unidades_sub:
                                unidad_padre = list(filter(lambda unidad: unidad['codigo'] == unidades_sub[0]['cod_unidad_org_padre'], data))
                                if unidad_padre:
                                    if unidad_padre[0]['cod_agrupacion_documental'] == None or unidad_padre[0]['cod_agrupacion_documental'] == '':
                                        return Response({'success':False, 'detail':'Debe marcar las unidades padre como subsecciones'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # CREACION DE UNIDADES
                    for nivel, unidades in groupby(nivel_unidades, itemgetter('id_nivel_organigrama')):
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=nivel).first()
                        for unidad in unidades:
                            unidad_serializer = self.serializer_class(data=unidad)
                            unidad_serializer.is_valid(raise_exception=True)
                            
                            unidad_org = None
                            
                            if unidad['cod_tipo_unidad'] == 'LI':
                                unidad_org = UnidadesOrganizacionales.objects.filter(codigo=unidad['cod_unidad_org_padre']).first()
                                unidad_org = unidad_org if unidad_org else None
                            else:
                                unidad['cod_agrupacion_documental'] = None
                            
                            UnidadesOrganizacionales.objects.create(
                                id_nivel_organigrama=nivel_instance,
                                nombre=unidad['nombre'],
                                codigo=unidad['codigo'],
                                cod_tipo_unidad=unidad['cod_tipo_unidad'],
                                cod_agrupacion_documental=unidad['cod_agrupacion_documental'],
                                unidad_raiz=unidad['unidad_raiz'],
                                id_organigrama=organigrama,
                                id_unidad_org_padre=unidad_org
                            )
                    
                    return Response({'success':True,'detail': 'Actualizacion exitosa de las unidades'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success':False, 'detail':'Debe crear por lo menos una unidad'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success':False, 'detail':'El organigrama ya está terminado, por lo cual no es posible realizar acciones sobre las unidades'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success':False, 'detail':'El organigrama no existe'}, status=status.HTTP_404_NOT_FOUND)


class GetUnidades(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.filter()
        
    def get(self, request):
        consulta = request.query_params.get('pk')
        if consulta == None:
            unidades = UnidadesOrganizacionales.objects.all().values()
            if len(unidades) == 0:
                return Response({'success': False, 'detail' : 'Aún no hay unidades registradas'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'success': True, 'Unidades' : unidades}, status=status.HTTP_200_OK)
        unidades = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = int(consulta)).values()
        unidades_vector = unidades[0]
        id_niveles = unidades_vector['id_nivel_organigrama_id']
        nivel = NivelesOrganigrama.objects.filter(id_nivel_organigrama = id_niveles).values()
        unidades_vector['id_nivel_organigrama_id'] = nivel
        return Response({'success': True, 'Unidades' : unidades_vector}, status=status.HTTP_200_OK)

class GetUnidadesByOrganigrama(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.filter()
        
    def get(self, request, id_organigrama):
        organigrama = Organigramas.objects.filter(id_organigrama=id_organigrama).first()
        if organigrama:
            unidades = UnidadesOrganizacionales.objects.filter(id_organigrama = id_organigrama).values()
            if unidades:
                return Response({'success': True, 'detail': 'Se encontraron unidades para el organigrama', 'data' : unidades}, status=status.HTTP_200_OK)
            else:
                return Response({'success': True, 'detail': 'No se encontraron unidades para el organigrama', 'data' : unidades}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'El organigrama no existe'}, status=status.HTTP_404_NOT_FOUND)

#VIEWS FOR ORGANIGRAMA
class FinalizarOrganigrama(generics.UpdateAPIView):
    serializer_class=OrganigramaSerializer
    queryset=Organigramas.objects.all()
    
    def put(self,request,pk):
        confirm = request.query_params.get('confirm')
        organigrama_a_finalizar=Organigramas.objects.filter(id_organigrama=pk).first()
        if organigrama_a_finalizar:
            if not organigrama_a_finalizar.fecha_terminado:
                niveles=NivelesOrganigrama.objects.filter(id_organigrama=pk) 
                unidades=UnidadesOrganizacionales.objects.filter(id_organigrama=pk) 
                nivel_list= [nivel.id_nivel_organigrama for nivel in niveles] 
                nivel_unidad_list=[unidad.id_nivel_organigrama.id_nivel_organigrama for unidad in unidades]
                if not niveles:
                    return Response({'success':False,'detail':'No se puede finalizar organigrama si no cuenta con minimo un nivel'}, status=status.HTTP_403_FORBIDDEN)
                if not unidades:
                    return Response({'success':False,'detail':'No se puede finalizar organigrama porque debe contener por lo menos una unidad'}, status=status.HTTP_403_FORBIDDEN)
               #Confirmación de unidades para borrar las que no están siendo utilizadas
                if confirm == 'true':
                    nivel_difference_list = [nivel for nivel in nivel_list if nivel not in nivel_unidad_list]
                    nivel_difference_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama__in=nivel_difference_list)
                    nivel_difference_list1=sorted(nivel_difference_list,reverse=True)
                    nivel_list1=sorted(nivel_list,reverse=True)
                    cont=0
                    for nivel in nivel_difference_list1:
                        nivel_difference_values = NivelesOrganigrama.objects.filter(id_nivel_organigrama=nivel).values().first()
                        if nivel == nivel_list1[cont]:
                            cont = cont+1
                            nivel_difference_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=nivel).first()
                            nivel_difference_instance.delete()
                        else:
                            return Response({"Detail":"No se puede borrar",'La unidad que no se puede borrar es= ':nivel_difference_values})
                    return Response({'success':True,'detail':'Niveles eliminadas'},status=status.HTTP_200_OK)
                if nivel_list and not nivel_unidad_list: # si los niveles no se está utilizando (hace comparacion de dos listas)
                    nivel_difference_list = [nivel for nivel in nivel_list if nivel not in nivel_unidad_list]
                    nivel_difference_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama__in=nivel_difference_list).values()
                    return Response({'success':False,'detail':'No se puede finalizar organigrama porque debe utilizar todos los niveles', 'Niveles sin asignar': nivel_difference_instance}, status=status.HTTP_403_FORBIDDEN)
                if not set(nivel_list).issubset(nivel_unidad_list): 
                    nivel_difference_list = [nivel for nivel in nivel_list if nivel not in nivel_unidad_list]
                    print('NO SE ESTAN UTILIZANDO',nivel_difference_list)
                    nivel_difference_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama__in=nivel_difference_list).values()
                    return Response({'success':False,'detail':'No se puede finalizar organigrama porque debe utilizar todos los niveles', 'Niveles sin asignar': nivel_difference_instance}, status=status.HTTP_403_FORBIDDEN)
                organigrama_a_finalizar.fecha_terminado=datetime.now()
                organigrama_a_finalizar.save()
                return Response({'success':True,'detail':'Se Finalizo el organigrama correctamente'},status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'Ya se encuentra finalizado este Organigrama'})

        return Response({'success':False,'detail':'No existe organigrama'},status=status.HTTP_403_FORBIDDEN)
class CreateOrgChart(generics.CreateAPIView):
    serializer_class = OrganigramaPostSerializer
    queryset = Organigramas.objects.all()
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pass
        except:
            return Response({'success': False, 'detail': 'Validar la data ingresada, el nombre debe ser único y es requerido, la descripción y la versión son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        serializador = serializer.save()

        #Auditoria Crear Organigrama
        usuario = request.user.id_usuario
        descripcion = {"Nombre": str(serializador.nombre), "Versión": str(serializador.version)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 15,
            "cod_permiso": "CR",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': True, 'detail': serializer.data}, status=status.HTTP_201_CREATED)

class UpdateOrganigrama(generics.RetrieveUpdateAPIView):
    serializer_class = OrganigramaPutSerializer
    queryset= Organigramas.objects.all()
    lookup_field='id_organigrama'
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_organigrama):
        organigrama = Organigramas.objects.get(id_organigrama=id_organigrama)   
        previous_organigrama = copy.copy(organigrama)
        if organigrama.fecha_terminado:
            return Response({'success': False, 'detail': 'No se puede actualizar un organigrama que ya está terminado'})   
        ccd = list(CuadrosClasificacionDocumental.objects.filter(id_organigrama=organigrama.id_organigrama).values())
        if not len(ccd):
            serializer = self.serializer_class(organigrama, data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                pass
            except:
                return Response({'success': False, 'detail': 'Validar la data ingresada, el nombre debe ser único y es requerido, la descripción y la versión son requeridos'},status=status.HTTP_400_BAD_REQUEST)    
            serializer.save()

            # AUDITORIA DE UPDATE DE ORGANIGRAMA
            user_logeado = request.user.id_usuario
            dirip = Util.get_client_ip(request)
            descripcion = {'nombre':str(previous_organigrama.nombre), 'version':str(previous_organigrama.version)}
            valores_actualizados={'previous':previous_organigrama, 'current':organigrama}
            auditoria_data = {
                'id_usuario': user_logeado,
                'id_modulo': 15,
                'cod_permiso': 'AC',
                'subsistema': 'TRSV',
                'dirip': dirip,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }
            Util.save_auditoria(auditoria_data)
            return Response({'success': True, 'detail': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'sucsess': False, 'detail': 'Ya está siendo usado este organigrama'}, status=status.HTTP_403_FORBIDDEN)

class GetOrganigrama(generics.ListAPIView):
    serializer_class = OrganigramaSerializer  

    def get(self, request):
        consulta = request.query_params.get('pk')
        if consulta == None:
            organigramas = Organigramas.objects.all().values()
            if len(organigramas) == 0:
                return Response({'success':False, 'detail' : 'Aún no hay organigramas registrados'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'Organigramas' : organigramas}, status=status.HTTP_200_OK) 
        organigrama = Organigramas.objects.filter(id_organigrama=int(consulta)).values()
        if len(organigrama) == 0:
            return Response({'success': False, 'detail' : 'No se encontró el organigrama ingresado'}, status=status.HTTP_404_NOT_FOUND)
        niveles = NivelesOrganigrama.objects.filter(id_organigrama=int(consulta)).values()
        if len(niveles) == 0:
            niveles = 'No hay niveles registrados'
            unidades = 'No hay unidades registradas'
            datos_finales = {'Organigrama' : organigrama, 'Niveles' : niveles, 'Unidades' : unidades}
            return Response({'Organigrama' : datos_finales}, status=status.HTTP_200_OK)   
        unidades = UnidadesOrganizacionales.objects.filter(id_organigrama=int(consulta)).values()
        if len(unidades) == 0:
            unidades = 'No hay unidades registradas'
            datos_finales = {'Organigrama' : organigrama, 'Niveles' : niveles, 'Unidades' : unidades}
            return Response({'Organigrama' : datos_finales}, status=status.HTTP_200_OK)
        datos_finales = {'Organigrama' : organigrama, 'Niveles' : niveles, 'Unidades' : unidades}
        return Response({'Organigrama' : datos_finales}, status=status.HTTP_200_OK)

class GetSeccionSubsecciones(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    
    def get(self, request, id_organigrama):
        organigrama = Organigramas.objects.filter(id_organigrama=id_organigrama).first()
        if organigrama:
            unidades = UnidadesOrganizacionales.objects.filter(Q(id_organigrama=id_organigrama) & ~Q(cod_agrupacion_documental=None))
            serializer = self.serializer_class(unidades, many=True)
            return Response({'success':True, 'detail':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'Debe consultar por un organigrama válido'}, status=status.HTTP_404_NOT_FOUND)
            
class GetOrganigramasTerminados(generics.ListAPIView):
    serializer_class = OrganigramaSerializer
    queryset = Organigramas.objects.filter(~Q(fecha_terminado=None) & Q(fecha_retiro_produccion=None))  
