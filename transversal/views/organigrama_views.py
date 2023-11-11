from rest_framework import status
from rest_framework import generics, views
from rest_framework.views import APIView
from rest_framework.response import Response
from itertools import groupby
from gestion_documental.models.plantillas_models import AccesoUndsOrg_PlantillaDoc
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.serializers.ccd_serializers import CCDSerializer
from seguridad.permissions.permissions_gestor import PermisoActualizarOrganigramas
from seguridad.utils import Util
from django.db.models import Q, F
from datetime import datetime
from django.contrib.auth import get_user
from django.db.models import Max
from django.db import transaction
import copy
from operator import itemgetter
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from transversal.models.alertas_models import PersonasAAlertar
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.serializers.organigrama_serializers import ( 
    GetCambiosUnidadMasivosSerializer,
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
    ActUnidadOrgAntiguaSerializer,
    TemporalPersonasUnidadSerializer
    )
from transversal.models.organigrama_models import (
    Organigramas,
    UnidadesOrganizacionales,
    NivelesOrganigrama,
    TemporalPersonasUnidad,
    CambiosUnidadMasivos
    )
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from seguridad.models import User
from transversal.models.base_models import HistoricoCargosUndOrgPersona
from transversal.models.personas_models import Personas
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

# VIEWS FOR NIVELES ORGANIGRAMA
class UpdateNiveles(generics.UpdateAPIView):
    serializer_class = NivelesUpdateSerializer
    queryset = NivelesOrganigrama.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_organigrama):
        data = request.data
        persona_logueada = request.user.persona.id_persona

        #VALIDACION DE ORGANIGRAMA
        try:
            organigrama = Organigramas.objects.get(id_organigrama=id_organigrama)
            pass
        except:
            raise ValidationError('No se pudo encontrar un organigrama con el parámetro ingresado')
        
        if organigrama.id_persona_cargo:
            if organigrama.id_persona_cargo.id_persona != persona_logueada:
                raise PermissionDenied('Este organigrama actualmente solo podrá ser editado por ' + organigrama.id_persona_cargo.primer_nombre + ' ' + organigrama.id_persona_cargo.primer_apellido)
            
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
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        persona_logueada = request.user.persona.id_persona
        
        organigrama=Organigramas.objects.filter(id_organigrama=pk).first()
        
        if organigrama:            
            if not organigrama.actual:
                if not organigrama.fecha_terminado:
                    if organigrama.id_persona_cargo:
                        if organigrama.id_persona_cargo.id_persona != persona_logueada:
                            raise PermissionDenied('Este organigrama actualmente solo podrá ser editado por ' + organigrama.id_persona_cargo.primer_nombre + ' ' + organigrama.id_persona_cargo.primer_apellido)
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
                            elif unidad_raiz[0]['cod_tipo_unidad'] != 'LI':
                                raise ValidationError('La unidad raíz solo puede ser de línea')
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
                            unidades_codigo_list = [unidad['codigo'] for unidad in unidades_list]# if unidad['cod_tipo_unidad'] == 'LI']
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
                                # unidades_sub = list(filter(lambda unidad: unidad['cod_agrupacion_documental'] == 'SUB', unidades_list))
                                # if unidades_sub:
                                #     unidad_padre = list(filter(lambda unidad: unidad['codigo'] == unidades_sub[0]['cod_unidad_org_padre'], data))
                                #     if unidad_padre:
                                #         if unidad_padre[0]['cod_agrupacion_documental'] == None or unidad_padre[0]['cod_agrupacion_documental'] == '':
                                #             raise ValidationError('Debe marcar las unidades padre como subsecciones')
                                
                                # VALIDACIÓN QUE EL HIJO DE UNIDAD STAFF SEA DE TIPO LINEA
                                unidades_sub = list(filter(lambda unidad: unidad['cod_agrupacion_documental'] != 'SEC' and unidad['cod_tipo_unidad'] != 'LI', unidades_list))
                                if unidades_sub:
                                    unidad_padre = list(filter(lambda unidad: unidad['codigo'] == unidades_sub[0]['cod_unidad_org_padre'], data))
                                    if unidad_padre:
                                        if unidad_padre[0]['cod_tipo_unidad'] != 'LI':
                                            raise ValidationError('Los hijos de una unidad staff deben ser de tipo línea')
                            
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

                                # if unidad['cod_tipo_unidad'] != 'LI': 
                                #     unidad['cod_agrupacion_documental'] = None
                                
                                UnidadesOrganizacionales.objects.create(
                                    id_nivel_organigrama=nivel_instance,
                                    nombre=unidad['nombre'],
                                    codigo=unidad['codigo'],
                                    cod_tipo_unidad=unidad['cod_tipo_unidad'],
                                    cod_agrupacion_documental=unidad['cod_agrupacion_documental'],
                                    unidad_raiz=unidad['unidad_raiz'],
                                    activo=unidad['activo'],
                                    id_organigrama=organigrama,
                                    id_unidad_org_padre=unidad_org
                                )
                        
                        return Response({'success':True, 'detail':'Actualizacion exitosa de las unidades'}, status=status.HTTP_201_CREATED)
                    else:
                        raise ValidationError('Debe crear por lo menos una unidad')
                else:
                    raise ValidationError('El organigrama ya está terminado, por lo cual no es posible realizar acciones sobre las unidades')
            else:
                # ELIMINAR UNIDADES
                unidades_instances = UnidadesOrganizacionales.objects.filter(id_organigrama=pk)
                unidades_actualizar = [unidad for unidad in data if unidad['id_unidad_organizacional']]
                unidades_actualizar_list = [unidad['id_unidad_organizacional'] for unidad in unidades_actualizar]
                
                unidades_eliminar = unidades_instances.exclude(id_unidad_organizacional__in=unidades_actualizar_list)
                unidades_eliminar_usados = unidades_eliminar.filter(item_usado=True)
                
                if unidades_eliminar_usados:
                    raise PermissionDenied('No puede eliminar unidades que ya se encuentran en uso')
                
                for unidad in unidades_eliminar:
                    unidad_eliminar_padre = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad.id_unidad_organizacional)
                    if unidad_eliminar_padre:
                        raise PermissionDenied('No puede eliminar unidades que tengan hijos')
                    
                unidades_eliminar_sec_sub = unidades_eliminar.exclude(cod_agrupacion_documental=None)
                if unidades_eliminar_sec_sub:
                    raise PermissionDenied('No puede eliminar unidades de tipo Sección o Subsección')
                
                unidades_eliminar.delete()
                
                # CREAR UNIDADES
                unidades_crear = [unidad for unidad in data if not unidad['id_unidad_organizacional']]
                
                if unidades_crear:
                    nivel_unidades = sorted(data, key=itemgetter('id_nivel_organigrama'))
                    
                    # VALIDACION QUE NO TENGAN AGRUPACION DOCUMENTAL
                    cod_agrupacion_doc_list = [unidad['cod_agrupacion_documental'] for unidad in unidades_crear]
                    if 'SEC' in cod_agrupacion_doc_list or 'SUB' in cod_agrupacion_doc_list:
                        raise PermissionDenied('No puede añadir nuevas Secciones o Subsecciones al Organigrama actual')
                    
                    niveles_list = [unidad['id_nivel_organigrama'] for unidad in data]
                    niveles_existe = NivelesOrganigrama.objects.filter(id_nivel_organigrama__in=niveles_list)
                    
                    if niveles_existe.count() != len(list(dict.fromkeys(niveles_list))):
                        raise ValidationError('Uno o varios niveles que está asociando no existen')
                    
                    # VALIDACIÓN DE EXISTENCIA DE NIVELES
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
                        elif unidad_raiz[0]['cod_tipo_unidad'] != 'LI':
                            raise ValidationError('La unidad raíz solo puede ser de línea')
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
                        unidades_codigo_list = [unidad['codigo'] for unidad in unidades_list]# if unidad['cod_tipo_unidad'] == 'LI']
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
                            # unidades_sub = list(filter(lambda unidad: unidad['cod_agrupacion_documental'] == 'SUB', unidades_list))
                            # if unidades_sub:
                            #     unidad_padre = list(filter(lambda unidad: unidad['codigo'] == unidades_sub[0]['cod_unidad_org_padre'], data))
                            #     if unidad_padre:
                            #         if unidad_padre[0]['cod_agrupacion_documental'] == None or unidad_padre[0]['cod_agrupacion_documental'] == '':
                            #             raise ValidationError('Debe marcar las unidades padre como subsecciones')
                            
                            # VALIDACIÓN QUE EL HIJO DE UNIDAD STAFF SEA DE TIPO LINEA
                            unidades_sub = list(filter(lambda unidad: unidad['cod_agrupacion_documental'] != 'SEC' and unidad['cod_tipo_unidad'] != 'LI', unidades_list))
                            if unidades_sub:
                                unidad_padre = list(filter(lambda unidad: unidad['codigo'] == unidades_sub[0]['cod_unidad_org_padre'], data))
                                if unidad_padre:
                                    if unidad_padre[0]['cod_tipo_unidad'] != 'LI':
                                        raise ValidationError('Los hijos de una unidad staff deben ser de tipo línea')
                        
                        #VALIDACIÓN QUE CUANDO ES UNA UNIDAD DE APOYO O SOPORTE EL PADRE DEBE SER DE NIVEL INMEDIATAMENTE ANTERIOR
                        unidades_padre_staff_list = [unidad['cod_unidad_org_padre'] for unidad in unidades_list if unidad['cod_tipo_unidad'] != 'LI']

                        if not set(unidades_padre_staff_list).issubset(padre_unidad_list):
                            raise ValidationError('Debe asociar unidades padre de línea inmediatamente anteriores para las unidades staff') 
                            
                        padre_unidad_list = unidades_codigo_list

                    # CREACION DE UNIDADES
                    nivel_unidades = sorted(unidades_crear, key=itemgetter('id_nivel_organigrama'))
                    
                    for nivel, unidades in groupby(nivel_unidades, itemgetter('id_nivel_organigrama')):
                        nivel_instance = NivelesOrganigrama.objects.filter(id_nivel_organigrama=nivel).first()
                        for unidad in unidades_crear:
                            unidad_org = UnidadesOrganizacionales.objects.filter(codigo=unidad['cod_unidad_org_padre'], id_organigrama=pk).first()
                            unidad_org = unidad_org if unidad_org else None

                            # if unidad['cod_tipo_unidad'] != 'LI': 
                            #     unidad['cod_agrupacion_documental'] = None
                            
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
                
                # ACTIVAR/DESACTIVAR UNIDADES
                unidades_actualizar_instances = unidades_instances.filter(id_unidad_organizacional__in=unidades_actualizar_list)
                
                if unidades_actualizar:
                    for unidad in unidades_actualizar:
                        unidad_instance = unidades_actualizar_instances.filter(id_unidad_organizacional=unidad['id_unidad_organizacional']).first()
                        if not unidad_instance:
                            raise ValidationError('La unidad que desea actualizar no existe')
                            
                        if unidad_instance.activo != unidad['activo']:
                            if unidad['activo'] == False:
                                if unidad_instance.cod_agrupacion_documental:
                                    raise PermissionDenied('Error: Sólo se pueden desactivar Unidades Organizacionales que no sean Secciones o Subsecciones')
                                
                                personas = Personas.objects.filter(id_unidad_organizacional_actual=unidad_instance.id_unidad_organizacional, es_unidad_organizacional_actual=True)
                                if personas:
                                    raise PermissionDenied('Error: No es posible desactivar una Unidad Organizacional mientras esté asignada a una o más personas')
                                
                                lideres = LideresUnidadesOrg.objects.filter(id_unidad_organizacional=unidad_instance.id_unidad_organizacional)
                                if lideres:
                                    raise PermissionDenied('Error: No es posible desactivar una Unidad Organizacional mientras esta tenga un líder asignado')
                                
                                personas_alertas = PersonasAAlertar.objects.filter(id_unidad_org_lider=unidad_instance.id_unidad_organizacional)
                                if personas_alertas:
                                    raise PermissionDenied('Error: No es posible desactivar una Unidad Organizacional mientras hayan alertas configuradas con destino a su líder')
                                
                                unidad_es_padre = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad_instance.id_unidad_organizacional, activo=True)
                                if unidad_es_padre:
                                    raise PermissionDenied('Error: No es posible desactivar una Unidad Organizacional mientras tenga Unidades hijas activas')
                                #ELIMINA RELACIONES DE ACCESO EN PLANTILLAS
                                accesos =AccesoUndsOrg_PlantillaDoc.objects.filter(id_und_organizacional=unidad_instance.id_unidad_organizacional)
                                accesos.delete()
                                
                                
                            unidad_instance.activo = unidad['activo']
                            unidad_instance.save()
                
                return Response({'success':True, 'detail':'Actualizacion exitosa de las unidades'}, status=status.HTTP_201_CREATED)
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
            unidades = UnidadesOrganizacionales.objects.filter(id_organigrama = id_organigrama).values('id_unidad_organizacional', 'id_organigrama', 'id_nivel_organigrama', 'nombre', 'codigo', 'cod_tipo_unidad', 'cod_agrupacion_documental', 'unidad_raiz', 'activo', 'item_usado', 'id_unidad_org_padre')
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
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
        persona_logueada = request.user.persona.id_persona
        confirm = request.query_params.get('confirm')
        organigrama_a_finalizar=Organigramas.objects.filter(id_organigrama=pk).first()
        if organigrama_a_finalizar:
            if organigrama_a_finalizar.id_persona_cargo:
                if organigrama_a_finalizar.id_persona_cargo.id_persona != persona_logueada:
                    raise PermissionDenied('Este organigrama actualmente solo podrá ser editado por ' + organigrama_a_finalizar.id_persona_cargo.primer_nombre + ' ' + organigrama_a_finalizar.id_persona_cargo.primer_apellido)
            
            if not organigrama_a_finalizar.fecha_terminado:
                if not organigrama_a_finalizar.ruta_resolucion or organigrama_a_finalizar.ruta_resolucion == '':
                    raise PermissionDenied('No se puede finalizar organigrama sin antes adjuntar la resolución')
            
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
        data._mutable = True
        
        data['id_persona_cargo']=persona
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
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
        persona_logueada = request.user.persona.id_persona
        
        organigrama = Organigramas.objects.filter(id_organigrama=id_organigrama).first()
        if not organigrama:
            raise NotFound('El organigrama ingresado no existe')
        
        previous_organigrama = copy.copy(organigrama)
        
        if organigrama.fecha_terminado:
            raise PermissionDenied('No se puede actualizar un organigrama que ya está terminado') 
        
        if organigrama.id_persona_cargo:
            if organigrama.id_persona_cargo.id_persona != persona_logueada:
                raise PermissionDenied('Este organigrama actualmente solo podrá ser editado por ' + organigrama.id_persona_cargo.primer_nombre + ' ' + organigrama.id_persona_cargo.primer_apellido)
        
        ccd = list(CuadrosClasificacionDocumental.objects.filter(id_organigrama=organigrama.id_organigrama).values())
        if not len(ccd):
            serializer = self.serializer_class(organigrama, data=request.data)
            serializer.is_valid(raise_exception=True)
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
    

