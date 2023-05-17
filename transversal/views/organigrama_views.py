from rest_framework import status
from rest_framework import generics, views
from rest_framework.views import APIView
from rest_framework.response import Response
from itertools import groupby
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.serializers.ccd_serializers import CCDSerializer
from seguridad.utils import Util
from django.db.models import Q, F
from datetime import datetime
from django.contrib.auth import get_user
import copy
from operator import itemgetter
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from transversal.serializers.organigrama_serializers import ( 
    NewUserOrganigramaSerializer,
    OrganigramaCambioDeOrganigramaActualSerializer,
    OrganigramaSerializer,
    OrganigramaPutSerializer,
    PersonaOrgSerializer, 
    UnidadesPutSerializer, 
    OrganigramaActivateSerializer, 
    NivelesUpdateSerializer, 
    NivelesGetSerializer,
    UnidadesGetSerializer,
    OrganigramaPostSerializer,
    ActUnidadOrgAntiguaSerializer
    )
from transversal.models.organigrama_models import (
    Organigramas,
    UnidadesOrganizacionales,
    NivelesOrganigrama
    )
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from seguridad.models import User, Personas, HistoricoCargosUndOrgPersona
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

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
            raise ValidationError('No se pudo encontrar un organigrama con el parámetro ingresado')
        
        #VALIDA SI NO HA CREADO NINGÚN NIVEL
        if not data:
            raise ValidationError('No se puede guardar sin crear al menos un nivel')
        
        #VALIDACIÓN QUE ID_ORGANIGRAMA SEA EL MISMO
        niveles_list_id = [nivel['id_organigrama'] for nivel in data]
        if len(set(niveles_list_id)) != 1:
            raise ValidationError('Debe validar que los niveles pertenezcan a un mismo Organigrama')
        else:
            if niveles_list_id[0] != int(id_organigrama):
                raise ValidationError('El id organigrama de la petición debe ser igual al enviado en url')

        #VALIDACION DE FECHA DE TERMINADO
        if organigrama.fecha_terminado != None:
            raise PermissionDenied('El organigrama ya está terminado, por lo cúal no es posible realizar acciones sobre los niveles')

        #CREACION DE NIVELES Y VALIDACION DEL ORDEN DE NIVEL
        contador = 1
        for nivel in data:
            orden_nivel = nivel.get('orden_nivel')
            
            if orden_nivel == contador:
                contador += 1
                pass
            else:
                raise ValidationError('No coincide el orden de los niveles')
        
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
        
        #Validacion NO PODER ELIMINAR un nivel que ya está siendo usado
        niveles_eliminar_list = [nivel.id_nivel_organigrama for nivel in niveles_total]
        if UnidadesOrganizacionales.objects.filter(id_nivel_organigrama__in=niveles_eliminar_list).exists():
            raise ValidationError('El nivel que intenta eliminar ya se encuentra relacionado con una unidad organizacional')
        niveles_total.delete()

        return Response({'success':True, 'detail':'Actualizacion exitosa de los niveles'}, status=status.HTTP_201_CREATED)

class GetNiveles(generics.ListAPIView):
    serializer_class = NivelesGetSerializer

    def get(self, request):
        consulta = request.query_params.get('pk')
        if consulta == None:
            niveles = NivelesOrganigrama.objects.all().values()
            if len(niveles) == 0:
                raise NotFound( 'Aún no hay niveles registrados')
            return Response({'success':True, 'Niveles' : niveles}, status=status.HTTP_200_OK)
        else:
            nivel = NivelesOrganigrama.objects.filter(id_nivel_organigrama=int(consulta)).values()
            return Response({'success':True, 'Nivel': nivel}, status=status.HTTP_200_OK)


