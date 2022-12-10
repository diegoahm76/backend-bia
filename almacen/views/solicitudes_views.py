from almacen.models.bienes_models import CatalogoBienes
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from almacen.serializers.organigrama_serializers import UnidadesOrganizacionales, UnidadesGetSerializer
from rest_framework import generics,status
from rest_framework.response import Response
from almacen.models import UnidadesOrganizacionales, NivelesOrganigrama
from seguridad.models import Personas, User
from rest_framework.decorators import api_view
from seguridad.utils import Util
from seguridad.models import (
    Personas,
    User
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


class SearchVisibleBySolicitud(generics.ListAPIView):
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
            return Response({'success':True,'detail':'Se encontró elementos','data':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'No se encontró elementos','data':bien_final},status=status.HTTP_404_NOT_FOUND)



def id_responsable(request):
    data = request.data
    id_responsable = data['id_responsable']
    try:
        responsable = Personas.objects.get(id_persona=id_responsable)   
    except:
        return Response({'Success':False,'detail':'no existe ninguna persona correspondiente al id del funcionario responsable de la unidad'})
    try:
        unidad_org_responsable = UnidadesOrganizacionales.objects.get(id_unidad_org=responsable.id_unidad_org)
    except:
        return Response({'Success':False, 'Detail':'la persona responsable no tiene esta unidad organizacional asignada'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        solicitante = Personas.objects.get(id_persona=data['id_PersonaSolicita'])   
    except:
        return Response({'Success':False,'detail':'no existe ninguna persona correspondiente al id del funcionario solicitante de la unidad'})
    try:
        unidad_org_solicitante = UnidadesOrganizacionales.objects.get(id_unidad_org=solicitante.id_unidad_org)
    except:
        return Response({'Success':False, 'Detail':'la persona solicitante no tiene esta unidad organizacional asignada'},status=status.HTTP_400_BAD_REQUEST)
    if unidad_org_responsable.id_nivel_organigrama < unidad_org_solicitante.id_nivel_organigrama:
        pass
        lista_de_jerarquia = []
        nivel =unidad_org_solicitante
        for i in range(unidad_org_responsable.orden_nivel,unidad_org_solicitante.orden_nivel):

            nivel = UnidadesOrganizacionales.objects.get(id_unidad_org_padre=nivel.id_unidad_org_padre)
          

    else:
        return Response({'Success':False,'Detail':'el nivel de organigrama del responsable es mayor o igual el solicitante'})


@api_view(['GET'])
def get_orgchart_tree(request,pk):
    orgchart_list=[]
    try:
        persona = Personas.objects.get(id_persona=int(pk))
    except:
        return Response({'Success':False,'Detail':'no existe la persona con el id = '+pk},status=status.HTTP_400_BAD_REQUEST)    
    try:
        user = User.objects.get(persona=pk)
    except:
        return Response({'Success':False,'Detail':'no existe usuario asignado a esta persona'}, status=status.HTTP_400_BAD_REQUEST)
    if user.tipo_usuario != 'I':
        return Response({'Success':False,'Detail':'su tipo de usuario no corresponde con el esperado para esta consulta'},status=status.HTTP_400_BAD_REQUEST)
    try:
        print(persona.id_unidad_organizacional_actual.id_unidad_organizacional)
        unidad_organizacional = UnidadesOrganizacionales.objects.get(id_unidad_organizacional=persona.id_unidad_organizacional_actual.id_unidad_organizacional)
    except:
        return Response({'Success':False,'Detail':'la persona no tiene ninguna unidad organizacional asignada'})
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
        
        user_logeado = request.user
        info_solicitud['fecha_solicitud'] = str(date.today())
        info_solicitud['id_persona_solicita'] = user_logeado.persona.id_persona
        info_solicitud['id_unidad_org_del_solicitante'] = user_logeado.persona.id_unidad_organizacional_actual.id_unidad_organizacional
        info_solicitud['solicitud_abierta'] = True
        info_solicitud['es_solicitud_de_conservacion'] = False
        solicitudes_existentes = SolicitudesConsumibles.objects.all()
        bienes_repetidos = [i['id_bien'] for i in items_solicitud]
        if len(bienes_repetidos) != len(set(bienes_repetidos)):
            return Response({'success':False,'data':'Solo puede ingresar una vez un bien en una solicitud' },status=status.HTTP_404_NOT_FOUND)
        if solicitudes_existentes:
            numero_solicitudes_no_conservacion = [i.nro_solicitud_por_tipo for i in solicitudes_existentes if i.es_solicitud_de_conservacion == False]
            info_solicitud['nro_solicitud_por_tipo'] = max(numero_solicitudes_no_conservacion) + 1
        else:
            info_solicitud['nro_solicitud_por_tipo'] = 1
        #numero_solicitudes_no_conservacion = [i.nro_solicitud_por_tipo for i in solicitudes_existentes if i.es_solicitud_de_conservacion == False]
        
        # SE CREAN ALGUNAS VARIABLES AUXILIARES
        unidades_organiacionales_misma_linea = []
        count = 0
        # VALIDACIONES ITEMS DE LA SOLICITUD
        for i in items_solicitud:
            bien = CatalogoBienes.objects.filter(id_bien = i['id_bien']).first
            if not bien:
                return Response({'success':False,'data':'El bien (' + bien.nombre + ') no existe' },status=status.HTTP_404_NOT_FOUND)
            if not str(i['cantidad']).isdigit():
                return Response({'success':False,'data':'La cantidad debe ser un número entero' },status=status.HTTP_404_NOT_FOUND)
            if not str(i['nro_posicion']).isdigit():
                return Response({'success':False,'data':'El número de posición debe ser un número entero' },status=status.HTTP_404_NOT_FOUND)
            unidad_de_medida = UnidadesMedida.objects.filter(id_unidad_medida = i['id_unidad_medida']).first()
            print("Unidad de medida", unidad_de_medida)
            if not unidad_de_medida:
                return Response({'success':False,'data':'La unidad de medida (' + unidad_de_medida.nombre + ') no existe' },status=status.HTTP_404_NOT_FOUND)

        aux_nro_posicion = [i['nro_posicion'] for i in items_solicitud]
         
        if len(aux_nro_posicion) != len(set(aux_nro_posicion)):
            return Response({'success':False,'data':'Los números de posición deben ser diferentes entre ellos' },status=status.HTTP_404_NOT_FOUND)
        
        # VALIDACIÓN DE LA LINEA DEL ORGANIGRAMA A LA QUE PERTENECE EL USUARIO SOLICITANTE Y EL USUARIO SUPERVISOR DEL SOLICITANTE
        aux_niveles_organigrama = NivelesOrganigrama.objects.all().values()
        
        niveles_organigrama = [i['orden_nivel'] for i in aux_niveles_organigrama]
        unidades_iguales_y_arriba = []
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
        
        unidades_arriba = user_logeado.persona.id_unidad_organizacional_actual.id_unidad_org_padre.nombre
        unidades_organiacionales_misma_linea.append(unidades_arriba)
        unidades_iguales_y_arriba.append(unidades_arriba)
        count = user_logeado.persona.id_unidad_organizacional_actual.id_unidad_org_padre.id_nivel_organigrama.orden_nivel - 1
        aux_menor = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = user_logeado.persona.id_unidad_organizacional_actual.id_unidad_org_padre.id_unidad_organizacional).first()
        unidades_organiacionales_misma_linea.append(aux_menor.id_unidad_org_padre.nombre)
        unidades_iguales_y_arriba.append(aux_menor.id_unidad_org_padre.nombre)
        while count >= 1:
            aux_menor = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = aux_menor.id_unidad_org_padre.id_unidad_organizacional).first()
            if aux_menor.id_unidad_org_padre:
                unidades_organiacionales_misma_linea.append(aux_menor.id_unidad_org_padre.nombre)
                unidades_iguales_y_arriba.append(aux_menor.id_unidad_org_padre.nombre)
            count = count - 1
        unidades_organiacionales_misma_linea = sorted(unidades_organiacionales_misma_linea)
        
        unidad_para_la_que_solicita = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = info_solicitud['id_unidad_para_la_que_solicita']).values().first()
        
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'data':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        if not unidad_para_la_que_solicita:
            return Response({'success':False,'data':'La unidad organizacional ingresada no existe'},status=status.HTTP_404_NOT_FOUND)
        if not unidad_para_la_que_solicita['nombre'] in unidades_organiacionales_misma_linea:
            return Response({'success':False,'data':'La unidad organizacional para la que solicita no pertenece a la linea del organigrama a la que pertenece el solicitante'},status=status.HTTP_404_NOT_FOUND)
        
        funcionario_responsable = Personas.objects.filter(id_persona = info_solicitud['id_funcionario_responsable_unidad']).first()
        info_solicitud['id_unidad_org_del_responsable'] = funcionario_responsable.id_unidad_organizacional_actual.id_unidad_organizacional
        if not funcionario_responsable.id_unidad_organizacional_actual.nombre in unidades_iguales_y_arriba or funcionario_responsable.id_unidad_organizacional_actual.nombre == None:
            return Response({'success':False,'data':'La persona que ingresó como responsable no es ningún superior de la persona que solicita'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=info_solicitud)
        serializer.is_valid(raise_exception=True)
        serializer.save()        
        dirip = Util.get_client_ip(request)
        print("Id_solicitud_bienes", str(serializer.data['id_solicitud_consumibles']))
        
        descripcion = {'id_solicitud_consumibles':str(serializer.data['id_solicitud_consumibles']), 'fecha_solicitud':str(info_solicitud['fecha_solicitud']), 'id_persona_solicita':str(info_solicitud['id_persona_solicita']), 'id_unidad_org_del_solicitante':str(info_solicitud['id_unidad_org_del_solicitante']), 'id_funcionario_responsable_unidad':str(info_solicitud['id_funcionario_responsable_unidad']), 'id_unidad_org_del_responsable':str(info_solicitud['id_unidad_org_del_responsable'])}
        valores_actualizados= None
        auditoria_data = {
            'id_usuario': user_logeado.id_usuario,
            'id_modulo': 35,
            'cod_permiso': 'CR',
            'subsistema': 'ALMA',
            'dirip': dirip,
            'descripcion': descripcion,
            'valores_actualizados': valores_actualizados
        }
        Util.save_auditoria(auditoria_data)
        
        for i in items_solicitud:
           i['id_solicitud_consumibles'] = serializer.data['id_solicitud_consumibles']
             
        serializer = self.serializer_item_solicitud(data=items_solicitud, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success':True,'data':'Solicitud registrada con éxito', 'Numero solicitud' : info_solicitud["nro_solicitud_por_tipo"]},status=status.HTTP_200_OK)
