from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time, timedelta
from datetime import timezone
from django.db.models import Count
import copy
import json

from transversal.models.personas_models import Personas
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
    GetBienSembradoSerializer,
    DeleteBienesConsumidosSerializer,
    GetSiembrasSerializer
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from conservacion.models.inventario_models import (
    InventarioViveros
)
from conservacion.models.cuarentena_models import (
    CuarentenaMatVegetal,
    ItemsLevantaCuarentena,
    BajasVivero
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
            raise ValidationError ('El vivero ingresado no existe')
        
        # SE VALIDA QUE EL DATO COMÚN SEA CORRECTO EN TODOS LOS ELEMENTOS (SE HAYA PUESTO EL MISMO VIVERO QUE CADA CAMA)
        if datos_ingresados == []:
            camas_existentes = CamasGerminacionVivero.objects.filter(id_vivero=id_vivero_procesar)
            if not camas_existentes:
                raise ValidationError ('Este vivero no tiene camas de germinación asociadas')
            for i in camas_existentes:
                if ((i.item_activo != False) or (i.item_activo != False)):
                    raise ValidationError ('No es posible eliminar una cama si está activa o si ya ha sido usada')
            
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
                    raise ValidationError ('No es posible eliminar una cama si está activa o si ya ha sido usada')
            
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


class GetCamasGerminacionList(generics.ListAPIView):
    
    serializer_class = GetCamasGerminacionSerializer 
    queryset = CamasGerminacionVivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self,request):
    
        id_vivero = request.query_params.get('id_vivero')
        if id_vivero:
            camas = self.queryset.all().filter(id_vivero = id_vivero) 
        else:
            camas = self.queryset.all()
    
        serializador = self.serializer_class(camas,many=True)
        
        return Response({'success':True, 'detail':'Busqueda exitosa', 'data': serializador.data},status=status.HTTP_200_OK)
    
class GetCamasGerminacionByIdList(generics.CreateAPIView):
    serializer_class = GetCamasGerminacionSerializer 
    queryset = CamasGerminacionVivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        camas_list = request.data.get('camas_list')
        
        camas = self.queryset.all().filter(id_cama_germinacion_vivero__in = camas_list)
    
        serializador = self.serializer_class(camas,many=True)
        
        return Response({'success':True, 'detail':'Busqueda exitosa', 'data': serializador.data},status=status.HTTP_200_OK)
    
    
class GetCamasGerminacionesByIdVivero(generics.ListAPIView):
    serializer_class = GetCamasGerminacionSerializer
    queryset = CamasGerminacionVivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_vivero):
        lista = []
        instances = self.queryset.all().filter(item_activo=True, id_vivero=id_vivero)
        
        for intance in instances:
            registro_cama = intance.camasgerminacionviverosiembra_set.all()
            if not registro_cama:
                lista.append(intance)
        
        serializer = self.serializer_class(lista, many=True)
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
            raise NotFound('No se encontraron viveros')
        
    