class GetOrganigramaById(generics.RetrieveAPIView):
    serializer_class = OrganigramaSerializer

    def get(self, request, id_organigrama):
        organigrama = Organigramas.objects.get(id_organigrama=id_organigrama)
        if not organigrama:
            raise NotFound( 'No se encontró el organigrama ingresado')
        serializador = self.serializer_class(organigrama, many=False)
        return Response({'success':True, 'detail':'Se encontro el organigrama', 'data' :serializador.data}, status=status.HTTP_200_OK)
        

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
        if not nuevo_user_organigrama.fecha_a_finalizar_cargo_actual or nuevo_user_organigrama.fecha_a_finalizar_cargo_actual < fecha_sistema.date():
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
        
        if organigrama.id_persona_cargo.id_persona != persona_logueado and persona_logueado != persona_super_usuario.persona.id_persona:
            raise NotFound('No tiene permisos para asignar este organigrama.')
        
        if persona.id_persona == organigrama.id_persona_cargo.id_persona:
            raise NotFound('La persona no se puede reasignar asi mismo.')
        
        if not persona.fecha_a_finalizar_cargo_actual or persona.fecha_a_finalizar_cargo_actual < fecha_sistema.date():
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
    permission_classes = [IsAuthenticated, PermisoActualizarOrganigramas]
    
    def put(self, request, id_organigrama):
        persona_logueada = request.user.persona
                
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
        organigrama.id_persona_cargo = persona_logueada
        
        organigrama.save()
        return Response({'succes': True, 'detail':'Se reanudo correctamente el organigrama.'}, status=status.HTTP_200_OK)

