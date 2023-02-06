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

from seguridad.models import Personas
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.models.siembras_models import (
    CamasGerminacionVivero,
    Siembras,
    CamasGerminacionViveroSiembra,
    ConsumosSiembra,
)
from conservacion.models.viveros_models import (
    Vivero,
)
from conservacion.serializers.viveros_serializers import (
    ViveroSerializer,
)
from conservacion.serializers.camas_siembras_serializers import (
    CamasGerminacionPost,
    CreateSiembrasSerializer,
    GetNumeroLoteSerializer,
    GetCamasGerminacionSerializer,
    CreateSiembraInventarioViveroSerializer,
    CreateBienesConsumidosSerializer,
    GetSiembraSerializer,
    GetBienesPorConsumirSerializer,
    UpdateSiembraSerializer,
    UpdateBienesConsumidosSerializer,
    DeleteSiembraSerializer,
    GetBienesConsumidosSiembraSerializer,
    GetBienSembradoSerializer
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.utils import UtilConservacion

class CamasGerminacion(generics.UpdateAPIView):
    serializer_class = CamasGerminacionPost
    queryset = CamasGerminacionVivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id_vivero_procesar):
        datos_ingresados = request.data

        # SE VALIDA QUE EL VIVERO INGRESADO EXISTA
        instancia_vivero_ingresado = Vivero.objects.filter(id_vivero=id_vivero_procesar).first()
        if not instancia_vivero_ingresado:
            return Response({'success':False,'detail':'El vivero ingresado no existe'},status=status.HTTP_400_BAD_REQUEST)
        
        # SE VALIDA QUE EL DATO COMÚN SEA CORRECTO EN TODOS LOS ELEMENTOS (SE HAYA PUESTO EL MISMO VIVERO QUE CADA CAMA)
        if datos_ingresados == []:
            camas_existentes = CamasGerminacionVivero.objects.filter(id_vivero=id_vivero_procesar)
            if not camas_existentes:
                return Response({'success':False,'detail':'Este vivero no tiene camas de germinación asociadas'},status=status.HTTP_400_BAD_REQUEST)
            for i in camas_existentes:
                if ((i.item_activo != False) or (i.item_activo != False)):
                    return Response({'success':False,'detail':'No es posible eliminar una cama si está activa o si ya ha sido usada'},status=status.HTTP_400_BAD_REQUEST)
            
            # SE ELIMINAN LOS ELEMENTOS
            camas_existentes.delete()
            return Response({'success':True,'detail':'Camas de germinación elimanadas con éxito'},status=status.HTTP_200_OK)
        else:
            # SE OBTIENEN LAS CAMAS QUE SE QUIEREN ELIMINAR
            camas_existentes = CamasGerminacionVivero.objects.filter(id_vivero=instancia_vivero_ingresado.id_vivero)
            id_camas_existentes = [i.id_cama_germinacion_vivero for i in camas_existentes]
            id_camas_entrantes = [i['id_cama_germinacion_vivero'] for i in datos_ingresados if i['id_cama_germinacion_vivero'] != None]
            lista_elementos_eliminar = [i for i in id_camas_existentes if i not in id_camas_entrantes]
            
            # VALIDACIONES COMPLEMENTARIAS DE LOS ELEMENTOS A ELIMINAR
            for i in lista_elementos_eliminar:
                instancia_validacion_camas_germinacion = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=i).first()
                if ((instancia_validacion_camas_germinacion.item_activo != False) or (instancia_validacion_camas_germinacion.item_activo != False)):
                    return Response({'success':False,'detail':'No es posible eliminar una cama si está activa o si ya ha sido usada'},status=status.HTTP_400_BAD_REQUEST)
            
            # SE VALIDAN LOS ELEMENTOS QUE SE QUIEREN ACTUALIZAR Y LOS QUE SE QUIEREN CREAR
            lista_elementos_crear = []
            lista_elementos_actualizar = []
            for i in datos_ingresados:
                i['id_vivero'] = id_vivero_procesar
                
                # Se valida cual se quiere actualizar y cual se quiere crear
                if i['id_cama_germinacion_vivero'] == None:
                    lista_elementos_crear.append(i)
                else:
                    instancia_validacion_camas_germinacion = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=i['id_cama_germinacion_vivero']).first()
                    if instancia_validacion_camas_germinacion.nombre != i['nombre']:
                        if instancia_validacion_camas_germinacion.item_ya_usado != False:
                            return Response({'success':False,'detail':'No es posible modificar el nombre a una cama que tenga el campo (item_ya_usado) en (true)'},status=status.HTTP_200_OK)
                    lista_elementos_actualizar.append(i)
            
            # SE CREAN LOS ELEMENTOS
            serializer_crear = self.serializer_class(data=lista_elementos_crear, many=True)
            serializer_crear.is_valid(raise_exception=True)
            serializer_crear.save()
            
            # SE ACTUALIZAN LOS ELEMENTOS
            for i in lista_elementos_actualizar:
                instancia_elemento_actualizar = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=i['id_cama_germinacion_vivero']).first()
                serializer_actualizar = self.serializer_class(instancia_elemento_actualizar, data=i)
                serializer_actualizar.is_valid(raise_exception=True)
                serializer_actualizar.save()
            
            # SE ELIMINAN LOS ELEMENTOS
            instancia_elementos_eliminar = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero__in = lista_elementos_eliminar)
            instancia_elementos_eliminar.delete()

            return Response({'success':True,'detail':'Camas de germinación creadas o actualizadas con éxito'},status=status.HTTP_200_OK)
        