@method_decorator(transaction.atomic, name='dispatch')    
class CreateSiembraView(generics.CreateAPIView):
    serializer_class = CreateSiembrasSerializer
    serializer_class_consumidos = CreateBienesConsumidosSerializer
    queryset = Siembras.objects.all()
    permission_classes = [IsAuthenticated]
    
    def create_maestro(self, request):
        data_siembra = json.loads(request.data['data_siembra'])
        data_siembra['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        
        #VALIDAR QUE NO SEA UNA FECHA SUPERIOR A HOY
        fecha_siembra = data_siembra.get('fecha_siembra')
        fecha_actual = datetime.now()
        fecha_siembra_strptime = datetime.strptime(fecha_siembra, '%Y-%m-%d %H:%M:%S')
        if fecha_siembra_strptime > fecha_actual:
            raise ValidationError('La fecha de siembra no puede ser superior a la actual')

        #VALIDAR QUE EL VIVERO ESTÉ DISPONIBLE PARA SELECCIONAR
        vivero = Vivero.objects.filter(id_vivero=data_siembra['id_vivero']).filter(~Q(fecha_ultima_apertura=None) & Q(fecha_cierre_actual=None)).first()
        if not vivero:
            raise ValidationError('Verifique que el vivero seleccionado se encuentre abierto')
        
        #VALIDAR QUE EL MATERIAL VEGETAL SEA UN BIEN CON LOS REQUISITOS
        bien = CatalogoBienes.objects.filter(id_bien=data_siembra['id_bien_sembrado']).first()
        if bien.cod_tipo_elemento_vivero !='MV' and not bien.solicitable_vivero and bien.es_semilla_vivero and bien.nivel_jerarquico != '5':
            raise ValidationError('El bien seleccionado no cumple los requisitos para que la siembra pueda ser creada')
        
        #ASIGNACIÓN NÚMERO LOTE
        lote = Siembras.objects.filter(id_bien_sembrado=data_siembra['id_bien_sembrado'], id_vivero=data_siembra['id_vivero'], agno_lote=fecha_siembra_strptime.year).order_by('-nro_lote').first()
        contador = 0
        if lote:
            contador = lote.nro_lote
        numero_lote = contador + 1
        data_siembra['nro_lote'] = numero_lote
        
        #VALIDACIÓN QUE NO SEA UNA FECHA SUPERIOR A 30 DÍAS
        if fecha_siembra_strptime < (fecha_actual - timedelta(days=30)):
            raise ValidationError('No se puede crear una siembra con antiguedad mayor a 30 días')
        
        #VALIDAR FECHA DISPONIBLE PARA SIEMBRA
        lote_busqueda = InventarioViveros.objects.filter(id_bien=data_siembra['id_bien_sembrado'], id_vivero=data_siembra['id_vivero'], agno_lote = fecha_siembra_strptime.year).last() # preguntar si agno lote es necesario
        if lote_busqueda:
            print("LOTE_BUSQUEDA: ", lote_busqueda)
            lote_instance = InventarioViveros.objects.filter(nro_lote=lote_busqueda.nro_lote, id_bien=lote_busqueda.id_bien.id_bien, id_vivero=lote_busqueda.id_vivero.id_vivero, agno_lote=lote_busqueda.agno_lote).first()
            print(lote_instance)
            if fecha_siembra_strptime < lote_instance.fecha_ingreso_lote_etapa:
                raise ValidationError('No se puede crear una siembra con una fecha anterior a la última siembra registrada')
        
        #VALIDAR QUE LA CAMA DE GERMINACIÓN EXISTA
        if not len(data_siembra['cama_germinacion']):
            raise ValidationError('No se puede crear una siembra sin una cama de germinación')
        cama = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero__in=data_siembra['cama_germinacion'])
        if len(set(data_siembra['cama_germinacion'])) != len(cama):
            raise ValidationError('Todas las camas seleccionadas deben existir')
        
        #VALIDACIÓN QUE TODAS LAS CAMAS ENVIADAS PERTENEZCAN AL VIVERO DE LA SIEMBRA
        id_viveros_camas_list = [camita.id_vivero.id_vivero for camita in cama] 
        if len(set(id_viveros_camas_list)) > 1:
            raise ValidationError('Las camas seleccionadas deben estar relacionadas a solo un vivero')
        if int(id_viveros_camas_list[0]) != int(data_siembra['id_vivero']):
            raise ValidationError('Las camas seleccionadas deben estar relacionadas al mismo vivero que la siembra')
        
        #VALIDACION PARA VERIFICAR QUE LAS CAMAS ESTEN ACTIVAS
        for cama_item in cama:
            if not cama_item.item_activo:
                raise ValidationError('la cama de germinacion '+cama_item.nombre+' no está activa')
            registro_cama = cama_item.camasgerminacionviverosiembra_set.all()
            if registro_cama:
                raise ValidationError('la cama de germinacion '+cama_item.nombre+' no está libre')

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
        
        #DETALLES
        
        siembra = serializer.save()

        data_serializada = serializer.data
        data_serializada['cama_germinacion'] = []

        #CREACIÓN DE ASOCIACIÓN ENTRE SIEMBRA Y CAMAS
        camas_guardadas_list = []

        for cama_item in data_siembra['cama_germinacion']:
            cama_instance = cama.filter(id_cama_germinacion_vivero=cama_item).first()
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
            "nro_lote": siembra.nro_lote,
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
        
        # AUDITORIA CREACIÓN DE SIEMBRA MAESTRO SIN DETALLE
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
        
        return siembra

    def post(self, request):
        # CREAR SIEMBRA
        siembra_creada = self.create_maestro(request)
        
        data_bienes_consumidos = json.loads(request.data['data_bienes_consumidos'])
    
        for bien in data_bienes_consumidos:
            
            bien['id_siembra'] = siembra_creada.id_siembra

        
        #VALIDACIÓN QUE EL ID_BIEN ENVIADO EXISTA EN INVENTARIO VIVERO
        id_bien = [bien['id_bien_consumido'] for bien in data_bienes_consumidos if bien.get('id_bien_consumido')]

        bien_in_inventario_viveros = InventarioViveros.objects.filter(id_bien__in=id_bien, id_siembra_lote_germinacion=None, id_vivero=siembra_creada.id_vivero.id_vivero).distinct('id_bien','id_siembra_lote_germinacion','id_vivero')         
        if len(set(id_bien)) != len(bien_in_inventario_viveros):
            raise NotFound('Todos los bienes enviados deben existir')
        
        #VALIDACIÓN QUE EL ID_MEZCLA ENVIADO EXISTA EN INVENTARIO VIVERO
        id_mezclas = [bien['id_mezcla_consumida'] for bien in data_bienes_consumidos if bien.get('id_mezcla_consumida')]

        mezlca_in_inventario_viveros = InventarioViveros.objects.filter(id_mezcla__in=id_mezclas, id_siembra_lote_germinacion=None, id_vivero=siembra_creada.id_vivero.id_vivero).distinct('id_mezcla','id_siembra_lote_germinacion','id_vivero')         
        if len(set(id_mezclas)) != len(mezlca_in_inventario_viveros):
            raise NotFound('Todas las mezclas enviadas deben existir')

        #VALIDACIÓN QUE EN LOS BIENES ENVIADOS SOLO HAYA UNA SEMILLA
        bienes_semilla = []
        for bien in bien_in_inventario_viveros:
            if bien.id_bien.es_semilla_vivero == True:
                bienes_semilla.append(bien)
        
        if len(bienes_semilla) > 1:
            raise PermissionDenied('No se puede guardar los bienes consumidos por que tiene más de una semilla')

        #VALIDACIÓN QUE SI TENGA LA CANTIDAD ENVIADA COMO DISPONIBLE POR CONSUMIR
        for one_bien in data_bienes_consumidos:
            if one_bien.get('id_bien_consumido'):
                bien = InventarioViveros.objects.filter(id_bien=one_bien['id_bien_consumido'], id_siembra_lote_germinacion=None, id_vivero=siembra_creada.id_vivero.id_vivero).first()
                if bien.id_bien.cod_tipo_elemento_vivero == 'MV' or bien.id_bien.cod_tipo_elemento_vivero == 'IN':
                    bien.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_consumir(bien)
                    if one_bien['cantidad'] > int(bien.cantidad_disponible_bien):
                        one_bien['cantidad_disponible'] = bien.cantidad_disponible_bien
                        raise ValidationError(f'La cantidad del bien {bien.id_bien.nombre} elegido no puede superar su cantidad disponible {str(bien.cantidad_disponible_bien)}')
            else:
                mezcla = InventarioViveros.objects.filter(id_mezcla=one_bien['id_mezcla_consumida'], id_siembra_lote_germinacion=None, id_vivero=siembra_creada.id_vivero.id_vivero).first()
                mezcla.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_mezclas_siembras(bien)
                if one_bien['cantidad'] > int(mezcla.cantidad_disponible_bien):
                    one_bien['cantidad_disponible'] = mezcla.cantidad_disponible_bien
                    raise ValidationError(f'La cantidad de la mezcla {mezcla.id_mezcla.nombre} elegida no puede superar su cantidad disponible {str(mezcla.cantidad_disponible_bien)}')

        # #VALIDACIÓN QUE NO VENGA ID BIEN Y ID MEZCLA CONSUMIDA POR EL MISMO BIEN
        #    if one_bien['id_bien_consumido'] and one_bien['id_mezcla_consumida']:
        #         return Response({'success': True, 'detail': 'En un registro de bienes consumidos no se puede agregar una mezcla y un bien al mismo tiempo'}, status=status.HTTP_403_FORBIDDEN)

        #CREACIÓN DE BIENES CONSUMIDOS
        bienes_consumidos_no_existentes = []
        valores_creados_detalles = []
        for bien in data_bienes_consumidos:
            bien_consumido = None
            
            if bien.get('id_bien_consumido'):
                bien_consumido = ConsumosSiembra.objects.filter(id_siembra=bien['id_siembra'], id_bien_consumido=bien['id_bien_consumido']).first()
            else:
                bien_consumido = ConsumosSiembra.objects.filter(id_siembra=bien['id_siembra'], id_mezcla_consumida=bien['id_mezcla_consumida']).first()
            
            if bien_consumido:
                bien_consumido.cantidad = bien_consumido.cantidad if bien_consumido.cantidad else 0
                bien_consumido.cantidad = bien_consumido.cantidad + bien['cantidad']
                bien_consumido.save()

                #SE AFECTA CANTIDAD CONSUMO INTERNO EN INVENTARIO VIVEROS
                bien_in_inventario_viveros_serializador = None
                
                if bien.get('id_bien_consumido'):
                    bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien['id_bien_consumido'], id_vivero=siembra_creada.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
                else:
                    bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_mezcla=bien['id_mezcla_consumida'], id_vivero=siembra_creada.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
                
                cantidad_existente_consumida = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
                bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_existente_consumida + bien['cantidad']
                bien_in_inventario_viveros_serializador.save()

                valores_creados_detalles.append({'NombreBienConsumido': bien_consumido.id_bien_consumido.nombre if bien_consumido.id_bien_consumido else bien_consumido.id_mezcla_consumida.nombre})
            else:
                bienes_consumidos_no_existentes.append(bien)

        serializer = self.serializer_class_consumidos(data=bienes_consumidos_no_existentes, many=True)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        #SE AFECTA LA CANTIDAD DISPONIBLE EN INVENTARIO VIVEROS
        # for bien in serializador:
        #     bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien.id_bien_consumido.id_bien, id_vivero=siembra_creada.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
        #     cantidad_existente_consumida = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
        #     bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_existente_consumida + bien.cantidad
        #     bien_in_inventario_viveros_serializador.save()

        # # AUDITORIA BIENES CONSUMIDOS DETALLE SIEMBRAS
        # for bien in serializador:
        #     valores_creados_detalles.append({'nombre_bien_consumido': bien.id_bien_consumido.nombre})

        descripcion = {"NombreBienSembrado": str(siembra_creada.id_bien_sembrado.nombre), "Vivero": str(siembra_creada.id_vivero.id_vivero),"Agno": str(siembra_creada.agno_lote), "NroLote": str(siembra_creada.nro_lote)}
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
    

        return Response({'success': True, 'detail': 'Se creo la siembra correctamente', 'data': serializer.data if serializer.data else data_bienes_consumidos}, status=status.HTTP_201_CREATED)