class CambioDeOrganigramaActual(generics.UpdateAPIView):
    serializer_class = OrganigramaCambioDeOrganigramaActualSerializer
    queryset = Organigramas.objects.exclude(fecha_terminado=None)
    queryset2 = CuadrosClasificacionDocumental.objects.all()
    
    def put(self,request):
        data = request.data
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        organigrama_seleccionado = self.queryset.filter(id_organigrama=data['organigrama'], fecha_retiro_produccion=None).first()
        organigrama_actual = self.queryset.filter(actual=True).first()
        ccd_actual = self.queryset2.filter(actual=True).first()
        
        if not organigrama_seleccionado:
            raise ValidationError('El organigrama elegido no se encuentra terminado o ha sido retirado de producción')
        elif organigrama_seleccionado.actual:
            raise ValidationError('No puede activar un organigrama que ya se encuentra activado')
        
        tca_actual = TablasControlAcceso.objects.filter(id_trd__id_ccd=ccd_actual).first()
        previous_activacion_organigrama = copy.copy(organigrama_seleccionado)
        
        temporal_all = TemporalPersonasUnidad.objects.all()
        
        if not ccd_actual:
            organigrama_seleccionado.justificacion_nueva_version = data['justificacion']
            organigrama_seleccionado.actual = True
            organigrama_seleccionado.fecha_puesta_produccion = datetime.now()
            
            if organigrama_actual:
                previous_desactivacion_organigrama = copy.copy(organigrama_actual)
                organigrama_actual.fecha_retiro_produccion = datetime.now()
                organigrama_actual.actual = False
                organigrama_actual.save()
                
                if temporal_all:
                    organigrama_anterior = list(temporal_all.values_list('id_unidad_org_anterior__id_organigrama__id_organigrama', flat=True).distinct())
                    id_organigrama_anterior = organigrama_anterior[0]
                    if organigrama_actual.id_organigrama != id_organigrama_anterior:
                        temporal_all.delete()
                
                # Auditoria Organigrama desactivado
                descripcion = {"NombreOrganigrama":str(organigrama_actual.nombre),"VersionOrganigrama":str(organigrama_actual.version)}
                valores_actualizados={'previous':previous_desactivacion_organigrama, 'current':organigrama_actual}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 15,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)
            
            organigrama_seleccionado.save()
            if temporal_all:
                organigrama_nuevo = list(temporal_all.values_list('id_unidad_org_nueva__id_organigrama__id_organigrama', flat=True).distinct())
                id_organigrama_nuevo = organigrama_nuevo[0]
                if organigrama_seleccionado.id_organigrama != id_organigrama_nuevo:
                    temporal_all.delete()

            # Auditoria Organigrama activado
            descripcion = {"NombreOrganigrama":str(organigrama_seleccionado.nombre),"VersionOrganigrama":str(organigrama_seleccionado.version)}
            valores_actualizados={'previous':previous_activacion_organigrama, 'current':organigrama_seleccionado}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 15,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)
        else:
            if not data.get('id_ccd'):
                raise ValidationError('Debe seleccionar un CCD')
            
            #CCD SELECCIONADO
            ccd_seleccionado = self.queryset2.filter(id_ccd=data.get('id_ccd'), id_organigrama=organigrama_seleccionado.id_organigrama).first()
            if not ccd_seleccionado:
                raise ValidationError('Debe seleccionar un CCD que pertenezca al organigrama que desea activar')
            
            if not ccd_seleccionado.fecha_terminado or ccd_seleccionado.fecha_retiro_produccion:
                raise ValidationError('El CCD seleccionado no se encuentra terminado o ha sido retirado de producción')
                
            tca = TablasControlAcceso.objects.filter(id_trd__id_ccd=ccd_seleccionado.id_ccd).first()

            previous_activacion_ccd = copy.copy(tca.id_trd.id_ccd)
            previous_activacion_trd = copy.copy(tca.id_trd)
            previous_activacion_tca = copy.copy(tca)

            previous_desactivacion_organigrama = copy.copy(tca_actual.id_trd.id_ccd.id_organigrama)
            previous_desactivacion_ccd = copy.copy(tca_actual.id_trd.id_ccd)
            previous_desactivacion_trd = copy.copy(tca_actual.id_trd)
            previous_desactivacion_tca = copy.copy(tca_actual)
            
            #ACTIVACION ORG
            
            organigrama_seleccionado.justificacion_nueva_version = data['justificacion']
            organigrama_seleccionado.actual = True
            organigrama_seleccionado.fecha_puesta_produccion = datetime.now()
            
            #ACTIVACION CCD
            
            tca.id_trd.id_ccd.actual = True
            tca.id_trd.id_ccd.fecha_puesta_produccion = datetime.now()
            tca.id_trd.id_ccd.justificacion = data['justificacion']
            
            #ACTIVACION TRD
            
            tca.id_trd.actual = True
            tca.id_trd.fecha_puesta_produccion = datetime.now()
            
            #ACTIVACION TCA
            
            tca.actual = True
            tca.fecha_puesta_produccion = datetime.now()
            
            #DESACTIVACION INSTRUMENTOS ARCHIVISTICOS ACTUALES
            
            tca_actual = TablasControlAcceso.objects.filter(id_trd__id_ccd=ccd_actual).first()
            
            #DESACTIVACION ORGANIGRAMA
            
            tca_actual.id_trd.id_ccd.id_organigrama.actual = False
            tca_actual.id_trd.id_ccd.id_organigrama.fecha_retiro_produccion = datetime.now()
            
            #DESACTIVACION CCD
            
            tca_actual.id_trd.id_ccd.actual = False
            tca_actual.id_trd.id_ccd.fecha_retiro_produccion = datetime.now()
    
            #DESACTIVACION TRD
            
            tca_actual.id_trd.actual = False
            tca_actual.id_trd.fecha_retiro_produccion = datetime.now()
            
            #DESACTIVACION TCA
            
            tca_actual.actual = False
            tca_actual.fecha_retiro_produccion = datetime.now()
            
            #GUARDADO ACTIVACION
            organigrama_seleccionado.save()
            tca.id_trd.id_ccd.save()
            tca.id_trd.save()
            tca.save()
            
            #GUARDADO DESACTIVACION
            tca_actual.id_trd.id_ccd.id_organigrama.save()
            tca_actual.id_trd.id_ccd.save()
            tca_actual.id_trd.save()
            tca_actual.save()
            
            if temporal_all:
                organigrama_anterior = list(temporal_all.values_list('id_unidad_org_anterior__id_organigrama__id_organigrama', flat=True).distinct())
                id_organigrama_anterior = organigrama_anterior[0]
                if tca_actual.id_trd.id_ccd.id_organigrama.id_organigrama != id_organigrama_anterior:
                    temporal_all.delete()
                    
                organigrama_nuevo = list(temporal_all.values_list('id_unidad_org_nueva__id_organigrama__id_organigrama', flat=True).distinct())
                id_organigrama_nuevo = organigrama_nuevo[0]
                if organigrama_seleccionado.id_organigrama != id_organigrama_nuevo:
                    temporal_all.delete()
            
            
            # Auditoria Organigrama desactivado
            descripcion = {"NombreOrganigrama":str(tca_actual.id_trd.id_ccd.id_organigrama.nombre),"VersionOrganigrama":str(tca_actual.id_trd.id_ccd.id_organigrama.version)}
            valores_actualizados={'previous':previous_desactivacion_organigrama, 'current':tca_actual.id_trd.id_ccd.id_organigrama}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 15,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)
            
            # Auditoria Organigrama activado
            descripcion = {"NombreOrganigrama":str(organigrama_seleccionado.nombre),"VersionOrganigrama":str(organigrama_seleccionado.version)}
            valores_actualizados={'previous':previous_activacion_organigrama, 'current':organigrama_seleccionado}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 15,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria CCD desactivado
            descripcion = {"NombreCCD":str(tca_actual.id_trd.id_ccd.nombre),"VersionCCD":str(tca_actual.id_trd.id_ccd.version)}
            valores_actualizados={'previous':previous_desactivacion_ccd, 'current':tca_actual.id_trd.id_ccd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 27,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria CCD activado
            descripcion = {"NombreCCD":str(tca.id_trd.id_ccd.nombre),"VersionCCD":str(tca.id_trd.id_ccd.version)}
            valores_actualizados={'previous':previous_activacion_ccd, 'current':tca.id_trd.id_ccd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 27,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria TRD desactivado
            descripcion = {"NombreTRD":str(tca_actual.id_trd.nombre),"VersionTRD":str(tca_actual.id_trd.version)}
            valores_actualizados={'previous':previous_desactivacion_trd, 'current':tca_actual.id_trd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 29,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria TRD activado
            descripcion = {"NombreTRD":str(tca.id_trd.nombre),"VersionTRD":str(tca.id_trd.version)}
            valores_actualizados={'previous':previous_activacion_trd, 'current':tca.id_trd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 29,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria TCA desactivado
            descripcion = {"NombreTCA":str(tca_actual.nombre),"VersionTCA":str(tca_actual.version)}
            valores_actualizados={'previous':previous_desactivacion_tca, 'current':tca_actual}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 31,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria TCA activado
            descripcion = {"NombreTCA":str(tca.nombre),"VersionTCA":str(tca.version)}
            valores_actualizados={'previous':previous_activacion_tca, 'current':tca}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 31,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)
            
        #unidades de personas desactivar
        if organigrama_actual:
            unidades_utilizadas=UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama)
            unidades_list=[id.id_unidad_organizacional for id in unidades_utilizadas]
            persona_organigrama_a_remplazar=Personas.objects.filter(id_unidad_organizacional_actual__in=unidades_list)
            for persona in persona_organigrama_a_remplazar:
                persona.es_unidad_organizacional_actual=False
                persona.save()
            
        return Response({'success':True, 'detail':'Se ha activado correctamente el organigrama'}, status=status.HTTP_201_CREATED)
    
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

class ObtenerOrganigramasPosibles(generics.ListAPIView):
    serializer_class = NewUserOrganigramaSerializer
    queryset = Organigramas.objects.filter(actual=False, fecha_retiro_produccion=None).exclude(fecha_terminado=None)
    
    def get (self,request):
        serializador = self.serializer_class(self.queryset.all(), many=True)
        
        return Response({'success':True,'detail':'Los organigramas posibles para activar son los siguientes','data':serializador.data},status=status.HTTP_200_OK)

class ActualizacionUnidadOrganizacionalAntigua(generics.UpdateAPIView):
    serializer_class = ActUnidadOrgAntiguaSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        nueva_id_unidad_organizacional = request.data.get('id_nueva_unidad_organizacional')
        lista_id_personas = request.data.get('personas', [])
        user = request.user
        nombre_de_usuario = user.nombre_de_usuario
        
        cambios_temporal = TemporalPersonasUnidad.objects.all().exists()
        if cambios_temporal:
            raise PermissionDenied('No puede realizar estos cambios. Aún hay cambios de unidades organizacionales pendientes por procesar')

        unidad_organizacional = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=nueva_id_unidad_organizacional).first()
        if not unidad_organizacional:
            raise ValidationError('La nueva unidad organizacional que estás asignando no existe')

        # Obtener la fecha de retiro de producción más actual
        fecha_actual = datetime.now()
        organigrama_actual = Organigramas.objects.filter(fecha_retiro_produccion__lte=fecha_actual).order_by('-fecha_retiro_produccion').first()

        if organigrama_actual.fecha_retiro_produccion and organigrama_actual.actual:
            raise ValidationError('El organigrama está fuera de producción y no puede ser el actual')

        personas = Personas.objects.filter(id_persona__in=lista_id_personas, id_unidad_organizacional_actual__id_organigrama=organigrama_actual.id_organigrama)
        if len(set(lista_id_personas)) != len(personas):
            raise ValidationError('Debe asegurarse de que todas las personas tengan asignadas una unidad del último organigrama retirado de la producción')
        
        lista_id_unidades = [persona.id_unidad_organizacional_actual.id_unidad_organizacional for persona in personas]
        if len(set(lista_id_unidades)) > 1:
            raise ValidationError('Debe asegurarse de que todas las personas elegidas pertenezcan a una misma unidad')

        instance_unidad_anterior = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=lista_id_unidades[0]).first()
        
        queryset = Personas.objects.filter(
            es_unidad_organizacional_actual=False,
            id_persona__in=lista_id_personas
        )

        if queryset.exists():
            personas_actualizadas = []

            # Obtener el consecutivo actual
            consecutivo_actual = CambiosUnidadMasivos.objects.filter(tipo_cambio='UnidadAUnidad').aggregate(max_consecutivo=Max('consecutivo'))['max_consecutivo'] or 0

            for persona in queryset:
                historico = HistoricoCargosUndOrgPersona(
                    id_persona=persona,
                    id_cargo=persona.id_cargo,
                    id_unidad_organizacional=persona.id_unidad_organizacional_actual,
                    fecha_inicial_historico=persona.fecha_asignacion_unidad,
                    fecha_final_historico=fecha_actual,
                    observaciones_vinculni_cargo=None,
                    justificacion_cambio_und_org=f'Cambio mediante proceso del sistema de Traslado Masivo de Unidad a Unidad',
                    desvinculado=False
                )
                historico.save()

                persona.id_unidad_organizacional_actual = unidad_organizacional
                persona.es_unidad_organizacional_actual = True
                persona.fecha_asignacion_unidad = fecha_actual
                persona.save(update_fields=['id_unidad_organizacional_actual', 'es_unidad_organizacional_actual', 'fecha_asignacion_unidad'])
                personas_actualizadas.append(persona)

            if personas_actualizadas:
                # Incrementar el consecutivo
                consecutivo_actual += 1

                # Crear el registro en CambiosUnidadMasivos
                cambio_unidad_masivo = CambiosUnidadMasivos(
                    consecutivo=consecutivo_actual,
                    fecha_cambio=fecha_actual,
                    id_persona_cambio=user.persona,
                    tipo_cambio='UnidadAUnidad',
                    justificacion=f'Se realizó el traslado masivo de {len(personas_actualizadas)} personas desde la unidad del organigrama anterior {instance_unidad_anterior.nombre} hasta la unidad del organigrama nuevo {unidad_organizacional.nombre}',
                )
                cambio_unidad_masivo.save()
                
                # Auditoria traslado masivo de unidades por entidad
                user_logeado = user.id_usuario
                dirip = Util.get_client_ip(request)
                descripcion = {'TipoCambio':'UnidadAUnidad', 'Consecutivo':str(consecutivo_actual), 'FechaCambio':str(fecha_actual)}
                auditoria_data = {
                    'id_usuario': user_logeado,
                    'id_modulo': 115,
                    'cod_permiso': 'EJ',
                    'subsistema': 'TRSV',
                    'dirip': dirip,
                    'descripcion': descripcion
                }
                Util.save_auditoria(auditoria_data)

                return Response({'success': True, 'detail': 'Las personas han sido actualizadas exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise ValidationError('No se encontraron personas para actualizar')
        else:
            raise ValidationError('No se encontraron personas para actualizar')

class GetUnidadOrgDesactualizada(generics.ListAPIView):
    serializer_class = ActUnidadOrgAntiguaSerializer

    def get(self, request):
        id_unidad_organizacional_actual = self.request.data.get('id_unidad_organizacional_actual')
        fecha_actual = datetime.now()
        ultimo_organigrama_retirado = Organigramas.objects.filter(fecha_retiro_produccion__lte=fecha_actual).order_by('-fecha_retiro_produccion').first()
        
        if not ultimo_organigrama_retirado:
            raise PermissionDenied('Aún no se ha retirado ningún organigrama')

        if ultimo_organigrama_retirado.fecha_retiro_produccion and ultimo_organigrama_retirado.actual:
            raise ValidationError('El organigrama está fuera de producción y no puede ser el actual')

        if id_unidad_organizacional_actual:
            try:
                id_unidad_organizacional_actual = int(id_unidad_organizacional_actual)
                queryset = Personas.objects.filter(
                    id_unidad_organizacional_actual=id_unidad_organizacional_actual,
                    es_unidad_organizacional_actual=False,
                    id_unidad_organizacional_actual__id_organigrama=ultimo_organigrama_retirado.id_organigrama
                )
            except ValueError:
                return Personas.objects.none()
        else:
            queryset = Personas.objects.filter(
                es_unidad_organizacional_actual=False,
                id_unidad_organizacional_actual__id_organigrama=ultimo_organigrama_retirado.id_organigrama
            )
            
        if not queryset.exists():
            raise NotFound('No se encuentran personas con esta unidad organizacional fuera de producción')
        
        serializador = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializador.data}, status=status.HTTP_200_OK)

