from almacen.models.bienes_models import CatalogoBienes
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from almacen.serializers.organigrama_serializers import UnidadesOrganizacionales, UnidadesGetSerializer
from rest_framework import generics,status
from rest_framework.response import Response
from almacen.models import UnidadesOrganizacionales, NivelesOrganigrama
from seguridad.models import Personas, User
from rest_framework.decorators import api_view
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from seguridad.models import (
    Personas,
    User,
    ClasesTerceroPersona
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales,
    NivelesOrganigrama
)
from almacen.models.generics_models import (
    UnidadesMedida
)

from almacen.models.solicitudes_models import (
    SolicitudesConsumibles,
    ItemsSolicitudConsumible
)
from django.db.models import Q
from rest_framework.response import Response
from datetime import datetime, date
from almacen.serializers.solicitudes_serialiers import ( 
    CrearSolicitudesPostSerializer,
    CrearItemsSolicitudConsumiblePostSerializer
    )
from seguridad.serializers.personas_serializers import PersonasSerializer
import copy

class FiltroBienSolicitableVivero(generics.ListAPIView):
    serializer_class=CatalogoBienesSerializer
    queryset=CatalogoBienes.objects.all()
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','codigo_bien','nombre_cientifico','cod_tipo_elemento_vivero']:
                if key != 'cod_tipo_elemento_vivero':
                    filter[key+'__icontains']=value
                else: 
                    filter[key]=value
        nodos=[2,3,4,5]
        filter['nivel_jerarquico__in'] = nodos
        filter['solicitable_vivero'] = True
        filter['cod_tipo_bien'] = 'C'
        bien_especial=CatalogoBienes.objects.filter(**filter)
        filter['visible_solicitudes']= True
        filter['nro_elemento_bien']=None
        bien_normal=CatalogoBienes.objects.filter(**filter)
        list_normal=[bien.id_bien for bien in bien_normal]
        list_false=[]
        for item in bien_especial:
            if item.nivel_jerarquico == 5:
                if item.visible_solicitudes == False and item.solicitable_vivero == True:
                    bien_padre_nodo4 = CatalogoBienes.objects.filter(id_bien=item.id_bien_padre.id_bien).first()
                    if bien_padre_nodo4.visible_solicitudes == False and bien_padre_nodo4.solicitable_vivero == True:
                        bien_padre_nodo3 = CatalogoBienes.objects.filter(id_bien=bien_padre_nodo4.id_bien_padre.id_bien).first()
                        if bien_padre_nodo3.visible_solicitudes == False and bien_padre_nodo3.solicitable_vivero == True:
                            bien_padre_nodo2=CatalogoBienes.objects.filter(id_bien=bien_padre_nodo3.id_bien_padre.id_bien).first()
                            if bien_padre_nodo2.visible_solicitudes == False and bien_padre_nodo2.solicitable_vivero == True:
                                list_false.append(item.id_bien)
        list_normal.extend(list_false)
        bien_final=CatalogoBienes.objects.filter(id_bien__in=list_normal)
        serializador=self.serializer_class(bien_final,many=True)
        if bien_final:
            return Response({'success':True,'detail':'Se encontró elementos','detail':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'No se encontró elementos','detail':bien_final},status=status.HTTP_404_NOT_FOUND)
    