class GetCamasGerminacionesView(generics.ListAPIView):
    serializer_class = GetCamasGerminacionSerializer
    queryset = CamasGerminacionVivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_vivero):
        data = self.queryset.all().filter(item_activo=True, id_vivero=id_vivero)
        serializer = self.serializer_class(data, many=True)
        return Response({'success':True, 'detail':'Busqueda exitosa', 'data': serializer.data},status=status.HTTP_200_OK)

class FilterViverosByNombreAndMunicipioView(generics.ListAPIView):
    serializer_class = ViveroSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter = {}
        for key, value in request.query_params.items():
            if key in ['nombre','cod_municipio']:
                if key != 'cod_municipio':
                    filter[key + '__icontains'] = value
                else:
                    filter[key] = value
        vivero = Vivero.objects.filter(~Q(fecha_ultima_apertura=None) & (Q(vivero_en_cuarentena=False) | Q(vivero_en_cuarentena=None)) & Q(fecha_cierre_actual=None)).filter(**filter)
        if vivero:
            serializer = self.serializer_class(vivero, many=True)
            return Response({'success': True, 'detail': 'Se encontraron viveros', 'data': serializer.data}, status=status.HTTP_200_OK)
        else: 
            return Response({'success': False, 'detail': 'No se encontraron viveros'}, status=status.HTTP_404_NOT_FOUND)
        