class GetUnidadesOrganigramaRetiradoReciente(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()

    def get(self, request):
        organigramas = Organigramas.objects.filter(actual=False).exclude(fecha_retiro_produccion=None).order_by('-fecha_retiro_produccion')
        
        if not organigramas:
            raise NotFound('No existe organigramas retirados de produccion')
        
        organigrama_retirado = organigramas.first()
        
        unidades_organigrama_retirado = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_retirado.id_organigrama)
        
        serializer = self.serializer_class(unidades_organigrama_retirado, many=True)
        return Response({'success':True, 'detail':'Consulta Organigrama Retirado Reciente Exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class ListadoUnidadOrgDesactSinTemporal(generics.ListAPIView):
    serializer_class = ActUnidadOrgAntiguaSerializer

    def get(self, request):
        fecha_actual = datetime.now()
        organigrama_actual = Organigramas.objects.filter(fecha_retiro_produccion__lte=fecha_actual).order_by('-fecha_retiro_produccion').first()

        if organigrama_actual.fecha_retiro_produccion and organigrama_actual.actual:
            raise ValidationError('El organigrama está fuera de producción y no puede ser el actual')

        queryset = Personas.objects.filter(
            es_unidad_organizacional_actual=False,
            id_unidad_organizacional_actual__id_organigrama=organigrama_actual.id_organigrama
        ).exclude(Q(id_persona__in=TemporalPersonasUnidad.objects.values('id_persona')))
        
        serializador = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializador.data}, status=status.HTTP_200_OK)