class GetBienSolicitableVivero(generics.ListAPIView):
    serializer_class=CatalogoBienesSerializer
    queryset=CatalogoBienes.objects.all()
    def get(self,request):
        if not request.query_params.items():
            return Response({'success': False, 'detail': 'Debe ingresar el parámetro de búsqueda', 'detail':[]}, status=status.HTTP_404_NOT_FOUND) 
        filter={}
        nodos=[2,3,4,5]
        filter['nivel_jerarquico__in'] = nodos
        filter['codigo_bien']=request.query_params.get('codigo_bien')
        filter['solicitable_vivero'] = True
        filter['cod_tipo_bien'] = 'C'
        filter['nro_elemento_bien']=None
        bien_especial=CatalogoBienes.objects.filter(**filter)
        filter['visible_solicitudes']= True
        bien_normal=CatalogoBienes.objects.filter(**filter)
        list_normal=[bien.id_bien for bien in bien_normal]
        list_false=[]
        for item in bien_especial:
            if item.nivel_jerarquico == 5:
                if item.visible_solicitudes == False and item.solicitable_vivero == True:
                    bien_padre_nodo4 = CatalogoBienes.objects.filter(id_bien=item.id_bien_padre.id_bien).first()
                    if bien_padre_nodo4.visible_solicitudes == False and bien_padre_nodo4.solicitable_vivero == True:
                        bien_padre_nodo3 = CatalogoBienes.objects.filter(id_bien=bien_padre_nodo4.id_bien_padre.id_bien).first()
                        if bien_padre_nodo3.visible_solicitudes == False and bien_padre_nodo3.solicitable_vivero == True:
                            bien_padre_nodo2=CatalogoBienes.objects.filter(id_bien=bien_padre_nodo3.id_bien_padre.id_bien).first()
                            if bien_padre_nodo2.visible_solicitudes == False and bien_padre_nodo2.solicitable_vivero == True:
                                list_false.append(item.id_bien)
        list_normal.extend(list_false)
        bien_final=CatalogoBienes.objects.filter(id_bien__in=list_normal)
        serializador=self.serializer_class(bien_final,many=True)
        if bien_final:
            return Response({'success':True,'detail':'Se encontró elementos','detail':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'No se encontró elementos','detail':bien_final},status=status.HTTP_404_NOT_FOUND)
    
class FiltroVisibleBySolicitud(generics.ListAPIView):
    serializer_class=CatalogoBienesSerializer
    queryset=CatalogoBienes.objects.all()
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','codigo_bien']:
                filter[key+'__icontains']=value
        nodos=[2,3,4,5]
        filter['nivel_jerarquico__in'] = nodos
        filter['nro_elemento_bien']=None
        bien_especial=CatalogoBienes.objects.filter(**filter)
        # filter['nivel_jerarquico__in'] = nodos
        filter['visible_solicitudes']= True
        bien_normal=CatalogoBienes.objects.filter(**filter)
        list_normal=[bien.id_bien for bien in bien_normal]
        list_false=[]
        for item in bien_especial:
            if item.nivel_jerarquico==5:
                if item.visible_solicitudes==False:
                    bien_padre_nodo4=CatalogoBienes.objects.filter(id_bien=item.id_bien_padre.id_bien).first()
                    if bien_padre_nodo4.visible_solicitudes==False:
                        bien_padre_nodo3=CatalogoBienes.objects.filter(id_bien=bien_padre_nodo4.id_bien_padre.id_bien).first()
                        if bien_padre_nodo3.visible_solicitudes==False:
                            bien_padre_nodo2=CatalogoBienes.objects.filter(id_bien=bien_padre_nodo3.id_bien_padre.id_bien).first()
                            if bien_padre_nodo2.visible_solicitudes==False:
                                list_false.append(item.id_bien)
        list_normal.extend(list_false)
        bien_final=CatalogoBienes.objects.filter(id_bien__in=list_normal)
        serializador=self.serializer_class(bien_final,many=True)
        if bien_final:
            return Response({'success':True,'detail':'Se encontró elementos','detail':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'No se encontró elementos','detail':bien_final},status=status.HTTP_404_NOT_FOUND)