class UpdateSiembraView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateSiembraSerializer
    serializer_class_detalles = UpdateBienesConsumidosSerializer
    queryset = Siembras.objects.all()
    permission_classes = [IsAuthenticated]

    def update_maestro(self, request, id_siembra):
        data_siembra = request.data['data_siembra']
        
        #VALIDACIÓN QUE LA SIEMBRA EXISTA
        siembra = Siembras.objects.filter(id_siembra=id_siembra).first()
        copy_siembra = copy.copy(siembra)
        if not siembra:
            raise NotFound('No se encontró ninguna siembra con el parámetro ingresado')
        
        #VALIDACIÓN QUE LA PERSONA QUE SIEMBRA EXISTA
        persona = Personas.objects.filter(id_persona=data_siembra['id_persona_siembra']).first()
        if not persona:
            raise ValidationError('No existe ninguna persona con el parámetro ingresado')
        
        #OBTENGO CAMAS ACTUALES RELACIONADAS A LA SIEMBRA Y LAS NUEVAS QUE ME ENVÍAN
        camas = CamasGerminacionViveroSiembra.objects.filter(id_siembra=id_siembra)       
        id_camas_list = [cama.id_cama_germinacion_vivero.id_cama_germinacion_vivero for cama in camas]
        id_camas_enviadas = data_siembra['cama_germinacion']
        
        #VALIDACIÓN QUE UNA SIEMBRA NO SE QUEDE SIN CAMAS DE GERMINACIÓN
        if not id_camas_enviadas:
            raise PermissionDenied('Una siembra debe tener por lo menos una cama de germinación')

        #VALIDACIÓN QUE TODAS LAS CAMAS ENVIADAS EXISTAN
        camas_list = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero__in=id_camas_enviadas)
        if len(set(id_camas_enviadas)) != len(camas_list):
            raise ValidationError('Todas las camas seleccionadas deben existir')
        
        #VALIDACIÓN QUE TODAS LAS CAMAS ENVIADAS PERTENEZCAN AL VIVERO DE LA SIEMBRA
        id_viveros_camas_list = [cama.id_vivero.id_vivero for cama in camas_list] 
        if len(set(id_viveros_camas_list)) > 1:
            raise ValidationError('Las camas seleccionadas deben estar relacionadas a solo un vivero')
        if int(id_viveros_camas_list[0]) != int(siembra.id_vivero.id_vivero):
            raise ValidationError('Las camas seleccionadas deben estar relacionadas al mismo vivero que la siembra')
        
        #ELIMINACIÓN DE CAMAS NO ENVIADAS AL ACTUALIZAR
        valores_eliminados_detalles = []
        for cama_existente in id_camas_list:
            if cama_existente not in id_camas_enviadas:
                cama_existente_instance = CamasGerminacionViveroSiembra.objects.filter(id_siembra=id_siembra, id_cama_germinacion_vivero=cama_existente).first()
                
                valores_eliminados_detalles.append(
                    {
                        'NombreCama': cama_existente_instance.id_cama_germinacion_vivero.nombre,
                        'NombreVivero': cama_existente_instance.id_cama_germinacion_vivero.id_vivero.nombre,
                        'IdSiembra': cama_existente_instance.id_siembra.id_siembra
                    }
                )
                
                cama_existente_instance.delete()
                
        #CREACIÓN DE NUEVAS CAMAS RELACIONADAS A LA SIEMBRA
        valores_creados_detalles = []
        for cama in id_camas_enviadas:
            cama_instance = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=cama).first()
            if cama not in id_camas_list:
                cama_vivero_siembra = CamasGerminacionViveroSiembra.objects.create(
                    id_siembra = siembra,
                    id_cama_germinacion_vivero = cama_instance
                )
                
                valores_creados_detalles.append(
                    {
                        'NombreCama': cama_vivero_siembra.id_cama_germinacion_vivero.nombre,
                        'NombreVivero': cama_vivero_siembra.id_cama_germinacion_vivero.id_vivero.nombre,
                        'IdSiembra': cama_vivero_siembra.id_siembra.id_siembra
                    }
                )

        #ACTUALIZACIÓN DE SIEMBRA
        serializador_siembra = self.serializer_class(siembra, data=data_siembra, many=False)
        serializador_siembra.is_valid(raise_exception=True)
        serializador_siembra_instancia = serializador_siembra.save()

        #SE GENERAN LOS CAMPOS PARA LA AUDITORIA
        # serializer = GetSiembraSerializer(siembra, many=False)
        # data = serializer.data
        # camas_actualizadas = CamasGerminacionViveroSiembra.objects.filter(id_siembra=id_siembra)
        # camas_actualizadas = [cama_vivero.id_cama_germinacion_vivero for cama_vivero in camas_actualizadas]
        # serializer_camas_germinacion = GetCamasGerminacionSerializer(camas_actualizadas, many=True)
        # data['camas_germinacion'] = serializer_camas_germinacion.data
        
        valores_actualizados_maestro = {'previous':copy_siembra, 'current':siembra}
        
        # AUDITORIA ACTUALIZAR SIEMBRA Y CAMAS DE GERMINACIÓN
        # descripcion = {"nombre_bien_sembrado": str(siembra.id_bien_sembrado.nombre), "vivero": str(siembra.id_vivero.id_vivero), "agno": str(siembra.agno_lote), "nro_lote": str(siembra.nro_lote)}
        # direccion=Util.get_client_ip(request)
        # auditoria_data = {
        #     "id_usuario" : request.user.id_usuario,
        #     "id_modulo" : 50,
        #     "cod_permiso": "AC",
        #     "subsistema": 'CONS',
        #     "dirip": direccion,
        #     "descripcion": descripcion,
        #     "valores_actualizados_detalles": valores_actualizados_detalles
        # }
        # Util.save_auditoria_maestro_detalle(auditoria_data)
        
        return_obj = {
            'instancia':serializador_siembra_instancia,
            'valores_actualizados_maestro':valores_actualizados_maestro,
            'valores_creados_detalles':valores_creados_detalles,
            'valores_eliminados_detalles':valores_eliminados_detalles
        }

        return return_obj
    
    def delete_detalles(self, request, siembra):
        data_bienes_consumidos = request.data['data_bienes_consumidos']
        id_list_bienes_consumidos = [bien_consumido['id_consumo_siembra'] for bien_consumido in data_bienes_consumidos]
        bien_in_consumos = ConsumosSiembra.objects.filter(id_siembra=siembra.id_siembra).exclude(id_consumo_siembra__in=id_list_bienes_consumidos)
        
        #INICIA PROCESO DE ELIMINACIÓN
        valores_eliminados_detalles = []
        for bien in bien_in_consumos:
            if bien.id_bien_consumido:
                bien_in_inventario = InventarioViveros.objects.filter(id_bien=bien.id_bien_consumido, id_siembra_lote_germinacion=None, id_vivero=siembra.id_vivero.id_vivero).first()
            elif bien.id_mezcla_consumida:
                bien_in_inventario = InventarioViveros.objects.filter(id_mezcla=bien.id_mezcla_consumida, id_siembra_lote_germinacion=None, id_vivero=siembra.id_vivero.id_vivero).first()
                
            bien_in_inventario.cantidad_consumos_internos = bien_in_inventario.cantidad_consumos_internos - bien.cantidad
            bien_in_inventario.save()
            valores_eliminados_detalles.append({'NombreBienConsumido': bien.id_bien_consumido.nombre if bien.id_bien_consumido else bien.id_mezcla_consumida.nombre})
            bien.delete()

        # AUDITORIA BIENES CONSUMIDOS DETALLE SIEMBRAS
        # descripcion = {"nombre_bien_sembrado": str(siembra.id_bien_sembrado.nombre), "vivero": str(siembra.id_vivero.id_vivero),"agno": str(siembra.agno_lote), "nro_lote": str(siembra.nro_lote)}
        # direccion=Util.get_client_ip(request)
        # auditoria_data = {
        #     "id_usuario" : request.user.id_usuario,
        #     "id_modulo" : 50,
        #     "cod_permiso": "BO",
        #     "subsistema": 'CONS',
        #     "dirip": direccion,
        #     "descripcion": descripcion,
        #     "valores_eliminados_detalles": valores_eliminados_detalles
        # }
        # Util.save_auditoria_maestro_detalle(auditoria_data)
        
        # data = ConsumosSiembra.objects.filter(id_siembra=id_siembra)
        # serializer = self.serializer_class(data, many=True)
        
        return_obj = {
            'instancia':bien_in_consumos,
            'valores_eliminados_detalles':valores_eliminados_detalles
        }
        
        return return_obj
    
    def put(self, request, id_siembra):
        # ACTUALIZAR SIEMBRA
        siembra_actualizada = self.update_maestro(request, id_siembra)
        instancia_siembra_actualizada = siembra_actualizada['instancia']
        # ELIMINAR DETALLES
        detalles_eliminados = self.delete_detalles(request, instancia_siembra_actualizada)
        valores_eliminados_detalles = siembra_actualizada['valores_eliminados_detalles']
        valores_eliminados_detalles.extend(detalles_eliminados['valores_eliminados_detalles'])
        
        data_bienes_consumidos = request.data['data_bienes_consumidos']
        
        if data_bienes_consumidos:
            #VALIDACIÓN QUE TODOS LOS ITEMS TENGAN UNA SOLA SIEMBRA Y SEA LA MISMA ENVIADA EN LA URL
            id_siembra_list = [bien['id_siembra'] for bien in data_bienes_consumidos]
            if len(set(id_siembra_list)) > 1:
                raise ValidationError('Todos los bienes consumidos deben pertenecer a solo una siembra')
            if int(id_siembra_list[0]) != int(id_siembra):
                raise ValidationError('Todos los bienes consumidos deben asociarse a la siembra seleccionada')
            
            #VALIDACIÓN QUE EL ID_BIEN ENVIADO EXISTA EN INVENTARIO VIVERO
            id_bien = [bien['id_bien_consumido'] for bien in data_bienes_consumidos if bien.get('id_bien_consumido')]
            bien_in_inventario_viveros = InventarioViveros.objects.filter(id_bien__in=id_bien, id_siembra_lote_germinacion=None, id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero)
            if len(set(id_bien)) != len(bien_in_inventario_viveros):
                raise ValidationError('Todos los bienes por consumir deben existir')
            
            #VALIDACIÓN QUE EL ID_MEZCLA ENVIADO EXISTA EN INVENTARIO VIVERO
            id_mezclas = [bien['id_mezcla_consumida'] for bien in data_bienes_consumidos if bien.get('id_mezcla_consumida')]

            mezlca_in_inventario_viveros = InventarioViveros.objects.filter(id_mezcla__in=id_mezclas, id_siembra_lote_germinacion=None, id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero)       
            if len(set(id_mezclas)) != len(mezlca_in_inventario_viveros):
                raise NotFound('Todas las mezclas enviadas deben existir')
        
            #VALIDACIÓN QUE EN LOS BIENES ENVIADOS SOLO HAYA UNA SEMILLA
            bienes_semilla = []
            for bien in bien_in_inventario_viveros:
                if bien.id_bien.es_semilla_vivero == True:
                    bienes_semilla.append(bien)
            
            if len(bienes_semilla) > 1:
                raise PermissionDenied('No se puede guardar los bienes consumidos por que tiene más de una semilla')

        #SEPARO ENTRE LO QUE SE CREA Y LO QUE SE ACTUALIZA
        bienes_actualizar = [bien for bien in data_bienes_consumidos if bien['id_consumo_siembra'] != None]
        bienes_crear = [bien for bien in data_bienes_consumidos if bien['id_consumo_siembra'] == None]

        #VALIDACIÓN QUE SI TENGA LA CANTIDAD ENVIADA COMO DISPONIBLE POR CONSUMIR
        for one_bien in bienes_crear:
            if one_bien.get('id_bien_consumido'):
                bien = InventarioViveros.objects.filter(id_bien=one_bien['id_bien_consumido'], id_siembra_lote_germinacion=None, id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero).first()
                if bien.id_bien.cod_tipo_elemento_vivero == 'MV' or bien.id_bien.cod_tipo_elemento_vivero == 'IN':
                    bien.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_consumir(bien)
                    if one_bien['cantidad'] > int(bien.cantidad_disponible_bien):
                        one_bien['cantidad_disponible'] = bien.cantidad_disponible_bien
                        raise ValidationError(f'La cantidad del bien {bien.id_bien.nombre} elegido no puede superar su cantidad disponible {str(bien.cantidad_disponible_bien)}')
            else:
                mezcla = InventarioViveros.objects.filter(id_mezcla=one_bien['id_mezcla_consumida'], id_siembra_lote_germinacion=None, id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero).first()
                mezcla.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_mezclas_siembras(bien)
                if one_bien['cantidad'] > int(mezcla.cantidad_disponible_bien):
                    one_bien['cantidad_disponible'] = mezcla.cantidad_disponible_bien
                    raise ValidationError(f'La cantidad de la mezcla {mezcla.id_mezcla.nombre} elegida no puede superar su cantidad disponible {str(mezcla.cantidad_disponible_bien)}')

        #VALIDACIÓN QUE LOS BIENES CONSUMIDOS POR ACTUALIZAR EXISTAN
        bienes_actualizar_id = [bien['id_consumo_siembra'] for bien in bienes_actualizar]
        bienes_actualizar_instance = ConsumosSiembra.objects.filter(id_consumo_siembra__in=bienes_actualizar_id)
        if len(set(bienes_actualizar_id)) != len(bienes_actualizar_instance):
            raise ValidationError('Todos los bienes consumidos por actualizar deben existir')

        #VALIDAR CANTIDADES DE LOS QUE SE QUIEREN ACTUALIZAR
        for bien_actualizar in bienes_actualizar:
            bien_cantidad_disponible = None
            if bien_actualizar.get('id_bien_consumido'):
                bien_cantidad_disponible = InventarioViveros.objects.filter(id_bien=bien_actualizar['id_bien_consumido'], id_siembra_lote_germinacion=None, id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero).first()
                cantidad_disponible = UtilConservacion.get_cantidad_disponible_consumir(bien_cantidad_disponible)
                if cantidad_disponible < bien_actualizar['cantidad']:
                    raise ValidationError(f'El bien {bien_cantidad_disponible.id_bien.nombre} no tiene cantidades disponibles para consumirse')
            else:
                bien_cantidad_disponible = InventarioViveros.objects.filter(id_mezcla=bien_actualizar['id_mezcla_consumida'], id_siembra_lote_germinacion=None, id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero).first()
                cantidad_disponible = UtilConservacion.get_cantidad_disponible_mezclas_siembras(bien_cantidad_disponible)
                if cantidad_disponible < bien_actualizar['cantidad']:
                    raise ValidationError(f'La mezcla {bien_cantidad_disponible.id_mezcla.nombre} no tiene cantidades disponibles para consumirse')
            
        """
        
        Inicia el proceso de actualización
        
        """

        valores_actualizados_detalles = []

        for bien_actualizar in bienes_actualizar:
            bien_instance = ConsumosSiembra.objects.filter(id_consumo_siembra=bien_actualizar['id_consumo_siembra'], id_siembra=id_siembra).first()
            bien_instance_copy = copy.copy(bien_instance)
            
            bien_in_inventario_viveros_serializador = None
            
            if bien_actualizar.get('id_bien_consumido'):
                bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien_actualizar['id_bien_consumido'], id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
            else:
                bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_mezcla=bien_actualizar['id_mezcla_consumida'], id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
            
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
            
            valores_actualizados_detalles.append({'descripcion': {'NombreBienConsumido' : bien_instance.id_bien_consumido.nombre if bien_instance.id_bien_consumido else bien_instance.id_mezcla_consumida.nombre},'previous':bien_instance_copy,'current':bien_instance})
        
        """
        
        Inicia el proceso de creación
        
        """

        #CREACIÓN DE BIENES CONSUMIDOS
        bienes_consumidos_no_existentes = []
        valores_creados_detalles = []
        for bien in bienes_crear:
            bien_consumido = None
            
            if bien.get('id_bien_consumido'):
                bien_consumido = ConsumosSiembra.objects.filter(id_siembra=bien['id_siembra'], id_bien_consumido=bien['id_bien_consumido']).first()
            else:
                bien_consumido = ConsumosSiembra.objects.filter(id_siembra=bien['id_siembra'], id_mezcla_consumida=bien['id_mezcla_consumida']).first()
            
            if bien_consumido:
                bien_consumido.cantidad = bien_consumido.cantidad if bien_consumido.cantidad else 0
                bien_consumido.cantidad = bien_consumido.cantidad + bien['cantidad']
                bien_consumido.save()

                #SE AFECTA CANTIDAD CONSUMO INTERNO EN INVENTARIO VIVEROS
                bien_in_inventario_viveros_serializador = None
                
                if bien.get('id_bien_consumido'):
                    bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien['id_bien_consumido'], id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
                else:
                    bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_mezcla=bien['id_mezcla_consumida'], id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
                
                cantidad_existente_consumida = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
                bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_existente_consumida + bien['cantidad']
                bien_in_inventario_viveros_serializador.save()

                valores_creados_detalles.append({'NombreBienConsumido': bien_consumido.id_bien_consumido.nombre if bien_consumido.id_bien_consumido else bien_consumido.id_mezcla_consumida.nombre})
            else:
                bienes_consumidos_no_existentes.append(bien)

        valores_creados_detalles.extend(siembra_actualizada['valores_creados_detalles'])
        
        serializer = self.serializer_class_detalles(data=bienes_consumidos_no_existentes, many=True)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()

        #SE AFECTA LA CANTIDAD DISPONIBLE EN INVENTARIO VIVEROS
        # for bien in serializador:
        #     bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien.id_bien_consumido.id_bien, id_vivero=instancia_siembra_actualizada.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
        #     cantidad_existente_consumida = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
        #     bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_existente_consumida + bien.cantidad
        #     bien_in_inventario_viveros_serializador.save()

        # # AUDITORIA BIENES CONSUMIDOS DETALLE SIEMBRAS
        # for bien in serializador:
        #     valores_creados_detalles.append({'NombreBienConsumido': bien.id_bien_consumido.nombre})

        descripcion = {"NombreBienSembrado": str(instancia_siembra_actualizada.id_bien_sembrado.nombre), "NombreVivero": str(instancia_siembra_actualizada.id_vivero.id_vivero),"AñoLote": str(instancia_siembra_actualizada.agno_lote), "NroLote": str(instancia_siembra_actualizada.nro_lote)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 50,
            "cod_permiso": "AC",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_maestro": siembra_actualizada['valores_actualizados_maestro'],
            "valores_creados_detalles": valores_creados_detalles,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success': True, 'detail': 'Actualización exitosa'}, status=status.HTTP_201_CREATED)

class GetSiembraByIdView(generics.RetrieveAPIView):
    serializer_class = GetSiembraSerializer
    queryset = Siembras.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_siembra):
        siembra = Siembras.objects.filter(id_siembra=id_siembra).first()
        if not siembra:
            raise ValidationError('No se encontró ninguna siembra con el parámetro ingresado')
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
            raise ValidationError('No se encontró ninguna siembra con el parámetro ingresado')

        #VALIDACIÓN SI EXISTE EL CODIGO BIEN EN INVENTARIO VIVERO
        bien_in_inventario = InventarioViveros.objects.filter(Q(id_bien__codigo_bien=codigo_bien) & Q(id_vivero=id_vivero) & Q(id_bien__nivel_jerarquico=5)).first()
        if not bien_in_inventario:
            raise ValidationError('No existe el bien por consumir en el vivero seleccionado')
        if bien_in_inventario.id_bien.cod_tipo_elemento_vivero != 'IN' and bien_in_inventario.id_bien.cod_tipo_elemento_vivero != 'MV':
            raise PermissionDenied ('El bien seleccionado debe ser de tipo insumo o material vegetal')

        if bien_in_inventario.id_bien.cod_tipo_elemento_vivero == 'MV':
            if bien_in_inventario.id_bien.es_semilla_vivero != True:
                raise PermissionDenied('El bien seleccionado debe ser material vegetal de tipo semilla')

        bien_in_inventario.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_consumir(bien_in_inventario)
        if bien_in_inventario.cantidad_disponible_bien < 1:
            raise ValidationError('El bien seleccionado no tiene cantidades disponibles para consumir')

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