class CreateSiembraView(generics.CreateAPIView):
    serializer_class = CreateSiembrasSerializer
    queryset = Siembras.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_siembra = json.loads(request.data['data_siembra'])
        data_siembra['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        
        #VALIDAR QUE NO SEA UNA FECHA SUPERIOR A HOY
        fecha_siembra = data_siembra.get('fecha_siembra')
        fecha_actual = datetime.now()
        fecha_siembra_strptime = datetime.strptime(fecha_siembra, '%Y-%m-%d %H:%M:%S')
        if fecha_siembra_strptime > fecha_actual:
            return Response({'success': False, 'detail': 'La fecha de siembra no puede ser superior a la actual'}, status=status.HTTP_400_BAD_REQUEST)

        #ASIGNACIÓN NÚMERO LOTE
        lote = Siembras.objects.filter(id_bien_sembrado=data_siembra['id_bien_sembrado'], id_vivero=data_siembra['id_vivero'], agno_lote=fecha_siembra_strptime.year).order_by('-nro_lote').first()
        contador = 0
        if lote:
            contador = lote.nro_lote
        numero_lote = contador + 1
        data_siembra['nro_lote'] = numero_lote
        
        #VALIDACIÓN QUE NO SEA UNA FECHA SUPERIOR A 30 DÍAS
        if fecha_siembra_strptime < (fecha_actual - timedelta(days=30)):
            return Response({'success': False, 'detail': 'No se puede crear una siembra con antiguedad mayor a 30 días'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDAR FECHA DISPONIBLE PARA SIEMBRA
        lote_busqueda = InventarioViveros.objects.filter(id_bien=data_siembra['id_bien_sembrado'], id_vivero=data_siembra['id_vivero'], agno_lote=data_siembra['agno_lote']).order_by('-nro_lote').first()
        if lote_busqueda:
            lote_instance = InventarioViveros.objects.filter(nro_lote=lote_busqueda.nro_lote, id_bien=lote_busqueda.id_bien.id_bien, id_vivero=lote_busqueda.id_vivero.id_vivero, agno_lote=lote_busqueda.agno_lote).filter(cod_etapa_lote='G').first()
            print(lote_instance)
            if fecha_siembra_strptime < lote_instance.fecha_ingreso_lote_etapa:
                return Response({'success': False, 'detail': 'No se puede crear una siembra con una fecha anterior a la última siembra registrada'})
        
        #VALIDAR QUE EL VIVERO ESTÉ DISPONIBLE PARA SELECCIONAR
        vivero = Vivero.objects.filter(id_vivero=data_siembra['id_vivero']).filter(~Q(fecha_ultima_apertura=None) & (Q(vivero_en_cuarentena=False) | Q(vivero_en_cuarentena=None)) & Q(fecha_cierre_actual=None)).first()
        if not vivero:
            return Response({'success': False, 'detail': 'El vivero seleccionado no cumple los requisitos para que la siembra pueda ser creada'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDAR QUE EL MATERIAL VEGETAL SEA UN BIEN CON LOS REQUISITOS
        bien = CatalogoBienes.objects.filter(id_bien=data_siembra['id_bien_sembrado']).first()
        if not bien.cod_tipo_elemento_vivero =='MV' and not bien.solicitable_vivero == True and not  bien.es_semilla_vivero == False and not bien.nivel_jerarquico == '5':
            return Response({'success': False, 'detail': 'El bien seleccionado no cumple los requisitos para que la siembra pueda ser creada'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDAR QUE LA CAMA DE GERMINACIÓN EXISTA
        if not len(data_siembra['cama_germinacion']):
            return Response({'success': False, 'detail': 'No se puede crear una siembra sin una cama de germinación'}, status=status.HTTP_400_BAD_REQUEST)
        cama = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero__in=data_siembra['cama_germinacion'])
        if len(set(data_siembra['cama_germinacion'])) != len(cama):
            return Response({'success': False, 'detail': 'Todas las camas seleccionadas deben existir'}, status=status.HTTP_404_NOT_FOUND)
        
        #VALIDACIÓN QUE TODAS LAS CAMAS ENVIADAS PERTENEZCAN AL VIVERO DE LA SIEMBRA
        id_viveros_camas_list = [camita.id_vivero.id_vivero for camita in cama] 
        if len(set(id_viveros_camas_list)) > 1:
            return Response({'success': False, 'detail': 'Las camas seleccionadas deben estar relacionadas a solo un vivero'}, status=status.HTTP_400_BAD_REQUEST)
        if int(id_viveros_camas_list[0]) != int(data_siembra['id_vivero']):
            return Response({'success': False, 'detail': 'Las camas seleccionadas deben estar relacionadas al mismo vivero que la siembra'}, status=status.HTTP_400_BAD_REQUEST)

        #CREACIÓN SIEMBRA
        siembra_dict = {
            "id_vivero": data_siembra['id_vivero'],
            "id_bien_sembrado": data_siembra['id_bien_sembrado'],
            "agno_lote": fecha_siembra_strptime.year,
            "nro_lote": data_siembra['nro_lote'],
            "fecha_siembra": data_siembra['fecha_siembra'],
            "observaciones": data_siembra['observaciones'],
            "distancia_entre_semillas": data_siembra['distancia_entre_semillas'],
            "id_persona_siembra": data_siembra['id_persona_siembra'],
            "ruta_archivo_soporte": data_siembra['ruta_archivo_soporte']
        }
        serializer = self.serializer_class(data=siembra_dict, many=False)
        serializer.is_valid(raise_exception=True)
        siembra = serializer.save()

        data_serializada = serializer.data
        data_serializada['cama_germinacion'] = []


        #CREACIÓN DE ASOCIACIÓN ENTRE SIEMBRA Y CAMAS
        camas_guardadas_list = []

        for cama in data_siembra['cama_germinacion']:
            cama_instance = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=cama).first()
            camas_guardadas = CamasGerminacionViveroSiembra.objects.create(
                id_siembra = siembra,
                id_cama_germinacion_vivero = cama_instance  
            )
            data_cama = {'id_cama': camas_guardadas.id_cama_germinacion_vivero.id_cama_germinacion_vivero, 'nombre_cama': camas_guardadas.id_cama_germinacion_vivero.nombre}
            data_serializada['cama_germinacion'].append(data_cama)
            camas_guardadas_list.append(camas_guardadas)
            cama_instance.item_ya_usado = True
            cama_instance.save()

        #CREACIÓN DE REGISTRO EN INVENTARIO VIVEROS
        inventario_vivero_dict = {
            "id_vivero": data_siembra['id_vivero'],
            "id_bien": data_siembra['id_bien_sembrado'],
            "agno_lote": siembra.agno_lote,
            "cod_etapa_lote": 'G',
            "es_produccion_propia_lote": True,
            "fecha_ingreso_lote_etapa": siembra.fecha_siembra,
            "id_siembra_lote_germinacion": siembra.id_siembra,
            "siembra_lote_cerrada": False
        }
        serializer_inventario = CreateSiembraInventarioViveroSerializer(data=inventario_vivero_dict, many=False)
        serializer_inventario.is_valid(raise_exception=True)
        serializer_inventario.save()
        
        # AUDITORIA ELIMINACIÓN DE ITEMS ENTREGA
        descripcion = {"nombre_bien_sembrado": str(siembra.id_bien_sembrado.nombre), "id_vivero": str(siembra.id_vivero.id_vivero), "agno": str(siembra.agno_lote), "nro_lote": str(siembra.nro_lote)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 50,
            "cod_permiso": "CR",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success': True, 'detail': 'Siembra creada exitosamente', 'data': data_serializada}, status=status.HTTP_201_CREATED)


class CreateBienesConsumidosView(generics.CreateAPIView):
    serializer_class = CreateBienesConsumidosSerializer
    queryset = ConsumosSiembra.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, id_siembra):
        data_bienes_consumidos = request.data
        siembra = Siembras.objects.filter(id_siembra=id_siembra).first()
        if not siembra:
            return Response({'success': False, 'detail': 'No se encontró ninguna siembra con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

        #VALIDACIÓN QUE TODOS LOS ITEMS TENGAN UNA SOLA SIEMBRA Y SEA LA MISMA ENVIADA EN LA URL
        id_siembra_list = [bien['id_siembra'] for bien in data_bienes_consumidos]
        if len(set(id_siembra_list)) > 1:
            return Response({'success': False, 'detail': 'Todos los bienes consumidos deben pertenecer a una siembra'}, status=status.HTTP_400_BAD_REQUEST)
        if int(id_siembra_list[0]) != int(id_siembra):
            return Response({'success': False, 'detail': 'Todos los bienes consumidos deben asociarse a la siembra seleccionada'}, status=status.HTTP_400_BAD_REQUEST)
            
        #VALIDACIÓN QUE EL ID_BIEN ENVIADO EXISTA EN INVENTARIO VIVERO
        id_bien = [bien['id_bien_consumido'] for bien in data_bienes_consumidos]
        bien_in_inventario_viveros = InventarioViveros.objects.filter(id_bien__in=id_bien, id_siembra_lote_germinacion=None, id_vivero=siembra.id_vivero.id_vivero)
        if len(set(id_bien)) != len(bien_in_inventario_viveros):
            return Response({'success': False, 'detail': 'Todos los bienes enviados deben existir'}, status=status.HTTP_404_NOT_FOUND)

        #VALIDACIÓN QUE EN LOS BIENES ENVIADOS SOLO HAYA UNA SEMILLA
        bienes_semilla = []
        for bien in bien_in_inventario_viveros:
            if bien.id_bien.es_semilla_vivero == True:
                bienes_semilla.append(bien)
        
        if len(bienes_semilla) > 1:
            return Response({'success': False, 'detail': 'No se puede guardar los bienes consumidos por que tiene más de una semilla'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN QUE SI TENGA LA CANTIDAD ENVIADA COMO DISPONIBLE POR CONSUMIR
        for one_bien in data_bienes_consumidos:
            bien = InventarioViveros.objects.filter(id_bien=one_bien['id_bien_consumido'], id_siembra_lote_germinacion=None, id_vivero=siembra.id_vivero.id_vivero).first()
            if bien.id_bien.cod_tipo_elemento_vivero == 'MV' or bien.id_bien.cod_tipo_elemento_vivero == 'IN':
                bien.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_consumir(bien)
                if one_bien['cantidad'] > int(bien.cantidad_disponible_bien):
                    one_bien['cantidad_disponible'] = bien.cantidad_disponible_bien
                    return Response({'success': False, 'detail': 'No se puede despachar un bien que no tiene cantidades disponibles', 'data': one_bien}, status=status.HTTP_400_BAD_REQUEST)

        # #VALIDACIÓN QUE NO VENGA ID BIEN Y ID MEZCLA CONSUMIDA POR EL MISMO BIEN
        #     if one_bien['id_bien_consumido'] and one_bien['id_mezcla_consumida']:
        #         return Response({'success': True, 'detail': 'En un registro de bienes consumidos no se puede agregar una mezcla y un bien al mismo tiempo'}, status=status.HTTP_403_FORBIDDEN)

        #CREACIÓN DE BIENES CONSUMIDOS
        bienes_consumidos_no_existentes = []
        valores_creados_detalles = []
        for bien in data_bienes_consumidos:
            bien_consumido = ConsumosSiembra.objects.filter(id_siembra=bien['id_siembra'], id_bien_consumido=bien['id_bien_consumido'], id_mezcla_consumida=bien['id_mezcla_consumida']).first()
            if bien_consumido:
                bien_consumido.cantidad = bien_consumido.cantidad if bien_consumido.cantidad else 0
                bien_consumido.cantidad = bien_consumido.cantidad + bien['cantidad']
                bien_consumido.save()

                #SE AFECTA CANTIDAD CONSUMO INTERNO EN INVENTARIO VIVEROS
                bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien['id_bien_consumido'], id_vivero=siembra.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
                cantidad_existente_consumida = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
                bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_existente_consumida + bien['cantidad']
                bien_in_inventario_viveros_serializador.save()

                valores_creados_detalles.append({'nombre_bien_consumido': bien_consumido.id_bien_consumido.nombre})
            else:
                bienes_consumidos_no_existentes.append(bien)

        serializer = self.serializer_class(data=bienes_consumidos_no_existentes, many=True)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        #SE AFECTA LA CANTIDAD DISPONIBLE EN INVENTARIO VIVEROS
        for bien in serializador:
            bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien.id_bien_consumido.id_bien, id_vivero=siembra.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
            cantidad_existente_consumida = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
            bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_existente_consumida + bien.cantidad
            bien_in_inventario_viveros_serializador.save()

        # AUDITORIA BIENES CONSUMIDOS DETALLE SIEMBRAS
        for bien in serializador:
            valores_creados_detalles.append({'nombre_bien_consumido': bien.id_bien_consumido.nombre})

        descripcion = {"nombre_bien_sembrado": str(siembra.id_bien_sembrado.nombre), "vivero": str(siembra.id_vivero.id_vivero),"agno": str(siembra.agno_lote), "nro_lote": str(siembra.nro_lote)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 50,
            "cod_permiso": "CR",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success': True, 'detail': 'Bienes consumidos guardados exitosamente', 'data': serializer.data if serializer.data else data_bienes_consumidos}, status=status.HTTP_201_CREATED)


class UpdateSiembraView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateSiembraSerializer
    queryset = Siembras.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_siembra):
        data_siembra = request.data
        
        #VALIDACIÓN QUE LA SIEMBRA EXISTA
        siembra = Siembras.objects.filter(id_siembra=id_siembra).first()
        copy_siembra = copy.copy(siembra)
        if not siembra:
            return Response({'success':False, 'detail': 'No se encontró ninguna siembra con el parámetro ingresado'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE LA PERSONA QUE SIEMBRA EXISTA
        persona = Personas.objects.filter(id_persona=data_siembra['id_persona_siembra']).first()
        if not persona:
            return Response({'success': False, 'detail': 'No existe ninguna persona con el parámetro ingresado'}, status=status.HTTP_400_BAD_REQUEST)
        
        #OBTENGO CAMAS ACTUALES RELACIONADAS A LA SIEMBRA Y LAS NUEVAS QUE ME ENVÍAN
        camas = CamasGerminacionViveroSiembra.objects.filter(id_siembra=id_siembra)       
        id_camas_list = [cama.id_cama_germinacion_vivero.id_cama_germinacion_vivero for cama in camas]
        id_camas_enviadas = data_siembra['cama_germinacion']
        
        #VALIDACIÓN QUE UNA SIEMBRA NO SE QUEDE SIN CAMAS DE GERMINACIÓN
        if not id_camas_enviadas:
            return Response({'success': False, 'detail': 'Una siembra debe tener por lo menos una cama de germinación'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN QUE TODAS LAS CAMAS ENVIADAS EXISTAN
        camas_list = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero__in=id_camas_enviadas)
        if len(set(id_camas_enviadas)) != len(camas_list):
            return Response({'success': False, 'detail': 'Todas las camas seleccionadas deben existir'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE TODAS LAS CAMAS ENVIADAS PERTENEZCAN AL VIVERO DE LA SIEMBRA
        id_viveros_camas_list = [cama.id_vivero.id_vivero for cama in camas_list] 
        if len(set(id_viveros_camas_list)) > 1:
            return Response({'success': False, 'detail': 'Las camas seleccionadas deben estar relacionadas a solo un vivero'}, status=status.HTTP_400_BAD_REQUEST)
        if int(id_viveros_camas_list[0]) != int(siembra.id_vivero.id_vivero):
            return Response({'success': False, 'detail': 'Las camas seleccionadas deben estar relacionadas al mismo vivero que la siembra'}, status=status.HTTP_400_BAD_REQUEST)

        #CREACIÓN DE NUEVAS CAMAS RELACIONADAS A LA SIEMBRA
        for cama in id_camas_enviadas:
            cama_instance = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=cama).first()
            if cama not in id_camas_list:
                CamasGerminacionViveroSiembra.objects.create(
                    id_siembra = siembra,
                    id_cama_germinacion_vivero = cama_instance
                )

        #ELIMINACIÓN DE CAMAS NO ENVIADAS AL ACTUALIZAR        
        for cama_existente in id_camas_list:
            if cama_existente not in id_camas_enviadas:
                cama_existente_instance = CamasGerminacionViveroSiembra.objects.filter(id_siembra=id_siembra, id_cama_germinacion_vivero=cama_existente).first()
                cama_existente_instance.delete()

        #ACTUALIZACIÓN DE SIEMBRA
        serializador_siembra = self.serializer_class(siembra, data=data_siembra, many=False)
        serializador_siembra.is_valid(raise_exception=True)
        serializador_siembra_instancia = serializador_siembra.save()

        #SE GENERAN LOS CAMPOS PARA LA AUDITORIA
        serializer = GetSiembraSerializer(siembra, many=False)
        data = serializer.data
        camas_actualizadas = CamasGerminacionViveroSiembra.objects.filter(id_siembra=id_siembra)
        data['camas_germinacion'] = []
        valores_actualizados_detalles = []

        for cama in camas_actualizadas:
            data_cama = {'id_cama': cama.id_cama_germinacion_vivero.id_cama_germinacion_vivero, 'nombre_cama': cama.id_cama_germinacion_vivero.nombre}
            data['camas_germinacion'].append(data_cama)
            valores_actualizados_detalles.append({'descripcion': {'nombre': cama.id_cama_germinacion_vivero.nombre}, 'previous': copy_siembra, 'current': serializador_siembra_instancia})

        # AUDITORIA ACTUALIZAR SIEMBRA Y CAMAS DE GERMINACIÓN
        descripcion = {"nombre_bien_sembrado": str(siembra.id_bien_sembrado.nombre), "vivero": str(siembra.id_vivero.id_vivero), "agno": str(siembra.agno_lote), "nro_lote": str(siembra.nro_lote)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 50,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles": valores_actualizados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success': True, 'detail': 'Actualización exitosa', 'data': data}, status=status.HTTP_201_CREATED)
    

class GetSiembrasView(generics.RetrieveAPIView):
    serializer_class = GetSiembraSerializer
    queryset = Siembras.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_siembra):
        siembra = Siembras.objects.filter(id_siembra=id_siembra).first()
        if not siembra:
            return Response({'success':False, 'detail': 'No se encontró ninguna siembra con el parámetro ingresado'}, status=status.HTTP_400_BAD_REQUEST)
        camas_germinacion = CamasGerminacionViveroSiembra.objects.filter(id_siembra=id_siembra)
       
        serializer = self.serializer_class(siembra, many=False)
        data = serializer.data

        data['camas_germinacion'] = []
        for cama in camas_germinacion:
            data_cama = {'id_cama': cama.id_cama_germinacion_vivero.id_cama_germinacion_vivero, 'nombre_cama': cama.id_cama_germinacion_vivero.nombre}
            data['camas_germinacion'].append(data_cama)

        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': data}, status=status.HTTP_200_OK)


class GetBienesPorConsumirView(generics.ListAPIView):
    serializer_class = GetBienesPorConsumirSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_vivero, codigo_bien):
        
        #VALIDACIÓN SI EXISTE VIVERO
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success':False, 'detail': 'No se encontró ninguna siembra con el parámetro ingresado'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN SI EXISTE EL CODIGO BIEN EN INVENTARIO VIVERO
        bien_in_inventario = InventarioViveros.objects.filter(Q(id_bien__codigo_bien=codigo_bien) & Q(id_vivero=id_vivero) & Q(id_bien__nivel_jerarquico=5)).first()
        if not bien_in_inventario:
            return Response({'success':False, 'detail': 'No existe el bien por consumir en el vivero seleccionado'}, status=status.HTTP_400_BAD_REQUEST)
        if bien_in_inventario.id_bien.cod_tipo_elemento_vivero != 'IN' and bien_in_inventario.id_bien.cod_tipo_elemento_vivero != 'MV':
            return Response({'success': True, 'detail': 'El bien seleccionado debe ser de tipo insumo o material vegetal'}, status=status.HTTP_403_FORBIDDEN)

        if bien_in_inventario.id_bien.cod_tipo_elemento_vivero == 'MV':
            if bien_in_inventario.id_bien.es_semilla_vivero != True:
                return Response({'success': False, 'detail': 'El bien seleccionado debe ser material vegetal de tipo semilla'}, status=status.HTTP_403_FORBIDDEN)

        bien_in_inventario.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_consumir(bien_in_inventario)
        if bien_in_inventario.cantidad_disponible_bien < 1:
            return Response({'success': False, 'detail': 'El bien seleccionado no tiene cantidades disponibles para consumir'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(bien_in_inventario, many=False)

        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class GetBienSembradoView(generics.ListAPIView):
    serializer_class = GetBienSembradoSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bien = CatalogoBienes.objects.filter(cod_tipo_elemento_vivero='MV', solicitable_vivero=True, es_semilla_vivero=False, nivel_jerarquico='5')
        serializer = self.serializer_class(bien, many=True)
        return Response({'success': True, 'detail': 'Búsqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class GetBusquedaBienesConsumidos(generics.ListAPIView):
    serializer_class = GetBienesPorConsumirSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_vivero):
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success': False, 'detail': 'No se encontró ningún vivero con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        
        #CREACIÓN DE FILTROS SEGÚN QUERYPARAMS
        filter = {}
        for key, value in request.query_params.items():
            if key in ['cod_tipo_elemento_vivero', 'codigo_bien', 'nombre']:
                if key != 'cod_tipo_elemento_vivero':
                    filter['id_bien__' + key + '__icontains'] = value
                else:
                    filter['id_bien__' + key] = value

        bienes_por_consumir = InventarioViveros.objects.filter(id_vivero=id_vivero, id_siembra_lote_germinacion=None)
        bienes_filtrados = bienes_por_consumir.filter(**filter).exclude(id_bien__cod_tipo_elemento_vivero='HE').exclude(id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=False)
        if not bienes_filtrados:
            return Response({'success': False, 'detail': 'No existe ningún bien que se pueda consumir'}, status=status.HTTP_400_BAD_REQUEST)
    
        #CAMBIAR VALORES EN CANTIDAD DISPONIBLE BIEN
        bien_con_cantidades = []
        for bien in bienes_filtrados:
            if bien.id_bien.cod_tipo_elemento_vivero == 'MV' or bien.id_bien.cod_tipo_elemento_vivero == 'IN':
                bien.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_consumir(bien)
                
                #VALIDACIÓN QUE LA CANTIDAD DISPONIBLE SEA MAYOR A 0
                if bien.cantidad_disponible_bien > 0:
                    bien_con_cantidades.append(bien)

        serializer = self.serializer_class(bien_con_cantidades, many=True)

        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class GetBienesConsumidosSiembraView(generics.ListAPIView):
    serializer_class = GetBienesConsumidosSiembraSerializer
    queryset = ConsumosSiembra.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_siembra):

        #VALIDACIÓN QUE LA SIEMBRA EXISTA
        siembra = Siembras.objects.filter(id_siembra=id_siembra).first()
        if not siembra:
            return Response({'success':False, 'detail': 'No se encontró ninguna siembra con el parámetro ingresado'}, status=status.HTTP_400_BAD_REQUEST)

        bienes_consumidos = ConsumosSiembra.objects.filter(id_siembra=id_siembra)
        serializer = self.serializer_class(bienes_consumidos, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class UpdateBienConsumido(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateBienesConsumidosSerializer
    queryset = ConsumosSiembra.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_siembra):
        data_siembra = request.data
        
        #VALIDACIÓN QUE LA SIEMBRA EXISTA
        siembra = Siembras.objects.filter(id_siembra=id_siembra).first()
        if not siembra:
            return Response({'success':False, 'detail': 'No se encontró ninguna siembra con el parámetro ingresado'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE TODOS LOS ITEMS TENGAN UNA SOLA SIEMBRA Y SEA LA MISMA ENVIADA EN LA URL
        id_siembra_list = [bien['id_siembra'] for bien in data_siembra]
        if len(set(id_siembra_list)) > 1:
            return Response({'success': False, 'detail': 'Todos los bienes consumidos deben pertenecer a solo una siembra'}, status=status.HTTP_400_BAD_REQUEST)
        if int(id_siembra_list[0]) != int(id_siembra):
            return Response({'success': False, 'detail': 'Todos los bienes consumidos deben asociarse a la siembra seleccionada'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN QUE EL ID_BIEN ENVIADO EXISTA EN INVENTARIO VIVERO
        id_bien = [bien['id_bien_consumido'] for bien in data_siembra]
        bien_in_inventario_viveros = InventarioViveros.objects.filter(id_bien__in=id_bien, id_siembra_lote_germinacion=None, id_vivero=siembra.id_vivero.id_vivero)
        if len(set(id_bien)) != len(bien_in_inventario_viveros):
            return Response({'success': False, 'detail': 'Todos los bienes por consumir deben existir'}, status=status.HTTP_404_NOT_FOUND)
        
        #VALIDACIÓN QUE EN LOS BIENES ENVIADOS SOLO HAYA UNA SEMILLA
        bienes_semilla = []
        for bien in bien_in_inventario_viveros:
            if bien.id_bien.es_semilla_vivero == True:
                bienes_semilla.append(bien)
        
        if len(bienes_semilla) > 1:
            return Response({'success': False, 'detail': 'No se puede guardar los bienes consumidos por que tiene más de una semilla'}, status=status.HTTP_403_FORBIDDEN)

        #SEPARO ENTRE LO QUE SE CREA Y LO QUE SE ACTUALIZA
        bienes_actualizar = [bien for bien in data_siembra if bien['id_consumo_siembra'] != None]
        bienes_crear = [bien for bien in data_siembra if bien['id_consumo_siembra'] == None]

        #VALIDACIÓN QUE SI TENGA LA CANTIDAD ENVIADA COMO DISPONIBLE POR CONSUMIR
        for one_bien in bienes_crear:
            bien = InventarioViveros.objects.filter(id_bien=one_bien['id_bien_consumido'], id_siembra_lote_germinacion=None, id_vivero=siembra.id_vivero.id_vivero).first()
            if bien.id_bien.cod_tipo_elemento_vivero == 'MV' or bien.id_bien.cod_tipo_elemento_vivero == 'IN':
                bien.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_consumir(bien)
                if one_bien['cantidad'] > int(bien.cantidad_disponible_bien):
                    one_bien['cantidad_disponible'] = bien.cantidad_disponible_bien
                    return Response({'success': False, 'detail': f"El bien {bien.id_bien.nombre} no tiene disponible la cantidad que se quiere despachar, actualmente tiene {one_bien['cantidad_disponible']} unidades disponibles"}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE LOS BIENES CONSUMIDOS POR ACTUALIZAR EXISTAN
        bienes_actualizar_id = [bien['id_consumo_siembra'] for bien in bienes_actualizar]
        bienes_actualizar_instance = ConsumosSiembra.objects.filter(id_consumo_siembra__in=bienes_actualizar_id)
        if len(set(bienes_actualizar_id)) != len(bienes_actualizar_instance):
            return Response({'success': False, 'detail': 'Todos los bienes consumidos por actualizar deben existir'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDAR CANTIDADES DE LOS QUE SE QUIEREN ACTUALIZAR
        for bien_actualizar in bienes_actualizar:
            bien_cantidad_disponible = InventarioViveros.objects.filter(id_bien=bien_actualizar['id_bien_consumido'], id_siembra_lote_germinacion=None, id_vivero=siembra.id_vivero.id_vivero).first()
            cantidad_disponible = UtilConservacion.get_cantidad_disponible_consumir(bien_cantidad_disponible)
            if cantidad_disponible < bien_actualizar['cantidad']:
                return Response({'success': False, 'detail': f'El bien {bien_cantidad_disponible.id_bien.nombre} no tiene cantidades disponibles para consumirse'}, status=status.HTTP_400_BAD_REQUEST)

        """
        
        Inicia el proceso de actualización
        
        """
        valores_actualizados_detalles = []

        for bien_actualizar in bienes_actualizar:
            bien_instance = ConsumosSiembra.objects.filter(id_consumo_siembra=bien_actualizar['id_consumo_siembra'], id_siembra=id_siembra).first()
            bien_instance_copy = copy.copy(bien_instance)
            bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien_actualizar['id_bien_consumido'], id_vivero=siembra.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
            
            if bien_actualizar['cantidad'] > bien_instance.cantidad:
                cantidad_anterior = bien_instance.cantidad
                bien_instance.cantidad = bien_actualizar['cantidad']
                bien_instance.observaciones = bien_actualizar['observaciones']
                bien_instance.save()

                cantidad_inventario = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
                bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_inventario - cantidad_anterior + bien_instance.cantidad
                bien_in_inventario_viveros_serializador.save()
            
            elif bien_actualizar['cantidad'] < bien_instance.cantidad:
                cantidad_anterior = bien_instance.cantidad
                bien_instance.cantidad = bien_actualizar['cantidad']
                bien_instance.observaciones = bien_actualizar['observaciones']
                bien_instance.save()

                cantidad_inventario = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
                bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_inventario - cantidad_anterior + bien_instance.cantidad
                bien_in_inventario_viveros_serializador.save()

            else:
                bien_instance.observaciones = bien_actualizar['observaciones']
                bien_instance.save()
            
            valores_actualizados_detalles.append({'descripcion': {'nombre' : bien_instance.id_bien_consumido.nombre},'previous':bien_instance_copy,'current':bien_instance})

        """
        
        Inicia el proceso de creación
        
        """

        #CREACIÓN DE BIENES CONSUMIDOS
        bienes_consumidos_no_existentes = []
        valores_creados_detalles = []
        for bien in bienes_crear:
            bien_consumido = ConsumosSiembra.objects.filter(id_siembra=bien['id_siembra'], id_bien_consumido=bien['id_bien_consumido'], id_mezcla_consumida=bien['id_mezcla_consumida']).first()
            if bien_consumido:
                bien_consumido.cantidad = bien_consumido.cantidad if bien_consumido.cantidad else 0
                bien_consumido.cantidad = bien_consumido.cantidad + bien['cantidad']
                bien_consumido.save()

                #SE AFECTA CANTIDAD CONSUMO INTERNO EN INVENTARIO VIVEROS
                bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien['id_bien_consumido'], id_vivero=siembra.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
                cantidad_existente_consumida = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
                bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_existente_consumida + bien['cantidad']
                bien_in_inventario_viveros_serializador.save()

                valores_creados_detalles.append({'nombre_bien_consumido': bien_consumido.id_bien_consumido.nombre})
            else:
                bienes_consumidos_no_existentes.append(bien)

        serializer = self.serializer_class(data=bienes_consumidos_no_existentes, many=True)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        #SE AFECTA LA CANTIDAD DISPONIBLE EN INVENTARIO VIVEROS
        for bien in serializador:
            bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien.id_bien_consumido.id_bien, id_vivero=siembra.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
            cantidad_existente_consumida = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
            bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_existente_consumida + bien.cantidad
            bien_in_inventario_viveros_serializador.save()

        # AUDITORIA BIENES CONSUMIDOS DETALLE SIEMBRAS
        for bien in serializador:
            valores_creados_detalles.append({'nombre_bien_consumido': bien.id_bien_consumido.nombre})

        descripcion = {"nombre_bien_sembrado": str(siembra.id_bien_sembrado.nombre), "vivero": str(siembra.id_vivero.id_vivero),"agno": str(siembra.agno_lote), "nro_lote": str(siembra.nro_lote)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 50,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_actualizados_detalles": valores_actualizados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        data = ConsumosSiembra.objects.filter(id_siembra=id_siembra)
        serializer = self.serializer_class(data, many=True)
        return Response({'success': True, 'detail': 'Actualización exitosa', 'data': serializer.data}, status=status.HTTP_201_CREATED)

class DeleteBienConsumido(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateBienesConsumidosSerializer
    queryset = ConsumosSiembra.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_siembra):
        pass


class DeleteSiembra(generics.RetrieveDestroyAPIView):
    serializer_class = DeleteSiembraSerializer
    queryset = Siembras.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_siembra):
        pass