class GetNivelesByOrganigrama(generics.ListAPIView):
    serializer_class = NivelesGetSerializer
    queryset = NivelesOrganigrama.objects.all()
    lookup_field = 'id_organigrama'

    def get(self, request, id_organigrama):
        niveles = NivelesOrganigrama.objects.filter(id_organigrama=id_organigrama)
        if not niveles:
            return Response({'success':True, 'detail':'No se encontraron niveles para el organigrama ingresado', 'data': niveles.values()}, status=status.HTTP_200_OK)
        serializer = self.serializer_class(niveles, many=True)
        return Response({'success':True, 'detail':'Se encontraron los siguientes niveles para el organigrama ingresado', 'data': serializer.data}, status=status.HTTP_200_OK)


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
                    
                    # VALIDACIONES
                    
                    # ELIMINACION DE UNIDADES
                    unidades_eliminar = UnidadesOrganizacionales.objects.filter(id_organigrama=pk)
                    unidades_eliminar.delete()
                    
                    # VALIDACIONES SERIALIZER
                    # unidades_serializer = self.serializer_class(data=unidades_crear, many=True)
                    # unidades_serializer.is_valid(raise_exception=True)
                    
                    # VALIDACIÓN DE EXISTENCIA DE NIVELES
                    niveles_list = [unidad['id_nivel_organigrama'] for unidad in data]
                    niveles_existe = NivelesOrganigrama.objects.filter(id_nivel_organigrama__in=niveles_list)
                    if niveles_existe.count() != len(list(dict.fromkeys(niveles_list))):
                        raise ValidationError('Uno o varios niveles que está asociando no existen')
                    
                    # VALIDACIÓN DE UNA SOLA RAÍZ          
                    raiz_list = [unidad['unidad_raiz'] for unidad in data]
                    if raiz_list.count(True) > 1:
                        raise ValidationError('No puede definir más de una unidad como raíz')
                    
                    # VALIDACIÓN DE CÓDIGO ÚNICO          
                    codigo_list = [unidad['codigo'] for unidad in data]
                    if len(set(codigo_list)) != len(codigo_list):
                        raise ValidationError('No puede definir más de una unidad con el mismo código')
                    
                    # VALIDACIÓN DE NOMBRE ÚNICO          
                    nombre_list = [unidad['nombre'] for unidad in data]
                    if len(set(nombre_list)) != len(nombre_list):
                        raise ValidationError('No puede definir más de una unidad con el mismo nombre')
                    
                    # VALIDACIÓN DE EXISTENCIA UNIDAD RAÍZ Y PERTENENCIA A NIVEL UNO
                    unidad_raiz = list(filter(lambda unidad: unidad['unidad_raiz'] == True, data))
                    if unidad_raiz:
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=unidad_raiz[0]['id_nivel_organigrama']).first()
                        if nivel_instance.orden_nivel != 1:
                           raise ValidationError('La unidad raíz solo puede pertenecer al nivel uno')
                    else:
                        raise ValidationError('Debe enviar la unidad raíz')
                    
                    # VALIDACIÓN QUE SECCIÓN SEA UNIDAD RAÍZ
                    seccion_raiz = list(filter(lambda unidad: unidad['cod_agrupacion_documental'] == 'SEC', data))
                    if seccion_raiz:
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=seccion_raiz[0]['id_nivel_organigrama']).first()
                        if nivel_instance.orden_nivel != 1:
                            raise ValidationError('La sección solo puede pertenecer a la unidad raíz')
                    
                    # VALIDACIÓN QUE UNIDADES STAFF SEAN DE NIVEL SUPERIOR AL UNO
                    staff_unidades = list(filter(lambda unidad: unidad['cod_tipo_unidad'] != 'LI', data))
                    for unidad in staff_unidades:
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=unidad['id_nivel_organigrama']).first()
                        if nivel_instance.orden_nivel < 2:
                            raise ValidationError('Las unidades de staff deben tener un nivel superior al uno')

                    # VALIDACIÓN DE EXISTENCIA DE SECCIÓN Y UNA SOLA SECCIÓN
                    seccion_list = [unidad['cod_agrupacion_documental'] for unidad in data]
                    if seccion_list:
                        if seccion_list.count('SEC') > 1:
                            raise ValidationError('No puede definir más de una unidad como sección')
                        if ('SUB' in seccion_list) and ('SEC' not in seccion_list):
                            raise ValidationError('Debe definir la sección para las subsecciones')
                    
                    # VALIDACIÓN DE EXISTENCIA DE UNIDADES PADRE
                    unidades_codigo_list = [unidad['codigo'] for unidad in data]
                    unidades_padre_list = [unidad['cod_unidad_org_padre'] for unidad in data if unidad['cod_unidad_org_padre'] is not None]
                    
                    if not set(unidades_padre_list).issubset(unidades_codigo_list):
                        raise ValidationError('Debe asociar unidades padre que existan')          
                    
                    # VALIDACIÓN DE UNA UNIDAD EN NIVEL UNO
                    padre_unidad_list = []
                    current_cod_unidades = []
                    for nivel, unidades in groupby(nivel_unidades, itemgetter('id_nivel_organigrama')):
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=nivel).first()
                        unidades_list = list(unidades)
                        
                        # VALIDACIÓN DE UNIDAD PADRE QUE SEA DE  LÍNEA Y DE NIVEL SUPERIOR
                        unidades_codigo_list = [unidad['codigo'] for unidad in unidades_list if unidad['cod_tipo_unidad'] == 'LI']
                        current_cod_unidades.extend(unidades_codigo_list)
                        unidades_padre_list = [unidad['cod_unidad_org_padre'] for unidad in unidades_list if unidad['cod_unidad_org_padre'] is not None]
                        if not set(unidades_padre_list).issubset(current_cod_unidades):
                            raise ValidationError('Debe asociar unidades padre de línea superiores a unidades hijos')   
                        
                        # VALIDACIÓN DE UNA UNIDAD EN NIVEL UNO
                        if nivel_instance.orden_nivel == 1 and (len(unidades_list) > 1):
                            raise ValidationError('Solo debe establecer una unidad para el nivel uno')
                        if nivel_instance.orden_nivel != 1:
                            
                            # VALIDACIÓN DEFINIR PADRES EN TODAS LOS NIVELES MENOS EL UNO
                            unidades_org = list(filter(lambda unidad: unidad['cod_unidad_org_padre'] == None or unidad['cod_unidad_org_padre'] == '', unidades_list))
                            if unidades_org:
                                raise ValidationError('Debe definir el padre en todas las unidades distintas a la raiz')                
                            
                            # VALIDACIÓN QUE EL PADRE DE SUBSECCIÓN ESTÉ MARCADO COMO SUBSECCIÓN
                            unidades_sub = list(filter(lambda unidad: unidad['cod_agrupacion_documental'] == 'SUB', unidades_list))
                            if unidades_sub:
                                unidad_padre = list(filter(lambda unidad: unidad['codigo'] == unidades_sub[0]['cod_unidad_org_padre'], data))
                                if unidad_padre:
                                    if unidad_padre[0]['cod_agrupacion_documental'] == None or unidad_padre[0]['cod_agrupacion_documental'] == '':
                                        raise ValidationError('Debe marcar las unidades padre como subsecciones')
                        #VALIDACIÓN QUE CUANDO ES UNA UNIDAD DE APOYO O SOPORTE EL PADRE DEBE SER DE NIVEL INMEDIATAMENTE ANTERIOR
                        unidades_padre_staff_list = [unidad['cod_unidad_org_padre'] for unidad in unidades_list if unidad['cod_tipo_unidad'] != 'LI']

                        if not set(unidades_padre_staff_list).issubset(padre_unidad_list):
                            raise ValidationError('Debe asociar unidades padre de línea inmediatamente anteriores para las unidades staff') 
                            
                        padre_unidad_list = unidades_codigo_list

                    # CREACION DE UNIDADES
                    for nivel, unidades in groupby(nivel_unidades, itemgetter('id_nivel_organigrama')):
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=nivel).first()
                        for unidad in unidades:
                            unidad_org = UnidadesOrganizacionales.objects.filter(codigo=unidad['cod_unidad_org_padre'], id_organigrama=pk).first()
                            unidad_org = unidad_org if unidad_org else None

                            if unidad['cod_tipo_unidad'] != 'LI': 
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
                    
                    return Response({'success':True, 'detail':'Actualizacion exitosa de las unidades'}, status=status.HTTP_201_CREATED)
                else:
                    raise ValidationError('Debe crear por lo menos una unidad')
            else:
                raise ValidationError('El organigrama ya está terminado, por lo cual no es posible realizar acciones sobre las unidades')
        else:
            raise NotFound('El organigrama no existe')


