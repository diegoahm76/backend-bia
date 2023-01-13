from almacen.models.bienes_models import CatalogoBienes
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from almacen.serializers.despachos_serializers import SerializersDespachoConsumo, SerializersItemDespachoConsumo, SerializersSolicitudesConsumibles, SerializersItemsSolicitudConsumible, SearchBienInventarioSerializer
from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.models import Personas, User
from rest_framework.decorators import api_view
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, date
import copy
import json
from almacen.serializers.despachos_serializers import (
    CerrarSolicitudDebidoInexistenciaSerializer,
    SerializersDespachoConsumo,
    SerializersItemDespachoConsumo,
    SerializersSolicitudesConsumibles,
    SerializersItemsSolicitudConsumible,
    AgregarBienesConsumoConservacionSerializer
)
from almacen.models.solicitudes_models import (
    SolicitudesConsumibles, 
    DespachoConsumo, 
    ItemDespachoConsumo, 
    SolicitudesConsumibles, 
    ItemsSolicitudConsumible
)
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
    UnidadesMedida,
    Bodegas
)
from almacen.models.inventario_models import (
    Inventario
)
from almacen.serializers.solicitudes_serialiers import ( 
    CrearSolicitudesPostSerializer,
    CrearItemsSolicitudConsumiblePostSerializer
    )
from seguridad.serializers.personas_serializers import PersonasSerializer

