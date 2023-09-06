from almacen.models.bienes_models import CatalogoBienes
from rest_framework import generics,status
from rest_framework.response import Response
from almacen.serializers.solicitudes_serialiers import PersonasResponsablesFilterSerializer
from transversal.models import UnidadesOrganizacionales, NivelesOrganigrama
from seguridad.models import Personas
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from transversal.models.entidades_models import ConfiguracionEntidad
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales,
    NivelesOrganigrama
)
from almacen.models.solicitudes_models import (
    SolicitudesConsumibles,
    ItemsSolicitudConsumible
)
from django.db.models import Q
from rest_framework.response import Response
from datetime import datetime, date
from almacen.serializers.solicitudes_viveros_serializers import ( 
    CrearSolicitudesviverosPostSerializer,
    CrearItemsSolicitudViveroPostSerializer
    )
from seguridad.serializers.personas_serializers import PersonasSerializer
import copy

class CreateSolicitudViveros(generics.UpdateAPIView):
    serializer_class = CrearSolicitudesviverosPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    serializer_item_solicitud = CrearItemsSolicitudViveroPostSerializer
    
    def put(self, request, *args, **kwargs):
        # SE OBTIENEN LOS DATOS DE LA SOLICITUD DEL JSON
        datos_ingresados = request.data
        info_solicitud = datos_ingresados['info_solicitud']
        items_solicitud = datos_ingresados['items_solicitud']
        valores_creados_detalles = []
        user_logeado = request.user
        if str(user_logeado) == 'AnonymousUser':
            raise NotFound('Esta solicitud solo la puede ejecutar un usuario logueado')
        if len(items_solicitud) <= 0:
            raise NotFound('La solicitud debe tener items')
        if info_solicitud['id_solicitud_consumibles'] == None:
            bandera_actualizar = False
        else:
            instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=info_solicitud['id_solicitud_consumibles']).first()
            if not instancia_solicitud:
                raise NotFound('Si desea actualizar una solicitud, ingrese un id de solicitud de consumibles válido')
            else:
                instancia_solicitud_previous = copy.copy(instancia_solicitud)
                bandera_actualizar = True
        
        # ASIGNACIÓN DE DATOS POR DEFECTO A LA TABLA SOLICITUDES
        info_solicitud['fecha_solicitud'] = str(date.today())
        info_solicitud['id_persona_solicita'] = user_logeado.persona.id_persona
        if user_logeado.persona.id_unidad_organizacional_actual == None:
            raise NotFound('El usuario solicitante debe tener asignada una unidad organizacional')
        info_solicitud['id_unidad_org_del_solicitante'] = user_logeado.persona.id_unidad_organizacional_actual.id_unidad_organizacional
        info_solicitud['solicitud_abierta'] = True
        solicitudes_existentes = SolicitudesConsumibles.objects.all()
        bienes_repetidos = [i['id_bien'] for i in items_solicitud]
        unidad_para_la_que_solicita = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = info_solicitud['id_unidad_para_la_que_solicita']).values().first()
        if info_solicitud['id_funcionario_responsable_unidad'] != None and info_solicitud['id_funcionario_responsable_unidad'] != '':
            funcionario_responsable = Personas.objects.filter(id_persona = info_solicitud['id_funcionario_responsable_unidad']).first()
            if not funcionario_responsable:
                raise NotFound('El funcionario responsable no existe')
            
            coordinador_viveros = ConfiguracionEntidad.objects.filter(id_persona_coord_viveros_actual=info_solicitud['id_funcionario_responsable_unidad']).first()
            if not coordinador_viveros:
                raise NotFound('El funcionario responsable debe ser el Coordinador de Viveros actual')
            
            # if funcionario_responsable.id_unidad_organizacional_actual == None:
            #     raise NotFound('El funcionario responsable debe tener asignada una unidad organizacional')
            # if user_logeado.persona.id_unidad_organizacional_actual.id_unidad_organizacional == funcionario_responsable.id_unidad_organizacional_actual.id_unidad_organizacional:
            #     raise NotFound('El funcionario responsable no puede ser de la misma unidad organizacional del que solicita')
            
            info_solicitud['id_unidad_org_del_responsable'] = funcionario_responsable.id_unidad_organizacional_actual.id_unidad_organizacional
        else:
            info_solicitud['id_unidad_org_del_responsable'] = None
        # VALIDACIONES PRIMARIAS        
        if not unidad_para_la_que_solicita:
            raise NotFound('La unidad organizacional ingresada no existe')
        if len(bienes_repetidos) != len(set(bienes_repetidos)):
            raise NotFound('Solo puede ingresar una vez un bien en una solicitud')
        # ASIGNACIÓN DEL NÚMERO DE SOLICITUD
        info_solicitud['es_solicitud_de_conservacion'] = True

        # SE CREAN ALGUNAS VARIABLES AUXILIARES
        unidades_organiacionales_misma_linea = []
        count = 0
        # VALIDACIONES ITEMS DE LA SOLICITUD
        for i in items_solicitud:
            if bandera_actualizar == True:
                if i['id_item_solicitud_consumible'] != None: 
                    instancia_item = ItemsSolicitudConsumible.objects.filter(id_item_solicitud_consumible = i['id_item_solicitud_consumible']).first()
                else:
                    instancia_item = None
                if instancia_item:
                    if str(instancia_item.id_solicitud_consumibles) != str(info_solicitud['id_solicitud_consumibles']):
                        raise NotFound('El item (' + str(instancia_item.id_item_solicitud_consumible) + ') no tiene relación con la solicitud')
            bien = CatalogoBienes.objects.filter(id_bien = i['id_bien']).first()
            if not bien:
                raise NotFound('El bien (' + str(i['id_bien']) + ') no existe')
            if bien.nivel_jerarquico > 5 or bien.nivel_jerarquico < 2:
                raise NotFound('El bien (' + bien.nombre + ') no es de nivel 5')
            if bien.cod_tipo_bien != 'C':
                raise NotFound('El bien (' + bien.nombre + ') no es de consumo')
            if not str(i['cantidad']).isdigit():
                raise NotFound('La cantidad debe ser un número entero')
            if not str(i['nro_posicion']).isdigit():
                raise NotFound('El número de posición debe ser un número entero')
            if bien.solicitable_vivero != True:
                raise NotFound('En este módulo solo se pueden despachar bienes solicitables por vivero')
            
            i['id_unidad_medida'] = bien.id_unidad_medida.id_unidad_medida
        aux_nro_posicion = [i['nro_posicion'] for i in items_solicitud]

        if len(aux_nro_posicion) != len(set(aux_nro_posicion)):
            raise NotFound('Los números de posición deben ser diferentes entre ellos')
        
        if str(user_logeado.persona.id_unidad_organizacional_actual.cod_tipo_unidad) == 'AS' or str(user_logeado.persona.id_unidad_organizacional_actual.cod_tipo_unidad) == 'AP':
            instancia_nivel_1 = NivelesOrganigrama.objects.filter(id_nivel_organigrama = 1).first()
            unidad_padre_de_todos = UnidadesOrganizacionales.objects.filter(id_nivel_organigrama = instancia_nivel_1).first()
            padre_de_todos = Personas.objects.filter(id_unidad_organizacional_actual = unidad_padre_de_todos).first()
            if user_logeado.persona.id_unidad_organizacional_actual.id_unidad_organizacional != info_solicitud['id_unidad_para_la_que_solicita']:
                raise NotFound('Un usuario de una unidad de apoyo o asesor solo le puede hacer solicitudes a la misma unidad a la que pertenece')

            # if (info_solicitud['id_funcionario_responsable_unidad'] != padre_de_todos.id_persona and info_solicitud['id_funcionario_responsable_unidad'] != '' and info_solicitud['id_funcionario_responsable_unidad'] != None) or info_solicitud['id_funcionario_responsable_unidad'] == user_logeado.persona.id_persona:
            #     raise NotFound('El usuario supervisor no puede ser el mismo usuario que solicita, el funcionario supervisor solo puede ser de unidad organizacional nivel 1')
        # VALIDACIÓN DE LA LINEA DEL ORGANIGRAMA A LA QUE PERTENECE EL USUARIO SOLICITANTE Y EL USUARIO SUPERVISOR DEL SOLICITANTE
        else:
            if int(info_solicitud['id_funcionario_responsable_unidad']) == user_logeado.persona.id_persona:
                raise NotFound('El usuario quien solicita no puede ser el supervisor')
            aux_niveles_organigrama = NivelesOrganigrama.objects.all().values()
            
            niveles_organigrama = [i['orden_nivel'] for i in aux_niveles_organigrama]
            unidades_iguales_y_arriba = []
            valores_actualizados_detalles = []
            valores_creados_detalles = []
            aux_unidades_mismo_nivel = user_logeado.persona.id_unidad_organizacional_actual.nombre
            unidades_organiacionales_misma_linea.append(aux_unidades_mismo_nivel)
            unidades_iguales_y_arriba.append(aux_unidades_mismo_nivel)
            if (user_logeado.persona.id_unidad_organizacional_actual.id_nivel_organigrama.orden_nivel + 1) <= max(niveles_organigrama): 
                lista_aux_1 = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre = user_logeado.persona.id_unidad_organizacional_actual).values()
                unidades_organiacionales_misma_linea.extend([i['nombre'] for i in lista_aux_1])
                count = user_logeado.persona.id_unidad_organizacional_actual.id_nivel_organigrama.orden_nivel + 2
                while (count) <= max(niveles_organigrama):
                    aux_1 = None
                    lista_aux_2 = []
                    for i in lista_aux_1:
                        aux_1 = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre = i['id_unidad_organizacional']).values()
                        unidades_organiacionales_misma_linea.extend([i['nombre'] for i in aux_1])
                        lista_aux_2.extend(aux_1)
                    lista_aux_1 = lista_aux_2
                    count += 1
            
            if user_logeado.persona.id_unidad_organizacional_actual.unidad_raiz == False:
                unidades_arriba = user_logeado.persona.id_unidad_organizacional_actual.id_unidad_org_padre.nombre
                unidades_organiacionales_misma_linea.append(unidades_arriba)
                unidades_iguales_y_arriba.append(unidades_arriba)
                count = user_logeado.persona.id_unidad_organizacional_actual.id_unidad_org_padre.id_nivel_organigrama.orden_nivel - 1
                aux_menor = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = user_logeado.persona.id_unidad_organizacional_actual.id_unidad_org_padre.id_unidad_organizacional).first()
                if aux_menor.id_nivel_organigrama.orden_nivel >= 2:
                    if aux_menor.id_unidad_org_padre.unidad_raiz == False:
                        unidades_organiacionales_misma_linea.append(aux_menor.id_unidad_org_padre.nombre)
                        unidades_iguales_y_arriba.append(aux_menor.id_unidad_org_padre.nombre)
                        while count >= 1:
                            aux_menor = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = aux_menor.id_unidad_org_padre.id_unidad_organizacional).first()
                            if aux_menor.id_unidad_org_padre:
                                unidades_organiacionales_misma_linea.append(aux_menor.id_unidad_org_padre.nombre)
                                unidades_iguales_y_arriba.append(aux_menor.id_unidad_org_padre.nombre)
                            count = count - 1
                        unidades_organiacionales_misma_linea = sorted(unidades_organiacionales_misma_linea)
            if not unidad_para_la_que_solicita['nombre'] in unidades_organiacionales_misma_linea:
                raise NotFound('La unidad organizacional para la que solicita no pertenece a la linea del organigrama a la que pertenece el solicitante')
            
            # if not funcionario_responsable.id_unidad_organizacional_actual.nombre in unidades_iguales_y_arriba or funcionario_responsable.id_unidad_organizacional_actual.nombre == None:
            #     raise NotFound('La persona que ingresó como responsable no es ningún superior de la persona que solicita')
        # Creacion de solicitudes
        if bandera_actualizar == False:
            if solicitudes_existentes:
                numero_solicitudes_conservacion = [i.nro_solicitud_por_tipo for i in solicitudes_existentes if i.es_solicitud_de_conservacion == True]
                if len(numero_solicitudes_conservacion) > 0:
                    info_solicitud['nro_solicitud_por_tipo'] = max(numero_solicitudes_conservacion) + 1
                else:
                    info_solicitud['nro_solicitud_por_tipo'] = 1
            else:
                info_solicitud['nro_solicitud_por_tipo'] = 1   
            
            serializer = self.serializer_class(data=info_solicitud)
            serializer.is_valid(raise_exception=True)
            serializer.save()        
            
            for i in items_solicitud:
                i['id_solicitud_consumibles'] = serializer.data['id_solicitud_consumibles']
                aux_bien = CatalogoBienes.objects.filter(id_bien=i['id_bien']).first()
                valores_creados_detalles.append({'nombre' : aux_bien.nombre})
            serializer = self.serializer_item_solicitud(data=items_solicitud, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            descripcion = {"numero_entrada_almacen": str(info_solicitud['nro_solicitud_por_tipo']), "fecha_solicitud": str(info_solicitud['fecha_solicitud'])}
            direccion=Util.get_client_ip(request)
        
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 35,
                "cod_permiso": "CR",
                "subsistema": 'ALMA',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_creados_detalles": valores_creados_detalles
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
        #Actualizacion solicitudes
        elif bandera_actualizar == True:
            info_solicitud['nro_solicitud_por_tipo'] = instancia_solicitud.nro_solicitud_por_tipo
            serializer = self.serializer_class(instancia_solicitud, data=info_solicitud)
            serializer.is_valid(raise_exception=True)
            serializer.save() 
            dirip = Util.get_client_ip(request)
            aux_items_enviados = [i['id_item_solicitud_consumible'] for i in items_solicitud if i['id_item_solicitud_consumible'] != None]      
            instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=info_solicitud['id_solicitud_consumibles']).first()
            instancia_items_eliminar = ItemsSolicitudConsumible.objects.filter(~Q(id_item_solicitud_consumible__in=aux_items_enviados) & Q(id_solicitud_consumibles=instancia_solicitud.id_solicitud_consumibles))
            nombre_items_eliminar = [{'nombre' : i.id_bien.nombre} for i in instancia_items_eliminar]
            valores_eliminados_detalles = nombre_items_eliminar
            instancia_items_eliminar.delete()
            for j in items_solicitud:
                j['id_solicitud_consumibles'] = serializer.data['id_solicitud_consumibles']
                if j['id_item_solicitud_consumible'] == None:
                    #del j['id_item_solicitud_consumible']
                    serializer_act = self.serializer_item_solicitud(data=j, many=False)
                    serializer_act.is_valid(raise_exception=True)
                    serializer_act.save()
                    aux_bien = CatalogoBienes.objects.filter(id_bien=j['id_bien']).first()
                    valores_creados_detalles.append({'nombre':aux_bien.nombre})
                else:
                    instancia_item = ItemsSolicitudConsumible.objects.filter(id_item_solicitud_consumible = j['id_item_solicitud_consumible']).first()
                    previous_instancia_item = copy.copy(instancia_item)
                    if not instancia_item:
                        raise NotFound('Uno de los id de los items no es válido')
                    serializer_act = self.serializer_item_solicitud(instancia_item, data=j, many=False)
                    serializer_act.is_valid(raise_exception=True)
                    serializer_act.save()
                    valores_actualizados_detalles.append({'descripcion': {'nombre':instancia_item.id_bien.nombre}, 'previous':previous_instancia_item,'current':instancia_item})
            descripcion = {"numero_entrada_almacen": str(info_solicitud['nro_solicitud_por_tipo']), "fecha_solicitud": str(info_solicitud['fecha_solicitud'])}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 35,
                "cod_permiso": "AC",
                "subsistema": 'ALMA',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_eliminados_detalles": valores_eliminados_detalles,
                "valores_creados_detalles": valores_creados_detalles,
                "valores_actualizados_detalles": valores_actualizados_detalles
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
            return Response({'success':True, 'detail':'Solicitud actualizada con éxito', 'Numero solicitud' : info_solicitud["nro_solicitud_por_tipo"]},status=status.HTTP_200_OK)
        return Response({'success':True, 'detail':'Solicitud registrada con éxito', 'Numero solicitud' : info_solicitud["nro_solicitud_por_tipo"]},status=status.HTTP_200_OK)
    