class GetVisibleBySolicitud(generics.ListAPIView):
    serializer_class=CatalogoBienesSerializer
    queryset=CatalogoBienes.objects.all()
    def get(self,request):
        
        if not request.query_params.items():
            return Response({'success': False, 'detail': 'Debe ingresar el parámetro de búsqueda', 'detail':[]}, status=status.HTTP_404_NOT_FOUND) 
        filter={}
        filter['codigo_bien']=request.query_params.get('codigo_bien')
        nodos=[2,3,4,5]
        filter['nivel_jerarquico__in'] = nodos
        filter['nro_elemento_bien']=None
        bien_especial=CatalogoBienes.objects.filter(**filter)
        filter['visible_solicitudes']= True
        bien_normal=CatalogoBienes.objects.filter(**filter)
        list_normal=[bien.id_bien for bien in bien_normal]
        list_false=[]
        for item in bien_especial:
            if item.nivel_jerarquico==5:
                if item.visible_solicitudes==False:
                    bien_padre_nodo4=CatalogoBienes.objects.filter(id_bien=item.id_bien_padre.id_bien).first()
                    if bien_padre_nodo4.visible_solicitudes==False:
                        bien_padre_nodo3=CatalogoBienes.objects.filter(id_bien=bien_padre_nodo4.id_bien_padre.id_bien).first()
                        if bien_padre_nodo3.visible_solicitudes==False:
                            bien_padre_nodo2=CatalogoBienes.objects.filter(id_bien=bien_padre_nodo3.id_bien_padre.id_bien).first()
                            if bien_padre_nodo2.visible_solicitudes==False:
                                list_false.append(item.id_bien)
        list_normal.extend(list_false)
        bien_final=CatalogoBienes.objects.filter(id_bien__in=list_normal)
        serializador=self.serializer_class(bien_final,many=True)
        if bien_final:
            return Response({'success':True,'detail':'Se encontró elementos','detail':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'No se encontró elementos','detail':bien_final},status=status.HTTP_404_NOT_FOUND)