class ListaTemporalPersonasUnidad(generics.ListAPIView):
    serializer_class = TemporalPersonasUnidadSerializer
    queryset = TemporalPersonasUnidad.objects.all().order_by('id_unidad_org_nueva__nombre')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.exists():
            id_organigrama_nuevo = self.queryset.all().values_list('id_unidad_org_nueva__id_organigrama__id_organigrama', flat=True).distinct()
            id_organigrama_nuevo = list(id_organigrama_nuevo)
            id_organigrama_nuevo = id_organigrama_nuevo[0] if id_organigrama_nuevo else None
            
            id_organigrama_anterior = self.queryset.all().values_list('id_unidad_org_anterior__id_organigrama__id_organigrama', flat=True).distinct()
            id_organigrama_anterior = list(id_organigrama_anterior)
            id_organigrama_anterior = id_organigrama_anterior[0] if id_organigrama_anterior else None
            
            nombre_organigrama_nuevo = None
            if id_organigrama_nuevo:
                nombre_organigrama_nuevo = Organigramas.objects.filter(id_organigrama=id_organigrama_nuevo).first()
                nombre_organigrama_nuevo = nombre_organigrama_nuevo.nombre
                
            nombre_organigrama_anterior = None
            if id_organigrama_anterior:
                nombre_organigrama_anterior = Organigramas.objects.filter(id_organigrama=id_organigrama_anterior).first()
                nombre_organigrama_anterior = nombre_organigrama_anterior.nombre
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    'success': True,
                    'detail': 'Resultados de la búsqueda',
                    'id_organigrama_anterior': id_organigrama_anterior,
                    'nombre_organigrama_anterior': nombre_organigrama_anterior,
                    'id_organigrama_nuevo': id_organigrama_nuevo,
                    'nombre_organigrama_nuevo': nombre_organigrama_nuevo,
                    'data': serializer.data
                }, status=status.HTTP_200_OK
            )
        else:
            raise ValidationError('No hay ninguna persona en proceso de actualización de unidad organizacional')

