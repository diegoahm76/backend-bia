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
    DeleteItemsSolicitudSerializer,
    GetSolicitudesViverosSerializer,
    ListarSolicitudIDSerializer,
    AnulacionSolicitudesSerializer,
    UpdateSolicitudesSerializer,
    CreateItemsSolicitudSerializer,
    UpdateItemsSolicitudSerializer,
    DeleteItemsSolicitudSerializer,
    CerrarSolicitudNoDisponibilidadSerializer
)
from conservacion.models.viveros_models import (
    Vivero
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales,
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

    def get(self, request, tipodocumento, numerodocumento):
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

        lista_unidades_permitidas = [unidad.id_unidad_organizacional for unidad in linea_jerarquica]

        if user.persona.id_unidad_organizacional_actual.id_unidad_organizacional not in lista_unidades_permitidas:
            return Response({'success': False, 'detail': 'No se puede seleccionar una persona que no esté al mismo nivel o superior en la linea jerarquica'}, status=status.HTTP_403_FORBIDDEN)

        persona_serializer = self.serializer_class(user.persona, many=False)
        return Response({'success': True,'data': persona_serializer.data}, status=status.HTTP_200_OK)


class GetFuncionarioByFiltersView(generics.ListAPIView):
    serializer_class = PersonasSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        #VALIDACIÓN QUE LA PERSONA QUE HACE LA SOLICITUD TENGA UNIDAD ORGANIZACIONAL
        persona_logeada = request.user.persona
        if not persona_logeada.id_unidad_organizacional_actual:
            return Response({'success': False, 'detail': 'La persona que realiza la busqueda debe estar asociada a una unidad organizacional'}, status=status.HTTP_400_BAD_REQUEST)
        
        #ELABORACIÓN DE FILTRO PARA EL QUERY
        filter = {}
        for key, value in request.query_params.items():
            if key in ['primer_nombre', 'primer_apellido', 'numero_documento']:
                if key != 'numero_documento':
                    filter['persona__' +key + '__icontains'] = value
                else:
                    filter['persona__' + key] = value

        query_personas = self.queryset.all().filter(**filter)

        #VALIDACIÓN QUE LOS USUARIOS DEBEN SER INTERNOS
        usuarios_filtrados = query_personas.exclude(~Q(tipo_usuario='I'))
        
        #VALIDACIÓN SOBRE CUALIDADES DE LAS PERSONAS EN TORNO A LA LINEA JERARQUICA
        persona_pasa_validaciones = []
        for usuario in usuarios_filtrados:
            if usuario.persona.id_unidad_organizacional_actual:
                if usuario.persona.id_unidad_organizacional_actual.id_organigrama.actual == True:
                    if usuario:
                        linea_jerarquica = UtilConservacion.get_linea_jerarquica_superior(persona_logeada)
                        lista_unidades_permitidas = [unidad.id_unidad_organizacional for unidad in linea_jerarquica]
                        if usuario.persona.id_unidad_organizacional_actual.id_unidad_organizacional in lista_unidades_permitidas:
                            persona_pasa_validaciones.append(usuario.persona)

        serializer = self.serializer_class(persona_pasa_validaciones, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


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

        # VALIDACIÓN QUE EL ID BIEN ENVIADO CUMPLA CON LAS CONDICIONES DADAS POR EL EQUIPO DE MODELADO
        id_bienes = [bien['codigo_bien'] for bien in data_items_solicitud]
        id_bienes_instance = CatalogoBienes.objects.filter(codigo_bien__in=id_bienes)
        if len(set(id_bienes)) != len(id_bienes_instance):
            return Response({'success': False, 'detail': 'Todos los bienes seleccionados deben existir'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE EL NUMERO DE POSICIÓN SEA ÚNICO POR ITEM
        nro_posicion_list = [bien['nro_posicion'] for bien in data_items_solicitud]
        if len(nro_posicion_list) != len(set(nro_posicion_list)):
            return Response({'success': False, 'detail': 'El numero de posición debe ser único para todos los items solicitados'}, status=status.HTTP_400_BAD_REQUEST)
            
        for bien in data_items_solicitud:
            bien = InventarioViveros.objects.filter(id_bien__codigo_bien=bien['codigo_bien'], id_vivero=vivero.id_vivero)
            if not bien:
                return Response({'success': False, 'detail': 'El bien seleccionado no se encuentra relacionado al vivero seleccionado'}, status=status.HTTP_403_FORBIDDEN)
             
            if bien[0].id_bien.solicitable_vivero != True:
                return Response({'success': False, 'detail': 'El bien seleccionado no es solicitable por vivero'}, status=status.HTTP_403_FORBIDDEN)
            
            if bien[0].id_bien.cod_tipo_bien != 'C':
                return Response({'success': False, 'detail': 'El bien seleccionado no es consumible'}, status=status.HTTP_403_FORBIDDEN)
                
            if bien[0].id_bien.cod_tipo_elemento_vivero == 'HE':
                return Response({'success': False, 'detail': 'El bien seleccionado debe ser de tipo insumo o material vegetal'}, status=status.HTTP_403_FORBIDDEN)

            if bien[0].id_bien.cod_tipo_elemento_vivero == 'MV' and bien[0].id_bien.es_semilla_vivero == True:
                return Response({'success': False, 'detail': 'El bien seleccionado debe ser material vegetal que no sea semilla'}, status=status.HTTP_403_FORBIDDEN)

            if bien[0].id_bien.cod_tipo_elemento_vivero == 'MV':

                #VALIDACIÓN QUE LOS BIENES ESTÉN EN ALGUN LOTE ETAPA DE DISTRIBUCIÓN O PRODUCCIÓN
                bien_in_inventario_no_germinacion = []
                for biensito in bien:
                    if biensito.cod_etapa_lote != 'G':
                        bien_in_inventario_no_germinacion.append(biensito)

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
        
            elif bien[0].id_bien.cod_tipo_elemento_vivero == 'IN':

                #VALIDACIÓN QUE EL BIEN TENGA SALDO DISPONIBLE
                bien_in_inventario = bien.first()
                bien = bien_in_inventario.id_bien
                bien.saldo_disponible = UtilConservacion.get_saldo_disponible_solicitud_viveros(bien_in_inventario)    
                if not bien.saldo_disponible > 0:
                    return Response({'success': False, 'detail': f'El bien {bien.nombre} de tipo insumo no tiene cantidades disponibles para solicitar'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(data=data_solicitud, many=False)
        serializer.is_valid(raise_exception=True)
        solicitud_maestro = serializer.save()

        for item in data_items_solicitud:
            item['id_solicitud_viveros'] = solicitud_maestro.id_solicitud_vivero
        
        serializador_items = CreateItemsSolicitudSerializer(data=data_items_solicitud, many=True)
        serializador_items.is_valid(raise_exception=True)
        items_guardados = serializador_items.save()
        
        # AUDITORIA SOLICITUDES A VIVEROS
        valores_creados_detalles = []
        for bien in items_guardados:
            valores_creados_detalles.append({'nombre_bien': bien.id_bien.nombre})

        descripcion = {"numero_solicitud": str(solicitud_maestro.nro_solicitud)}
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

        return Response({'success': True, 'detail': 'Creación de solicitud exitosa', 'data_maestro': serializer.data, 'data_items': serializador_items.data}, status=status.HTTP_201_CREATED)
    
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
            bienes_con_cantidades = []
            for bien in bienes_filtrados:
                bien_in_inventario = InventarioViveros.objects.filter(id_bien=bien.id_bien, id_vivero=id_vivero).first()
                if bien_in_inventario:
                    bien.saldo_disponible = UtilConservacion.get_saldo_disponible_solicitud_viveros(bien_in_inventario)
                    bien.cod_tipo_elemento_vivero = 'Insumo'
                    if bien.saldo_disponible > 0:
                        bienes_con_cantidades.append(bien)

            serializer = self.serializer_class(bienes_con_cantidades, many=True)
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
                bien['cod_tipo_elemento_vivero'] = 'Material Vegetal'
                bien['saldo_total_produccion'] = bien.get('saldo_total_produccion') if bien.get('saldo_total_produccion') else 0
                bien['saldo_total_distribucion'] = bien.get('saldo_total_distribucion') if bien.get('saldo_total_distribucion') else 0

        return Response({'success': False, 'detail': 'Busqueda exitosa', 'data': outputList})


class GetSolicitudesView(generics.ListAPIView):
    serializer_class = GetSolicitudesViverosSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        solicitudes = self.queryset.all()
        serializer = self.serializer_class(solicitudes, many=True)
        return Response({'success': True, 'detail': 'Obtenido exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)


class GetItemsSolicitudView(generics.ListAPIView):
    serializer_class = ListarSolicitudIDSerializer
    queryset = ItemSolicitudViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_solicitud):

        # VALIDACIÓN QUE LA SOLICITUD SELECCIONADA EXISTA
        solicitud = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud:
            return Response({'success':False, 'detail':'La solicitud seleccionada no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        #VALIDACIÓN QUE LA SOLICITUD SELECCIONADA NO ESTÉ ANULADA
        if solicitud.solicitud_anulada_solicitante==True:
            return Response({'success':False, 'detail':'La solicitud seleccionada se encuentra anulada'}, status=status.HTTP_400_BAD_REQUEST)    
        
        #BUSCAR LOS ITEMS DE ESA SOLICITUD
        solicitudid = self.queryset.all().filter(id_solicitud_viveros=id_solicitud) 
        serializador = self.serializer_class(solicitudid, many=True)

        return Response({'sucess':True, 'detail':'Busqueda exitosa','data': serializador.data}, status=status.HTTP_200_OK)

class UpdateSolicitudesView(generics.UpdateAPIView):
    serializer_class = UpdateSolicitudesSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_solicitud):
        data_solicitud = json.loads(request.data['data_solicitud'])
        data_solicitud['ruta_archivo_info_tecnico'] = request.FILES.get('ruta_archivo_info_tecnico')

        #VALIDACIÓN QUE LA PERSONA QUE HACE LA SOLICITUD TENGA UNIDAD ORGANIZACIONAL Y SEA USUARIO INTERNO
        usuario_logeado = request.user
        persona_logeada = request.user.persona
        
        if not persona_logeada.id_unidad_organizacional_actual:
            return Response({'success': False, 'detail': 'La persona que realiza la busqueda debe estar asociada a una unidad organizacional'}, status=status.HTTP_400_BAD_REQUEST)
        if usuario_logeado.tipo_usuario != "I":
            return Response({'success': False, 'detail': 'La persona que realiza la busqueda debe ser usuario interno'}, status=status.HTTP_400_BAD_REQUEST)

        # VALIDACIÓN QUE LA SOLICITUD SELECCIONADA EXISTA
        solicitud_act = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud_act:
            return Response({'success':False, 'detail':'La solicitud seleccionada no existe'}, status=status.HTTP_400_BAD_REQUEST) 
        solicitud_copy = copy.copy(solicitud_act)

        # VALIDACIÓN QUE LA PERSONA QUE ACTUALIZA ES LA MISMA QUE CREÓ LA SOLICITUD
        if solicitud_act.id_persona_solicita.id_persona != persona_logeada.id_persona:
            return Response({'success':False, 'detail':'Solo la persona que realizó el registro de solicitud puede realizar actualizaciones'}, status=status.HTTP_403_FORBIDDEN) 
        
        # VALIDACIÓN QUE LA ACTUALIZACIÓN NO SE HAGA EN UN TIEMPO SUPERIOR A DOS DIAS
        if  datetime.now() > (solicitud_act.fecha_solicitud + timedelta(hours=48)):
            return Response({'success':False, 'detail':'No se pueden realizar actualizaciones en solicitudes que tienen más de 2 días de haber sido creadas'}, status=status.HTTP_403_FORBIDDEN) 
        
        # VALIDACIÓN ESTADO DE LA APROBACIÓN DEL RESPONSABLE DE LA UNIDAD
        if solicitud_act.revisada_responsable != False:
            return Response({'success':False, 'detail':'No se pueden realizar actualizaciones en solicitudes que ya fueron aprobadas o rechazadas por el responsable de la unidad'}, status=status.HTTP_403_FORBIDDEN) 
        
        # VALIDACIÓN QUE EL FUNCIONARIO ENVIADO EXISTA
        persona_instance = Personas.objects.filter(id_persona=data_solicitud['id_funcionario_responsable_und_destino']).first()
        if not persona_instance:
            return Response({'success':False, 'detail':'El funcionario no existe'}, status=status.HTTP_400_BAD_REQUEST) 
           
        # VALIDACIÓN DE LINEA JERARQUICA SUPERIOR O IGUAL
        linea_jerarquica = UtilConservacion.get_linea_jerarquica_superior(persona_logeada)
        lista_unidades_permitidas = [unidad.id_unidad_organizacional for unidad in linea_jerarquica]

        if persona_instance.id_unidad_organizacional_actual.id_unidad_organizacional not in lista_unidades_permitidas:
            return Response({'success': False, 'detail': 'No se puede seleccionar una persona que no esté al mismo nivel o superior en la linea jerarquica'}, status=status.HTTP_403_FORBIDDEN)

        # VALIDACIÓN QUE LA FECHA SELECCIONADA SEA SUPERIOR A LA EXISTENTE
        fecha_strp = datetime.strptime(data_solicitud['fecha_retiro_material'], '%Y-%m-%d')
        if solicitud_act.fecha_solicitud <= fecha_strp:
            return Response({'success': False, 'detail': 'La fecha seleccionada no es superior a la existente'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(solicitud_act, data=data_solicitud, many=False)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        instancia_post_save = SolicitudesViveros.objects.filter(id_solicitud_vivero=serializador.id_solicitud_vivero).first()
        serializador_post_save = GetSolicitudesViverosSerializer(instancia_post_save, many=False)

       # AUDITORIA ACTUALIZAR SOLICITUD
        usuario = request.user.id_usuario
        direccion = Util.get_client_ip(request)
        descripcion = {"numero_solicitud": str(instancia_post_save.nro_solicitud)}
        valores_actualizados = {'current': serializador, 'previous': solicitud_copy}
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 60,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion, 
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success':True, 'detail':'Actualización exitosa', 'data': serializador_post_save.data}, status=status.HTTP_201_CREATED) 


class AnulacionSolicitudesView(generics.RetrieveUpdateAPIView):
    serializer_class = AnulacionSolicitudesSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, solicitudsita):   
        #VALIDACIÓN QUE LA SOLICITUD SELECCIONADA EXISTA            
        solicitud_anular = SolicitudesViveros.objects.filter(id_solicitud_vivero=solicitudsita).first()
        copia_solicitud = copy.copy(solicitud_anular)
        if not solicitud_anular.solicitud_abierta == True and not solicitud_anular.gestionada_viveros == False:
            return Response({'success':False, 'detail':'La solicitud ya ha sido gestionada por viveros y no puede ser anulada'}, status=status.HTTP_200_OK)
        
        # ASIGNACIÓN DE INFORMACIÓN A SOLICITUD
        solicitud_anular.solicitud_anulada_solicitante = True
        solicitud_anular.justificacion_anulacion_solicitante = request.data['justificacion']
        solicitud_anular.fecha_anulacion_solicitante = datetime.now()
        solicitud_anular.solicitud_abierta = False
        solicitud_anular.save()

        # ELIMINACIÓN DE ITEMS DE SOLICITUD
        items_anulacion = ItemSolicitudViveros.objects.filter(id_solicitud_viveros=solicitud_anular)
        valores_eliminados_detalles = []
        for item in items_anulacion:
            valores_eliminados_detalles.append({'nombre' : item.id_bien.nombre})
            item.delete()  

        # AUDITORIA ANULAR SOLICITUD
        usuario = request.user.id_usuario
        direccion = Util.get_client_ip(request)
        descripcion = {"numero_solicitud": str(copia_solicitud.nro_solicitud)}
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 60,
            "cod_permiso": "AN",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion, 
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success':True, 'detail':'La solicitud ha sido anulada con éxito'}, status=status.HTTP_200_OK)             
            

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
        
        #VALIDACIÓN QUE LA PERSONA QUE HACE LA SOLICITUD TENGA UNIDAD ORGANIZACIONAL Y SEA USUARIO INTERNO
        usuario_logeado = request.user
        persona_logeada = request.user.persona
        
        if not persona_logeada.id_unidad_organizacional_actual:
            return Response({'success': False, 'detail': 'La persona que realiza la acción debe estar asociada a una unidad organizacional'}, status=status.HTTP_400_BAD_REQUEST)
        if usuario_logeado.tipo_usuario != "I":
            return Response({'success': False, 'detail': 'La persona que realiza la acción debe ser usuario interno'}, status=status.HTTP_400_BAD_REQUEST)

        # VALIDACIÓN QUE LA SOLICITUD SELECCIONADA EXISTA
        solicitud_instance = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud_instance:
            return Response({'success':False, 'detail':'La solicitud seleccionada no existe'}, status=status.HTTP_400_BAD_REQUEST) 
        solicitud_copy = copy.copy(solicitud_instance)

        # VALIDACIÓN QUE LA PERSONA QUE ACTUALIZA ES LA MISMA QUE CREÓ LA SOLICITUD
        if solicitud_instance.id_persona_solicita.id_persona != persona_logeada.id_persona:
            return Response({'success':False, 'detail':'Solo la persona que realizó el registro de solicitud puede realizar actualizaciones'}, status=status.HTTP_403_FORBIDDEN) 
        
        # VALIDACIÓN QUE LA ACTUALIZACIÓN NO SE HAGA EN UN TIEMPO SUPERIOR A DOS DIAS
        if datetime.now() > (solicitud_instance.fecha_solicitud + timedelta(hours=48)):
            return Response({'success':False, 'detail':'No se pueden realizar actualizaciones en solicitudes que tienen más de 2 días de haber sido creadas'}, status=status.HTTP_403_FORBIDDEN) 
        
        # VALIDACIÓN ESTADO DE LA APROBACIÓN DEL RESPONSABLE DE LA UNIDAD
        if solicitud_instance.revisada_responsable != False:
            return Response({'success':False, 'detail':'No se pueden realizar actualizaciones en solicitudes que ya fueron aprobadas o rechazadas por el responsable de la unidad'}, status=status.HTTP_403_FORBIDDEN)

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
        descripcion = ({"numero_solicitud": str(solicitud.nro_solicitud)})
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

class UpdateItemsSolicitudView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateItemsSolicitudSerializer
    permission_classes = [IsAuthenticated]
    queryset = ItemSolicitudViveros.objects.all()
    lookup_field = 'id_solicitud'
    lookup_url_kwarg = 'id_solicitud'
    
    def patch(self, request, id_solicitud):
        data = request.data

        #VALIDACIÓN QUE LA PERSONA QUE HACE LA SOLICITUD TENGA UNIDAD ORGANIZACIONAL Y SEA USUARIO INTERNO
        usuario_logeado = request.user
        persona_logeada = request.user.persona
        
        if not persona_logeada.id_unidad_organizacional_actual:
            return Response({'success': False, 'detail': 'La persona que realiza la acción debe estar asociada a una unidad organizacional'}, status=status.HTTP_400_BAD_REQUEST)
        if usuario_logeado.tipo_usuario != "I":
            return Response({'success': False, 'detail': 'La persona que realiza la acción debe ser usuario interno'}, status=status.HTTP_400_BAD_REQUEST)

        # VALIDACIÓN QUE LA SOLICITUD SELECCIONADA EXISTA
        solicitud_instance = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud_instance:
            return Response({'success':False, 'detail':'La solicitud seleccionada no existe'}, status=status.HTTP_400_BAD_REQUEST) 
        solicitud_copy = copy.copy(solicitud_instance)

        # VALIDACIÓN QUE LA PERSONA QUE ACTUALIZA ES LA MISMA QUE CREÓ LA SOLICITUD
        if solicitud_instance.id_persona_solicita.id_persona != persona_logeada.id_persona:
            return Response({'success':False, 'detail':'Solo la persona que realizó el registro de solicitud puede realizar actualizaciones'}, status=status.HTTP_403_FORBIDDEN) 
        
        # VALIDACIÓN QUE LA ACTUALIZACIÓN NO SE HAGA EN UN TIEMPO SUPERIOR A DOS DIAS
        if datetime.now() > (solicitud_instance.fecha_solicitud + timedelta(hours=48)):
            return Response({'success':False, 'detail':'No se pueden realizar actualizaciones en solicitudes que tienen más de 2 días de haber sido creadas'}, status=status.HTTP_403_FORBIDDEN) 
        
        # VALIDACIÓN ESTADO DE LA APROBACIÓN DEL RESPONSABLE DE LA UNIDAD
        if solicitud_instance.revisada_responsable != False:
            return Response({'success':False, 'detail':'No se pueden realizar actualizaciones en solicitudes que ya fueron aprobadas o rechazadas por el responsable de la unidad'}, status=status.HTTP_403_FORBIDDEN)
        
        #SEPARACIÓN DE DATA ENTRE LO QUE SE ACTUALIZA Y LO QUE SE CREA
        data_items_actualizacion = [item for item in data if item['id_item_solicitud_viveros'] != None and item['id_item_solicitud_viveros'] != '']
        data_items_creacion = [item for item in data if item['id_item_solicitud_viveros'] == None or item['id_item_solicitud_viveros'] == '']

        #INICIA PROCESO DE VALIDACIONES PARA CREACIÓN

        # VALIDACIÓN QUE EL ID BIEN ENVIADO CUMPLA CON LAS CONDICIONES DADAS POR EL EQUIPO DE MODELADO
        id_bienes = [bien['codigo_bien'] for bien in data_items_creacion]
        id_bienes_instance = CatalogoBienes.objects.filter(codigo_bien__in=id_bienes)
        if len(set(id_bienes)) != len(id_bienes_instance):
            return Response({'success': False, 'detail': 'Todos los bienes seleccionados deben existir'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE EL NUMERO DE POSICIÓN SEA ÚNICO POR ITEM
        nro_posicion_list = [bien['nro_posicion'] for bien in data]
        if len(nro_posicion_list) != len(set(nro_posicion_list)):
            return Response({'success': False, 'detail': 'El numero de posición debe ser único para todos los items solicitados'}, status=status.HTTP_400_BAD_REQUEST)
            
        for biensito in data_items_creacion:
            print('revienta acpa')
            bien = InventarioViveros.objects.filter(id_bien__codigo_bien=biensito['codigo_bien'], id_vivero=solicitud_instance.id_vivero_solicitud.id_vivero)
            if not bien:
                return Response({'success': False, 'detail': 'El bien seleccionado no se encuentra relacionado al vivero seleccionado'}, status=status.HTTP_403_FORBIDDEN)
             
            if bien[0].id_bien.solicitable_vivero != True:
                return Response({'success': False, 'detail': 'El bien seleccionado no es solicitable por vivero', 'data': biensito}, status=status.HTTP_403_FORBIDDEN)
            
            if bien[0].id_bien.cod_tipo_bien != 'C':
                return Response({'success': False, 'detail': 'El bien seleccionado no es consumible'}, status=status.HTTP_403_FORBIDDEN)
                
            if bien[0].id_bien.cod_tipo_elemento_vivero == 'HE':
                return Response({'success': False, 'detail': 'El bien seleccionado debe ser de tipo insumo o material vegetal'}, status=status.HTTP_403_FORBIDDEN)

            if bien[0].id_bien.cod_tipo_elemento_vivero == 'MV' and bien[0].id_bien.es_semilla_vivero == True:
                return Response({'success': False, 'detail': 'El bien seleccionado debe ser material vegetal que no sea semilla'}, status=status.HTTP_403_FORBIDDEN)

            if bien[0].id_bien.cod_tipo_elemento_vivero == 'MV':

                #VALIDACIÓN QUE LOS BIENES ESTÉN EN ALGUN LOTE ETAPA DE DISTRIBUCIÓN O PRODUCCIÓN
                bien_in_inventario_no_germinacion = []
                for biensito in bien:
                    if biensito.cod_etapa_lote != 'G':
                        bien_in_inventario_no_germinacion.append(biensito)

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
        
            elif bien[0].id_bien.cod_tipo_elemento_vivero == 'IN':

                #VALIDACIÓN QUE EL BIEN TENGA SALDO DISPONIBLE
                bien_in_inventario = bien.first()
                bien = bien_in_inventario.id_bien
                bien.saldo_disponible = UtilConservacion.get_saldo_disponible_solicitud_viveros(bien_in_inventario)    
                if not bien.saldo_disponible > 0:
                    return Response({'success': False, 'detail': f'El bien {bien.nombre} de tipo insumo no tiene cantidades disponibles para solicitar'}, status=status.HTTP_403_FORBIDDEN)


        #GUARDADO DE ITEMS QUE SE ESTÁN CREANDO
        serializador_items = CreateItemsSolicitudSerializer(data=data_items_creacion, many=True)
        serializador_items.is_valid(raise_exception=True)
        items_guardados = serializador_items.save()

        items_finales = ItemSolicitudViveros.objects.filter(id_solicitud_viveros=id_solicitud).order_by('nro_posicion')
        serializador = ListarSolicitudIDSerializer(items_finales, many=True)
        
        # AUDITORIA SOLICITUDES A VIVEROS
        valores_creados_detalles = []
        for bien in items_guardados:
            valores_creados_detalles.append({'nombre_bien': bien.id_bien.nombre})

        descripcion = {"numero_solicitud": str(solicitud_instance.nro_solicitud)}
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
        return Response({'success': True, 'detail': 'Actualización exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)


class CerrarSolicitudNoDisponibilidadView(generics.RetrieveUpdateAPIView):
    serializer_class = CerrarSolicitudNoDisponibilidadSerializer
    queryset = SolicitudesViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_solicitud):
        data = request.data

        solicitud = SolicitudesViveros.objects.filter(id_solicitud_vivero=id_solicitud).first()
        if not solicitud:
            return Response({'success':False, 'detail':'La solicitud seleccionada no existe'}, status=status.HTTP_400_BAD_REQUEST) 

        if solicitud.solicitud_abierta != True and solicitud.gestionada_viveros == True:
            return Response({'success':False, 'detail':'La solicitud seleccionada ya fue gestionada'}, status=status.HTTP_400_BAD_REQUEST) 

        if datetime.now().date() <= solicitud.fecha_retiro_material:
            return Response({'success':False, 'detail':'Para que la solicitud sea cerrada por no disponibilidad, la fecha de retiro de material debe ser superior'}, status=status.HTTP_400_BAD_REQUEST) 

        data['fecha_cierre_no_dispo'] = datetime.now()
        data['id_persona_cierre_no_dispo_viveros'] = request.user.persona.id_persona
        data['solicitud_abierta'] = False
        data['fecha_cierra_solicitud'] = datetime.now()
        data['gestionada_viveros'] = True

        serializer = self.serializer_class(solicitud, data=data)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        data = GetSolicitudesViverosSerializer(solicitud, many=False).data

        return Response({'success': True, 'detail': 'Solicitud cerrada por no disponibilidad exitosamente', 'data': data}, status=status.HTTP_201_CREATED)