def id_responsable(request):
    data = request.data
    id_responsable = data['id_responsable']
    try:
        responsable = Personas.objects.get(id_persona=id_responsable)   
    except:
        return Response({'success':False,'detail':'No existe ninguna persona correspondiente al id del funcionario responsable de la unidad'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        unidad_org_responsable = UnidadesOrganizacionales.objects.get(id_unidad_org=responsable.id_unidad_org)
    except:
        return Response({'success':False, 'detail':'La persona responsable no tiene esta unidad organizacional asignada'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        solicitante = Personas.objects.get(id_persona=data['id_PersonaSolicita'])   
    except:
        return Response({'success':False,'detail':'No existe ninguna persona correspondiente al id del funcionario solicitante de la unidad'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        unidad_org_solicitante = UnidadesOrganizacionales.objects.get(id_unidad_org=solicitante.id_unidad_org)
    except:
        return Response({'success':False, 'detail':'La persona solicitante no tiene esta unidad organizacional asignada'},status=status.HTTP_400_BAD_REQUEST)
    if unidad_org_responsable.id_nivel_organigrama < unidad_org_solicitante.id_nivel_organigrama:
        pass
        lista_de_jerarquia = []
        nivel =unidad_org_solicitante
        for i in range(unidad_org_responsable.orden_nivel,unidad_org_solicitante.orden_nivel):

            nivel = UnidadesOrganizacionales.objects.get(id_unidad_org_padre=nivel.id_unidad_org_padre)
          

    else:
        return Response({'success':False,'detail':'El nivel de organigrama del responsable es mayor o igual el solicitante'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_orgchart_tree(request,pk):
    orgchart_list=[]
    try:
        persona = Personas.objects.get(id_persona=int(pk))
    except:
        return Response({'success':False,'detail':'No existe la persona con el id = '+pk},status=status.HTTP_400_BAD_REQUEST)    
    try:
        user = User.objects.get(persona=pk)
    except:
        return Response({'success':False,'detail':'No existe usuario asignado a esta persona'}, status=status.HTTP_400_BAD_REQUEST)
    if user.tipo_usuario != 'I':
        return Response({'success':False,'detail':'Su tipo de usuario no corresponde con el esperado para esta consulta'},status=status.HTTP_400_BAD_REQUEST)
    try:
        unidad_organizacional = UnidadesOrganizacionales.objects.get(id_unidad_organizacional=persona.id_unidad_organizacional_actual.id_unidad_organizacional)
    except:
        return Response({'success':False,'detail':'La persona no tiene ninguna unidad organizacional asignada'},status=status.HTTP_400_BAD_REQUEST)
    orgchart_list.append(unidad_organizacional)
    nivel = NivelesOrganigrama.objects.get(id_nivel_organigrama=unidad_organizacional.id_nivel_organigrama.id_nivel_organigrama).orden_nivel
    
    
    print(nivel)
    while(nivel>1):
        unidad_organizacional = UnidadesOrganizacionales.objects.get(id_unidad_organizacional=unidad_organizacional.id_unidad_org_padre.id_unidad_organizacional)
        orgchart_list.append(unidad_organizacional)
        nivel = NivelesOrganigrama.objects.get(id_nivel_organigrama=unidad_organizacional.id_nivel_organigrama.id_nivel_organigrama).orden_nivel
    
    serializer = UnidadesGetSerializer(orgchart_list,many=True)
    return Response(serializer.data)
    

class CreateSolicitud(generics.UpdateAPIView):
    serializer_class = CrearSolicitudesPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    serializer_item_solicitud = CrearItemsSolicitudConsumiblePostSerializer
    
    def put(self, request, *args, **kwargs):
        # SE OBTIENEN LOS DATOS DE LA SOLICITUD DEL JSON
        datos_ingresados = request.data
        info_solicitud = datos_ingresados['info_solicitud']
        items_solicitud = datos_ingresados['items_solicitud']
        valores_creados_detalles = []
        user_logeado = request.user
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'detail':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        if len(items_solicitud) <= 0:
            return Response({'success':False,'detail':'La solicitud debe tener items'},status=status.HTTP_404_NOT_FOUND)
        if info_solicitud['id_solicitud_consumibles'] == None:
            bandera_actualizar = False
        else:
            instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=info_solicitud['id_solicitud_consumibles']).first()
            if not instancia_solicitud:
                return Response({'success':False,'detail':'Si desea actualizar una solicitud, ingrese un id de solicitud de consumibles válido'},status=status.HTTP_404_NOT_FOUND)
            else:
                instancia_solicitud_previous = copy.copy(instancia_solicitud)
                bandera_actualizar = True
        
        # ASIGNACIÓN DE DATOS POR DEFECTO A LA TABLA SOLICITUDES
        info_solicitud['fecha_solicitud'] = str(date.today())
        info_solicitud['id_persona_solicita'] = user_logeado.persona.id_persona
        if user_logeado.persona.id_unidad_organizacional_actual == None:
            return Response({'success':False,'detail':'El usuario solicitante debe tener asignada una unidad organizacional' },status=status.HTTP_404_NOT_FOUND)
        info_solicitud['id_unidad_org_del_solicitante'] = user_logeado.persona.id_unidad_organizacional_actual.id_unidad_organizacional
        info_solicitud['solicitud_abierta'] = True
        solicitudes_existentes = SolicitudesConsumibles.objects.all()
        bienes_repetidos = [i['id_bien'] for i in items_solicitud]
        unidad_para_la_que_solicita = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = info_solicitud['id_unidad_para_la_que_solicita']).values().first()
        if info_solicitud['id_funcionario_responsable_unidad'] != None and info_solicitud['id_funcionario_responsable_unidad'] != '':
            funcionario_responsable = Personas.objects.filter(id_persona = info_solicitud['id_funcionario_responsable_unidad']).first()
            if not funcionario_responsable:
                return Response({'success':False,'detail':'El funcionario responsable no existe' },status=status.HTTP_404_NOT_FOUND)
            if funcionario_responsable.id_unidad_organizacional_actual == None:
                return Response({'success':False,'detail':'El funcionario responsable debe tener asignada una unidad organizacional' },status=status.HTTP_404_NOT_FOUND)
            if user_logeado.persona.id_unidad_organizacional_actual.id_unidad_organizacional == funcionario_responsable.id_unidad_organizacional_actual.id_unidad_organizacional:
                return Response({'success':False,'detail':'El funcionario responsable no puede ser de la misma unidad organizacional del que solicita' },status=status.HTTP_404_NOT_FOUND)
            info_solicitud['id_unidad_org_del_responsable'] = funcionario_responsable.id_unidad_organizacional_actual.id_unidad_organizacional
        else:
            info_solicitud['id_unidad_org_del_responsable'] = None
        # VALIDACIONES PRIMARIAS        
        if not unidad_para_la_que_solicita:
            return Response({'success':False,'detail':'La unidad organizacional ingresada no existe'},status=status.HTTP_404_NOT_FOUND)
        if len(bienes_repetidos) != len(set(bienes_repetidos)):
            return Response({'success':False,'detail':'Solo puede ingresar una vez un bien en una solicitud' },status=status.HTTP_404_NOT_FOUND)
        # ASIGNACIÓN DEL NÚMERO DE SOLICITUD
        info_solicitud['es_solicitud_de_conservacion'] = False
        
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
                        return Response({'success':False,'detail':'El item (' + str(instancia_item.id_item_solicitud_consumible) + ') no tiene relación con la solicitud' },status=status.HTTP_404_NOT_FOUND)
            bien = CatalogoBienes.objects.filter(id_bien = i['id_bien']).first()
            if not bien:
                return Response({'success':False,'detail':'El bien (' + i['id_bien'] + ') no existe' },status=status.HTTP_404_NOT_FOUND)
            if bien.nivel_jerarquico > 5 or bien.nivel_jerarquico < 2:
                return Response({'success':False,'detail':'El bien (' + bien.nombre + ') no es de nivel 5' },status=status.HTTP_404_NOT_FOUND)
            if bien.cod_tipo_bien != 'C':
                return Response({'success':False,'detail':'El bien (' + bien.nombre + ') no es de consumo' },status=status.HTTP_404_NOT_FOUND)
            if not str(i['cantidad']).isdigit():
                return Response({'success':False,'detail':'La cantidad debe ser un número entero' },status=status.HTTP_404_NOT_FOUND)
            if not str(i['nro_posicion']).isdigit():
                return Response({'success':False,'detail':'El número de posición debe ser un número entero' },status=status.HTTP_404_NOT_FOUND)
            # unidad_de_medida = UnidadesMedida.objects.filter(id_unidad_medida = i['id_unidad_medida']).first()
            # if not unidad_de_medida:
            #     return Response({'success':False,'detail':'La unidad de medida (' + unidad_de_medida.nombre + ') no existe' },status=status.HTTP_404_NOT_FOUND)
            i['id_unidad_medida'] = bien.id_unidad_medida.id_unidad_medida
        aux_nro_posicion = [i['nro_posicion'] for i in items_solicitud]

        if len(aux_nro_posicion) != len(set(aux_nro_posicion)):
            return Response({'success':False,'detail':'Los números de posición deben ser diferentes entre ellos' },status=status.HTTP_404_NOT_FOUND)
        
        if str(user_logeado.persona.id_unidad_organizacional_actual.cod_tipo_unidad) == 'AS' or str(user_logeado.persona.id_unidad_organizacional_actual.cod_tipo_unidad) == 'AP':
            instancia_nivel_1 = NivelesOrganigrama.objects.filter(id_nivel_organigrama = 1).first()
            unidad_padre_de_todos = UnidadesOrganizacionales.objects.filter(id_nivel_organigrama = instancia_nivel_1).first()
            padre_de_todos = Personas.objects.filter(id_unidad_organizacional_actual = unidad_padre_de_todos).first()
            if user_logeado.persona.id_unidad_organizacional_actual.id_unidad_organizacional != info_solicitud['id_unidad_para_la_que_solicita']:
                return Response({'success':False,'detail':'Un usuario de una unidad de apoyo o asesor solo le puede hacer solicitudes a la misma unidad a la que pertenece' },status=status.HTTP_404_NOT_FOUND)

            if (info_solicitud['id_funcionario_responsable_unidad'] != padre_de_todos.id_persona and info_solicitud['id_funcionario_responsable_unidad'] != '' and info_solicitud['id_funcionario_responsable_unidad'] != None) or info_solicitud['id_funcionario_responsable_unidad'] == user_logeado.persona.id_persona:
                return Response({'success':False,'detail':'El usuario supervisor no puede ser el mismo usuario que solicita, el funcionario supervisor solo puede ser de unidad organizacional nivel 1' },status=status.HTTP_404_NOT_FOUND)
        # VALIDACIÓN DE LA LINEA DEL ORGANIGRAMA A LA QUE PERTENECE EL USUARIO SOLICITANTE Y EL USUARIO SUPERVISOR DEL SOLICITANTE
        else:
            if int(info_solicitud['id_funcionario_responsable_unidad']) == user_logeado.persona.id_persona:
                return Response({'success':False,'detail':'El usuario quien solicita no puede ser el supervisor' },status=status.HTTP_404_NOT_FOUND)
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
                return Response({'success':False,'detail':'La unidad organizacional para la que solicita no pertenece a la linea del organigrama a la que pertenece el solicitante'},status=status.HTTP_404_NOT_FOUND)
            
            if not funcionario_responsable.id_unidad_organizacional_actual.nombre in unidades_iguales_y_arriba or funcionario_responsable.id_unidad_organizacional_actual.nombre == None:
                return Response({'success':False,'detail':'La persona que ingresó como responsable no es ningún superior de la persona que solicita'},status=status.HTTP_404_NOT_FOUND)
        # Creacion de solicitudes
        if bandera_actualizar == False:
            if solicitudes_existentes:
                numero_solicitudes_no_conservacion = [i.nro_solicitud_por_tipo for i in solicitudes_existentes if i.es_solicitud_de_conservacion == False]
                if len(numero_solicitudes_no_conservacion) > 0:
                    info_solicitud['nro_solicitud_por_tipo'] = max(numero_solicitudes_no_conservacion) + 1
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
                        return Response({'success':False,'detail':'Uno de los id de los items no es válido'},status=status.HTTP_404_NOT_FOUND)
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
            
            return Response({'success':True,'detail':'Solicitud actualizada con éxito', 'Numero solicitud' : info_solicitud["nro_solicitud_por_tipo"]},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'Solicitud registrada con éxito', 'Numero solicitud' : info_solicitud["nro_solicitud_por_tipo"]},status=status.HTTP_200_OK)

class GetSolicitudesPendentesPorAprobar(generics.ListAPIView):
# ESTA FUNCIONALIDAD PERMITE LISTAR LAS SOLICITUDES PENDIENTES DE APORVACIÓN PORL SUPERVISOR DESIGNADO
    serializer_class = CrearSolicitudesPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    def get(self, request, tipodocumento, numerodocumento):
        persona_responsable = Personas.objects.get(Q(tipo_documento=tipodocumento) & Q(numero_documento=numerodocumento) & Q(tipo_persona='N'))
        usuario = User.objects.filter(persona = persona_responsable.id_persona).first()
        if not usuario:
            return Response({'success':False,'detail':'Debe ingresar un usuario válido'},status=status.HTTP_400_BAD_REQUEST)        
        solicitudes_por_aprobar = SolicitudesConsumibles.objects.filter(Q(id_funcionario_responsable_unidad=persona_responsable.id_persona) & Q(revisada_responsable = False))
        serializer = self.serializer_class(solicitudes_por_aprobar, many=True)
        return Response({'success':True,'detail':serializer.data, },status=status.HTTP_200_OK)

class GetSolicitudesById_Solicitudes(generics.ListAPIView):
    # ESTA FUNCIONALIDAD PERMITE CONSULTAR SOLICITUDES DE BIENES DE CONSUMO POR ID_SOLICITUDES
    serializer_class = CrearSolicitudesPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    serializer_item_solicitud = CrearItemsSolicitudConsumiblePostSerializer
    
    def get(self, request, id_solicitud):
        intancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=id_solicitud).first()
        if not intancia_solicitud:
            return Response({'success':False,'detail':'Ingrese un ID válido'},status=status.HTTP_400_BAD_REQUEST)
        info_items = ItemsSolicitudConsumible.objects.filter(id_solicitud_consumibles=intancia_solicitud.id_solicitud_consumibles)
        serializer_info_solicitud = self.serializer_class(intancia_solicitud)
        serializer_items_solicitud = self.serializer_item_solicitud(info_items, many=True)
        datos_salida = {'info_solicitud' : serializer_info_solicitud.data, 'info_items' : serializer_items_solicitud.data}
        return Response({'success':True,'detail':datos_salida, },status=status.HTTP_200_OK)

class GetNroDocumentoSolicitudesBienesConsumo(generics.ListAPIView):
    # ESTA FUNCIONALIDAD PERMITE CONSULTAR EL ÚLTIMO NÚMERO DE DOCUMENTO DE LA CREACIÓN DE SOLICITUDES
    serializer_class = CrearSolicitudesPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    def get(self, request):
        nro_solicitud = SolicitudesConsumibles.objects.filter(es_solicitud_de_conservacion=False).order_by('nro_solicitud_por_tipo').last()
        return Response({'success':True,'Número de solicitud':nro_solicitud.nro_solicitud_por_tipo + 1, },status=status.HTTP_200_OK)
    
class RevisionSolicitudBienConsumosPorSupervisor(generics.UpdateAPIView):
    serializer_class = CrearSolicitudesPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    def put(self, request, id_solicitud,*args, **kwargs):
        datos_ingresados = request.data
        user_logeado = request.user
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'detail':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        if not str(id_solicitud).isdigit():
            return Response({'success':False,'detail':'El Id_solicitud debe ser un número entero' },status=status.HTTP_404_NOT_FOUND)
        if datos_ingresados['estado_aprobacion_responsable'] != 'A' and datos_ingresados['estado_aprobacion_responsable'] != 'R':
            return Response({'success':False,'detail':'El estado de aprobación debe ser A o R'},status=status.HTTP_404_NOT_FOUND)
        if len(datos_ingresados['justificacion_rechazo_responsable']) > 255:
            return Response({'success':False,'detail':'El número máximo de caracteres de la justificación es de 255'},status=status.HTTP_404_NOT_FOUND)
        
        instance = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=int(id_solicitud)).first()
        if not instance:
            return Response({'success':False,'detail':'Debe de ingresar un id de solicitud válido'},status=status.HTTP_404_NOT_FOUND)
        if instance.revisada_responsable == True:
            return Response({'success':False,'detail':'Esta solicitud ya ha sido aprobada'},status=status.HTTP_404_NOT_FOUND)
        if instance.id_funcionario_responsable_unidad.id_persona != user_logeado.persona.id_persona:
            return Response({'success':False,'detail':'Usted no es el funcionario responsable de esta solicitud'},status=status.HTTP_404_NOT_FOUND)
        instance.estado_aprobacion_responsable = datos_ingresados['estado_aprobacion_responsable']
        instance.revisada_responsable = True
        instance.fecha_aprobacion_responsable = str(date.today())
        if datos_ingresados['estado_aprobacion_responsable'] == 'R':
            instance.solicitud_abierta = False
            instance.justificacion_rechazo_responsable = datos_ingresados['justificacion_rechazo_responsable']
            instance.fecha_cierre_solicitud = str(date.today())
        instance.save()
        
        return Response({'success':True,'Número de solicitud':'Solicitud procesada con éxito', },status=status.HTTP_200_OK)
    
class SolicitudesPendientesDespachar(generics.ListAPIView):
    serializer_class = CrearSolicitudesPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    def get(self, request):
        pendientes_por_despachar = SolicitudesConsumibles.objects.filter(Q(estado_aprobacion_responsable='A') & Q(gestionada_almacen=False))
        serializer = self.serializer_class(pendientes_por_despachar, many=True)
        return Response({'success':True,'Solicitudes pendientes por despahcar':serializer.data, },status=status.HTTP_200_OK)

class RechazoSolicitudesBienesAlmacen(generics.UpdateAPIView):
    serializer_class = CrearSolicitudesPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    def put(self, request, id_solicitud,*args, **kwargs):
        datos_ingresados = request.data
        user_logeado = request.user
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'detail':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        if not str(id_solicitud).isdigit():
            return Response({'success':False,'detail':'El Id_solicitud debe ser un número entero' },status=status.HTTP_404_NOT_FOUND)
        if datos_ingresados['rechazada_almacen'] != True:
            return Response({'success':False,'detail':'La solicitud no fue rechazada, para rechazarla debe ingresar true'},status=status.HTTP_404_NOT_FOUND)
        if len(datos_ingresados['justificacion_rechazo_almacen']) > 255:
            return Response({'success':False,'detail':'El número máximo de caracteres de la justificación es de 255'},status=status.HTTP_404_NOT_FOUND)
        
        instance = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=int(id_solicitud)).first()
        if not instance:
            return Response({'success':False,'detail':'Debe de ingresar un id de solicitud válido'},status=status.HTTP_404_NOT_FOUND)
        if instance.revisada_responsable != True:
            return Response({'success':False,'detail':'La solicitud debe haber sido aprobada por el funcionario supervisor'},status=status.HTTP_404_NOT_FOUND)
        if instance.gestionada_almacen == True:
            return Response({'success':False,'detail':'La solicitud ya fue procesada por almacen'},status=status.HTTP_404_NOT_FOUND)
        
        instance.rechazada_almacen = datos_ingresados['rechazada_almacen']
        instance.justificacion_rechazo_almacen = datos_ingresados['justificacion_rechazo_almacen']
        instance.gestionada_almacen = True
        instance.fecha_rechazo_almacen = str(date.today())
        instance.fecha_cierre_solicitud = str(date.today())
        instance.solicitud_abierta = False
        instance.save()
        
        return Response({'success':True,'detail':'Solicitud procesada con éxito', },status=status.HTTP_200_OK)

class AnularSolicitudesBienesConsumo(generics.UpdateAPIView):
    serializer_class = CrearSolicitudesPostSerializer
    queryset=SolicitudesConsumibles.objects.all()
    
    def put(self, request, id_solicitud,*args, **kwargs):
        datos_ingresados = request.data
        user_logeado = request.user
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'detail':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        if not str(id_solicitud).isdigit():
            return Response({'success':False,'detail':'El Id_solicitud debe ser un número entero' },status=status.HTTP_404_NOT_FOUND)
        
        instance = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=int(id_solicitud)).first()
        if not instance:
            return Response({'success':False,'detail':'Debe de ingresar un id de solicitud válido'},status=status.HTTP_404_NOT_FOUND)
        if instance.id_persona_solicita.id_persona != user_logeado.persona.id_persona:
            return Response({'success':False,'detail':'La solicitud solo puede ser anulada por quien la realizó'},status=status.HTTP_404_NOT_FOUND)
        if instance.solicitud_abierta == False:
            return Response({'success':False,'detail':'La solicitud ya fue cerrada, no es posible anularla'},status=status.HTTP_404_NOT_FOUND)
        if datos_ingresados['solicitud_anulada_solicitante'] != True:
            return Response({'success':False,'detail':'La solicitud no fue anulada, para anularla debe ingresar true'},status=status.HTTP_404_NOT_FOUND)

        instancia_items_solicitud_eliminar = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=instance.id_solicitud_consumibles))
        
        instance.justificacion_anulacion_solicitante = datos_ingresados['justificacion_anulacion_solicitante']
        instance.solicitud_anulada_solicitante = datos_ingresados['solicitud_anulada_solicitante']
        instance.fecha_anulacion_solicitante = str(date.today())
        instance.fecha_cierre_solicitud = str(date.today())
        instance.solicitud_abierta = False
        instance.save()
        valores_eliminados_detalles = [{'nombre':i.id_bien.nombre} for i in instancia_items_solicitud_eliminar]
        instancia_items_solicitud_eliminar.delete()
        descripcion = {"numero_entrada_almacen": instance.nro_solicitud_por_tipo, "fecha_anulacion": instance.fecha_anulacion_solicitante}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 35,
            "cod_permiso": "BO",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        return Response({'success':True,'detail':'Solicitud procesada con éxito', },status=status.HTTP_200_OK)