class ListadoPersonasOrganigramaActual(generics.ListAPIView):
    serializer_class = ActUnidadOrgAntiguaSerializer

    def get_queryset(self):
        unidades_activas = UnidadesOrganizacionales.objects.filter(id_organigrama__actual=True)
        queryset = Personas.objects.filter(
            id_unidad_organizacional_actual__in=unidades_activas,
            es_unidad_organizacional_actual=True
        )
        personas_unidad_temp = TemporalPersonasUnidad.objects.all().values_list('id_persona', flat=True)
        queryset = queryset.exclude(id_persona__in=personas_unidad_temp)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('Ninguna persona está asignada al organigrama actual')

class GuardarActualizacionUnidadOrganizacional(generics.UpdateAPIView):
    serializer_class = ActUnidadOrgAntiguaSerializer
    
    def put(self, request, id_organigrama):
        personas_nuevas_unidades = request.data
        if not isinstance(personas_nuevas_unidades, list):
            raise ValidationError('El cuerpo de la solicitud debe ser una lista de objetos')
        
        organigrama_cambio = Organigramas.objects.filter(id_organigrama=id_organigrama, fecha_retiro_produccion=None, fecha_puesta_produccion=None).exclude(fecha_terminado=None).first()
        if not organigrama_cambio:
            raise ValidationError('No puede realizar el guardado parcial para el organigrama elegido. Debe seleccionar un organigrama valido')
        
        personas_enviadas = [persona_nueva_unidad.get('id_persona') for persona_nueva_unidad in personas_nuevas_unidades]
        unidades_enviadas = [persona_nueva_unidad.get('id_nueva_unidad_organizacional') for persona_nueva_unidad in personas_nuevas_unidades]
        
        # VALIDAR PERSONAS TENGAN UNIDAD ASIGNADA Y DEL ORGANIGRAMA ACTUAL
        unidades_actual_personas = Personas.objects.filter(id_persona__in=personas_enviadas, es_unidad_organizacional_actual=True)
        if len(personas_enviadas) != len(unidades_actual_personas):
            raise ValidationError('Debe enviar personas existentes y que tengan asignado una unidad organizacional del organigrama actual')
        
        # VALIDAR UNIDADES PERTENEZCAN A MISMA UNIDAD
        unidades_organigrama = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_enviadas, id_organigrama=id_organigrama)
        if len(set(unidades_enviadas)) != len(unidades_organigrama):
            raise ValidationError('Las unidades a las cuales desea realizar el cambio deben pertenecer a un mismo organigrama terminado')
        
        # ELIMINAR CAMBIOS PARCIALES DESELECCIONADOS
        TemporalPersonasUnidad.objects.exclude(id_persona__in=personas_enviadas).delete()
        
        # VALIDAR SI CAMBIAN ORGANIGRAMA
        temporal_all = TemporalPersonasUnidad.objects.all()
        if temporal_all:
            temporal_all_list = list(temporal_all.values_list('id_unidad_org_nueva__id_organigrama__id_organigrama', flat=True).distinct())
            if temporal_all_list[0] != int(id_organigrama):
                raise ValidationError('Si desea cambiar el organigrama nuevo debe desmarcar a todas las personas con cambios parciales antes de continuar')

        for persona_nueva_unidad in personas_nuevas_unidades:
            id_persona = persona_nueva_unidad.get('id_persona')
            nueva_id_unidad_organizacional = persona_nueva_unidad.get('id_nueva_unidad_organizacional')
            try:
                persona = Personas.objects.get(id_persona=id_persona)
            except Personas.DoesNotExist:
                raise ValidationError(f'La persona con ID {id_persona} no existe')

            # Verificar si existe un registro en TemporalPersonasUnidad para la persona actual
            temporal_persona = temporal_all.filter(id_persona=persona).first()

            nueva_unidad = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=nueva_id_unidad_organizacional).first()

            if temporal_persona:
                if temporal_persona.id_unidad_org_nueva != nueva_unidad.id_unidad_organizacional:
                    temporal_persona.id_unidad_org_nueva = nueva_unidad
                    temporal_persona.save()
            else:
                unidad_anterior = persona.id_unidad_organizacional_actual
                TemporalPersonasUnidad.objects.create(
                    id_persona=persona,
                    id_unidad_org_anterior=unidad_anterior,
                    id_unidad_org_nueva=nueva_unidad
                )

        return Response({'success': True, 'detail': 'Las personas han sido guardadas exitosamente'}, status=status.HTTP_201_CREATED)