class GetBusquedaBienesConsumidosView(generics.ListAPIView):
    serializer_class = GetBienesPorConsumirSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_vivero):
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            raise NotFound('No se encontró ningún vivero con el parámetro ingresado')
        
        tipo_bien = request.query_params.get('cod_tipo_elemento_vivero')
        codigo_bien = request.query_params.get('codigo_bien', '')
        nombre = request.query_params.get('nombre', '')
        
        if tipo_bien:
            tipo_bien = 'id_mezcla' if tipo_bien == 'MZ' else 'id_bien'
        
        #CREACIÓN DE FILTROS SEGÚN QUERYPARAMS
        filter = {}
        for key, value in request.query_params.items():
            if key in ['cod_tipo_elemento_vivero', 'codigo_bien', 'nombre']:
                if tipo_bien:
                    if tipo_bien == 'id_bien' and key == 'nombre':
                        if value != '':
                            filter['id_bien__' + key+ '__icontains'] = value
                    elif tipo_bien == 'id_bien' and key == 'codigo_bien':
                        if value != '':
                            filter['id_bien__' + key+ '__icontains'] = value
                    elif tipo_bien == 'id_mezcla' and key == 'nombre':
                        if value != '':
                            filter['id_mezcla__'+key+'__icontains'] = value
                    elif tipo_bien == 'id_bien' and key == 'cod_tipo_elemento_vivero':
                        if value != '':
                            filter['id_bien__' + key] = value
                    elif tipo_bien == 'id_mezcla' and key == 'cod_tipo_elemento_vivero':
                        if value != '':
                            filter['id_bien__isnull'] = True

        bienes_por_consumir = InventarioViveros.objects.filter(id_vivero=id_vivero, id_siembra_lote_germinacion=None)
        bienes_filtrados = bienes_por_consumir.filter(**filter)
        bienes_filtrado_final = []
        for bien in bienes_filtrados:
            if bien.id_bien:
                if bien.id_bien.cod_tipo_elemento_vivero != 'HE' and bien.id_bien.cod_tipo_elemento_vivero != None and (bien.id_bien.cod_tipo_elemento_vivero=='IN' or (bien.id_bien.cod_tipo_elemento_vivero=='MV' and bien.id_bien.es_semilla_vivero==True)):
                    if not tipo_bien:
                        if codigo_bien in bien.id_bien.codigo_bien and nombre.lower() in bien.id_bien.nombre.lower():
                            bienes_filtrado_final.append(bien)
                    else:
                        bienes_filtrado_final.append(bien)
            elif bien.id_mezcla:
                if not tipo_bien:
                    if nombre.lower() in bien.id_mezcla.nombre.lower():
                        bienes_filtrado_final.append(bien)
                else:
                    bienes_filtrado_final.append(bien)
        
        if not bienes_filtrados:
            raise ValidationError('No existe ningún bien que se pueda consumir')
    
        #CAMBIAR VALORES EN CANTIDAD DISPONIBLE BIEN
        bien_con_cantidades = []
        for bien in bienes_filtrado_final:
            if bien.id_bien:
                if bien.id_bien.cod_tipo_elemento_vivero == 'MV' or bien.id_bien.cod_tipo_elemento_vivero == 'IN':
                    bien.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_consumir(bien)
                    
                    #VALIDACIÓN QUE LA CANTIDAD DISPONIBLE SEA MAYOR A 0
                    if bien.cantidad_disponible_bien > 0:
                        bien_con_cantidades.append(bien)
            else:
                bien.cantidad_disponible_bien = UtilConservacion.get_cantidad_disponible_mezclas_siembras(bien)
                
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
            raise ValidationError('No se encontró ninguna siembra con el parámetro ingresado')

        bienes_consumidos = ConsumosSiembra.objects.filter(id_siembra=id_siembra)
        serializer = self.serializer_class(bienes_consumidos, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

# class UpdateBienConsumidoView(generics.RetrieveUpdateAPIView):
#     serializer_class = UpdateBienesConsumidosSerializer
#     queryset = ConsumosSiembra.objects.all()
#     permission_classes = [IsAuthenticated]

#     def put(self, request, id_siembra):
        
# class DeleteBienesConsumidosView(generics.RetrieveDestroyAPIView):
#     serializer_class = DeleteBienesConsumidosSerializer
#     queryset = ConsumosSiembra.objects.all()
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, id_siembra):
        