class GetUnidades(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.filter()
        
    def get(self, request):
        consulta = request.query_params.get('pk')
        if consulta == None:
            unidades = UnidadesOrganizacionales.objects.all().values()
            if len(unidades) == 0:
                raise NotFound( 'Aún no hay unidades registradas')
            return Response({'success':True, 'Unidades' : unidades}, status=status.HTTP_200_OK)
        unidades = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = int(consulta)).values()
        unidades_vector = unidades[0]
        id_niveles = unidades_vector['id_nivel_organigrama_id']
        nivel = NivelesOrganigrama.objects.filter(id_nivel_organigrama = id_niveles).values()
        unidades_vector['id_nivel_organigrama_id'] = nivel
        return Response({'success':True, 'Unidades' : unidades_vector}, status=status.HTTP_200_OK)

class GetUnidadesByOrganigrama(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.filter()
        
    def get(self, request, id_organigrama):
        organigrama = Organigramas.objects.filter(id_organigrama=id_organigrama).first()
        if organigrama:
            unidades = UnidadesOrganizacionales.objects.filter(id_organigrama = id_organigrama).values('id_unidad_organizacional', 'id_organigrama', 'id_nivel_organigrama', 'nombre', 'codigo', 'cod_tipo_unidad', 'cod_agrupacion_documental', 'unidad_raiz', 'id_unidad_org_padre')
            for unidad in unidades:
                unidad_padre_instance = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=unidad['id_unidad_org_padre']).first()
                unidad['cod_unidad_org_padre'] = unidad_padre_instance.codigo if unidad_padre_instance else None
            if unidades:
                return Response({'success':True, 'detail':'Se encontraron unidades para el organigrama', 'data' : unidades}, status=status.HTTP_200_OK)
            else:
                return Response({'success':True, 'detail':'No se encontraron unidades para el organigrama', 'data' : unidades}, status=status.HTTP_200_OK)
        else:
            raise NotFound('El organigrama no existe')