class SearchFuncionarioResponsable(generics.ListAPIView):
    serializer_class=PersonasSerializer
    queryset=Personas.objects.all()
    permission_classes=[IsAuthenticated]
    
    def get(self, request):
        tipo_documento = request.query_params.get('tipo_documento')
        numero_documento = request.query_params.get('numero_documento')
        
        if (not tipo_documento or tipo_documento=='') and (not numero_documento or numero_documento==''):
            return Response({'success':False, 'detail':'Debe ingresar mínimo los parámetros de tipo documento y número de documento'}, status=status.HTTP_400_BAD_REQUEST)
        
        filter={}
        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento','id_unidad_organizacional_actual']:
                if value != '':
                    filter[key]=value
        
        persona = Personas.objects.filter(**filter).first()
        if not persona:
            return Response({'success':True, 'detail':'No se encontraron resultados', 'detail':{}}, status=status.HTTP_200_OK)
        
        funcionario_persona=ClasesTerceroPersona.objects.filter(id_persona=persona.id_persona, id_clase_tercero=2).first()
        if funcionario_persona:
            serializador_persona = self.serializer_class(persona)
            return Response({'success':True, 'detail':'Se encontró el funcionario responsable', 'detail':serializador_persona.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'La persona no es un funcionario', 'detail':{}}, status=status.HTTP_200_OK)