class DeleteSiembraView(generics.RetrieveDestroyAPIView):
    serializer_class = DeleteSiembraSerializer
    queryset = Siembras.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_siembra):
        data_siembra = request.data
        
        #VALIDACIÓN QUE LA SIEMBRA EXISTA
        siembra = Siembras.objects.filter(id_siembra=id_siembra).first()
        if not siembra:
            raise ValidationError('No se encontró ninguna siembra con el parámetro ingresado')

        #VALIDACIÓN QUE NO SE PUEDA ELIMINAR UNA SIEMBRA QUE TIENE CAMBIOS DE ETAPAS
        siembra_in_inventario = InventarioViveros.objects.filter(id_siembra_lote_germinacion=id_siembra, cod_etapa_lote='G', id_vivero=siembra.id_vivero.id_vivero, id_bien=siembra.id_bien_sembrado.id_bien).first()
        if siembra_in_inventario.fecha_ult_altura_lote or siembra_in_inventario.siembra_lote_cerrada == True:
            raise PermissionDenied('No se puede eliminar una siembra que tiene cambios de etapa')

        #VALIDACIÓN QUE NO SE PUEDA ELIMINAR UNA SIEMBRA QUE TIENE REGISTROS EN CUARENTENA
        siembra_cuarentena = CuarentenaMatVegetal.objects.filter(id_vivero=siembra.id_vivero.id_vivero, id_bien=siembra.id_bien_sembrado.id_bien, agno_lote=siembra.agno_lote, nro_lote=siembra.nro_lote).first()
        if siembra_cuarentena:
            raise PermissionDenied('No se puede cerrar una siembra que se encuentra en cuarentena')

        camas_siembra = CamasGerminacionViveroSiembra.objects.filter(id_siembra=id_siembra)
        
        consumos_siembra = ConsumosSiembra.objects.filter(id_siembra=id_siembra)
        for bien_consumido in consumos_siembra:
            bien_in_inventario_viveros_serializador = None
            
            if bien_consumido.id_bien_consumido:
                bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien_consumido.id_bien_consumido.id_bien, id_vivero=siembra.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
            else:
                bien_in_inventario_viveros_serializador = InventarioViveros.objects.filter(id_bien=bien_consumido.id_mezcla_consumida.id_mezcla, id_vivero=siembra.id_vivero.id_vivero, id_siembra_lote_germinacion=None).first()
            
            cantidad_existente = bien_in_inventario_viveros_serializador.cantidad_consumos_internos if bien_in_inventario_viveros_serializador.cantidad_consumos_internos else 0
            bien_in_inventario_viveros_serializador.cantidad_consumos_internos = cantidad_existente - bien_consumido.cantidad
            bien_in_inventario_viveros_serializador.save()


        # AUDITORIA BIENES CONSUMIDOS DETALLE SIEMBRAS
        valores_eliminados_detalles = []
        for bien in consumos_siembra:
            valores_eliminados_detalles.append({'NombreBienConsumido': bien.id_bien_consumido.nombre})
        
        for cama in camas_siembra:
            valores_eliminados_detalles.append({'NombreCama': cama.id_cama_germinacion_vivero.nombre})
            
        descripcion = {"NombreBienSembrado": str(siembra.id_bien_sembrado.nombre), "Vivero": str(siembra.id_vivero.id_vivero),"Agno": str(siembra.agno_lote), "NroLote": str(siembra.nro_lote)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 50,
            "cod_permiso": "BO",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        consumos_siembra.delete()
        siembra_in_inventario.delete()
        camas_siembra.delete()
        siembra.delete()

        return Response({'success': True, 'detail': 'Siembra eliminada exitosamente'}, status=status.HTTP_200_OK)

class GetSiembrasView(generics.ListAPIView):
    serializer_class = GetSiembrasSerializer
    queryset = Siembras.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = self.queryset.all()
        serializer = self.serializer_class(data, many=True)
        return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)