class ProcederActualizacionUnidad(generics.UpdateAPIView):
    serializer_class = ActUnidadOrgAntiguaSerializer
    permission_classes = [IsAuthenticated]
    
    def put(self, request, format=None):
        personas_nuevas_unidades = request.data
        if not isinstance(personas_nuevas_unidades, list):
            raise ValidationError('El cuerpo de la solicitud debe ser una lista de objetos')
        
        personas_actualizadas = []
        fecha_actual = datetime.now()
        user = request.user
        nombre_de_usuario = user.nombre_de_usuario
        
        with transaction.atomic():
            try:
                for persona_nueva_unidad in personas_nuevas_unidades:
                    id_persona = persona_nueva_unidad.get('id_persona')
                    nueva_id_unidad_organizacional = persona_nueva_unidad.get('id_nueva_unidad_organizacional')
                    
                    try:
                        persona = Personas.objects.get(id_persona=id_persona)
                    except Personas.DoesNotExist:
                        raise NotFound(f'La persona con ID {id_persona} no existe')
                    
                    # Crear registro histórico
                    historico = HistoricoCargosUndOrgPersona(
                        id_persona = persona,
                        id_cargo = persona.id_cargo,
                        id_unidad_organizacional = persona.id_unidad_organizacional_actual,
                        fecha_inicial_historico = persona.fecha_asignacion_unidad,
                        fecha_final_historico = fecha_actual,
                        observaciones_vinculni_cargo = None,
                        justificacion_cambio_und_org = f'Traslado Masivo de Unidad por Entidad por {nombre_de_usuario} el {fecha_actual.strftime("%Y-%m-%d %H:%M:%S")}',
                        desvinculado = False
                    )
                    historico.save()
                    
                    # Actualizar persona
                    persona.id_unidad_organizacional_actual = UnidadesOrganizacionales.objects.get(id_unidad_organizacional=nueva_id_unidad_organizacional)
                    persona.es_unidad_organizacional_actual = True
                    persona.fecha_asignacion_unidad = datetime.now() 
                    persona.save()
                    
                    personas_actualizadas.append(persona)

                if personas_actualizadas:
                    # Obtener el consecutivo actual
                    consecutivo_actual = CambiosUnidadMasivos.objects.filter(tipo_cambio='UnidadesTodas').aggregate(max_consecutivo=Max('consecutivo'))['max_consecutivo'] or 0

                    # Incrementar el consecutivo
                    consecutivo_actual += 1

                    # Crear el registro en CambiosUnidadMasivos
                    cambio_unidad_masivo = CambiosUnidadMasivos(
                        consecutivo=consecutivo_actual,
                        fecha_cambio=fecha_actual,
                        id_persona_cambio=user.persona,
                        tipo_cambio='UnidadesTodas',
                        justificacion=f'Se trasladaron {len(personas_actualizadas)} personas',
                    )
                    cambio_unidad_masivo.save()
                    
                    # Auditoria traslado masivo de unidades por entidad
                    user_logeado = request.user.id_usuario
                    dirip = Util.get_client_ip(request)
                    descripcion = {'TipoCambio':'UnidadesTodas', 'Consecutivo':str(consecutivo_actual), 'FechaCambio':str(fecha_actual)}
                    auditoria_data = {
                        'id_usuario': user_logeado,
                        'id_modulo': 114,
                        'cod_permiso': 'EJ',
                        'subsistema': 'TRSV',
                        'dirip': dirip,
                        'descripcion': descripcion
                    }
                    Util.save_auditoria(auditoria_data)
                        
                TemporalPersonasUnidad.objects.all().delete()
                
            except Exception as e:
                raise ValidationError('Error: ' + str(e))
        
        return Response({'success': True, 'detail': 'Las personas han sido actualizadas exitosamente'}, status=status.HTTP_200_OK)

