from conservacion.utils import UtilConservacion
from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time, timedelta
from datetime import timezone
import copy
import json
import operator
import operator, itertools

from conservacion.models.solicitudes_models import (
    SolicitudesViveros,
    ItemSolicitudViveros
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.serializers.solicitudes_serializers import (
    GetNumeroConsecutivoSolicitudSerializer,
    GetSolicitudByNumeroSolicitudSerializer,
    GetUnidadOrganizacionalSerializer,
    CreateSolicitudViverosSerializer,
    GetBienByCodigoViveroSerializer,
    GetBienByFilterSerializer,
    DeleteItemsSolicitudSerializer
)
from conservacion.models.viveros_models import (
    Vivero
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales,
    NivelesOrganigrama
)
from seguridad.serializers.personas_serializers import (
    PersonasSerializer
)
from seguridad.models import (
    Personas,
    User
)

class GetNumeroConsecutivoSolicitudView(generics.RetrieveAPIView):
    serializer_class = GetNumeroConsecutivoSolicitudSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        solicitud_vivero = SolicitudesViveros.objects.all().order_by('-nro_solicitud').first()
        numero_inicial = 0
        if solicitud_vivero:
            numero_inicial = solicitud_vivero.nro_solicitud
        numero_consecutivo = numero_inicial + 1

        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': numero_consecutivo}, status=status.HTTP_200_OK)


class GetSolicitudByNumeroSolicitudView(generics.RetrieveAPIView):
    serializer_class = GetSolicitudByNumeroSolicitudSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, nro_solicitud):
        solicitud = SolicitudesViveros.objects.filter(nro_solicitud=nro_solicitud).first()
        if not solicitud:
            return Response({'success': False, 'detail': 'No existe ninguna solicitud con el numero ingresado'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(solicitud, many=False)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetUnidadOrganizacionalView(generics.RetrieveAPIView):
    serializer_class = GetUnidadOrganizacionalSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        persona_logeada = request.user.persona
        linea_jerarquica = UtilConservacion.get_linea_jerarquica(persona_logeada)
        serializer = self.serializer_class(linea_jerarquica, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetFuncionarioResponsableView(generics.GenericAPIView):
    serializer_class = PersonasSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id_unidad_organizacional, tipodocumento, numerodocumento):
        persona_logeada = request.user.persona

        #VALIDACIÓN SI EXISTE LA PERSONA ENVIADA
        user = User.objects.filter(persona__tipo_documento=tipodocumento, persona__numero_documento=numerodocumento).first()
        if not user:
            return Response({'success': False, 'detail': 'No existe o no tiene usuario creado el funcionario responsable seleccionado'}, status=status.HTTP_404_NOT_FOUND)
        
        #VALIDACIÓN QUE EL USUARIO SEA INTERNO
        if user.tipo_usuario != 'I':
            return Response({'success': False, 'detail': 'El funcionario responsable debe ser un usuario interno'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN SI ESA PERSONA ESTÁ ASOCIADA A UNA UNIDAD ORGANIZACIONAL
        if not user.persona.id_unidad_organizacional_actual:
            return Response({'success': False, 'detail': 'La persona seleccionada no se encuentra relacionada con ninguna unidad organizacional'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN SI LA PERSONA SE ENCUENTRA EN UNA UNIDAD DE UN ORGANIGRAMA ACTUAL
        if user.persona.id_unidad_organizacional_actual.id_organigrama.actual != True:
            return Response({'success': False, 'detail': 'El responsable seleccionado no pertenece a un organigrama actual'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN DE LINEA JERARQUICA SUPERIOR O IGUAL
        linea_jerarquica = UtilConservacion.get_linea_jerarquica_superior(persona_logeada)
        print(linea_jerarquica)

        lista_unidades_permitidas = [unidad.id_unidad_organizacional for unidad in linea_jerarquica]
        print(lista_unidades_permitidas)

        if user.persona.id_unidad_organizacional_actual.id_unidad_organizacional not in lista_unidades_permitidas:
            return Response({'success': False, 'detail': 'No se puede seleccionar una persona que no esté al mismo nivel o superior en la linea jerarquica'}, status=status.HTTP_403_FORBIDDEN)

        persona_serializer = self.serializer_class(user.persona, many=False)
        return Response({'success': True,'data': persona_serializer.data}, status=status.HTTP_200_OK)

class CreateSolicitudViverosView(generics.CreateAPIView):
    serializer_class = CreateSolicitudViverosSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        persona_logeada = request.user.persona

        #ASIGNACIÓN DE INFORMACIÓN EN JSON Y EN VARIABLES CORRESPONDIENTES
        data_solicitud = json.loads(request.data['data_solicitud'])
        data_items_solicitud = json.loads(request.data['data_items_solicitados'])
        data_solicitud['ruta_archivo_info_tecnico'] = request.FILES.get('ruta_archivo_tecnico')
        data_solicitud['id_persona_solicita'] = persona_logeada.id_persona
        data_solicitud['id_unidad_org_del_solicitante'] = persona_logeada.id_unidad_organizacional_actual.id_unidad_organizacional
        data_solicitud['fecha_solicitud'] = datetime.now()

        #VALIDACIÓN QUE LA PERSONA QUE HACE LA SOLICITUD ESTÉ ASOCIADA A UNA UNIDAD Y QUE SEA ACTUAL
        if not persona_logeada.id_unidad_organizacional_actual:
            return Response({'succcess': False, 'detail': 'La persona que hace la solicitud debe pertenecer a una unidad organizacional'}, status=status.HTTP_400_BAD_REQUEST)
        if persona_logeada.id_unidad_organizacional_actual.id_organigrama.actual != True:
            return Response({'succcess': False, 'detail': 'La unidad organizacional de la persona que hace la solicitud debe pertenecer a un organigrama actual'}, status=status.HTTP_400_BAD_REQUEST)
        
        #ASIGNACIÓN NÚMERO CONSECUTIVO
        ultima_solicitud = SolicitudesViveros.objects.all().order_by('-nro_solicitud').first()
        auxiliar = 0
        if ultima_solicitud:
            auxiliar = ultima_solicitud.nro_solicitud
        consecutivo = auxiliar + 1
        data_solicitud['nro_solicitud'] = consecutivo

        #VALIDACIÓN QUE EL VIVERO SELECCIONADO EXISTA
        vivero = Vivero.objects.filter(id_vivero=data_solicitud['id_vivero_solicitud']).first()
        if not vivero:
            return Response({'success': False, 'detail': 'El vivero seleccionado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        if vivero.fecha_cierre_actual != None:
            return Response({'success': False, 'detail': 'El vivero seleccionado no puede estar cerrado'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE LA UNIDAD PARA LA QUE SOLICITA ESTÉ DENTRO DE LA LINEA JERARQUICA DE LA PERSONA LOGEADA
        linea_jerarquica = UtilConservacion.get_linea_jerarquica(persona_logeada)
        linea_jerarquica_id = [unidad.id_unidad_organizacional for unidad in linea_jerarquica]
        if data_solicitud['id_unidad_para_la_que_solicita'] not in linea_jerarquica_id:
            return Response({'success': False, 'detail': 'La unidad seleccionada debe hacer parte de su linea jerarquica'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN PARA QUE LA UNIDAD DEL RESPONSABLE SEA DE MISMA O SUPERIOR NIVEL EN LA LINEA JERARQUICA
        linea_jerarquica = UtilConservacion.get_linea_jerarquica_superior(persona_logeada)
        linea_jerarquica_id = [unidad.id_unidad_organizacional for unidad in linea_jerarquica]
        if data_solicitud['id_unidad_org_del_responsable'] not in linea_jerarquica_id:
            return Response({'success': False, 'detail': 'La unidad del responsable debe hacer parte de su linea jerarquica superior o igual'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=data_solicitud, many=False)
        serializer.is_valid(raise_exception=True)
        solicitud_maestro = serializer.save()

        for item in data_items_solicitud:
            item['id_solicitud_viveros'] = solicitud_maestro.id_solicitud_vivero

        # AUDITORIA SOLICITUDES A VIVEROS
        valores_creados_detalles = []
        for bien in data_items_solicitud:
            valores_creados_detalles.append({'':''})

        descripcion = {"nombre_bien_sembrado": str(solicitud_maestro.nro_solicitud)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 60,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success': True, 'detail': 'Creación de solicitud exitosa', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
class GetBienByCodigoViveroView(generics.ListAPIView):
    serializer_class = GetBienByCodigoViveroSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = ['id_vivero', 'codigito_bien']

    def get(self, request, id_vivero, codigito_bien):
        #VALIDACIONES SOBRE LA EXISTENCIA DEL BIEN Y EL TIPO DE BIEN ENVIADO
        bienes = InventarioViveros.objects.filter(id_bien__codigo_bien=codigito_bien, id_vivero=id_vivero)
        if not bienes:
            return Response({'success': False, 'detail': 'El bien seleccionado no se encuentra relacionado al vivero seleccionado'}, status=status.HTTP_403_FORBIDDEN)
             
        if bienes[0].id_bien.solicitable_vivero != True:
            return Response({'success': False, 'detail': 'El bien seleccionado no es solicitable por vivero'}, status=status.HTTP_403_FORBIDDEN)
        
        if bienes[0].id_bien.cod_tipo_bien != 'C':
            return Response({'success': False, 'detail': 'El bien seleccionado no es consumible'}, status=status.HTTP_403_FORBIDDEN)
            
        if bienes[0].id_bien.cod_tipo_elemento_vivero == 'HE':
            return Response({'success': False, 'detail': 'El bien seleccionado debe ser de tipo insumo o material vegetal'}, status=status.HTTP_403_FORBIDDEN)

        if bienes[0].id_bien.cod_tipo_elemento_vivero=='MV' and bienes[0].id_bien.es_semilla_vivero==True:
            return Response({'success': False, 'detail': 'El bien seleccionado debe ser material vegetal que no sea semilla'}, status=status.HTTP_403_FORBIDDEN)

        if bienes[0].id_bien.cod_tipo_elemento_vivero == 'MV':

            #VALIDACIÓN QUE LOS BIENES ESTÉN EN ALGUN LOTE ETAPA DE DISTRIBUCIÓN O PRODUCCIÓN
            bien_in_inventario_no_germinacion = []
            for bien in bienes:
                if bien.cod_etapa_lote != 'G':
                    bien_in_inventario_no_germinacion.append(bien)

            if not bien_in_inventario_no_germinacion:
                return Response({'success': False, 'detail': 'El bien seleccionado no tiene lotes que cumplan las condiciones para ser solicitado'}, status=status.HTTP_403_FORBIDDEN) 

            #VALIDACIÓN QUE EL BIEN EN ALGÚN LOTE TENGA SALDO DISPONIBLE
            saldo_disponible = False
            for bien in bien_in_inventario_no_germinacion:
                bien.id_bien.saldo_disponible = UtilConservacion.get_saldo_disponible_solicitud_viveros(bien)
                if bien.id_bien.saldo_disponible > 0:
                    saldo_disponible = True
                    pass
            
            if saldo_disponible == False:
                return Response({'success': False, 'detail': 'El bien seleccionado no tiene ningun saldo disponible en viveros'}, status=status.HTTP_403_FORBIDDEN)
            
            bien = bien_in_inventario_no_germinacion[0].id_bien
        
        elif bienes[0].id_bien.cod_tipo_elemento_vivero == 'IN':

            #VALIDACIÓN QUE EL BIEN TENGA SALDO DISPONIBLE
            bien_in_inventario = bienes.first()
            bien = bien_in_inventario.id_bien
            bien.saldo_disponible = UtilConservacion.get_saldo_disponible_solicitud_viveros(bien_in_inventario)    
            if not bien.saldo_disponible > 0:
                return Response({'success': False, 'detail': 'El bien de tipo insumo no tiene cantidades disponibles para solicitar'}, status=status.HTTP_403_FORBIDDEN)
                         
        serializer = self.serializer_class(bien, many=False)
        data = serializer.data

        #ASIGNACIÓN DE NUEVOS NOMBRES
        if data['cod_tipo_elemento_vivero'] == 'IN':
            data['cod_tipo_elemento_vivero'] = 'Insumo'
        else:
            data['cod_tipo_elemento_vivero'] = 'Material Vegetal'
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': data}, status=status.HTTP_200_OK)
    

class GetBienByFiltrosView(generics.ListAPIView):
    serializer_class =  GetBienByFilterSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_vivero):
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success': False, 'detail': 'No se encontró ningún vivero con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        
        #CREACIÓN DE FILTROS SEGÚN QUERYPARAMS
        query_param = request.query_params.get('cod_tipo_elemento_vivero')
        if not query_param:
            return Response({'success': False, 'detail': 'Es obligatorio seleccionar un tipo de bien'}, status=status.HTTP_400_BAD_REQUEST)

        if query_param == 'IN':
            #CREACIÓN DE FILTRO
            filter = {}
            for key, value in request.query_params.items():
                if key in ['cod_tipo_elemento_vivero', 'codigo_bien', 'nombre']:
                    if key != 'cod_tipo_elemento_vivero':
                        filter[key + '__icontains'] = value
                    else:
                        filter[key] = value

            bienes_por_consumir = CatalogoBienes.objects.filter(cod_tipo_bien='C', nivel_jerarquico=5, solicitable_vivero=True, cod_tipo_elemento_vivero='IN')
            bienes_filtrados = bienes_por_consumir.filter(**filter)

            #ASIGNACIÓN DE INFORMACIÓN SI EL TIPO DE BIEN ES DE TIPO INSUMO
            for bien in bienes_filtrados:
                bien_in_inventario = InventarioViveros.objects.filter(id_bien=bien.id_bien, id_vivero=id_vivero).first()
                if bien_in_inventario:
                    bien.saldo_disponible = UtilConservacion.get_saldo_disponible_solicitud_viveros(bien_in_inventario)

            serializer = self.serializer_class(bienes_filtrados, many=True)
            outputList = serializer.data

        else:
            #CREACIÓN DE FILTRO
            filter = {}
            for key, value in request.query_params.items():
                if key in ['cod_tipo_elemento_vivero', 'codigo_bien', 'nombre']:
                    if key != 'cod_tipo_elemento_vivero':
                        filter['id_bien__' + key + '__icontains'] = value
                    else:
                        filter['id_bien__' + key] = value

            #VALIDACIÓN DE FILTROS AL INTERIOR DE INVENTARIO VIVEROS
            bienes_por_consumir = InventarioViveros.objects.filter(id_vivero=id_vivero)
            bienes_filtrados_pre = bienes_por_consumir.filter(**filter).exclude(id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=True).exclude(cod_etapa_lote='G')
            if not bienes_filtrados_pre:
                return Response({'success': False, 'detail': 'No existe ningún bien que se pueda consumir'}, status=status.HTTP_400_BAD_REQUEST)
            
            #UNIÓN DE TODOS LOS RESULTADOS QUE TENGAN EL MISMO ID_VIVERO, ID_BIEN Y COD_ETAPA_LOTE
            bienes_filtrados = bienes_filtrados_pre.values('id_vivero', 'id_bien', 'cod_etapa_lote').annotate(cantidad_entrante=Sum('cantidad_entrante'), cantidad_bajas=Sum('cantidad_bajas'), cantidad_consumos_internos=Sum('cantidad_consumos_internos'), cantidad_salidas=Sum('cantidad_salidas'))

            #ASIGNACIÓN DE NUEVOS VALORES Y ELIMINACIÓN DE DATA YA NO USADA
            for bien in bienes_filtrados:
                if bien['cod_etapa_lote'] == 'P':
                    bien['saldo_total_produccion'] = UtilConservacion.get_saldo_disponible_solicitud_viveros_dict(bien)
                    del bien['cantidad_entrante']
                    del bien['cantidad_bajas']
                    del bien['cantidad_consumos_internos']
                    del bien['cantidad_salidas']
                    del bien['cod_etapa_lote']
                else: 
                    bien['saldo_total_distribucion'] = UtilConservacion.get_saldo_disponible_solicitud_viveros_dict(bien)
                    del bien['cantidad_entrante']
                    del bien['cantidad_bajas']
                    del bien['cantidad_consumos_internos']
                    del bien['cantidad_salidas']
                    del bien['cod_etapa_lote']

            #AGRUPAR LAS DOS ETAPAS DE LOS LOTES EN UN SOLO REGISTRO DEL BIEN 
            bienes_data = sorted(bienes_filtrados, key=operator.itemgetter("id_bien", "id_vivero"))
            outputList = []

            for bien_vivero, resto_de_campos in itertools.groupby(bienes_data, key=operator.itemgetter("id_bien", "id_vivero")):
                dict_auxiliar = {}
                for campo in resto_de_campos:
                    dict_auxiliar.update(campo)
                
                outputList.append(dict_auxiliar)

            #ASIGNACIÓN DE NUEVA INFORMACIÓN NECESARIA PARA SER PINTADA EN FRONTEND
            for bien in outputList:
                bien_in_catalogo = CatalogoBienes.objects.filter(id_bien=bien['id_bien']).first()
                bien['codigo_bien'] = bien_in_catalogo.codigo_bien
                bien['nombre'] = bien_in_catalogo.nombre
                bien['nombre_cientifico'] = bien_in_catalogo.nombre_cientifico
                bien['unidad_medida'] = bien_in_catalogo.id_unidad_medida.nombre

                solicitudes = ItemSolicitudViveros.objects.filter(id_solicitud_viveros__solicitud_abierta=True, id_solicitud_viveros__estado_aprobacion_coord_viveros='A', id_solicitud_viveros__id_vivero_solicitud=bien['id_vivero']).filter(id_bien=bien['id_bien'])
                cantidad = 0
                if solicitudes:
                    for solicitud in solicitudes:
                        cantidad += solicitud.cantidad
                
                bien['saldo_total_apartado'] = cantidad

                bien['saldo_total_produccion'] = bien.get('saldo_total_produccion') if bien.get('saldo_total_produccion') else 0
                bien['saldo_total_distribucion'] = bien.get('saldo_total_distribucion') if bien.get('saldo_total_distribucion') else 0

        return Response({'success': False, 'detail': 'Busqueda exitosa', 'data': outputList})

class DeleteItemsSolicitudView(generics.RetrieveDestroyAPIView):
    serializer_class = DeleteItemsSolicitudSerializer
    queryset = ItemSolicitudViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_solicitud):
        data_items = request.data

        #VALIDACIÓN QUE LA SOLICITUD ENVIADA EXISTA
        solicitud = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud:
            return Response({'success': False, 'detail': 'No se encontró ningún vivero con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

        #VALIDACIÓN QUE TODOS LOS ID DE LOS ITEMS ENVIADOS EXISTAN
        id_items_list = [item['id_item_solicitud_viveros'] for item in data_items]
        id_items_list_instance = ItemSolicitudViveros.objects.filter(id_item_solicitud_viveros__in=id_items_list)
        if len(set(id_items_list)) != len(id_items_list_instance):
            return Response({'success': False, 'detail': 'Los items seleccionados para eliminar deben existir'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE TODOS LOS ITEMS ENVIADOS PERTENEZCAN A LA SOLICITUD ENVIADA
        id_solicitud_list = [item.id_solicitud_viveros.id_solicitud_vivero for item in id_items_list_instance]
        if len(set(id_solicitud_list)) > 1:
            return Response({'success': False, 'detail': 'Todos los items seleccionados deben pertenecer a una sola solicitud'}, status=status.HTTP_400_BAD_REQUEST)
        if id_solicitud_list[0] != int(id_solicitud):
            return Response({'success': False, 'detail': 'Todos los items por eliminar deben pertenecer a la solicitud seleccionada'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE NO ELIMINE TODOS LOS ITEMS DE LA SOLICITUD ENVIADOS
        items_solicitud = ItemSolicitudViveros.objects.filter(id_solicitud_viveros=id_solicitud)
        if len(items_solicitud) == len(id_items_list):
            return Response({'success': False, 'detail': 'No se pueden eliminar todos los items de una solicitud'}, status=status.HTTP_403_FORBIDDEN)
        
        #ELIMINACION DE TODOS LOS ITEMS ENVIADOS
        valores_eliminados_detalles = []
        for item in id_items_list_instance:
            valores_eliminados_detalles.append({'nombre' : item.id_bien.nombre})
            item.delete()

        # AUDITORIA ELIMINACIÓN DE ITEMS SOLICITUD
        descripcion = ({"numero_despacho_almacen": str(solicitud.nro_solicitud)})
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 60,
            "cod_permiso": "AC",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success': True, 'detail': 'Items eliminados exitosamente'}, status=status.HTTP_200_OK)