class GetNroDocumentoSolicitudesBienesConsumoVivero(generics.ListAPIView):
# ESTA FUNCIONALIDAD PERMITE CONSULTAR EL ÚLTIMO NÚMERO DE DOCUMENTO DE LA CREACIÓN DE SOLICITUDES
    serializer_class = CrearSolicitudesviverosPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    def get(self, request):
        nro_solicitud = SolicitudesConsumibles.objects.filter(es_solicitud_de_conservacion=True).order_by('nro_solicitud_por_tipo').last()
        
        nro = 1
        if nro_solicitud:
            nro = nro_solicitud.nro_solicitud_por_tipo + 1
            
        return Response({'success':True, 'detail':nro, },status=status.HTTP_200_OK)

class RevisionSolicitudBienConsumosViveroPorSupervisor(generics.UpdateAPIView):
    serializer_class = CrearSolicitudesviverosPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    def put(self, request, id_solicitud,*args, **kwargs):
        datos_ingresados = request.data
        user_logeado = request.user
        if str(user_logeado) == 'AnonymousUser':
            raise NotFound('Esta solicitud solo la puede ejecutar un usuario logueado')
        if not str(id_solicitud).isdigit():
            raise NotFound('El Id_solicitud debe ser un número entero')
        if datos_ingresados['estado_aprobacion_responsable'] != 'A' and datos_ingresados['estado_aprobacion_responsable'] != 'R':
            raise NotFound('El estado de aprobación debe ser A o R')

        instance = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=int(id_solicitud)).first()
        if instance.es_solicitud_de_conservacion != True:
            raise NotFound('La solicitud que ingresó no es de vivero')
        if not instance:
            raise NotFound('Debe de ingresar un id de solicitud válido')
        if instance.revisada_responsable == True:
            raise NotFound('Esta solicitud ya ha sido aprobada')
        if instance.id_funcionario_responsable_unidad.id_persona != user_logeado.persona.id_persona:
            raise NotFound('Usted no es el funcionario responsable de esta solicitud')
        instance.estado_aprobacion_responsable = datos_ingresados['estado_aprobacion_responsable']
        instance.revisada_responsable = True
        instance.fecha_aprobacion_responsable = str(date.today())
        if datos_ingresados['estado_aprobacion_responsable'] == 'R':
            instance.solicitud_abierta = False
            instance.justificacion_rechazo_responsable = datos_ingresados['justificacion_rechazo_responsable']
            instance.fecha_cierre_solicitud = str(date.today())
        instance.save()
        
        return Response({'success':True,'Detail':'Solicitud aprobada con éxito', },status=status.HTTP_200_OK)

class SearchCoordinadorViveros(generics.ListAPIView):
    serializer_class=PersonasResponsablesFilterSerializer
    queryset=Personas.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self, request):
        coordinador_viveros = ConfiguracionEntidad.objects.all().first()
        coordinador_viveros = coordinador_viveros.id_persona_coord_viveros_actual if coordinador_viveros else {}
        data = {}
        detail = 'No se encontró el Coordinador de Viveros'
        if coordinador_viveros:
            serializador_personas = self.serializer_class(coordinador_viveros)
            data = serializador_personas.data
            detail = 'Se encontró el Coordinador de Viveros'
        return Response({'success':True, 'detail':detail, 'data':data}, status=status.HTTP_200_OK)