class GetHistoricoUnidadAUnidad(generics.ListAPIView):
    serializer_class = GetCambiosUnidadMasivosSerializer
    queryset = CambiosUnidadMasivos.objects.filter(tipo_cambio='UnidadAUnidad')
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = self.queryset.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success':True, 'detail':'Se encontró el siguiente histórico de traslados masivos de unidad a unidad', 'data': serializer.data}, status=status.HTTP_200_OK)
    
class GetHistoricoUnidadEntidad(generics.ListAPIView):
    serializer_class = GetCambiosUnidadMasivosSerializer
    queryset = CambiosUnidadMasivos.objects.filter(tipo_cambio='UnidadesTodas')
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = self.queryset.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success':True, 'detail':'Se encontró el siguiente histórico de traslados masivos de unidad por entidad', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class GetActualSeccionSubsecciones(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    
    def get(self, request, id_organigrama):
        organigrama = Organigramas.objects.filter(id_organigrama=id_organigrama).first()
        if organigrama:
            unidades = UnidadesOrganizacionales.objects.filter(
                Q(id_organigrama=id_organigrama) & 
                ~Q(cod_agrupacion_documental=None) &
                Q(actual=True)  # Agregar esta condición para filtrar por 'actual' en True
            )
            serializer = self.serializer_class(unidades, many=True)
            return Response({'success':True, 'detail':'Se encontraron las siguientes unidades', 'data':serializer.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('Debe consultar por un organigrama válido')