class CreateDespachoMaestro(generics.UpdateAPIView):
    serializer_class = SerializersDespachoConsumo
    queryset = DespachoConsumo
    serializer_item_consumo = SerializersItemDespachoConsumo
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_despacho = json.loads(datos_ingresados['info_despacho'])
        items_despacho = json.loads(datos_ingresados['items_despacho'])
        info_despacho['ruta_archivo_doc_con_recibido'] = request.FILES.get('ruta_archivo_doc_con_recibido')
        #Validaciones primarias
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'data':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        if info_despacho['es_despacho_conservacion'] != False:
            return Response({'success':False,'data':'En este servicio no se pueden procesar despachos de vivero, además verfique el campo (es_despacho_conservacion) debe ser True o False'},status=status.HTTP_404_NOT_FOUND)
        # if info_despacho['es_despacho_conservacion'] == False and info_despacho['id_entrada_almacen_cv'] != None:
        #     return Response({'success':False,'data':'Si ingresa (es_despacho_conservacion) en false, el campo id_entrada_almacen_cv debe ser null'},status=status.HTTP_404_NOT_FOUND)
        if len(info_despacho['motivo']) > 255:
            return Response({'success':False,'data':'El motivo debe tener como máximo 255 caracteres'},status=status.HTTP_404_NOT_FOUND)
        #Validaciones de la solicitud
        instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']).first()
        if not instancia_solicitud:
            return Response({'success':False,'data':'Debe ingresar un id de solicitud válido'},status=status.HTTP_404_NOT_FOUND)
        if instancia_solicitud.solicitud_abierta == False or instancia_solicitud.estado_aprobacion_responsable != 'A':
            return Response({'success':False,'data':'La solicitud a despachar debe de estar aprobada por el funcionario responsable y no debe de estar cerrada'},status=status.HTTP_404_NOT_FOUND)
        #Asignación de fecha de registro
        info_despacho['fecha_registro'] = datetime.now()
        #Se valida que la fecha de la solicitud no sea inferior a (fecha_actual - 8 días) ni superior a la actual
        fecha_despacho = datetime.strptime(info_despacho.get('fecha_despacho'), "%Y-%m-%d %H:%M:%S")
        aux_validacion_fechas = info_despacho['fecha_registro'] - fecha_despacho
        if int(aux_validacion_fechas.days) > 8 or int(aux_validacion_fechas.days) < 0:
            return Response({'success':False,'data':'La fecha ingresada no es permita dentro de los parametros existentes'},status=status.HTTP_404_NOT_FOUND)
        #Se valida que la fecha de aprobación de la solicitud sea inferior a la fecha de despacho
        fecha_aprobacion_solicitud = instancia_solicitud.fecha_aprobacion_responsable
        if fecha_despacho <= fecha_aprobacion_solicitud:
            return Response({'success':False,'data':'La fecha de despacho debe ser mayor o igual a la fecha de aprobación de la solicitud'},status=status.HTTP_404_NOT_FOUND)
        #Consulta y asignación de los campos que se repiten con solicitudes de bienes de consumos
        info_despacho['numero_solicitud_por_tipo'] = instancia_solicitud.nro_solicitud_por_tipo
        info_despacho['fecha_solicitud'] = instancia_solicitud.fecha_solicitud
        info_despacho['id_persona_solicita'] = instancia_solicitud.id_persona_solicita.id_persona
        info_despacho['id_unidad_para_la_que_solicita'] = instancia_solicitud.id_unidad_para_la_que_solicita.id_unidad_organizacional
        info_despacho['id_funcionario_responsable_unidad'] = instancia_solicitud.id_funcionario_responsable_unidad.id_persona
        #Asignación de persona que despacha
        info_despacho['id_persona_despacha'] = user_logeado.persona.id_persona
        #Asignacion de número de despacho
        despachos_existentes = DespachoConsumo.objects.all()
        if despachos_existentes:
            numero_despachos = [i.numero_despacho_consumo for i in despachos_existentes]
            info_despacho['numero_despacho_consumo'] = max(numero_despachos) + 1
        else:
            info_despacho['numero_despacho_consumo'] = 1
        # SE OBTIENEN TODOS LOS ITEMS DE LA SOLICITUD PARA LUEGO VALIDAR QUE LOS ITEMS DESPACHADOS ESTÉN DENTRO DE LA SOLICITUD
        items_solicitud = ItemsSolicitudConsumible.objects.filter(id_solicitud_consumibles=info_despacho['id_solicitud_consumo'])
        if not items_solicitud:
            return Response({'success':False,'data':'La solicitud que quiere despachar no tiene items, por favor añada items a la solicitud para poderla despachar' },status=status.HTTP_404_NOT_FOUND)
        id_items_solicitud = [i.id_bien.id_bien for i in items_solicitud]
        # SE VALIDA QUE EL NUMERO DE POSICION SEA UNICO
        nro_posicion_items = [i['numero_posicion_despacho'] for i in items_despacho]
        if len(nro_posicion_items) != len(set(nro_posicion_items)):
            return Response({'success':False,'data':'El número de posición debe ser único' },status=status.HTTP_404_NOT_FOUND)
        # VALIDACIONES EN ITEMS DEL DESPACHO
        aux_validacion_bienes_despachados_repetidos = []
        aux_validacion_bienes_despachados_contra_solicitados = []
        axu_validacion_cantidades_despachadas_total = []
        aux_validacion_bienes_repetidos = {}
        aux_validacion_unidades_dic = {}
        for i in items_despacho:
            bien_solicitado = i.get('id_bien_solicitado')
            if (bien_solicitado not in id_items_solicitud):
                return Response({'success':False,'data':'Uno de los bienes que intenta despachar no se encuentra dentro de la solicitud, verifique que cada id_bien_solicitado se encuentre dentro de la solicitud'},status=status.HTTP_404_NOT_FOUND)
            if bien_solicitado == None:
                return Response({'success':False,'data':'Debe ingresar un id de un bien solicitado'},status=status.HTTP_404_NOT_FOUND)
            bien_solicitado_instancia = CatalogoBienes.objects.filter(id_bien = i['id_bien_solicitado']).first()
            if not bien_solicitado_instancia:
                return Response({'success':False,'data':'El bien solicitado (' + i['id_bien_solicitado'] + ') no existe' },status=status.HTTP_404_NOT_FOUND)
            if bien_solicitado_instancia.nivel_jerarquico > 5 or bien_solicitado_instancia.nivel_jerarquico < 2:
                return Response({'success':False,'data':'Error en el numero_posicion (' + i['numero_posicion_despacho'] + '). El bien solicitado (' + bien_solicitado_instancia.nombre + ') no es de nivel 2 al 5' },status=status.HTTP_404_NOT_FOUND)
            if bien_solicitado_instancia.cod_tipo_bien != 'C':
                return Response({'success':False,'data':'El bien (' + bien_solicitado_instancia.nombre + ') no es de consumo' },status=status.HTTP_404_NOT_FOUND)
            item_solicitado_instancia = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']) & Q(id_bien=i['id_bien_solicitado'])).first()
            if item_solicitado_instancia.cantidad != i['cantidad_solicitada'] or item_solicitado_instancia.id_unidad_medida.id_unidad_medida != i['id_unidad_medida_solicitada']:
                return Response({'success':False,'data':'Error en el numero_posicion (' + i['numero_posicion_despacho'] + ') del despacho. La cantidad solicitada o la unidad de medida solicitada no corresponde a las registrada en la solicitud' },status=status.HTTP_404_NOT_FOUND)
            # VALIDACION 94:
            if i['cantidad_despachada'] == 0:
                if i['id_bien_despachado'] != 0:
                    return Response({'success':False,'data':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bien_despachado) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                if i['id_bodega'] != 0:
                    return Response({'success':False,'data':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (id_bodega) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                if i['observacion'] != 0:
                    return Response({'success':False,'data':'Si la cantidad a despachar de un bien solicitado es 0, en el campo (observacion) debe ingresar 0' },status=status.HTTP_404_NOT_FOUND)
                    
                if i['id_bien_despachado'] == 0:
                    i['id_bien_despachado'] = None
                if i['id_bodega'] == 0:
                    i['id_bodega'] = None
                if i['observacion'] == 0:
                    i['observacion'] = 0

            if i['cantidad_despachada'] > 0:
                bien_despachado = i.get('id_bien_despachado')
                if not bien_despachado:
                    return Response({'success':False,'data':'Debe ingresar un bien despachado' },status=status.HTTP_404_NOT_FOUND)
                bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado).first()
                if not bien_despachado_instancia:
                    return Response({'success':False,'data':'Debe ingresar un id_bien válido en el bien despachado' },status=status.HTTP_404_NOT_FOUND)
                nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                # SE VALIDA QUE EL BIEN DESPACHADO PERTENESCA A LA LINEA DEL BIEN SOLICITADO
                cont = nivel_bien_despachado
                arreglo_id_bienes_ancestros = []
                while cont>0:
                    arreglo_id_bienes_ancestros.append(bien_despachado_instancia.id_bien)
                    if bien_despachado_instancia.nivel_jerarquico > 1:
                        bien_despachado_instancia = CatalogoBienes.objects.filter(id_bien=bien_despachado_instancia.id_bien_padre.id_bien).first()
                        if not bien_despachado_instancia:
                            return Response({'success':False,'data':'Uno de los bienes no tiene padre' },status=status.HTTP_404_NOT_FOUND)
                        nivel_bien_despachado = int(bien_despachado_instancia.nivel_jerarquico)
                    cont -= 1
                # SE VALIDA QUE EL BIEN DESPACHADO SEA DESENDIENTE DEL BIEN SOLICITADO
                if (bien_solicitado_instancia.id_bien_padre.id_bien not in arreglo_id_bienes_ancestros):
                    return Response({'success':False,'data':'En el número de posición (' + i['numero_posicion_despacho'] + ') el bien solicitado no es de la misma linea del bien despachado' },status=status.HTTP_404_NOT_FOUND)
                bodega_solicita = i.get('id_bodega')
                if bodega_solicita == None:
                    return Response({'success':False,'data':'Debe ingresar un id de bodega válido'},status=status.HTTP_404_NOT_FOUND)
                instancia_bodega_solcitud = Bodegas.objects.filter(id_bodega = i['id_bodega']).first()
                if not instancia_bodega_solcitud:
                    return Response({'success':False,'data':'El id de bodega no existe' },status=status.HTTP_404_NOT_FOUND)
                observaciones = i.get('observacion')
                if observaciones == None:
                    return Response({'success':False,'data':'El JSON debe contener un campo (observaciones)' },status=status.HTTP_404_NOT_FOUND)
                if len(observaciones) > 30:
                    return Response({'success':False,'data':'La observacion solo puede contener hasta 30 caracteres' },status=status.HTTP_404_NOT_FOUND)
                # ESTO SE USA EN LA "VALIDACION 93" SE CREAN LAS CONDICIONES PARA LA VALIDACIÓN DE LA CANTIDAD DESPACHADA NO SUPERE LA SOLICITADA SI LAS UNIDADES SON IGUALES
                aux_validacion_unidades_solicitado = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']) & Q(id_bien=i['id_bien_solicitado'])).first()
                aux_validacion_unidades_despachado = CatalogoBienes.objects.filter(Q(id_bien=i['id_bien_despachado'])).first()
                if aux_validacion_unidades_solicitado.id_bien.id_unidad_medida.nombre == aux_validacion_unidades_despachado.id_unidad_medida.nombre:
                    if i['cantidad_despachada'] > aux_validacion_unidades_solicitado.cantidad:
                        return Response({'success':False,'data':'Una de las cantidades despachadas supera la cantidad solicitada' },status=status.HTTP_404_NOT_FOUND)
                    if not aux_validacion_bienes_repetidos.get(str(i['id_bien_solicitado'])):
                        aux_validacion_bienes_repetidos[str(i['id_bien_solicitado'])] = [i['cantidad_despachada']]
                    else:
                        aux_validacion_bienes_repetidos[str(i['id_bien_solicitado'])].append(i['cantidad_despachada'])
                    aux_validacion_unidades_dic[str(i['id_bien_solicitado'])] = True
                else:
                    aux_validacion_unidades_dic[str(i['id_bien_solicitado'])] = False

            # VALIDACION 90: SE VALIDA QUE UN BIEN DESPACHADO NO SE REPITA DENTRO DEL MISMO DESPACHO
            if [i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']] in aux_validacion_bienes_despachados_repetidos:
                return Response({'success':False,'data':'Error en los bienes despachados, no se puede despachar el mismo bien varias veces dentro de un despacho, elimine los bienes despachados repetidos' },status=status.HTTP_404_NOT_FOUND)
            # ESTO SE USA PARA LA "VALIDACION 90"
            aux_validacion_bienes_despachados_repetidos.append([i['id_bien_solicitado'], i['id_bien_despachado'], i['id_bodega']])
            # ESTO SE USA PARA LA "VALIDACION 91"
            aux_validacion_bienes_despachados_contra_solicitados.append(i['id_bien_solicitado'])
            # ESTO SE USA PARA LA "VALIDACION 92"
            axu_validacion_cantidades_despachadas_total.append(i['cantidad_despachada'])
            
        # VALIDACION 91: SE VALIDA QUE TODOS LOS BIENES SOLICITUADOS SE ENCUENTREN DENTRO DE LA SOLICITUD
        if len(items_solicitud) != len(set(aux_validacion_bienes_despachados_contra_solicitados)):
            return Response({'success':False,'data':'Error en los bienes despachados, se deben despachar cada uno de los bienes solicitados, si no desea despachar alguno de los bienes solicitados ingrese cantidad despachada en 0' },status=status.HTTP_404_NOT_FOUND)
        # VALIDACION 92: SE VALIDA QUE DENTRO DE LA SOLICITUD SE DESPACHE AL MENOS 1 BIEN, NO ES POSIBLE DESPACHAR TODO EN 0 
        axu_validacion_cantidades_despachadas_total = sum(axu_validacion_cantidades_despachadas_total)
        if axu_validacion_cantidades_despachadas_total < 1:
            return Response({'success':False,'data':'Debe despachar como mínimo una unidad de los bienes en la solicitud, si quiere cerrar la solicitud porque no hay stock disponible de ningún item por favor diríjase al módulo de cierre de solicitud por inexistencia' },status=status.HTTP_404_NOT_FOUND)
        # VALIDACION 93: SE VALIDAN LAS CANTIDADES SI TIENEN LA MISMA UNIDAD
        for key, value in aux_validacion_bienes_repetidos.items():
            aux_validacion_bienes_repetidos[key] = sum(value)
            aux_local_uno = ItemsSolicitudConsumible.objects.filter(Q(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']) & Q(id_bien=int(key))).first()
            if int(aux_validacion_bienes_repetidos[key]) > aux_local_uno.cantidad:
                return Response({'success':False,'data':'Una de las cantidades despachadas supera la cantidad solicitada' },status=status.HTTP_404_NOT_FOUND)
 
        serializer = self.serializer_class(data=info_despacho)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        serializer_items = self.serializer_item_consumo(data=items_despacho, many=True)
        serializer_items.is_valid(raise_exception=True)
        serializer_items.save()
        
        for i in items_despacho:
            inventaria_instancia = Inventario.objects.filter(Q(id_bien=i['id_bien_despachado'])&Q(id_bodega=i['id_bodega']))
            
        despacho_creado = DespachoConsumo.objects.filter(Q(id_solicitud_consumo=info_despacho['id_solicitud_consumo']) & Q(numero_despacho_consumo=info_despacho['numero_despacho_consumo'])).first()
        instancia_solicitud.id_despacho_consumo = despacho_creado.id_despacho_consumo
        instancia_solicitud.fecha_cierre_solicitud = despacho_creado.fecha_despacho
        instancia_solicitud.gestionada_almacen = True
        instancia_solicitud.solicitud_abierta = False
        print(despacho_creado.id_despacho_consumo)
        print(despacho_creado.fecha_despacho)
        return Response({'success':True,'data':'Despacho creado con éxito', 'Numero solicitud' : info_despacho["numero_despacho_consumo"]},status=status.HTTP_200_OK)
    

class CerrarSolicitudDebidoInexistenciaView(generics.RetrieveUpdateAPIView):
    serializer_class = CerrarSolicitudDebidoInexistenciaSerializer
    queryset = SolicitudesConsumibles.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_solicitud):
        data = request.data
        
        #VALIDACIÓN SI EXISTE LA SOLICITUD ENVIADA
        solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=id_solicitud).first()
        if not solicitud:
            return Response({'success': False, 'detail': 'No se encontró ninguna solicitud con los parámetros enviados'}, status=status.HTTP_404_NOT_FOUND)
        
        if solicitud.fecha_cierre_no_dispo_alm:
            return Response({'success': False, 'detail': 'No se puede cerrar una solicitud que ya está cerrada'}, status=status.HTTP_403_FORBIDDEN)
        
        #SUSTITUIR INFORMACIÓN A LA DATA
        data['fecha_cierre_no_dispo_alm'] = datetime.now()
        data['id_persona_cierre_no_dispo_alm'] = request.user.persona.id_persona
        data['solicitud_abierta'] = False
        data['fecha_cierre_solicitud'] = datetime.now()
        data['gestionada_almacen'] = True

        serializer = self.serializer_class(solicitud, data=data)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()
        print(serializador)
        
        #Auditoria Cerrar Solicitud
        usuario = request.user.id_usuario
        descripcion = {"Es solicitud conservación": str(serializador.es_solicitud_de_conservacion), "Numero solicitud por tipo": str(serializador.nro_solicitud_por_tipo)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 47,
            "cod_permiso": "AC",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': True, 'detail': 'Se cerró la solicitud correctamente'}, status=status.HTTP_201_CREATED)
        
    
class SearchSolicitudesAprobadasYAbiertos(generics.ListAPIView):
    serializer_class=SerializersSolicitudesConsumibles
    queryset=SolicitudesConsumibles.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        filter = {}
        fecha_despacho=request.query_params.get('fecha_despacho')
       
        if not fecha_despacho:
            return Response({'success':False,'detail':'Ingresa el parametro de fecha de despacho'},status=status.HTTP_400_BAD_REQUEST)
        
        filter['estado_aprobacion_responsable'] = "A"
        filter['solicitud_abierta'] = True
        fecha_despacho_strptime = datetime.strptime(
                fecha_despacho, '%Y-%m-%d %H:%M:%S')
        solicitudes=SolicitudesConsumibles.objects.filter(**filter).filter(fecha_aprobacion_responsable__lte=fecha_despacho_strptime)
        if solicitudes:
            serializador=self.serializer_class(solicitudes,many = True)
            return Response({'success':True,'detail':'Se encontraron solicitudes aprobadas y abiertas','data':serializador.data},status = status.HTTP_200_OK)
        else:
            return Response({'success':False,'detail':'No se encontraron solicitudes'},status = status.HTTP_404_NOT_FOUND) 
        
class GetDespachoConsumoByNumeroDespacho(generics.ListAPIView):
    serializer_class= SerializersDespachoConsumo
    queryset=DespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        numero_despacho_consumo=request.query_params.get('numero_despacho_consumo')
        if not numero_despacho_consumo:
            return Response({'success':False,'detail':'Ingresa el parametro de fecha de despacho'},status=status.HTTP_400_BAD_REQUEST)
        despacho=DespachoConsumo.objects.filter(numero_despacho_consumo=numero_despacho_consumo).first()
        if despacho:
            serializador=self.serializer_class(despacho,many=False)
            return Response ({'success':True,'detail':'Despacho encontrado','data':serializador.data},status=status.HTTP_200_OK)
        else:
            return Response ({'success':False,'detail':'No se encontraron despachos'},status=status.HTTP_404_NOT_FOUND)

class FiltroDespachoConsumo(generics.ListAPIView):
    serializer_class= SerializersDespachoConsumo
    queryset=DespachoConsumo.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        if (request.query_params.get('numero_solicitud_por_tipo') != None and request.query_params.get('numero_solicitud_por_tipo') != "") and (request.query_params.get('es_despacho_conservacion') == None or request.query_params.get('es_despacho_conservacion')== ""):
            return Response ({'success':False,'detail':'No puede filtrar por un número de solicitud sin haber definido si es despacho de conservación o no.'},status=status.HTTP_403_FORBIDDEN)
        if (request.query_params.get('es_despacho_conservacion') != None and request.query_params.get('es_despacho_conservacion') != "") and (request.query_params.get('numero_solicitud_por_tipo') == None or request.query_params.get('numero_solicitud_por_tipo')== ""):
            return Response ({'success':False,'detail':'Debe enviar el número de solicitud'},status=status.HTTP_403_FORBIDDEN)

        filter={}
        
        for key,value in request.query_params.items():
            if key in ['numero_solicitud_por_tipo', 'fecha_despacho','id_unidad_para_la_que_solicita','es_despacho_conservacion']:
                if key != 'id_unidad_para_la_que_solicita' and key != 'es_despacho_conservacion':
                    filter[key+"__startswith"]=value
                else:
                    if value != '':
                        filter[key]=value
        
        if filter.get('es_despacho_conservacion') == 'true':
            filter['es_despacho_conservacion']=True
        elif filter.get('es_despacho_conservacion') == 'false':
            filter['es_despacho_conservacion']=False
        
        despachos=DespachoConsumo.objects.filter(**filter)
        if despachos:
            serializador=self.serializer_class(despachos,many=True)
            return Response ({'success':True,'detail':'Despacho encontrado','data':serializador.data},status=status.HTTP_200_OK)
        return Response ({'success':True,'detail':'No se encontraron despachos','data':[]},status=status.HTTP_200_OK)

class SearchBienInventario(generics.ListAPIView):
    serializer_class=SearchBienInventarioSerializer
    queryset=Inventario.objects.all()
    
    def get(self,request):
        codigo_bien = request.query_params.get('codigo_bien')
        id_bodega = request.query_params.get('id_bodega')
        fecha_despacho = request.query_params.get('fecha_despacho')
        
        if (not codigo_bien or codigo_bien == '') or (not id_bodega or id_bodega == '') or (not fecha_despacho or fecha_despacho == ''):
            return Response({'success':False, 'detail':'Debe ingresar los parámetros de búsqueda'}, status=status.HTTP_400_BAD_REQUEST)

        bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien, cod_tipo_bien='C', nivel_jerarquico=5).first()
        fecha_despacho_strptime = datetime.strptime(fecha_despacho, '%Y-%m-%d %H:%M:%S')
        
        if bien:
            items_despachados = ItemDespachoConsumo.objects.filter(id_bien_despachado=bien.id_bien, id_despacho_consumo__fecha_despacho__gte=fecha_despacho_strptime)
            print("ID_BIEN: ", bien.id_bien)
            print("FECHA_DESPACHO: ", fecha_despacho_strptime)
            print("ITEMS_DESPACHADOS: ", items_despachados)
            if items_despachados:
                return Response({'success':False, 'detail':'El bien tiene despachos o entregas posteriores a la fecha de despacho elegida', 'data': []}, status=status.HTTP_200_OK)
                
            inventario = Inventario.objects.filter(id_bien=bien.id_bien, id_bodega=id_bodega).first()
            
            serializador_inventario = self.serializer_class(inventario)
            
            return Response({'success':True, 'detail':'Se encontró el siguiente resultado', 'data': serializador_inventario.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'El bien no existe', 'data': []}, status=status.HTTP_200_OK)
        
class SearchBienesInventario(generics.ListAPIView):
    serializer_class=SearchBienInventarioSerializer
    queryset=Inventario.objects.all()
    
    def get(self,request):
        id_bien = request.query_params.get('id_bien')
        
        if not id_bien or id_bien == '':
            return Response({'success':False, 'detail':'Debe ingresar el parámetro de búsqueda'}, status=status.HTTP_400_BAD_REQUEST)

        inventario = Inventario.objects.filter(id_bien=id_bien)
        
        serializador_inventario = self.serializer_class(inventario, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data': serializador_inventario.data}, status=status.HTTP_200_OK)

class AgregarBienesConsumoConservacionByCodigoBien(generics.ListAPIView):
    serializer_class=AgregarBienesConsumoConservacionSerializer
    queryset=CatalogoBienes.objects.all()
    
    def get(self,request):
        codigo_bien = request.query_params.get('codigo_bien')
        id_bodega = request.query_params.get('id_bodega')
        fecha_despacho = request.query_params.get('fecha_despacho')
        
        if (not codigo_bien or codigo_bien == '') or (not id_bodega or id_bodega == '') or (not fecha_despacho or fecha_despacho == ''):
            return Response({'success':False, 'detail':'Debe ingresar los parámetros de búsqueda'}, status=status.HTTP_400_BAD_REQUEST)

        bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien, solicitable_vivero=True, cod_tipo_bien='C', nivel_jerarquico=5).first()
        fecha_despacho_strptime = datetime.strptime(fecha_despacho, '%Y-%m-%d %H:%M:%S')
        print("BIEN: ", bien)
        if bien:
            items_despachados = ItemDespachoConsumo.objects.filter(id_bien_despachado=bien.id_bien, id_despacho_consumo__fecha_despacho__gte=fecha_despacho_strptime)
            print("ID_BIEN: ", bien.id_bien)
            print("FECHA_DESPACHO: ", fecha_despacho_strptime)
            print("ITEMS_DESPACHADOS: ", items_despachados)
            if items_despachados:
                return Response({'success':False, 'detail':'El bien tiene despachos o entregas posteriores a la fecha de despacho elegida', 'data': []}, status=status.HTTP_403_FORBIDDEN)
                
            bien_inventario = Inventario.objects.filter(id_bien=bien.id_bien, id_bodega=id_bodega).first()
            
            cantidad_actual=bien_inventario.cantidad_entrante_consumo - bien_inventario.cantidad_saliente_consumo
            bien_inventario.cantidad_disponible=cantidad_actual
            serializador=self.serializer_class(bien_inventario,many=False)
            
            return Response({'success':True, 'detail':'Se encontró el siguiente resultado','data':serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'El bien no existe', 'data': []}, status=status.HTTP_200_OK)
        

class AgregarBienesConsumoConservacionByLupa(generics.ListAPIView):
    serializer_class=AgregarBienesConsumoConservacionSerializer
    queryset=CatalogoBienes.objects.all()
    
    def get(self,request):
        codigo_bien = request.query_params.get('codigo_bien_solicitado')
        fecha_despacho = request.query_params.get('fecha_despacho')
        
        if (not codigo_bien or codigo_bien == '')  or (not fecha_despacho or fecha_despacho == ''):
            return Response({'success':False, 'detail':'Debe ingresar los parámetros de búsqueda'}, status=status.HTTP_400_BAD_REQUEST)

        bienes = CatalogoBienes.objects.filter(codigo_bien__startswith=codigo_bien, solicitable_vivero=True, cod_tipo_bien='C', nivel_jerarquico=5)

        fecha_despacho_strptime = datetime.strptime(fecha_despacho, '%Y-%m-%d %H:%M:%S')
        
        if bienes:
            bien_id_bien = [bien.id_bien for bien in bienes]
            items_despachados = ItemDespachoConsumo.objects.filter(id_bien_despachado__in=bien_id_bien, id_despacho_consumo__fecha_despacho__gte=fecha_despacho_strptime)
            items_despachados_list = [item.id_bien_despachado.id_bien for item in items_despachados]
            list_bienes_end = [bien for bien in bien_id_bien if bien not in items_despachados_list]
            bien_inventario = Inventario.objects.filter(id_bien__in=list_bienes_end)
            serializador = self.serializer_class(bien_inventario, many=True)
        
            return Response({'success':True, 'detail':'Se encontró el siguiente resultado','data':serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'El bien no existe', 'data': []}, status=status.HTTP_200_OK)