class GetUnidadesOrganigramaActual(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()

    def get(self, request):
        organigrama = Organigramas.objects.filter(actual=True)
        if not organigrama:
            raise NotFound('No existe ningún organigrama activado')
        if len(organigrama) > 1:
            raise PermissionDenied('Existe más de un organigrama actual, contacte a soporte')
        
        organigrama_actual = organigrama.first()
        unidades_organigrama_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama)
        serializer = self.serializer_class(unidades_organigrama_actual, many=True)
        return Response({'success':True, 'detail':'Consulta Exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


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
                    raise PermissionDenied('No se puede finalizar organigrama si no cuenta con minimo un nivel')
                if not unidades:
                    raise PermissionDenied('No se puede finalizar organigrama porque debe contener por lo menos una unidad')
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
                    return Response({'success':True, 'detail':'Niveles eliminadas'},status=status.HTTP_200_OK)
                if nivel_list and not nivel_unidad_list: # si los niveles no se está utilizando (hace comparacion de dos listas)
                    nivel_difference_list = [nivel for nivel in nivel_list if nivel not in nivel_unidad_list]
                    nivel_difference_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama__in=nivel_difference_list).values()
                    try:
                        raise PermissionDenied('No se puede finalizar organigrama porque debe utilizar todos los niveles')
                    except PermissionDenied as e:
                        return Response({'success':False, 'detail':'No se puede finalizar organigrama porque debe utilizar todos los niveles', 'Niveles sin asignar': nivel_difference_instance}, status=status.HTTP_403_FORBIDDEN)
                if not set(nivel_list).issubset(nivel_unidad_list): 
                    nivel_difference_list = [nivel for nivel in nivel_list if nivel not in nivel_unidad_list]
                    print('NO SE ESTAN UTILIZANDO',nivel_difference_list)
                    nivel_difference_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama__in=nivel_difference_list).values()
                    try:
                        raise PermissionDenied('No se puede finalizar organigrama porque debe utilizar todos los niveles')
                    except PermissionDenied as e:
                        return Response({'success':False, 'detail':'No se puede finalizar organigrama porque debe utilizar todos los niveles', 'Niveles sin asignar': nivel_difference_instance}, status=status.HTTP_403_FORBIDDEN)
                organigrama_a_finalizar.fecha_terminado=datetime.now()
                organigrama_a_finalizar.id_persona_cargo=None
                organigrama_a_finalizar.save()
                return Response({'success':True, 'detail':'Se Finalizo el organigrama correctamente'},status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('Ya se encuentra finalizado este Organigrama')

        raise PermissionDenied('No existe organigrama')
class CreateOrgChart(generics.CreateAPIView):
    serializer_class = OrganigramaPostSerializer
    queryset = Organigramas.objects.all()
    permission_classes = [IsAuthenticated]
    def post(self, request):
        
        persona = request.user.persona.id_persona
        data=request.data
        data['id_persona_cargo']=persona
        
        serializer = self.serializer_class(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            pass
        except:
            raise ValidationError('Validar la data ingresada, el nombre debe ser único y es requerido, la descripción y la versión son requeridos')
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

        return Response({'success':True, 'detail':serializer.data}, status=status.HTTP_201_CREATED)

class UpdateOrganigrama(generics.RetrieveUpdateAPIView):
    serializer_class = OrganigramaPutSerializer
    queryset= Organigramas.objects.all()
    lookup_field='id_organigrama'
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_organigrama):
        organigrama = Organigramas.objects.get(id_organigrama=id_organigrama)   
        previous_organigrama = copy.copy(organigrama)
        if organigrama.fecha_terminado:
            raise PermissionDenied('No se puede actualizar un organigrama que ya está terminado')   
        ccd = list(CuadrosClasificacionDocumental.objects.filter(id_organigrama=organigrama.id_organigrama).values())
        if not len(ccd):
            serializer = self.serializer_class(organigrama, data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                pass
            except:
                raise ValidationError('Validar la data ingresada, el nombre debe ser único y es requerido, la descripción y la versión son requeridos')    
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
            return Response({'success':True, 'detail':serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied('Ya está siendo usado este organigrama')

class GetOrganigrama(generics.ListAPIView):
    serializer_class = OrganigramaSerializer  

    def get(self, request):
        consulta = request.query_params.get('pk')
        if consulta == None:
            organigramas = Organigramas.objects.all()
            serializador = self.serializer_class(organigramas,many=True)
            if len(organigramas) == 0:
                raise NotFound( 'Aún no hay organigramas registrados')
            return Response({'Organigramas' : serializador.data}, status=status.HTTP_200_OK) 
        organigrama = Organigramas.objects.filter(id_organigrama=int(consulta))
        serializador = self.serializer_class(organigramas,many=True)
        if len(organigrama) == 0:
            raise NotFound( 'No se encontró el organigrama ingresado')
        niveles = NivelesOrganigrama.objects.filter(id_organigrama=int(consulta)).values()
        if len(niveles) == 0:
            niveles = 'No hay niveles registrados'
            unidades = 'No hay unidades registradas'
            datos_finales = {'Organigrama' : serializador.data, 'Niveles' : niveles, 'Unidades' : unidades}
            return Response({'Organigrama' : datos_finales}, status=status.HTTP_200_OK)   
        unidades = UnidadesOrganizacionales.objects.filter(id_organigrama=int(consulta)).values()
        if len(unidades) == 0:
            unidades = 'No hay unidades registradas'
            datos_finales = {'Organigrama' : serializador.data, 'Niveles' : niveles, 'Unidades' : unidades}
            return Response({'Organigrama' : datos_finales}, status=status.HTTP_200_OK)
        datos_finales = {'Organigrama' : serializador.data, 'Niveles' : niveles, 'Unidades' : unidades}
        return Response({'Organigrama' : datos_finales}, status=status.HTTP_200_OK)

class GetSeccionSubsecciones(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    
    def get(self, request, id_organigrama):
        organigrama = Organigramas.objects.filter(id_organigrama=id_organigrama).first()
        if organigrama:
            unidades = UnidadesOrganizacionales.objects.filter(Q(id_organigrama=id_organigrama) & ~Q(cod_agrupacion_documental=None))
            serializer = self.serializer_class(unidades, many=True)
            return Response({'success':True, 'detail':'Se encontraron las siguientes unidades', 'data':serializer.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('Debe consultar por un organigrama válido')
            
class GetOrganigramasTerminados(generics.ListAPIView):
    serializer_class = OrganigramaSerializer
    queryset = Organigramas.objects.filter(~Q(fecha_terminado=None) & Q(fecha_retiro_produccion=None))  

class GetUnidadesJerarquizadas(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.filter()
        
    def get(self, request, id_organigrama):
        organigrama = Organigramas.objects.filter(id_organigrama=id_organigrama).first()
        if organigrama:
            unidades = UnidadesOrganizacionales.objects.filter(id_organigrama=id_organigrama)
            if unidades:
                unidades_linea = unidades.values(
                    'id_organigrama',
                    'id_nivel_organigrama',
                    'codigo',
                    'cod_tipo_unidad',
                    'cod_agrupacion_documental',
                    'unidad_raiz', 
                    'id_unidad_org_padre',
                    classname = F('id_nivel_organigrama__nombre'),
                    orden_nivel=F('id_nivel_organigrama__orden_nivel'),
                    title=F('nombre'),
                    id=F('id_unidad_organizacional')
                )
                unidades_linea = sorted(unidades_linea, key=itemgetter('orden_nivel'))
                unidades_jerarquia = []
                for unidad in unidades_linea:
                    unidad['classname'] = str(unidad['classname']).replace(' ', '-')
                    unidad['children'] = [hijo for hijo in unidades_linea if hijo['id_unidad_org_padre']==unidad['id']]
                    if unidad['unidad_raiz']:
                        unidades_jerarquia.append(unidad)
                        
                return Response({'success':True, 'detail':'Se encontraron unidades para el organigrama', 'data' : unidades_jerarquia}, status=status.HTTP_200_OK)
            else:
                return Response({'success':True, 'detail':'No se encontraron unidades para el organigrama', 'data' : unidades}, status=status.HTTP_200_OK)
        else:
            raise NotFound('El organigrama no existe')
#BUSQUEDA USUARIO ORGANIGRAMA
class GetNuevoUserOrganigrama(generics.RetrieveAPIView):
    serializer_class = PersonaOrgSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self,request,tipo_documento,numero_documento):
        fecha_sistema = datetime.now()
        
        persona_log = request.user.persona.id_persona #para validar de que la persona no pueda reasignarse asi mismo el organigrama
        nuevo_user_organigrama = Personas.objects.filter(tipo_documento=tipo_documento, numero_documento=numero_documento).first()
        if not nuevo_user_organigrama:
            raise NotFound('No existe la persona con ese tipo y numero de documento.') 
        if not nuevo_user_organigrama.fecha_a_finalizar_cargo_actual or nuevo_user_organigrama.fecha_a_finalizar_cargo_actual < fecha_sistema:
            raise NotFound('La persona no se encuentra vinculada o la fecha de finalización del cargo ya expiro.') 
                
        if nuevo_user_organigrama.id_persona == persona_log:
            raise NotFound('La persona no se puede reasignar asi mismo.')              
        
        if nuevo_user_organigrama:
            serializador = self.serializer_class(nuevo_user_organigrama)
            return Response({'succes':True, 'detail':'Los datos coincidieron con los criterios de busqueda','data':serializador.data},status=status.HTTP_200_OK)
        
        else:
            raise NotFound('La persona no existe o no tiene un cargo actual')

#BUSQUEDA AVANZADA PERSONA ORGANIGRAMA
class GetNuevoUserOrganigramaFilters(generics.ListCreateAPIView):
    serializer_class = PersonaOrgSerializer
    queryset = Personas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self, request):
        filter={}
        for key, value in request.query_params.items():
            if key in ['primer_nombre','primer_apellido']:
                if value != '':
                    filter[key+'__icontains'] = value
                        
        fecha_sistema = datetime.now()
        filter['fecha_a_finalizar_cargo_actual__gt'] = fecha_sistema
        
        persona = self.queryset.all().filter(**filter).filter(~Q(id_cargo = None))
        serializador = self.serializer_class(persona,many=True)
        return Response({'succes': True, 'detail':'Se encontraron las siguientes personas', 'data':serializador.data}, status=status.HTTP_200_OK)

#DELEGAR USUARIO ORGANIGRAMA

class AsignarOrganigramaUser(generics.CreateAPIView):
    serializer_class = NewUserOrganigramaSerializer
    queryset = Personas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        fecha_sistema = datetime.now()
        
        id_persona = request.query_params.get('id_persona')
        id_organigrama = request.query_params.get('id_organigrama')
        
        if not id_persona and id_organigrama:
            raise NotFound('No pueden estar vacios los campos.')
        
        #validaciones de funcionamiento
        
        persona = Personas.objects.filter(id_persona=id_persona).first()
        organigrama = Organigramas.objects.filter(id_organigrama=id_organigrama).first()
        persona_super_usuario = User.objects.filter(id_usuario=1).first()
        
        if not persona:
            raise NotFound('No existe la persona ingresada.')
        
        if not organigrama:
            raise NotFound('No existe el organigrama ingresado.')
        
        persona_logueado = request.user.persona.id_persona
        
        if organigrama.id_persona_cargo.id_persona != persona_logueado  and  persona_logueado != persona_super_usuario.persona.id_persona:
            raise NotFound('No tiene permisos para asignar este organigrama.')
        
        if persona.id_persona == organigrama.id_persona_cargo.id_persona:
            raise NotFound('La persona no se puede reasignar asi mismo.')
        
        if not persona.fecha_a_finalizar_cargo_actual or persona.fecha_a_finalizar_cargo_actual < fecha_sistema:
            raise NotFound('La persona no se encuentra vinculada o la fecha de finalización del cargo ya expiro.')             
        
        if organigrama.fecha_terminado != None:
            raise NotFound('El organigrama ya se encuentra finalizado no se puede delegar.')             

        
        #DELEGAR ORGANIGRAMA
        
        #usuario_delegante = Personas.objects.filter(id_persona=persona_logueado).first()
        previous_organigrama = copy.copy(organigrama)
        organigrama.id_persona_cargo = persona
        organigrama.save()
        return Response({'succes':True, 'detail':'Se delego a la persona.'},status=status.HTTP_201_CREATED)             

class ReanudarOrganigrama(generics.RetrieveUpdateAPIView):
    serializer_class = NewUserOrganigramaSerializer
    queryset = Organigramas.objects.all()
    
    def put(self, request, id_organigrama):
                
        organigrama = Organigramas.objects.filter(id_organigrama=id_organigrama).first()
        
        if not organigrama:
            raise NotFound('No existe el Organigrama Ingresado.') #PARA ERRORES 404_NOT_FOUND
        
        if organigrama.fecha_terminado == None:
            raise PermissionDenied('El organigrama debe de estar finalizado para su Reanudación.')#PARA ERRORES 403_FORBIDDEN

        # persona_logueado = request.user.persona.id_persona
        
        # if persona_logueado != None:
        #     return Response({'succes':False, 'detail':'El Organigrama no debe de poseer un usuario asignado.'},status=status.HTTP_404_NOT_FOUND)             

        ccd_activo = CuadrosClasificacionDocumental.objects.filter(id_organigrama=id_organigrama).first()
        
        if ccd_activo:
            raise NotFound('El Organigrama ya esta siendo utilizado por un CCD.')             
        
        organigrama.fecha_terminado = None
        
        organigrama.save()
        return Response({'succes': True, 'detail':'Se reanudo correctamente el organigrama.'}, status=status.HTTP_200_OK)

class CambioDeOrganigramaActual(generics.UpdateAPIView):
    serializer_class = OrganigramaCambioDeOrganigramaActualSerializer
    queryset = Organigramas.objects.all()
    queryset2 = CuadrosClasificacionDocumental.objects.all()
    
    def put(self,request):
        
        data = request.data
        organigrama_seleccionado = self.queryset.filter(id_organigrama = data['organigrama']).first()
        organigrama_actual = self.queryset.filter(actual = True).first()
        ccd_actual = self.queryset2.filter(actual=True).first()
        
        if not ccd_actual:
            organigrama_seleccionado.justificacion_nueva_version = data['justificacion']
            organigrama_seleccionado.actual = True
            organigrama_seleccionado.fecha_puesta_produccion = datetime.now()
            
            if organigrama_actual:
                organigrama_actual.fecha_retiro_produccion = datetime.now()
                organigrama_actual.actual = False
            
        else:
            if not data.get('id_ccd'):
                raise ValidationError('Debe de seleccionar un CCD')
            
            #CCD SELECCIONADO
            ccd_seleccionado =  self.queryset2.filter(id_ccd=data.get('id_ccd'))
            tca = TablasControlAcceso.objects.filter(id_trd__id_ccd=ccd_seleccionado).first()
            
            #ACTIVACION TCA
            
            tca.actual = True
            tca.fecha_puesta_produccion = datetime.now()
            tca.justificacion_nueva_version = data['justificacion']
            
            #ACTIVACION TRD
            
            tca.id_trd.actual = True
            tca.id_trd.fecha_puesta_produccion = datetime.now()
            tca.id_trd.justificacion = data['justificacion']
            
            #ACTIVACION CCD
            
            tca.id_trd.id_ccd.actual = True
            tca.id_trd.id_ccd.fecha_puesta_produccion = datetime.now()
            tca.id_trd.id_ccd.justificacion = data['justificacion']
            
            #ACTIVACION ORG
            
            organigrama_seleccionado.justificacion_nueva_version = data['justificacion']
            organigrama_seleccionado.actual = True
            organigrama_seleccionado.fecha_puesta_produccion = datetime.now()

            #CCD ACTUAL
            
            tca_actual = TablasControlAcceso.objects.filter(id_trd__id_ccd=ccd_actual).first()
            
            #DESACTIVACION TCA
            
            tca_actual.actual = False
            tca_actual.fecha_puesta_produccion = datetime.now()
    
            #DESACTIVACION TRD
            
            tca_actual.id_trd.actual = False
            tca_actual.id_trd.fecha_puesta_produccion = datetime.now()
            
            #DESACTIVACION CCD
            
            tca_actual.id_trd.id_ccd.actual = False
            tca_actual.id_trd.id_ccd.fecha_puesta_produccion = datetime.now()
            
            #DESACTIVACION ORG
            
            tca_actual.id_trd.id_ccd.id_organigrama.actual = False
            tca_actual.id_trd.id_ccd.id_organigrama.fecha_puesta_produccion = datetime.now()
            
            #GUARDADO
            tca.save()
            tca.id_trd.id_ccd.id_organigrama.save()
            tca.id_trd.id_ccd.save()
            tca.id_trd.save()
            
            #GUARDADO
            tca_actual.save()
            tca_actual.id_trd.id_ccd.id_organigrama.save()
            tca_actual.id_trd.id_ccd.save()
            tca_actual.id_trd.save()
            
            return Response ({'success':True,'detail':'Se activó el instrumento archivistico correctamente '},status=status.HTTP_200_OK)
        
class GetCCDTerminadoByORG(generics.ListAPIView):
    serializer_class = CCDSerializer
    queryset = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_puesta_produccion=None))

    def get(self, request, id_organigrama):
        organigrama = Organigramas.objects.filter(id_organigrama = id_organigrama).first()
        if not organigrama:
            return Response({'success': False, 'detail': 'El organigrama ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)

        if organigrama.fecha_terminado == None or organigrama.fecha_retiro_produccion != None or organigrama.fecha_puesta_produccion!=None:
            return Response({'success': False, 'detail': 'El organigrama ingresado ya está retirado, no está terminado o ya está en producción'}, status=status.HTTP_403_FORBIDDEN)
        ccds = self.queryset.all().filter(id_organigrama = organigrama.id_organigrama)
        
        lista=[]
        if ccds:
            for t in ccds:
                tca = TablasControlAcceso.objects.filter(id_trd__id_ccd=t).first()
                if tca:
                    list.append(t)
                    
        if not ccds:
            return Response({'success': False, 'detail': 'No existe CCD terminado basado en el organigrama seleccionado'}, status=status.HTTP_403_FORBIDDEN)
        serializador = self.serializer_class(lista,many=True)
        serializer_data = serializador.data
    
        return Response({'success': True, 'detail': 'CCD', 'data': serializador.data},status=status.HTTP_200_OK)
    
class ObtenerOrganigramaActual(generics.ListAPIView):
    serializer_class = NewUserOrganigramaSerializer
    queryset = Organigramas.objects.all()
    
    def get (self,request):
        
        organigrama_actual = self.queryset.all().filter(actual = True).first()
        
        if organigrama_actual:
            serializador = self.serializer_class(organigrama_actual)
            
            return Response({'success':True,'detail':'Busqueda exitosa','data':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'Busqueda exitosa, no existe organigrama actual'},status=status.HTTP_200_OK)


class ActualizacionUnidadOrganizacionalAntigua(generics.UpdateAPIView):
    serializer_class = ActUnidadOrgAntiguaSerializer

    def put(self, request, *args, **kwargs):
        nueva_id_unidad_organizacional = request.data.get('nueva_id_unidad_organizacional')
        lista_id_personas = request.data.get('personas', [])
        user = request.user
        nombre_de_usuario = user.nombre_de_usuario

        try:
            unidad_organizacional = UnidadesOrganizacionales.objects.get(id_unidad_organizacional=nueva_id_unidad_organizacional)
        except UnidadesOrganizacionales.DoesNotExist:
            raise ValidationError('La nueva unidad organizacional que estás asignando no existe')

        # Obtener la fecha de retiro de producción más actual
        fecha_actual = datetime.now()
        organigrama_actual = Organigramas.objects.filter(fecha_retiro_produccion__lte=fecha_actual).order_by('-fecha_retiro_produccion').first()

        if organigrama_actual.fecha_retiro_produccion and organigrama_actual.actual:
            raise ValidationError('El organigrama esta fuera de producción por ende no puede ser el actual')

        personas = Personas.objects.filter(id_persona__in=lista_id_personas, id_unidad_organizacional_actual__id_organigrama=organigrama_actual.id_organigrama)
        if len(set(lista_id_personas)) != len(personas):
            raise ValidationError('Debe asegurarse que todas las personas tengan asignadas una unidad del último organigrama retirado de la producción')

        queryset = Personas.objects.filter(
            es_unidad_organizacional_actual=False,
            id_persona__in=lista_id_personas
        )

        if queryset is not None:
            personas_actualizadas = []

            for persona in queryset:
                historico = HistoricoCargosUndOrgPersona(
                    id_persona=persona,
                    id_cargo=persona.id_cargo,
                    id_unidad_organizacional=persona.id_unidad_organizacional_actual,
                    fecha_inicial_historico=persona.fecha_asignacion_unidad,
                    fecha_final_historico=fecha_actual,
                    observaciones_vinculni_cargo=None,
                    justificacion_cambio_und_org=f'Cambio masivo de unidad organizacional por {nombre_de_usuario} el {fecha_actual.strftime("%Y-%m-%d %H:%M:%S")}',
                    desvinculado=False
                )
                historico.save()

                persona.id_unidad_organizacional_actual = unidad_organizacional
                persona.es_unidad_organizacional_actual = True
                persona.fecha_asignacion_unidad = fecha_actual
                persona.save(update_fields=['id_unidad_organizacional_actual', 'es_unidad_organizacional_actual', 'fecha_asignacion_unidad'])
                personas_actualizadas.append(persona)

            if personas_actualizadas:
                return Response({'success': True, 'detail': 'Las personas han sido actualizadas exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise ValidationError('No se encontraron personas para actualizar')

class GetUnidadOrgDesactualizada(generics.ListAPIView):
    serializer_class = ActUnidadOrgAntiguaSerializer

    def get(self, request):
        id_unidad_organizacional_actual = self.request.data.get('id_unidad_organizacional_actual')
        
        # Obtener la fecha de retiro de producción más actual
        fecha_actual = datetime.now()
        organigrama_actual = Organigramas.objects.filter(fecha_retiro_produccion__lte=fecha_actual).order_by('-fecha_retiro_produccion').first()

        if organigrama_actual.fecha_retiro_produccion and organigrama_actual.actual:
            raise ValidationError('El organigrama está fuera de producción y no puede ser el actual')

        if id_unidad_organizacional_actual:
            try:
                id_unidad_organizacional_actual = int(id_unidad_organizacional_actual)
                queryset = Personas.objects.filter(
                    id_unidad_organizacional_actual=id_unidad_organizacional_actual,
                    es_unidad_organizacional_actual=False,
                    id_unidad_organizacional_actual__id_organigrama=organigrama_actual.id_organigrama
                )
            except ValueError:
                return Personas.objects.none()
        else:
            queryset = Personas.objects.filter(
                es_unidad_organizacional_actual=False,
                id_unidad_organizacional_actual__id_organigrama=organigrama_actual.id_organigrama
            )
            
        if not queryset.exists():
            raise NotFound('No se encuentran personas con esta unidad organizacional fuera de producción')
        
        serializador = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializador.data}, status=status.HTTP_200_OK)

class GetUnidadesOrganigramaRetiradoReciente(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()

    def get(self, request):
        organigramas = Organigramas.objects.filter(actual=False).order_by('-fecha_retiro_produccion')
        if not organigramas:
            raise NotFound('No existe organigramas retirados de produccion')
        
        organigrama_retirado = organigramas.first()
        unidades_organigrama_retirado = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_retirado.id_organigrama)
        serializer = self.serializer_class(unidades_organigrama_retirado, many=True)
        return Response({'success':True, 'detail':'Consulta Organigrama Retirado Reciente Exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

