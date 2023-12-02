from almacen.models.bienes_models import CatalogoBienes, EstadosArticulo, MetodosValoracionArticulos, TiposActivo, TiposDepreciacionActivos
from rest_framework import generics, status
from rest_framework.views import APIView
from almacen.choices.estados_articulo_choices import estados_articulo_CHOICES
from almacen.serializers.bienes_serializers import (
    CatalogoBienesSerializer,
    EntradaCreateSerializer,
    EntradaUpdateSerializer,
    CreateUpdateItemEntradaConsumoSerializer,
    SerializerItemEntradaActivosFijos,
    SerializerItemEntradaConsumo,
    SerializerUpdateItemEntradaActivosFijos,
    ItemEntradaSerializer,
    EntradaSerializer,
    CatalogoBienesActivoFijoPutSerializer,
    SerializerItemEntradaConsumoPut,
    TiposEntradasSerializer,
    CatalagoBienesYSerializer
)
from almacen.models.hoja_de_vida_models import (
    HojaDeVidaComputadores,
    HojaDeVidaVehiculos,
    HojaDeVidaOtrosActivos
)
from almacen.models.generics_models import (
    Bodegas,
)
from almacen.models.inventario_models import (
    Inventario,
    TiposEntradas
)
from almacen.utils import UtilAlmacen
from transversal.models.personas_models import (
    Personas
)
from almacen.serializers.inventario_serializers import (
    SerializerUpdateInventariosActivosFijos,
    SerializerUpdateInventariosConsumo
)
from almacen.models.generics_models import UnidadesMedida, PorcentajesIVA, Marcas
from almacen.models.bienes_models import EntradasAlmacen, ItemEntradaAlmacen
from seguridad.utils import Util
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timezone
import copy

class GeneradorCodigoCatalogo(generics.RetrieveAPIView):

    def generador_codigo_bien(self, bien_padre, nivel_jerarquico):
        niv_val = [[1,2,3,4,5],['0','0','00','000','00000'],['9','9','99','999','99999']]
        
        try:
            posicion = niv_val[0].index(nivel_jerarquico)
        except:
            raise ValidationError('El nivel jerarquico esta fuera de rango')

        catalago = CatalogoBienes.objects.filter(nivel_jerarquico=nivel_jerarquico)

        if bien_padre != None:
            catalago = catalago.filter(id_bien_padre = bien_padre.id_bien)

        catalago = catalago.order_by('codigo_bien').last()
        codigo_padre = bien_padre.codigo_bien if bien_padre != None else ''
        codigo_anterior  = catalago.codigo_bien[len(codigo_padre):] if catalago != None else niv_val[1][posicion]

        if codigo_anterior == niv_val[2][posicion]:
            raise ValidationError('No se puede generar mas codigos de bienes para este nivel jerarquico')
        
        codigo = str(int(codigo_padre+codigo_anterior) + 1)

        return codigo
    
    def get(self, request, *args, **kwargs):

        id_bien_padre = self.request.query_params.get('id_bien_padre', '')
        nivel_jerarquico = self.request.query_params.get('nivel_jerarquico', '')
        bien_padre = None

        if nivel_jerarquico == '':
            raise ValidationError('El nivel jerarquico es requerido')
        
        try:
            nivel_jerarquico = int(nivel_jerarquico)
        except:
            raise ValidationError('El nivel jerarquico debe ser un numero entero')
        
        if nivel_jerarquico < 1 or nivel_jerarquico > 5 or nivel_jerarquico == None:
            raise ValidationError('El nivel jerarquico esta fuera de rango')
        
        if id_bien_padre == '':
            id_bien_padre = None
        else:
            try:
                id_bien_padre = int(id_bien_padre)
            except:
                raise ValidationError('El id de bien padre debe ser un numero entero')
        
        if id_bien_padre != None:
            try:
                bien_padre = CatalogoBienes.objects.get(id_bien=id_bien_padre)
            except CatalogoBienes.DoesNotExist:
                raise ValidationError('El id de bien padre ingresado no existe')
            
            id_bien_padre = bien_padre.id_bien
            
            if nivel_jerarquico != (bien_padre.nivel_jerarquico + 1):
                raise ValidationError('El nivel jerarquico esta fuera de rango respeto al bien padre')
        
        codigo_bien = self.generador_codigo_bien(bien_padre, nivel_jerarquico)

        return Response({'success':True, 'detail':'Codigo de bien generado exitosamente', 'data':codigo_bien}, status=status.HTTP_200_OK)


class CatalogoBienesCreate(generics.CreateAPIView):
    serializer_class = CatalagoBienesYSerializer
    permission_classes = [IsAuthenticated]

    def create_catalogo_bienes(self, data):
        nivel_jerarquico = data['nivel_jerarquico']
        id_bien_padre = data['id_bien_padre']
        bien_padre = None
        
        if nivel_jerarquico < 1 or nivel_jerarquico > 5 or nivel_jerarquico == None:
            raise ValidationError('El nivel jerarquico esta fuera de rango')

        if id_bien_padre != None:
            try:
                bien_padre = CatalogoBienes.objects.get(id_bien=id_bien_padre)
            except CatalogoBienes.DoesNotExist:
                raise ValidationError('El id de bien padre ingresado no existe')
            
            id_bien_padre = bien_padre.id_bien
            
            if nivel_jerarquico != (bien_padre.nivel_jerarquico + 1):
                raise ValidationError('El nivel jerarquico esta fuera de rango')
            
        generador_instance = GeneradorCodigoCatalogo()
        data['codigo_bien'] = generador_instance.generador_codigo_bien(bien_padre, nivel_jerarquico)

        try:
            unidad_medida = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida'])
        except UnidadesMedida.DoesNotExist:
            raise ValidationError('El id de unidad de medida ingresado no existe')
        
        try:
            porcentaje_iva = PorcentajesIVA.objects.get(id_porcentaje_iva=data['id_porcentaje_iva'])
        except PorcentajesIVA.DoesNotExist:
            raise ValidationError('El id de porcentaje de iva ingresado no existe')
        
        catalogo_bien_data = {
            'nro_elemento_bien': data['nro_elemento_bien'],
            'codigo_bien': data['codigo_bien'],
            'nombre': data['nombre'],
            'cod_tipo_bien': data['cod_tipo_bien'],
            'nivel_jerarquico': data['nivel_jerarquico'],
            'descripcion': data['descripcion'],
            'id_unidad_medida': unidad_medida.id_unidad_medida,
            'id_porcentaje_iva': porcentaje_iva.id_porcentaje_iva,
            'visible_solicitudes': data['visible_solicitudes'],
            'id_bien_padre': id_bien_padre
        }

        if data['cod_tipo_bien'] == 'A':      
            try:
                unidad_medida_vida_util = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida_vida_util'])
            except UnidadesMedida.DoesNotExist:
                raise ValidationError('El id de unidad de medida vida util ingresado no existe')
            
            try:
                if data['id_marca']: marca = Marcas.objects.get(id_marca=data['id_marca'])
            except Marcas.DoesNotExist:
                raise ValidationError('El id de marca ingresado no existe')
            
            try:
                tipo_activo = TiposActivo.objects.filter(cod_tipo_activo=data['cod_tipo_activo']).first()
            except TiposActivo.DoesNotExist:
                raise ValidationError('El codigo de tipo de activo ingresado no existe')
            
            try:
                tipo_depreciacion = TiposDepreciacionActivos.objects.filter(cod_tipo_depreciacion=data['cod_tipo_depreciacion']).first()
            except TiposDepreciacionActivos.DoesNotExist:
                raise ValidationError('El codigo de tipo de depreciacion ingresado no existe')
            
            catalogo_bien_data['cod_tipo_activo'] = tipo_activo.cod_tipo_activo
            catalogo_bien_data['id_marca'] = marca.id_marca
            catalogo_bien_data['cod_tipo_depreciacion'] = tipo_depreciacion.cod_tipo_depreciacion
            catalogo_bien_data['cantidad_vida_util'] = data['cantidad_vida_util']
            catalogo_bien_data['id_unidad_medida_vida_util'] = unidad_medida_vida_util.id_unidad_medida
            catalogo_bien_data['valor_residual'] = data['valor_residual']
            catalogo_bien_data['maneja_hoja_vida'] = data['maneja_hoja_vida']

            serializer = self.serializer_class(data=catalogo_bien_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
        elif data['cod_tipo_bien'] == 'C':                              
            try:
                metodo_valoracion = MetodosValoracionArticulos.objects.filter(cod_metodo_valoracion=data['cod_metodo_valoracion']).first()
            except MetodosValoracionArticulos.DoesNotExist:
                raise ValidationError('El codigo de metodo de valoracion ingresado no existe')
            
            catalogo_bien_data['nombre_cientifico'] = data['nombre_cientifico']
            catalogo_bien_data['cod_metodo_valoracion'] = metodo_valoracion.cod_metodo_valoracion
            catalogo_bien_data['stock_minimo'] = data['stock_minimo']
            catalogo_bien_data['stock_maximo'] = data['stock_maximo']
            catalogo_bien_data['solicitable_vivero'] = data['solicitable_vivero']

            serializer = self.serializer_class(data=catalogo_bien_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        
        else:
            raise ValidationError('El codigo de tipo de bien ingresado no existe')
                        
        return serializer.data
            
    def post(self, request):
        data_in = request.data
        data = self.create_catalogo_bienes(data_in)

        if not data:
            raise ValidationError('No se pudo crear el bien')

        return Response({'success':True, 'detail':'Bien guardado exitosamente', 'data':data}, status=status.HTTP_201_CREATED)
            

class CatalogoBienesCreateUpdate(generics.UpdateAPIView):
    serializer_class = CatalagoBienesYSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request):
        data = request.data
        id_bien = data.get('id_bien')

        # CREATE
        if id_bien == None:
            catalogo_bien_instance = CatalogoBienesCreate()
            data = catalogo_bien_instance.create_catalogo_bienes(data)

            if not data:
                raise ValidationError('No se pudo crear el bien')

            return Response({'success':True, 'detail':'Bien guardado exitosamente', 'data':data}, status=status.HTTP_201_CREATED)

        # UPDATE
        else:
            try:
                catalogo_bien = CatalogoBienes.objects.get(id_bien=id_bien)
            except CatalogoBienes.DoesNotExist:
                raise ValidationError('No hay ningún bien referente al id bien ingresado')
            
            try:
                unidad_medida = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida'])
            except UnidadesMedida.DoesNotExist:
                raise ValidationError('El id de unidad de medida ingresado no existe')
            
            try:
                porcentaje_iva = PorcentajesIVA.objects.get(id_porcentaje_iva=data['id_porcentaje_iva'])
            except PorcentajesIVA.DoesNotExist:
                raise ValidationError('El id de porcentaje de iva ingresado no existe')
            
            catalogo_bien_data = {
                'nombre': data['nombre'],
                'descripcion': data['descripcion'],
                'id_unidad_medida': unidad_medida.id_unidad_medida,
                'id_porcentaje_iva': porcentaje_iva.id_porcentaje_iva,
                'visible_solicitudes': data['visible_solicitudes']
            }

            if data['cod_tipo_bien'] == 'A':      
                try:
                    unidad_medida_vida_util = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida_vida_util'])
                except UnidadesMedida.DoesNotExist:
                    raise ValidationError('El id de unidad de medida vida util ingresado no existe')
                
                try:
                    if data['id_marca']: marca = Marcas.objects.get(id_marca=data['id_marca'])
                except Marcas.DoesNotExist:
                    raise ValidationError('El id de marca ingresado no existe')
                
                try:
                    tipo_activo = TiposActivo.objects.filter(cod_tipo_activo=data['cod_tipo_activo']).first()
                except TiposActivo.DoesNotExist:
                    raise ValidationError('El codigo de tipo de activo ingresado no existe')
                
                try:
                    tipo_depreciacion = TiposDepreciacionActivos.objects.filter(cod_tipo_depreciacion=data['cod_tipo_depreciacion']).first()
                except TiposDepreciacionActivos.DoesNotExist:
                    raise ValidationError('El codigo de tipo de depreciacion ingresado no existe')
                
                catalogo_bien_data['id_marca'] = marca.id_marca
                catalogo_bien_data['cod_tipo_activo'] = tipo_activo.cod_tipo_activo
                catalogo_bien_data['cod_tipo_depreciacion'] = tipo_depreciacion.cod_tipo_depreciacion
                catalogo_bien_data['id_unidad_medida_vida_util'] = unidad_medida_vida_util.id_unidad_medida
                catalogo_bien_data['cantidad_vida_util'] = data['cantidad_vida_util']
                catalogo_bien_data['valor_residual'] = data['valor_residual']
                catalogo_bien_data['maneja_hoja_vida'] = data['maneja_hoja_vida']

                serializer = self.get_serializer(catalogo_bien, data=catalogo_bien_data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
            elif data['cod_tipo_bien'] == 'C':                              
                try:
                    metodo_valoracion = MetodosValoracionArticulos.objects.filter(cod_metodo_valoracion=data['cod_metodo_valoracion']).first()
                except MetodosValoracionArticulos.DoesNotExist:
                    raise ValidationError('El codigo de metodo de valoracion ingresado no existe')
                
                catalogo_bien_data['cod_metodo_valoracion'] = metodo_valoracion.cod_metodo_valoracion
                catalogo_bien_data['stock_minimo'] = data['stock_minimo']
                catalogo_bien_data['stock_maximo'] = data['stock_maximo']
                catalogo_bien_data['solicitable_vivero'] = data['solicitable_vivero']

                serializer = self.get_serializer(catalogo_bien, data=catalogo_bien_data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            
            else:
                raise ValidationError('El codigo de tipo de bien ingresado no existe')
            
            return Response({'success':True, 'detail':'Bien guardado exitosamente', 'data':data}, status=status.HTTP_201_CREATED)


class CatalogoBienesGetList(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer

    def get_catalogo_bienes(self, id_bien_padre, cont_padre):
        catalogo_bienes = CatalogoBienes.objects.filter(nro_elemento_bien=None, id_bien_padre=id_bien_padre).order_by('codigo_bien')
        serializer = self.serializer_class(catalogo_bienes, many=True)
        cont = 0
        data_out = []
        data_padre = serializer.data

        for data in data_padre:
            key = cont_padre + '-' + str(cont) if cont_padre != None else str(cont)
            data_out.append({
                'key': key,
                'data': {
                    'nombre': data['nombre'],
                    'codigo': data['codigo_bien'],
                    'id_nodo': data['id_bien'],
                    'editar': True,
                    'eliminar': False if CatalogoBienes.objects.filter(id_bien_padre=data['id_bien']).exists() else True,
                    'crear': data['nivel_jerarquico'] != 5,
                    'bien': data,
                },
                'children': self.get_catalogo_bienes(data['id_bien'], key)
            })

            # if data_out['children'] == []:
            #     data_out['eliminar'] = True
            #     del data_out['children']

            cont += 1
        return data_out
    
    def get(self, request):
        data = self.get_catalogo_bienes(None, None)

        return Response({'success':True, 'detail':'Se muestran el catalogo de bienes', 'data':data}, status=status.HTTP_200_OK)
    

# class CatalogoBienesGetList(generics.ListAPIView):
#     serializer_class = CatalogoBienesSerializer

#     def get_catalogo_bienes(self, id_bien_padre):
#         catalogo_bienes = CatalogoBienes.objects.filter(id_bien_padre=id_bien_padre).order_by('codigo_bien')
#         serializer = self.serializer_class(catalogo_bienes, many=True)
#         data_padre = serializer.data

#         for data in data_padre:
#             data['children'] = self.get_catalogo_bienes(data['id_bien'])
#             if data['children'] == []:
#                 del data['children']

#         return data_padre

#     def get(self, request):

#         data = self.get_catalogo_bienes(None)

#         return Response({'success': True, 'detail':'Se muestran el catalogo de bienes', 'data': data}, status=status.HTTP_200_OK)
    

# class CatalogoBienesGetList(generics.ListAPIView):
#     serializer_class = CatalogoBienesSerializer

#     def get_catalogo_bienes(self, id_bien_padre):
#         catalogo_bienes = CatalogoBienes.objects.filter(id_bien_padre=id_bien_padre).order_by('codigo_bien')
#         serializer = self.serializer_class(catalogo_bienes, many=True)
#         data_padre = serializer.data
#         data_out = {}
#         cont = 0

#         for data in data_padre:
#             data_out['key'] = str(cont)
#             data_out['data'] = {
#                 'nombre': data['nombre'],
#                 'codigo': data['codigo_bien'],
#                 'id_nodo': data['id_bien'],
#                 'editar': True,
#                 'eliminar': False,
#                 'crear': data['nivel_jerarquico'] != 5,
#                 'bien': data,
#             }
#             data_out['children'] = self.get_catalogo_bienes(data['id_bien'])

            # if data_out['children'] == []:
            #     data_out['eliminar'] = True
            #     del data_out['children']

#             data_padre[cont] = data_out
#             cont += 1

#         return data_padre

#     def get(self, request):

#         data = self.get_catalogo_bienes(None)

#         return Response({'success': True, 'detail':'Se muestran el catalogo de bienes', 'data': data}, status=status.HTTP_200_OK)


# class CatalogoBienesGetList(generics.ListAPIView):
#     serializer_class = CatalogoBienesSerializer

#     def crear_data(self, nodo, nodos_hijos):
#         return {
#             'key': str(nodo['id_bien']),
#             'data': {
#                 'nombre': nodo['nombre'],
#                 'codigo': nodo['codigo_bien'],
#                 'id_nodo': nodo['id_bien'],
#                 'editar': True,
#                 'eliminar': not bool(nodos_hijos),
#                 'crear': True,
#                 'bien': nodo,
#             },
#             'children': nodos_hijos,
#         }

#     def get(self, request):
#         nodos = CatalogoBienes.objects.filter(nro_elemento_bien=None).order_by('nivel_jerarquico')
#         nodos = self.serializer_class(nodos, many=True).data

#         if not nodos:
#             return Response({'success':True, 'detail':'No se encontró nada en almacén', 'data':nodos}, status=status.HTTP_200_OK)

#         nodos_por_nivel = {i: [] for i in range(1, 6)}
#         for nodo in nodos:
#             nodos_por_nivel[nodo['nivel_jerarquico']].append(nodo)

#         for nivel in range(5, 1, -1):
#             for nodo in nodos_por_nivel[nivel]:
#                 nodo_padre = next((n for n in nodos_por_nivel[nivel - 1] if n['id_bien'] == nodo['id_bien_padre']), None)
#                 if nodo_padre:
#                     if 'children' not in nodo_padre:
#                         nodo_padre['children'] = []
#                     nodo_padre['children'].append(self.crear_data(nodo, nodo.get('children', [])))

#         data_all = [self.crear_data(nodo, nodo.get('children', [])) for nodo in nodos_por_nivel[1]]

#         return Response({'success':True, 'detail':'Se encontró lo siguiente en almacén', 'data':data_all}, status=status.HTTP_200_OK)


# Creación y actualización de Catalogo de Bienes

class ValidacionCodigoBien(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,nivel,codigo_bien):
        if not codigo_bien.isdigit():
            raise ValidationError('El códgio debe ser un número')
        match nivel:
            case '1':
                if len(codigo_bien) != 1:
                    raise ValidationError('El nivel 1 solo puede tener un caracter')
                if int(codigo_bien) < 1 or int(codigo_bien) > 9:
                    raise ValidationError('El nivel 1 debe ser un número entre 1 y 9')
            case '2':
                if len(codigo_bien) != 2:
                    raise ValidationError('El nivel 2 debe ser de 2 caracteres')
                codigo_padre = codigo_bien[0]
                bien_padre = CatalogoBienes.objects.filter(
                    codigo_bien=codigo_padre)
                if not bien_padre:
                    raise ValidationError('El padre no existe')
            case '3':
                if len(codigo_bien) != 4:
                    raise ValidationError('El nivel 3 debe ser de 4 caracteres')
                codigo_padre = codigo_bien[0:2]
                bien_padre = CatalogoBienes.objects.filter(
                    codigo_bien=codigo_padre)
                if not bien_padre:
                    raise ValidationError('El padre no existe')
            case '4':
                if len(codigo_bien) != 7:
                    raise ValidationError('El nivel 4 debe ser de 7 caracteres')
                codigo_padre = codigo_bien[0:4]
                bien_padre = CatalogoBienes.objects.filter(
                    codigo_bien=codigo_padre)
                if not bien_padre:
                    raise ValidationError('El padre no existe')
            case '5':
                if len(codigo_bien) != 12:
                    raise ValidationError('El nivel 5 debe ser de 12 caracteres')
                codigo_padre = codigo_bien[0:7]
                bien_padre = CatalogoBienes.objects.filter(
                    codigo_bien=codigo_padre)
                if not bien_padre:
                    raise ValidationError('El padre no existe')
            case _:
                raise ValidationError('Ingrese un nivel válido, un numero entre 1 y 5')

        aux_bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien)
        if aux_bien:
            raise ValidationError('El código ingresado ya existe')
        return Response({'success':True, 'detail':'Codigo de bien válido'}, status=status.HTTP_201_CREATED)


class CreateCatalogoDeBienes(generics.UpdateAPIView):
    serializer_class = CatalogoBienesSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request):
        data = request.data

        # Update
        if data['id_bien'] != None:
            catalogo_bien = CatalogoBienes.objects.filter(id_bien=data['id_bien']).first()
            if catalogo_bien:
                try:
                    id_unidad_medida = UnidadesMedida.objects.get(
                        id_unidad_medida=data['id_unidad_medida'])
                    pass
                except:
                    raise ValidationError('El id de unidad de medida ingresado no existe')
                try:
                    id_porcentaje_iva = PorcentajesIVA.objects.get(
                        id_porcentaje_iva=data['id_porcentaje_iva'])
                    pass
                except:
                    raise ValidationError('El id de porcentaje de iva ingresado no existe')
                if data['cod_tipo_bien'] == 'A':
                    try:
                        id_unidad_medida_vida_util = UnidadesMedida.objects.get(
                            id_unidad_medida=data['id_unidad_medida_vida_util'])
                        pass
                    except:
                        raise ValidationError('El id de unidad de medida vida util ingresado no existe')
                try:
                    if data['id_marca']:
                        id_marca = Marcas.objects.get(id_marca=data['id_marca'])
                    pass
                except:
                    raise ValidationError('El id de marca ingresado no existe')

                match data['cod_tipo_bien']:
                    case 'A':
                        cod_tipo_activo_instance = TiposActivo.objects.filter(cod_tipo_activo=data['cod_tipo_activo']).first()
                        cod_tipo_depreciacion_instance = TiposDepreciacionActivos.objects.filter(cod_tipo_depreciacion=data['cod_tipo_depreciacion']).first()
                        catalogo_bien.nombre = data['nombre']
                        catalogo_bien.cod_tipo_activo = cod_tipo_activo_instance
                        catalogo_bien.id_porcentaje_iva = id_porcentaje_iva
                        catalogo_bien.cod_tipo_depreciacion = cod_tipo_depreciacion_instance
                        catalogo_bien.id_unidad_medida_vida_util = id_unidad_medida_vida_util
                        catalogo_bien.cantidad_vida_util = data['cantidad_vida_util']
                        catalogo_bien.valor_residual = data['valor_residual']
                        catalogo_bien.id_marca = id_marca
                        catalogo_bien.maneja_hoja_vida = data['maneja_hoja_vida']
                        catalogo_bien.visible_solicitudes = data['visible_solicitudes']
                        catalogo_bien.descripcion = data['descripcion']
                        catalogo_bien.save()
                        serializer = CatalogoBienesSerializer(
                            catalogo_bien, many=False)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    case 'C':
                        cod_metodo_valoracion_instance = MetodosValoracionArticulos.objects.filter(cod_metodo_valoracion=data['cod_metodo_valoracion']).first()
                        catalogo_bien.nombre = data['nombre']
                        catalogo_bien.cod_metodo_valoracion = cod_metodo_valoracion_instance
                        catalogo_bien.descripcion = data['descripcion']
                        catalogo_bien.id_unidad_medida = id_unidad_medida
                        catalogo_bien.id_porcentaje_iva = id_porcentaje_iva
                        catalogo_bien.stock_minimo = data['stock_minimo']
                        catalogo_bien.stock_maximo = data['stock_maximo']
                        catalogo_bien.solicitable_vivero = data['solicitable_vivero']
                        catalogo_bien.visible_solicitudes = data['visible_solicitudes']

                        catalogo_bien.save()
                        serializer = CatalogoBienesSerializer(
                            catalogo_bien, many=False)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    case _:
                        raise ValidationError('No hay ningun bien referente al id_bien enviado')
            else:
                raise ValidationError('No hay ningun bien referente al id_bien enviado')
        # Create
        else:
            # match de los 5 niveles jerarquicos
            match data['nivel_jerarquico']:
                case 1:
                    if int(data['codigo_bien']) >= 1 and len(data['codigo_bien']) == 1:
                        if CatalogoBienes.objects.filter(codigo_bien=data['codigo_bien']).exists():
                            raise ValidationError('Ya existe un codigo de bien relacionado en catalogo de bienes')
                        else:
                            nivel_bien_padre = None

                    else:
                        print(len(data['codigo_bien']))
                        raise ValidationError('Codigo bien fuera de rango')
                case 2:
                    if (int(data['codigo_bien'][0])) >= 1 and len(data['codigo_bien']) == 2:
                        if CatalogoBienes.objects.filter(codigo_bien=data['codigo_bien']).exists():
                            raise ValidationError('Ya existe un codigo de bien relacionado en catalogo de bienes')
                        else:
                            nivel_bien_padre = 1
                    else:
                        print((int(data['codigo_bien'][0])) >= 1)
                        print(len(data['codigo_bien']) == 2)
                        raise ValidationError('Codigo bien fuera de rango')
                case 3:
                    if int(data['codigo_bien'][0]) >= 1 and len(data['codigo_bien']) == 4:
                        if CatalogoBienes.objects.filter(codigo_bien=data['codigo_bien']).exists():
                            raise ValidationError('Ya existe un codigo de bien relacionado en catalogo de bienes')
                        else:
                            nivel_bien_padre = 2
                    else:
                        raise ValidationError('Codigo bien fuera de rango')
                case 4:
                    if int(data['codigo_bien'][0]) >= 1 and len(data['codigo_bien']) == 7:
                        if CatalogoBienes.objects.filter(codigo_bien=data['codigo_bien']).exists():
                            raise ValidationError('Ya existe un codigo de bien relacionado en catalogo de bienes')
                        else:
                            nivel_bien_padre = 3
                    else:
                        raise ValidationError('Codigo bien fuera de rango')
                case 5:
                    if int(data['codigo_bien'][0]) >= 1 and len(data['codigo_bien']) == 12:
                        nivel_bien_padre = 4
                    else:
                        raise ValidationError('Codigo bien fuera de rango')
                case _:
                    raise ValidationError('Nivel jerarquico fuera de rango')

            match data['cod_tipo_bien']:
                case 'A':
                    if CatalogoBienes.objects.filter(id_bien=data['id_bien_padre']).exists():
                        padre = CatalogoBienes.objects.get(
                            id_bien=data['id_bien_padre'])
                        nivel_padre = padre.nivel_jerarquico
                        #Crear un catalogo bien para nivel jerarquiro 1 activo fijo
                        if data['nivel_jerarquico']>1 and nivel_padre==nivel_bien_padre:
                                try:
                                    id_unidad_medida = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida'])
                                    pass
                                except:
                                   raise ValidationError('El id de unidad de medida ingresado no existe')
                                try:
                                    id_porcentaje_iva = PorcentajesIVA.objects.get(id_porcentaje_iva=data['id_porcentaje_iva'])
                                    pass
                                except:
                                    raise ValidationError('El id de porcentaje de iva ingresado no existe')
                                try:
                                    id_unidad_medida_vida_util = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida_vida_util'])
                                    pass
                                except:
                                    raise ValidationError('El id de unidad de medida vida util ingresado no existe')
                                try:
                                    if data['id_marca']:
                                        id_marca = Marcas.objects.get(id_marca=data['id_marca'])
                                    pass
                                except:
                                    raise ValidationError('El id de marca ingresado no existe')
                                
                                cod_tipo_activo_instance = TiposActivo.objects.filter(cod_tipo_activo=data['cod_tipo_activo']).first()
                                cod_tipo_depreciacion_instance = TiposDepreciacionActivos.objects.filter(cod_tipo_depreciacion=data['cod_tipo_depreciacion']).first()
                                catalogo_bien = CatalogoBienes.objects.create(
                                    id_bien=data['id_bien'],
                                    codigo_bien=data['codigo_bien'],
                                    nombre=data['nombre'],
                                    cod_tipo_bien=data['cod_tipo_bien'],
                                    cod_tipo_activo=cod_tipo_activo_instance,
                                    nivel_jerarquico=data['nivel_jerarquico'],
                                    descripcion=data['descripcion'],
                                    id_marca=id_marca,
                                    id_unidad_medida=id_unidad_medida,
                                    id_porcentaje_iva=id_porcentaje_iva,
                                    cod_tipo_depreciacion=cod_tipo_depreciacion_instance,
                                    cantidad_vida_util=data['cantidad_vida_util'],
                                    id_unidad_medida_vida_util=id_unidad_medida_vida_util,
                                    valor_residual=data['valor_residual'],
                                    maneja_hoja_vida=data['maneja_hoja_vida'],
                                    visible_solicitudes=data['visible_solicitudes'],
                                    id_bien_padre=padre  
                                )
                                serializer = self.serializer_class(catalogo_bien)
                        else:
                            raise ValidationError('el nivel del bien padre no corresponde con el nivel anterior')
                    elif data['nivel_jerarquico'] == 1:
                            try:
                                id_unidad_medida = UnidadesMedida.objects.get(
                                    id_unidad_medida=data['id_unidad_medida'])
                                pass
                            except:
                                raise ValidationError('El id de unidad de medida ingresado no existe')
                            try:
                                id_porcentaje_iva = PorcentajesIVA.objects.get(
                                    id_porcentaje_iva=data['id_porcentaje_iva'])
                                pass
                            except:
                                raise ValidationError('El id de porcentaje de iva ingresado no existe')
                            try:
                                id_unidad_medida_vida_util = UnidadesMedida.objects.get(
                                    id_unidad_medida=data['id_unidad_medida_vida_util'])
                                pass
                            except:
                                raise ValidationError('El id de unidad de medida vida util ingresado no existe')
                            try:
                                if data['id_marca']:
                                    id_marca = Marcas.objects.get(id_marca=data['id_marca'])
                                pass
                            except:
                                raise ValidationError('El id de marca ingresado no existe')
                            
                            cod_tipo_activo_instance = TiposActivo.objects.filter(cod_tipo_activo=data['cod_tipo_activo']).first()
                            cod_tipo_depreciacion_instance = TiposDepreciacionActivos.objects.filter(cod_tipo_depreciacion=data['cod_tipo_depreciacion']).first()
                            catalogo_bien = CatalogoBienes.objects.create(
                                id_bien=data['id_bien'],
                                codigo_bien=data['codigo_bien'],
                                nombre=data['nombre'],
                                cod_tipo_bien=data['cod_tipo_bien'],
                                cod_tipo_activo=cod_tipo_activo_instance,
                                nivel_jerarquico=data['nivel_jerarquico'],
                                descripcion=data['descripcion'],
                                id_marca=id_marca,
                                id_unidad_medida=id_unidad_medida,
                                id_porcentaje_iva=id_porcentaje_iva,
                                cod_tipo_depreciacion=cod_tipo_depreciacion_instance,
                                cantidad_vida_util=data['cantidad_vida_util'],
                                id_unidad_medida_vida_util=id_unidad_medida_vida_util,
                                valor_residual=data['valor_residual'],
                                maneja_hoja_vida=data['maneja_hoja_vida'],
                                visible_solicitudes=data['visible_solicitudes'],
                                id_bien_padre=None
                            )
                            serializer = self.serializer_class(catalogo_bien)
                case 'C':
                    if CatalogoBienes.objects.filter(id_bien=data['id_bien_padre']).exists():
                        padre = CatalogoBienes.objects.get(
                            id_bien=data['id_bien_padre'])
                        nivel_padre = padre.nivel_jerarquico
                        # Crear un catalogo bien para nivel jerarquiro 1 activo fijo
                        if data['nivel_jerarquico'] > 1 and nivel_padre == nivel_bien_padre:
                            try:
                                id_unidad_medida = UnidadesMedida.objects.get(
                                    id_unidad_medida=data['id_unidad_medida'])
                                pass
                            except:
                                raise ValidationError('El id de unidad de medida ingresado no existe')
                            try:
                                id_porcentaje_iva = PorcentajesIVA.objects.get(
                                    id_porcentaje_iva=data['id_porcentaje_iva'])
                                pass
                            except:
                                raise ValidationError('El id de porcentaje de iva ingresado no existe')
                            
                            cod_metodo_valoracion_instance = MetodosValoracionArticulos.objects.filter(cod_metodo_valoracion=data['cod_metodo_valoracion']).first()
                            catalogo_bien = CatalogoBienes.objects.create(
                                id_bien=data['id_bien'],
                                codigo_bien=data['codigo_bien'],
                                nombre=data['nombre'],
                                cod_tipo_bien=data['cod_tipo_bien'],
                                nivel_jerarquico=data['nivel_jerarquico'],
                                nombre_cientifico=data['nombre_cientifico'],
                                descripcion=data['descripcion'],
                                id_unidad_medida=id_unidad_medida,
                                id_porcentaje_iva=id_porcentaje_iva,
                                cod_metodo_valoracion=cod_metodo_valoracion_instance,
                                stock_minimo=data['stock_minimo'],
                                stock_maximo=data['stock_maximo'],
                                solicitable_vivero=data['solicitable_vivero'],
                                visible_solicitudes=data['visible_solicitudes'],
                                id_bien_padre=padre
                            )
                            serializer = self.serializer_class(catalogo_bien)
                        else:
                            raise ValidationError('el nivel del bien padre no corresponde con el nivel anterior')
                    elif data['nivel_jerarquico'] == 1:
                        try:
                            id_unidad_medida = UnidadesMedida.objects.get(
                                id_unidad_medida=data['id_unidad_medida'])
                            pass
                        except:
                            raise ValidationError('El id de unidad de medida ingresado no existe')
                        try:
                            id_porcentaje_iva = PorcentajesIVA.objects.get(
                                id_porcentaje_iva=data['id_porcentaje_iva'])
                            pass
                        except:
                            raise ValidationError('El id de porcentaje de iva ingresado no existe')

                        cod_metodo_valoracion_instance = MetodosValoracionArticulos.objects.filter(cod_metodo_valoracion=data['cod_metodo_valoracion']).first()
                        catalogo_bien = CatalogoBienes.objects.create(
                            id_bien=data['id_bien'],
                            codigo_bien=data['codigo_bien'],
                            nombre=data['nombre'],
                            cod_tipo_bien=data['cod_tipo_bien'],
                            nivel_jerarquico=data['nivel_jerarquico'],
                            nombre_cientifico=data['nombre_cientifico'],
                            descripcion=data['descripcion'],
                            id_unidad_medida=id_unidad_medida,
                            id_porcentaje_iva=id_porcentaje_iva,
                            cod_metodo_valoracion=cod_metodo_valoracion_instance,
                            stock_minimo=data['stock_minimo'],
                            stock_maximo=data['stock_maximo'],
                            solicitable_vivero=data['solicitable_vivero'],
                            visible_solicitudes=data['visible_solicitudes'],
                            id_bien_padre=None
                        )
                        serializer = self.serializer_class(catalogo_bien)
                            
            return Response({'success':True, 'detail':'Bien guardado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)


class GetCatalogoBienesList(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()

    def get(self, request):
        # GET TODOS LOS NODOS
        nodos_principales = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=1).order_by('codigo_bien')
        nodos_principales = self.serializer_class(nodos_principales, many=True).data
        if not nodos_principales:
            return Response({'success':True, 'detail':'No se encontró nada en almacén', 'data':nodos_principales}, status=status.HTTP_200_OK)
        
        data_all = []
        cont_all = 0
        
        for nodo in nodos_principales:
            data = {}
            data['key'] = str(cont_all)
            data['data'] = {}
            data['data']['nombre'] = nodo['nombre']
            data['data']['codigo'] = nodo['codigo_bien']
            data['data']['id_nodo'] = nodo['id_bien']
            data['data']['editar'] = True
            
            nodos_nivel_dos = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=2, id_bien_padre=nodo['id_bien']).order_by('codigo_bien')
            nodos_nivel_dos = self.serializer_class(nodos_nivel_dos, many=True).data
            
            data['data']['eliminar'] = True if not nodos_nivel_dos else False
            data['data']['crear'] = True
            data['data']['bien'] = nodo
            data['children'] = []
            if nodos_nivel_dos:
                #nodo['nodos_hijos'] = nodos_nivel_dos
                cont_dos = 0
                for nodo_dos in nodos_nivel_dos:
                    data_dos = {}
                    data_dos['key'] = str(cont_all) + "-" + str(cont_dos)
                    data_dos['data'] = {}
                    data_dos['data']['nombre'] = nodo_dos['nombre']
                    data_dos['data']['codigo'] = nodo_dos['codigo_bien']
                    data_dos['data']['id_nodo'] = nodo_dos['id_bien']
                    data_dos['data']['editar'] = True
                    
                    nodos_nivel_tres = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=3, id_bien_padre=nodo_dos['id_bien']).order_by('codigo_bien')
                    nodos_nivel_tres = self.serializer_class(nodos_nivel_tres, many=True).data
                    
                    data_dos['data']['eliminar'] = True if not nodos_nivel_tres else False
                    data_dos['data']['crear'] = True
                    data_dos['data']['bien'] = nodo_dos
                    data_dos['children'] = []
                    if nodos_nivel_tres:
                        #nodo_dos['nodos_hijos'] = nodos_nivel_tres
                        cont_tres = 0
                        for nodo_tres in nodos_nivel_tres:
                            data_tres = {}
                            data_tres['key'] = str(cont_all) + "-" + str(cont_dos) + "-" + str(cont_tres)
                            data_tres['data'] = {}
                            data_tres['data']['nombre'] = nodo_tres['nombre']
                            data_tres['data']['codigo'] = nodo_tres['codigo_bien']
                            data_tres['data']['id_nodo'] = nodo_tres['id_bien']
                            data_tres['data']['editar'] = True
                            
                            nodos_nivel_cuatro = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=4, id_bien_padre=nodo_tres['id_bien']).order_by('codigo_bien')
                            nodos_nivel_cuatro = self.serializer_class(nodos_nivel_cuatro, many=True).data
                            
                            data_tres['data']['eliminar'] = True if not nodos_nivel_cuatro else False
                            data_tres['data']['crear'] = True
                            data_tres['data']['bien'] = nodo_tres
                            data_tres['children'] = []
                            if nodos_nivel_cuatro:
                                #nodo_tres['nodos_hijos'] = nodos_nivel_cuatro
                                cont_cuatro = 0
                                for nodo_cuatro in nodos_nivel_cuatro:
                                    data_cuatro = {}
                                    data_cuatro['key'] = str(cont_all) + "-" + str(cont_dos) + "-" + str(cont_tres) + "-" + str(cont_cuatro)
                                    data_cuatro['data'] = {}
                                    data_cuatro['data']['nombre'] = nodo_cuatro['nombre']
                                    data_cuatro['data']['codigo'] = nodo_cuatro['codigo_bien']
                                    data_cuatro['data']['id_nodo'] = nodo_cuatro['id_bien']
                                    data_cuatro['data']['editar'] = True
                                    
                                    nodos_nivel_cinco = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=5, id_bien_padre=nodo_cuatro['id_bien']).order_by('codigo_bien')
                                    nodos_nivel_cinco = self.serializer_class(nodos_nivel_cinco, many=True).data
                                    
                                    data_cuatro['data']['eliminar'] = True if not nodos_nivel_cinco else False
                                    data_cuatro['data']['crear'] = True
                                    data_cuatro['data']['bien'] = nodo_cuatro
                                    data_cuatro['children'] = []
                                    if nodos_nivel_cinco:
                                        #nodo_cuatro['nodos_hijos'] = nodos_nivel_cinco
                                        cont_cinco = 0
                                        for nodo_cinco in nodos_nivel_cinco:
                                            data_cinco = {}
                                            data_cinco['key'] = str(cont_all) + "-" + str(cont_dos) + "-" + str(cont_tres) + "-" + str(cont_cuatro) + "-" + str(cont_cinco)
                                            data_cinco['data'] = {}
                                            data_cinco['data']['nombre'] = nodo_cinco['nombre']
                                            data_cinco['data']['codigo'] = nodo_cinco['codigo_bien']
                                            data_cinco['data']['id_nodo'] = nodo_cinco['id_bien']
                                            data_cinco['data']['editar'] = True
                                            
                                            elementos = CatalogoBienes.objects.filter(~Q(nro_elemento_bien=None) & Q(codigo_bien=nodo_cinco['codigo_bien']))
                                            
                                            data_cinco['data']['eliminar'] = True if not elementos else False
                                            data_cinco['data']['crear'] = False
                                            data_cinco['data']['bien'] = nodo_cinco
                                            data_cinco['children'] = []
                                            data_cuatro['children'].append(data_cinco)
                                            cont_cinco += 1
                                    data_tres['children'].append(data_cuatro)
                                    cont_cuatro += 1
                            data_dos['children'].append(data_tres)
                            cont_tres += 1
                    data['children'].append(data_dos)
                    cont_dos += 1
            data_all.append(data)
            cont_all += 1
        return Response({'success':True, 'detail':'Se encontró lo siguiente en almacén', 'data':data_all}, status=status.HTTP_200_OK)


class DeleteNodos(generics.RetrieveDestroyAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    lookup_field = 'id_bien'
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_bien):
        nodo = CatalogoBienes.objects.filter(id_bien=id_bien).first()
        if nodo:
            if nodo.nro_elemento_bien:
                registra_movimiento = Inventario.objects.filter(
                    id_bien=nodo.id_bien)
                if registra_movimiento:
                    raise ValidationError('No se puede eliminar un elemento que tenga movimientos en inventario')
                nodo.delete()

                # Auditoria Crear Organigrama
                usuario = request.user.id_usuario
                descripcion = {"Codigo bien": str(
                    nodo.codigo_bien), "Numero elemento bien": str(nodo.nro_elemento_bien)}
                direccion = Util.get_client_ip(request)
                auditoria_data = {
                    "id_usuario": usuario,
                    "id_modulo": 18,
                    "cod_permiso": "BO",
                    "subsistema": 'ALMA',
                    "dirip": direccion,
                    "descripcion": descripcion,
                }
                Util.save_auditoria(auditoria_data)
                return Response({'success':True, 'detail':'Eliminado el elemento'}, status=status.HTTP_200_OK)

            hijos = CatalogoBienes.objects.filter(id_bien_padre=nodo.id_bien)
            if hijos:
                raise PermissionDenied('No se puede eliminar un bien si es padre de otros bienes')
            nodo.delete()

            # Auditoria borrar catalogo
            usuario = request.user.id_usuario
            descripcion = {"Codigo bien": str(
                nodo.codigo_bien), "Numero elemento bien": str(nodo.nro_elemento_bien)}
            direccion = Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario": usuario,
                "id_modulo": 18,
                "cod_permiso": "BO",
                "subsistema": 'ALMA',
                "dirip": direccion,
                "descripcion": descripcion,
            }
            Util.save_auditoria(auditoria_data)
            return Response({'success':True, 'detail':'Se ha eliminado el bien correctamente'}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No se encontró ningún nodo con el parámetro ingresado')


class GetElementosByIdNodo(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()

    def get(self, request, id_nodo):
        nodo = CatalogoBienes.objects.filter(id_bien=id_nodo).first()
        if nodo:
            id_nodo = nodo.codigo_bien
            elementos = CatalogoBienes.objects.filter(
                Q(codigo_bien=id_nodo) & ~Q(nro_elemento_bien=None))
            elementos_serializer = self.serializer_class(elementos, many=True)
            return Response({'success':True, 'detail':'Busqueda exitosa', 'data': elementos_serializer.data})
        else:
            raise NotFound('No se encontró ningún elemento con el parámetro ingresado')


class SearchArticuloByDocIdentificador(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        for key, value in request.query_params.items():
            if key in ['cod_tipo_activo', 'doc_identificador_nro']:
                filter[key] = value
        if not filter.get('doc_identificador_nro'):
            raise NotFound('Debe enviar el parametro de número de identificación del bien')
        if not filter.get('cod_tipo_activo'):
            raise NotFound('Debe enviar el parametro del tipo de activo')

        bien = CatalogoBienes.objects.filter(**filter).filter(nivel_jerarquico=5).exclude(nro_elemento_bien=None).first()
        if bien:
            serializer = self.serializer_class(bien)
            data_serializado = serializer.data
            inventario = Inventario.objects.filter(
                id_bien=bien.id_bien).first()
            # transforma un choices en un diccionario
            diccionario_cod_estado_activo = dict(
                (x, y) for x, y in estados_articulo_CHOICES)
            estado = diccionario_cod_estado_activo[inventario.cod_estado_activo.cod_estado]
            data_serializado['estado'] = estado
            return Response({'success':True, 'detail':'Se encontraron elementos', 'Elementos': data_serializado}, status=status.HTTP_200_OK)
        try:
            raise NotFound('No se encontró elementos')
        except NotFound as e:
            return Response({'success':False, 'detail':'No se encontró elementos', 'data': bien}, status=status.HTTP_404_NOT_FOUND)


class SearchArticulosByNombreDocIdentificador(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        for key, value in request.query_params.items():
            if key in ['cod_tipo_activo', 'nombre', 'doc_identificador_nro']:
                if key != 'cod_tipo_activo':
                    filter[key+'__icontains'] = value
                else:
                    filter[key] = value
        if not filter.get('cod_tipo_activo'):
            raise NotFound('Debe enviar el parametro del tipo de activo')
        bien = CatalogoBienes.objects.filter(**filter).filter(nivel_jerarquico=5).exclude(nro_elemento_bien=None)
        if bien:
            serializer = self.serializer_class(bien, many=True)
            data_serializado = serializer.data
            id_bien_list = [item.id_bien for item in bien]
            inventario = Inventario.objects.filter(id_bien__in=id_bien_list)
            # transforma un choices en un diccionario
            diccionario_cod_estado_activo = dict(
                (x, y) for x, y in estados_articulo_CHOICES)

            for item in data_serializado:
                inventario_instance = inventario.filter(
                    id_bien=item['id_bien']).first()
                estado = inventario_instance.cod_estado_activo if inventario_instance else None
                item['estado'] = diccionario_cod_estado_activo[estado.cod_estado] if estado else None

            return Response({'success':True, 'detail':'Se encontraron elementos', 'Elementos': data_serializado}, status=status.HTTP_200_OK)
        try:
            raise NotFound('No se encontró elementos')
        except NotFound as e:
            return Response({'success':False, 'detail':'No se encontró elementos', 'data': bien}, status=status.HTTP_404_NOT_FOUND)


class SearchArticulos(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        for key, value in request.query_params.items():
            if key in ['nombre', 'codigo_bien', 'cod_tipo_activo']:
                if key != 'cod_tipo_activo':
                    filter[key+'__icontains'] = value
                else:
                    filter[key] = value
        filter['nro_elemento_bien'] = None
        filter['nivel_jerarquico'] = 5
        bien = CatalogoBienes.objects.filter(**filter).filter(Q(cod_tipo_activo__cod_tipo_activo__in=['Com','Veh','OAc']) | Q(cod_tipo_activo=None))
        serializador = self.serializer_class(bien, many=True)
        if bien:
            return Response({'success':True, 'detail':'Se encontró los elementos', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontró elementos')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró elementos', 'data': bien}, status=status.HTTP_404_NOT_FOUND)


class GetCatalogoBienesByCodigo(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.query_params.items():
            try:
                raise NotFound('Debe ingresar un parámetro de búsqueda')
            except NotFound as e:    
                return Response({'success':False, 'detail':'Debe ingresar un parámetro de búsqueda', 'data': []}, status=status.HTTP_404_NOT_FOUND)
        filters = {}
        filters['codigo_bien'] = request.query_params.get('codigo_bien')
        filters['nivel_jerarquico'] = 5
        filters['nro_elemento_bien'] = None

        bien = CatalogoBienes.objects.filter(**filters).filter(Q(cod_tipo_activo__cod_tipo_activo__in=['Com','Veh','OAc']) | Q(cod_tipo_activo=None)).first()
        bien_serializer = self.serializer_class(bien)

        if bien:
            return Response({'success':True, 'detail':'Busqueda exitosa', 'data': bien_serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontraron resultados')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontraron resultados', 'data': []}, status=status.HTTP_404_NOT_FOUND)


class GetNumeroEntrada(generics.ListAPIView):
    serializer_class = EntradaSerializer
    queryset = EntradasAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entrada = EntradasAlmacen.objects.all().order_by(
            '-numero_entrada_almacen').first()
        if not entrada:
            numero_entrada = 1
            return Response({'success':True, 'numero_entrada': numero_entrada})
        numero_entrada = entrada.numero_entrada_almacen + 1

        return Response({'success':True, 'numero_entrada': numero_entrada})


class CreateEntradaandItemsEntrada(generics.CreateAPIView):
    serializer_class = EntradaCreateSerializer
    queryset = EntradasAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        entrada_data = data.get('info_entrada')
        items_entrada = data.get('info_items_entrada')

        # VALIDACION QUE EN EL CAMPO CANTIDAD INGRESE POR LO MENOS UN ELEMENTO
        cantidad_list = [item['cantidad'] for item in items_entrada if item['cantidad'] == None or item['cantidad'] == "" or item['cantidad'] < 1]
        if cantidad_list:
            raise PermissionDenied('Debe ingresar una cantidad en todos los items de la entrada, y debe ser mayor a cero')

        # VALIDACIÓN QUE TODOS LOS ID_BIEN PADRES Y ID_BIEN ENVIADOS EXISTAN Y SEAN DE NIVEL 5
        id_bienes_enviados_validar = [item['id_bien'] for item in items_entrada if item['id_bien'] != None]
        id_bien_padre_enviados = [item['id_bien_padre'] for item in items_entrada if item['id_bien_padre'] != None]
        bienes_nodo_cinco = CatalogoBienes.objects.filter(id_bien__in=id_bienes_enviados_validar)
        if len(set(id_bienes_enviados_validar)) != len(bienes_nodo_cinco):
            raise ValidationError('Verificar que todos los id bien enviados existan')
        bienes_padre_nodo_cinco = CatalogoBienes.objects.filter( id_bien__in=id_bien_padre_enviados)
        for bien in bienes_nodo_cinco:
            if bien.nivel_jerarquico != 5:
                raise ValidationError('No se pueden seleccionar nodos que no sean nivel 5')
        for bien in bienes_padre_nodo_cinco:
            if bien.nivel_jerarquico != 5:
                raise ValidationError('No se pueden seleccionar nodos que no sean nivel 5')

        # VALIDACIÓN QUE TODAS LAS ENTRADAS DEBAN TENER UN ITEM
        if not len(items_entrada):
            raise ValidationError('No se puede guardar una entrada sin minimo un item de entrada')
        entrada_data['id_creador'] = request.user.persona.id_persona
        id_entrada = entrada_data.get('id_entrada_almacen')

        # VALIDACIÓN DE EXISTENCIA DE PROVEEDOR
        id_proveedor = entrada_data.get('id_proveedor')
        proveedor = Personas.objects.filter(id_persona=id_proveedor).first()
        if not proveedor:
            raise ValidationError('No se puede crear una entrada con un id_proveedor que no exista')

        # VALIDACIÓN DE EXISTENCIA DE TIPO ENTRADA
        id_tipo_entrada = entrada_data.get('id_tipo_entrada')
        tipo_entrada = Personas.objects.filter(id_persona=id_proveedor).first()
        if not tipo_entrada:
            raise ValidationError('No se puede crear una entrada con un tipo de entrada que no exista')

        # VALIDACIÓN DE FECHAS EN LA ENTRADA
        fecha_entrada = entrada_data.get('fecha_entrada')
        if fecha_entrada > str(datetime.now()):
            raise ValidationError('No se puede crear una entrada con una fecha superior a la actual')
        
        # VALIDACIÓN DE EXITENCIA DE BODEGA PARA ENTRADA
        id_bodega_entrada = entrada_data['id_bodega']
        bodega_entrada = Bodegas.objects.filter(id_bodega=id_bodega_entrada).first()
        if not bodega_entrada:
            raise ValidationError('La bodega seleccionada para la entrada no existe')

        # VALIDACIÓN DE EXISTENCIA DE BODEGAS
        id_bodegas_list = [item['id_bodega'] for item in items_entrada]
        if len(id_bodegas_list) != len(items_entrada):
            raise ValidationError('Todos los items deben estar asociados a una bodega')
        bodega = Bodegas.objects.filter(id_bodega__in=id_bodegas_list)
        if len(set(id_bodegas_list)) != len(bodega):
            raise ValidationError('Todas las bodegas enviadas en los items deben existir')
        if not bodega:
            raise NotFound('No existe ninguna bodega con los parámetro ingresado')

        # VALIDACIÓN QUE EL PORCENTAJE DE IVA EXISTA
        id_porcentajes_list = [item['porcentaje_iva'] for item in items_entrada]
        porcentajes_iva = PorcentajesIVA.objects.filter(id_porcentaje_iva__in=id_porcentajes_list)
        if len(set(id_porcentajes_list)) != len(porcentajes_iva):
            raise ValidationError('Todas los porcentajes iva enviados deben existir')

        # VALIDACIÓN QUE EL ID_UNIDAD_MEDIDA EXISTA
        unidad_medida_list = [item['id_unidad_medida_vida_util'] for item in items_entrada if item['id_bien_padre'] != None]
        unidades_medida = UnidadesMedida.objects.filter(id_unidad_medida__in=unidad_medida_list)
        if len(set(unidad_medida_list)) != len(unidades_medida):
            raise ValidationError('Todas las unidades de medida enviadas deben existir')

        # VALIDACIÓN QUE EL NUMERO POSICION NO VENGA REPETIDO
        numero_posicion_list = [item['numero_posicion'] for item in items_entrada]
        if len(set(numero_posicion_list)) != len(numero_posicion_list):
            raise ValidationError('Todas los numeros de posicion deben ser unicos')

        # VALIDACION EN CAMPO TIENE HOJA DE VIDA
        tiene_hoja_vida_list = [item['tiene_hoja_vida'] for item in items_entrada if item['id_bien_padre'] != None and item['tiene_hoja_vida'] != True and item['tiene_hoja_vida'] != False]
        if tiene_hoja_vida_list:
            raise ValidationError('Debe ser enviado un valor válido en el campo tiene hoja de vida')

        # VALIDACIÓN DEL NÚMERO DE ENTRADA
        numero_entrada_exist = EntradasAlmacen.objects.all().order_by('-numero_entrada_almacen').first()
        if numero_entrada_exist:
            entrada_data['numero_entrada_almacen'] = numero_entrada_exist.numero_entrada_almacen + 1
        else:
            entrada_data['numero_entrada_almacen'] = 1

        # SUMA DE TOTALES EN ITEMS Y ASIGNACIÓN A ENTRADA
        valor_total_items_list = [int(item['valor_total_item']) for item in items_entrada]
        valor_total_entrada = sum(valor_total_items_list)
        entrada_data['valor_total_entrada'] = valor_total_entrada

        # CREACIÓN DE LA ENTRADA
        serializer = self.serializer_class(data=entrada_data, many=False)
        serializer.is_valid(raise_exception=True)
        entrada_creada = serializer.save()
        entrada_serializada = EntradaSerializer(entrada_creada)

        # ASIGNACIÓN DEL ID DE LA ENTRADA QUE SE ACABÓ DE CREAR
        for item in items_entrada:
            item['id_entrada_almacen'] = entrada_creada.pk

        # FILTRAMOS LOS ACTIVOS FIJOS Y EMPEZAMOS CREACIÓN DE ACTIVOS FIJOS y CONSUMOS
        items_activos_fijos = list(filter(lambda item: item['id_bien_padre'] != None and item['id_bien'] == None, items_entrada))
        items_consumo = list(filter(lambda item: item['id_bien_padre'] == None and item['id_bien'] != None, items_entrada))
    
        # VALIDACION QUE LA FECHA DE ENTRADA SEA POSTERIOR A LOS ITEMS QUE SE ENCUENTRAN EN INVENTARIO
        for item in items_consumo:
            bien = CatalogoBienes.objects.filter(id_bien=item.get('id_bien')).first()
            bodega = Bodegas.objects.filter(id_bodega=item['id_bodega']).first()
            id_bien_inventario = Inventario.objects.filter(id_bien=bien.id_bien, id_bodega=bodega.id_bodega).first()
            fecha_entrega = datetime.strptime(fecha_entrada, '%Y-%m-%d %H:%M:%S')
            if id_bien_inventario:
                fecha_ingreso_existente = id_bien_inventario.fecha_ingreso
            else:
                fecha_ingreso_existente = None
            if id_bien_inventario and fecha_ingreso_existente:
                if fecha_entrega.date() < fecha_ingreso_existente:
                    raise ValidationError('la fecha de entrada tiene que ser posterior a la fecha de ingreso del bien en el inventario')
                
        # CREACIÓN DE CONSUMOS
        items_guardados = []
        items_guardados_data = []
        for item in items_consumo:
            id_bien_ = item.get('id_bien')
            cantidad = item.get('cantidad')
            id_bodega = item.get('id_bodega')

            # REALIZAR EL GUARDADO DE LOS ITEMS TIPO BIEN CONSUMO EN INVENTARIO
            bodega = Bodegas.objects.filter(id_bodega=id_bodega).first()
            match entrada_creada.id_tipo_entrada.cod_tipo_entrada:
                case 1:
                    tipo_doc_ultimo_movimiento = 'E_CPR'
                case 2:
                    tipo_doc_ultimo_movimiento = 'E_DON'
                case 3:
                    tipo_doc_ultimo_movimiento = 'E_RES'
                case 4:
                    tipo_doc_ultimo_movimiento = 'E_CPS'
                case 5:
                    tipo_doc_ultimo_movimiento = 'E_CMD'
                case 6:
                    tipo_doc_ultimo_movimiento = 'E_CNV'
                case 7:
                    tipo_doc_ultimo_movimiento = 'E_EMB'
                case 8:
                    tipo_doc_ultimo_movimiento = 'E_INC'
                case _:
                    raise ValidationError('El tipo de entrada ingresado no es valido')

            # CREA EL BIEN CONSUMO EN INVENTARIO O MODIFICA LA CANTIDAD POR BODEGA
            bien = CatalogoBienes.objects.filter(id_bien=id_bien_).first()
            id_bien_inventario = Inventario.objects.filter(id_bien=bien.id_bien, id_bodega=bodega.id_bodega).first()

            # SUMA EL REGISTRO SI ESTABA ESE BIEN EN ESA BODEGA EN INVENTARIO
            if id_bien_inventario:
                if id_bien_inventario.cantidad_entrante_consumo != None:
                    suma = id_bien_inventario.cantidad_entrante_consumo + cantidad
                    id_bien_inventario.cantidad_entrante_consumo = suma
                    id_bien_inventario.save()
                else:
                    id_bien_inventario.cantidad_entrante_consumo = cantidad
                    id_bien_inventario.save()
            else:
                fecha_entrada_date = datetime.strptime(fecha_entrada, '%Y-%m-%d %H:%M:%S')
                
                registro_inventario = Inventario.objects.create(
                    id_bien=bien,
                    id_bodega=bodega,
                    cod_tipo_entrada=entrada_creada.id_tipo_entrada,
                    cantidad_entrante_consumo=cantidad,
                    fecha_ingreso=fecha_entrada_date.date()
                )
            serializador_item_entrada_consumo = SerializerItemEntradaConsumo(data=item, many=False)
            serializador_item_entrada_consumo.is_valid(raise_exception=True)
            item_guardado = serializador_item_entrada_consumo.save()
            items_guardados.append(item_guardado)
            items_guardados_data.append(serializador_item_entrada_consumo.data)

        # CREACION DE ACTIVO FIJOS
        for item in items_activos_fijos:
            id_bien_padre = item.get('id_bien_padre')
            doc_identificador_bien = item.get('doc_identificador_bien')
            id_porcentaje_iva = item.get('porcentaje_iva')
            cantidad_vida_util = item.get('cantidad_vida_util')
            id_unidad_medida_vida_util = item.get('id_unidad_medida_vida_util')
            valor_residual = item.get('valor_residual')
            tiene_hoja_vida = item.get('tiene_hoja_vida')
            id_bodega = item.get('id_bodega')
            valor_total_item = item.get('valor_total_item')
            cod_estado = item.get('cod_estado')

            # CREACIÓN DE UN ITEM ACTIVO FIJO EN BASE A CAMPOS HEREDADOS DEL PADRE
            bien_padre = CatalogoBienes.objects.filter(id_bien=id_bien_padre).first()
            cod_estado_instance = EstadosArticulo.objects.filter(cod_estado=cod_estado).first()
            
            if not bien_padre:
                raise ValidationError('El bien padre ingresado no existe')
            
            bien_padre_serializado = CatalogoBienesSerializer(bien_padre)
            
            # ASIGNACIÓN DEL ÚLTIMO NÚMERO DEL ELEMENTO
            ultimo_numero_elemento = CatalogoBienes.objects.filter(Q(codigo_bien=bien_padre.codigo_bien) & ~Q(nro_elemento_bien=None)).order_by('-nro_elemento_bien').first()
            numero_elemento = 1
            if ultimo_numero_elemento:
                numero_elemento = ultimo_numero_elemento.nro_elemento_bien + 1

            # ASIGNACIÓN DE INFORMACIÓN PARA LA CREACIÓN DEL ELEMENTO
            data_create = bien_padre_serializado.data
            data_create['nro_elemento_bien'] = numero_elemento
            data_create['doc_identificador_nro'] = doc_identificador_bien
            data_create['id_porcentaje_iva'] = id_porcentaje_iva
            data_create['cantidad_vida_util'] = cantidad_vida_util
            data_create['id_unidad_medida_vida_util'] = id_unidad_medida_vida_util
            data_create['valor_residual'] = valor_residual
            data_create['tiene_hoja_vida'] = tiene_hoja_vida
            data_create['id_bien_padre'] = id_bien_padre
            del data_create['id_bien']
            del data_create['maneja_hoja_vida']
            del data_create['visible_solicitudes']
            serializer = CatalogoBienesSerializer(data=data_create, many=False)
            serializer.is_valid(raise_exception=True)
            elemento_creado = serializer.save()

            # REGISTRAR LA ENTRADA EN INVENTARIO
            bodega = Bodegas.objects.filter(id_bodega=id_bodega).first()
            match entrada_creada.id_tipo_entrada.cod_tipo_entrada:
                case 1:
                    tipo_doc_ultimo_movimiento = 'E_CPR'
                case 2:
                    tipo_doc_ultimo_movimiento = 'E_DON'
                case 3:
                    tipo_doc_ultimo_movimiento = 'E_RES'
                case 4:
                    tipo_doc_ultimo_movimiento = 'E_CPS'
                case 5:
                    tipo_doc_ultimo_movimiento = 'E_CMD'
                case 6:
                    tipo_doc_ultimo_movimiento = 'E_CNV'
                case 7:
                    tipo_doc_ultimo_movimiento = 'E_EMB'
                case 8:
                    tipo_doc_ultimo_movimiento = 'E_INC'
            
            fecha_entrada_date = datetime.strptime(fecha_entrada, '%Y-%m-%d %H:%M:%S')
            
            registro_inventario = Inventario.objects.create(
                id_bien=elemento_creado,
                id_bodega=bodega,
                cod_tipo_entrada=entrada_creada.id_tipo_entrada,
                fecha_ingreso=fecha_entrada_date.date(),
                id_persona_origen=entrada_creada.id_proveedor,
                numero_doc_origen=entrada_creada.numero_entrada_almacen,
                valor_ingreso=valor_total_item,
                ubicacion_en_bodega=True,
                cod_estado_activo=cod_estado_instance,
                fecha_ultimo_movimiento=datetime.now(),
                tipo_doc_ultimo_movimiento=tipo_doc_ultimo_movimiento,
                id_registro_doc_ultimo_movimiento=entrada_creada.id_entrada_almacen
            )
            if tiene_hoja_vida == True:
                if bien_padre.cod_tipo_activo:
                    match bien_padre.cod_tipo_activo.cod_tipo_activo:
                        case 'Com':
                            create_hoja_vida = HojaDeVidaComputadores.objects.create(
                                id_articulo=elemento_creado
                            )
                        case 'Veh':
                            create_hoja_vida = HojaDeVidaVehiculos.objects.create(
                                id_articulo=elemento_creado
                            )
                        case 'OAc':
                            create_hoja_vida = HojaDeVidaOtrosActivos.objects.create(
                                id_articulo=elemento_creado
                            )
            item['id_bien'] = elemento_creado.id_bien
            serializador_item_entrada = SerializerItemEntradaActivosFijos(data=item, many=False)
            serializador_item_entrada.is_valid(raise_exception=True)
            item_guardado = serializador_item_entrada.save()
            items_guardados.append(item_guardado)
            items_guardados_data.append(serializador_item_entrada.data)
    
        # AUDITORIA CREATE ENTRADA
        valores_creados_detalles = []
        for item in items_guardados:
            valores_creados_detalles.append({'nombre_bien':str(item.id_bien.nombre)})

        descripcion = {"nro_entrada": str(entrada_creada.numero_entrada_almacen),"fecha_entrada":str(entrada_creada.fecha_entrada)}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 34,
            "cod_permiso": "CR",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        return Response({'success':True, 'data_entrada_creada': entrada_serializada.data, 'data_items_creados': items_guardados_data})


# class DeleteItemsEntrada(generics.RetrieveDestroyAPIView):
#     serializer_class = ItemEntradaSerializer
#     queryset = ItemEntradaAlmacen.objects.all()
#     permission_classes = [IsAuthenticated]

#     def delete(self, request):
#         items_enviados = request.data

#         # VALIDAR QUE TODOS LOS ITEMS ENVIADOS DEBEN PERTENECER A LA MISMA ENTRADA
#         id_entrada = [item['id_entrada_almacen'] for item in items_enviados]
#         if len(set(id_entrada)) > 1:
#             raise PermissionDenied('Todos los items por eliminar deben pertenecer a la misma entrada')

#         # VALIDAR QUE TODOS LOS ID_ITEMS_ENVIADOS ENVIADOS PARA ELIMINAR EXISTAN
#         ids_items_enviados = [item['id_item_entrada_almacen']
#                               for item in items_enviados]
#         items_existentes = ItemEntradaAlmacen.objects.filter(
#             id_item_entrada_almacen__in=ids_items_enviados)
#         if len(set(ids_items_enviados)) != len(items_existentes):
#             raise ValidationError('Todos los id_items enviados para eliminar deben existir')

#         # VALIDAR QUE LA ENTRADA NO SE VAYA A QUEDAR SIN ITEMS
#         items_entrada = ItemEntradaAlmacen.objects.filter(
#             id_entrada_almacen=id_entrada[0])
#         id_items_entrada_existentes = [
#             item.id_item_entrada_almacen for item in items_entrada]
#         if len(ids_items_enviados) == len(id_items_entrada_existentes):
#             raise PermissionDenied('No se puede eliminar ya que una entrada no puede quedar sin items')

#         # VALIDACIÓN SI LA ENTRADA FUE EL ÚLTIMO MOVIMIENTO EN INVENTARIO
#         id_bienes_enviados = [item['id_bien'] for item in items_enviados]
#         inventario_item_instance = Inventario.objects.filter(
#             id_bien__in=id_bienes_enviados)
#         for item in inventario_item_instance:
#             item_entrada_instance = ItemEntradaAlmacen.objects.filter(
#                 id_bien=item.id_bien.id_bien).first()
#             if str(item_entrada_instance.id_entrada_almacen.id_entrada_almacen) != str(item.id_registro_doc_ultimo_movimiento):
#                 raise PermissionDenied('No se puede eliminar este item si la entrada no fue su último movimiento')

#         # VALIDACIÓN SI TIENE HOJA DE VIDA
#         valores_eliminados_detalles = []
#         id_entrada = 0

#         objects_items_enviado = [item for item in items_enviados]
#         for item in objects_items_enviado:
#             item_instance = ItemEntradaAlmacen.objects.filter(
#                 id_item_entrada_almacen=item['id_item_entrada_almacen']).first()
#             id_entrada = item_instance.id_entrada_almacen.id_entrada_almacen

#             if item_instance.id_bien.cod_tipo_bien == 'A':
#                 item_hv_comp = HojaDeVidaComputadores.objects.filter(
#                     id_articulo=item_instance.id_bien.id_bien).first()
#                 item_hv_veh = HojaDeVidaVehiculos.objects.filter(
#                     id_articulo=item_instance.id_bien.id_bien).first()
#                 item_hv_oac = HojaDeVidaOtrosActivos.objects.filter(
#                     id_articulo=item_instance.id_bien.id_bien).first()
#                 if item_hv_comp or item_hv_veh or item_hv_oac:
#                     raise PermissionDenied('No se puede eliminar por que tiene hoja de vida')

#                 bien_eliminar = CatalogoBienes.objects.filter(
#                     id_bien=item_instance.id_bien.id_bien).first()
#                 inventario_item_instance_delete = Inventario.objects.filter(
#                     id_bien=item_instance.id_bien.id_bien)

#                 # ELIMINA EL REGISTRO EN INVENTARIO, CATALOGO DE BIENES E ITEM ENTRADA
#                 inventario_item_instance_delete.delete()

#                 valores_eliminados_detalles.append(
#                     {'nombre': bien_eliminar.nombre})

#                 bien_eliminar.delete()
#                 item_instance.delete()

#         entrada = EntradasAlmacen.objects.filter(
#             id_entrada_almacen=id_entrada).first()

#         usuario = request.user.id_usuario
#         descripcion = {"numero_entrada_almacen": str(
#             entrada.numero_entrada_almacen), "fecha_entrada": str(entrada.fecha_entrada)}
#         direccion = Util.get_client_ip(request)

#         # AUDITORIA MAESTRO DETALLE
#         auditoria_data = {
#             "id_usuario": usuario,
#             "id_modulo": 34,
#             "cod_permiso": "AC",
#             "subsistema": 'ALMA',
#             "dirip": direccion,
#             "descripcion": descripcion,
#             "valores_eliminados_detalles": valores_eliminados_detalles
#         }
#         Util.save_auditoria_maestro_detalle(auditoria_data)

#         return Response({'success':True, 'detail':'Se ha eliminado correctamente'}, status=status.HTTP_200_OK)


class UpdateEntrada(generics.RetrieveUpdateAPIView):
    serializer_class = EntradaUpdateSerializer
    queryset = EntradasAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def update_maestro(self, request, id_entrada):
        data = request.data.get('info_entrada')

        # VALIDACIÓN QUE LA ENTRADA SELECCIONADA EXISTA
        entrada = EntradasAlmacen.objects.filter(
            id_entrada_almacen=id_entrada).first()
        entrada_previous = copy.copy(entrada)
        if not entrada:
            raise NotFound('No se encontró ninguna entrada con el parámetro ingresado')

        # VALIDACIÓN QUE EL TIPO ENTRADA ENVIADA EXISTA
        cod_tipo_entrada = data['id_tipo_entrada']
        tipo_entrada_instance = TiposEntradas.objects.filter(
            cod_tipo_entrada=cod_tipo_entrada).first()
        if not tipo_entrada_instance:
            raise ValidationError('No se encontró ningún tipo de entrada con el parámetro ingresado')

        # VALIDACIÓN QUE EL ID PROVEEDOR ENVIADO EXISTA
        id_proveedor = data['id_proveedor']
        proveedor = Personas.objects.filter(id_persona=id_proveedor).first()
        if not proveedor:
            raise ValidationError('No existe el proveedor enviado')

        # SI EL USUARIO ACTUALIZA EL TIPO DE ENTRADA
        if cod_tipo_entrada != entrada.id_tipo_entrada:
            match cod_tipo_entrada:
                case 1:
                    tipo_doc_ultimo_movimiento = 'E_CPR'
                case 2:
                    tipo_doc_ultimo_movimiento = 'E_DON'
                case 3:
                    tipo_doc_ultimo_movimiento = 'E_RES'
                case 4:
                    tipo_doc_ultimo_movimiento = 'E_CPS'
                case 5:
                    tipo_doc_ultimo_movimiento = 'E_CMD'
                case 6:
                    tipo_doc_ultimo_movimiento = 'E_CNV'
                case 7:
                    tipo_doc_ultimo_movimiento = 'E_EMB'
                case 8:
                    tipo_doc_ultimo_movimiento = 'E_INC'

            # VALIDACIÓN QUE TODOS LOS ITEMS TENGAN COMO ÚLTIMO MOVIMIENTO LA ENTRADA
            items_entrada = ItemEntradaAlmacen.objects.filter(
                id_entrada_almacen=entrada.id_entrada_almacen)
            id_bien_items_list = [item.id_bien for item in items_entrada]
            for id_bien in id_bien_items_list:
                bien_inventario = Inventario.objects.filter(
                    id_bien=id_bien).first()
                if str(bien_inventario.id_registro_doc_ultimo_movimiento) != str(entrada.id_entrada_almacen):
                    raise PermissionDenied('No se puede actualizar ya que los items asociados a esta entrada no tienen como último movimiento la entrada')

            # ACTUALIZA EL TIPO DE ENTRADA EN CADA UNO DE LOS ITEMS
            for id_bien in id_bien_items_list:
                bien_inventario = Inventario.objects.filter(
                    id_bien=id_bien).first()
                bien_inventario.cod_tipo_entrada = tipo_entrada_instance
                bien_inventario.tipo_doc_ultimo_movimiento = tipo_doc_ultimo_movimiento
                bien_inventario.id_persona_origen = proveedor
                bien_inventario.save()
        # VALIDACIÓN PERSONA ACTUALIZA
        persona_actualiza = request.user.persona
        if (persona_actualiza.id_persona != entrada.id_creador.id_persona):
            entrada.id_persona_ult_act_dif_creador = persona_actualiza
            entrada.fecha_ultima_actualizacion_diferente_creador = datetime.now()
            entrada.save()

        # ACTUALIZACIÓN DE LA ENTRADA
        serializer = EntradaUpdateSerializer(entrada, data=data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        valores_actualizados_maestro = {'previous':entrada_previous, 'current':entrada}
        
        return valores_actualizados_maestro

    def delete_items(self, request, id_entrada):
        items_enviados = request.data.get('info_items_entrada')

        id_items_enviados = [item_enviado['id_item_entrada_almacen'] for item_enviado in items_enviados if item_enviado['id_item_entrada_almacen']!=None]
        instances_items_eliminar = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=id_entrada).exclude(id_item_entrada_almacen__in=id_items_enviados)
        
        # VALIDAR QUE LA ENTRADA NO SE VAYA A QUEDAR SIN ITEMS
        if not id_items_enviados:
            raise PermissionDenied('No se puede eliminar ya que una entrada no puede quedar sin items')

        # VALIDACIÓN SI LA ENTRADA FUE EL ÚLTIMO MOVIMIENTO EN INVENTARIO
        id_bienes_enviados = [item.id_bien.id_bien for item in instances_items_eliminar]
        inventario_item_instance = Inventario.objects.filter(
            id_bien__in=id_bienes_enviados)
        for item in inventario_item_instance:
            item_entrada_instance = ItemEntradaAlmacen.objects.filter(
                id_bien=item.id_bien.id_bien).first()
            if str(item_entrada_instance.id_entrada_almacen.id_entrada_almacen) != str(item.id_registro_doc_ultimo_movimiento):
                raise PermissionDenied('No se puede eliminar este item si la entrada no fue su último movimiento')

        # VALIDACIÓN SI TIENE HOJA DE VIDA
        valores_eliminados_detalles = []
        id_entrada = 0

        objects_items_enviado = [item for item in instances_items_eliminar]
        for item_instance in objects_items_enviado:
            id_entrada = item_instance.id_entrada_almacen.id_entrada_almacen

            if item_instance.id_bien.cod_tipo_bien == 'A':
                item_hv_comp = HojaDeVidaComputadores.objects.filter(
                    id_articulo=item_instance.id_bien.id_bien).first()
                item_hv_veh = HojaDeVidaVehiculos.objects.filter(
                    id_articulo=item_instance.id_bien.id_bien).first()
                item_hv_oac = HojaDeVidaOtrosActivos.objects.filter(
                    id_articulo=item_instance.id_bien.id_bien).first()
                if item_hv_comp or item_hv_veh or item_hv_oac:
                    raise PermissionDenied('No se puede eliminar por que tiene hoja de vida')

                bien_eliminar = CatalogoBienes.objects.filter(
                    id_bien=item_instance.id_bien.id_bien).first()
                inventario_item_instance_delete = Inventario.objects.filter(
                    id_bien=item_instance.id_bien.id_bien)

                # ELIMINA EL REGISTRO EN INVENTARIO, CATALOGO DE BIENES E ITEM ENTRADA
                inventario_item_instance_delete.delete()

                valores_eliminados_detalles.append(
                    {'nombre': bien_eliminar.nombre})

                bien_eliminar.delete()
                item_instance.delete()

        return valores_eliminados_detalles

    def put(self, request, id_entrada):
        data = request.data.get('info_items_entrada')
        entrada_almacen = EntradasAlmacen.objects.filter(
            id_entrada_almacen=id_entrada).first()
        if not entrada_almacen:
            raise NotFound('La entrada ingresada no existe')
        
        valores_actualizados_maestro = self.update_maestro(request, id_entrada)
        valores_eliminados_detalles = self.delete_items(request, id_entrada)

        # VALIDACIÓN DE QUE TODOS LOS ID_ITEMS ENVIADOS EXISTAN
        items_actualizar = [item['id_item_entrada_almacen']
                            for item in data if item['id_item_entrada_almacen'] != None]
        items_entrada_actualizar = ItemEntradaAlmacen.objects.filter(
            id_item_entrada_almacen__in=items_actualizar)
        if len(set(items_actualizar)) != len(items_entrada_actualizar):
            raise ValidationError('Todos los id_items enviados deben existir')

        # VALIDACIÓN QUE LAS CANTIDADES ENVIADAS DEBEN SER MAYORES A 0
        cantidades_list = [item['cantidad'] for item in data if item['cantidad']
                           == None or item['cantidad'] == "" or item['cantidad'] == 0]
        if cantidades_list:
            raise ValidationError('Todos las cantidades enviadas deben ser mayores a cero')

        # VALIDACIÓN QUE EL NÚMERO DE POSICIÓN SEA ÚNICO EN LA ENTRADA
        numero_posicion = [item['numero_posicion'] for item in data]
        if len(numero_posicion) != len(set(numero_posicion)):
            raise ValidationError('Todos los numero de posición deben ser únicos')

        # VALIDAR QUE EL ID_ENTRADA SEA EL MISMO
        items_entrada_id_list = [item['id_entrada_almacen'] for item in data]
        if len(set(items_entrada_id_list)) != 1:
            raise ValidationError('Debe validar que los items de las entradas pertenezcan a una misma entrada')
        else:
            if items_entrada_id_list[0] != int(id_entrada):
                raise ValidationError('El id_entrada de los items de la petición debe ser igual al enviado en url')

        # VALIDACIÓN DE EXISTENCIA DE UNIDADES MEDIDAS VIDA UTIL
        unidades_medida_vida_util_list = [item['id_unidad_medida_vida_util']
                                          for item in data if item['id_unidad_medida_vida_util'] != None]
        unidades_medida_vida_util_existe = UnidadesMedida.objects.filter(
            id_unidad_medida__in=unidades_medida_vida_util_list)
        if unidades_medida_vida_util_existe.count() != len(set(unidades_medida_vida_util_list)):
            raise ValidationError('Una o varias unidades de medida que está asociando en los items no existen')

        # VALIDACIÓN DE EXISTENCIA DE BODEGAS
        bodegas_list = [item['id_bodega'] for item in data]
        bodegas_existe = Bodegas.objects.filter(id_bodega__in=bodegas_list)
        if bodegas_existe.count() != len(set(bodegas_list)):
            raise ValidationError('Una o varias bodegas que están asociando en los items no existen')

        # VALIDACIÓN DE EXISTENCIA PORCENTAJES IVA
        porcentajes_iva_list = [item['porcentaje_iva'] for item in data]
        porcentajes_iva_existe = PorcentajesIVA.objects.filter(
            id_porcentaje_iva__in=porcentajes_iva_list)
        if porcentajes_iva_existe.count() != len(set(porcentajes_iva_list)):
            raise ValidationError('Uno o varios porcentajes iva que están asociando en los items no existen')

        # VALIDACIÓN DE EXISTENCIA BIENES Y BIENES PADRE
        bienes_list = [item['id_bien']
                       for item in data if item['id_bien'] != None]
        bienes_padre_list = [item['id_bien_padre']
                             for item in data if item['id_item_entrada_almacen'] == None and item['id_bien_padre'] != None]
        bienes_list.extend(bienes_padre_list)
        bienes_existe = CatalogoBienes.objects.filter(id_bien__in=bienes_list)
        if bienes_existe.count() != len(set(bienes_list)):
            raise ValidationError('Uno o varios bienes que están asociando en los items no existen')

        # CONOCER LOS QUE SE VAN A CREAR
        items_por_crear = [
            item for item in data if item['id_item_entrada_almacen'] == None]

        # CONOCER LOS QUE EXISTEN Y NO SE VAN A ACTUALIZAR
        items_existen_sin_actualizar = ItemEntradaAlmacen.objects.filter(
            id_entrada_almacen=id_entrada).exclude(id_item_entrada_almacen__in=items_actualizar)

        # VALIDACIÓN QUE EL DOC_IDENTIFICADOR SEA ÚNICO EN LA ENTRADA
        doc_identificadores_existentes = [
            item.doc_identificador_bien for item in items_existen_sin_actualizar if item.doc_identificador_bien != None]
        docs_identificadores_list = [item['doc_identificador_bien']
                                     for item in data if item['doc_identificador_bien'] != None]
        doc_identificadores_existentes.extend(docs_identificadores_list)
        if len(set(doc_identificadores_existentes)) != len(doc_identificadores_existentes):
            raise ValidationError('Todos los documentos identificadores deben ser únicos')
        if len(docs_identificadores_list) != len(set(docs_identificadores_list)):
            raise ValidationError('Todos los documentos identificadores deben ser únicos')

        # TOTAL VALOR ENTRADA
        valor_total_items_actualizar_list = [
            float(item.valor_total_item) for item in items_entrada_actualizar]
        valor_total_item_existen_list = [
            float(item.valor_total_item) for item in items_existen_sin_actualizar]
        valor_total_item_crear_list = [
            float(item['valor_total_item']) for item in items_por_crear]
        valor_total_entrada = valor_total_items_actualizar_list + \
            valor_total_item_existen_list + valor_total_item_crear_list
        valor_total_entrada = sum(valor_total_entrada)

        # SEPARAR LO QUE SE CREA EN ACTIVOS FIJOS Y DE CONSUMO
        items_activos_fijos_crear_list = [
            item for item in items_por_crear if item['id_bien_padre'] != None and item['id_bien'] == None]
        items_consumo_crear_list = [
            item for item in items_por_crear if item['id_bien_padre'] == None and item['id_bien'] != None]

        # OBTENER TIPO DOC ULTIMO MOVIMIENTO DE ENTRADA
        tipo_doc_ultimo_movimiento = ''
        match entrada_almacen.id_tipo_entrada.cod_tipo_entrada:
            case 1:
                tipo_doc_ultimo_movimiento = 'E_CPR'
            case 2:
                tipo_doc_ultimo_movimiento = 'E_DON'
            case 3:
                tipo_doc_ultimo_movimiento = 'E_RES'
            case 4:
                tipo_doc_ultimo_movimiento = 'E_CPS'
            case 5:
                tipo_doc_ultimo_movimiento = 'E_CMD'
            case 6:
                tipo_doc_ultimo_movimiento = 'E_CNV'
            case 7:
                tipo_doc_ultimo_movimiento = 'E_EMB'
            case 8:
                tipo_doc_ultimo_movimiento = 'E_INC'

        # VARIABLES AUDITORIAS
        valores_creados_detalles = []
        valores_actualizados_detalles = []

        # CREACIÓN ACTIVOS FIJOS
        items_guardados = []
        for item in items_activos_fijos_crear_list:
            id_bien_padre = item.get('id_bien_padre')
            doc_identificador_bien = item.get('doc_identificador_bien')
            id_porcentaje_iva = item.get('porcentaje_iva')
            cantidad_vida_util = item.get('cantidad_vida_util')
            id_unidad_medida_vida_util = item.get('id_unidad_medida_vida_util')
            valor_residual = item.get('valor_residual')
            tiene_hoja_vida = item.get('tiene_hoja_vida')
            id_bodega = item.get('id_bodega')
            valor_total_item = item.get('valor_total_item')
            cod_estado = item.get('cod_estado')
            
            cod_estado_instance = EstadosArticulo.objects.filter(cod_estado=cod_estado).first()

            # CREACIÓN DE UN ITEM ACTIVO FIJO EN BASE A CAMPOS HEREDADOS DEL PADRE
            bien_padre = CatalogoBienes.objects.filter(
                id_bien=id_bien_padre).first()
            bien_padre_serializado = CatalogoBienesSerializer(bien_padre)

            # ASIGNACIÓN DEL ÚLTIMO NÚMERO DEL ELEMENTO
            ultimo_numero_elemento = CatalogoBienes.objects.filter(Q(codigo_bien=bien_padre.codigo_bien) & ~Q(
                nro_elemento_bien=None)).order_by('-nro_elemento_bien').first()
            numero_elemento = 1
            if ultimo_numero_elemento:
                numero_elemento = ultimo_numero_elemento.nro_elemento_bien + 1

            # ASIGNACIÓN DE INFORMACIÓN PARA LA CREACIÓN DEL ELEMENTO
            data_create = bien_padre_serializado.data
            data_create['nro_elemento_bien'] = numero_elemento
            data_create['doc_identificador_nro'] = doc_identificador_bien
            data_create['id_porcentaje_iva'] = id_porcentaje_iva
            data_create['cantidad_vida_util'] = cantidad_vida_util
            data_create['id_unidad_medida_vida_util'] = id_unidad_medida_vida_util
            data_create['valor_residual'] = valor_residual
            data_create['tiene_hoja_vida'] = tiene_hoja_vida
            data_create['id_bien_padre'] = id_bien_padre
            del data_create['id_bien']
            del data_create['maneja_hoja_vida']
            del data_create['visible_solicitudes']
            serializer = CatalogoBienesSerializer(data=data_create, many=False)
            serializer.is_valid(raise_exception=True)
            elemento_creado = serializer.save()

            # REGISTRAR LA ENTRADA EN INVENTARIO
            bodega = Bodegas.objects.filter(id_bodega=id_bodega).first()

            registro_inventario = Inventario.objects.create(
                id_bien=elemento_creado,
                id_bodega=bodega,
                cod_tipo_entrada=entrada_almacen.id_tipo_entrada,
                fecha_ingreso=entrada_almacen.fecha_entrada.date(),
                id_persona_origen=entrada_almacen.id_proveedor,
                numero_doc_origen=entrada_almacen.numero_entrada_almacen,
                valor_ingreso=valor_total_item,
                ubicacion_en_bodega=True,
                cod_estado_activo=cod_estado_instance,
                fecha_ultimo_movimiento=datetime.now(),
                tipo_doc_ultimo_movimiento=tipo_doc_ultimo_movimiento,
                id_registro_doc_ultimo_movimiento=entrada_almacen.id_entrada_almacen
            )
            if tiene_hoja_vida == True:
                match bien_padre.cod_tipo_activo:
                    case 'Com':
                        create_hoja_vida = HojaDeVidaComputadores.objects.create(
                            id_articulo=elemento_creado
                        )
                    case 'Veh':
                        create_hoja_vida = HojaDeVidaVehiculos.objects.create(
                            id_articulo=elemento_creado
                        )
                    case 'OAc':
                        create_hoja_vida = HojaDeVidaOtrosActivos.objects.create(
                            id_articulo=elemento_creado
                        )
            item['id_bien'] = elemento_creado.id_bien
            serializador_item_entrada = SerializerItemEntradaActivosFijos(
                data=item, many=False)
            serializador_item_entrada.is_valid(raise_exception=True)
            serializador_item_entrada.save()
            items_guardados.append(serializador_item_entrada.data)
            valores_creados_detalles.append({'nombre': elemento_creado.nombre})

        # CREACIÓN DE CONSUMO
        for item in items_consumo_crear_list:
            id_bien_ = item.get('id_bien')
            cantidad = item.get('cantidad')
            id_bodega = item.get('id_bodega')

            # REALIZAR EL GUARDADO DE LOS ITEMS TIPO BIEN CONSUMO EN INVENTARIO
            bodega = Bodegas.objects.filter(id_bodega=id_bodega).first()

            # CREA EL BIEN CONSUMO EN INVENTARIO O MODIFICA LA CANTIDAD POR BODEGA
            bien = CatalogoBienes.objects.filter(id_bien=id_bien_).first()
            id_bien_inventario = Inventario.objects.filter(
                id_bien=bien.id_bien, id_bodega=bodega.id_bodega).first()

            # SUMA EL REGISTRO SI ESTABA ESE BIEN EN ESA BODEGA EN INVENTARIO
            if id_bien_inventario:
                if id_bien_inventario.cantidad_entrante_consumo != None:
                    suma = id_bien_inventario.cantidad_entrante_consumo + cantidad
                    id_bien_inventario.cantidad_entrante_consumo = suma
                    id_bien_inventario.save()
                else:
                    id_bien_inventario.cantidad_entrante_consumo = cantidad
                    id_bien_inventario.save()
            else:
                registro_inventario = Inventario.objects.create(
                    id_bien=bien,
                    id_bodega=bodega,
                    cod_tipo_entrada=entrada_almacen.id_tipo_entrada,
                    cantidad_entrante_consumo=cantidad,
                    fecha_ingreso=entrada_almacen.fecha_entrada.date()
                )
            serializador_item_entrada_consumo = SerializerItemEntradaConsumo(
                data=item, many=False)
            serializador_item_entrada_consumo.is_valid(raise_exception=True)
            serializador_item_entrada_consumo.save()
            items_guardados.append(serializador_item_entrada_consumo.data)

            valores_creados_detalles.append({'nombre': bien.nombre})

        # SEPARAR LO QUE SE ACTUALIZA EN ACTIVOS FIJOS Y DE CONSUMO
        items_activos_fijos_actualizar_list = [
            item for item in items_entrada_actualizar if item.id_bien.cod_tipo_bien == 'A']
        items_consumo_actualizar_list = [
            item for item in items_entrada_actualizar if item.id_bien.cod_tipo_bien == 'C']

        # ACTUALIZAR ACTIVOS FIJOS
        items_activos_fijos_actualizar_id_list = [
            item.id_bien.id_bien for item in items_activos_fijos_actualizar_list]
        catalogo_bienes_fijos_actualizar = CatalogoBienes.objects.filter(
            id_bien__in=items_activos_fijos_actualizar_id_list)
        inventario_fijos_actualizar = Inventario.objects.filter(
            id_bien__in=items_activos_fijos_actualizar_id_list)
        items_actualizables = [inventario for inventario in inventario_fijos_actualizar if str(inventario.id_registro_doc_ultimo_movimiento) == str(
            entrada_almacen.id_entrada_almacen) and str(inventario.tipo_doc_ultimo_movimiento) == str(tipo_doc_ultimo_movimiento)]
        items_no_actualizables = [inventario for inventario in inventario_fijos_actualizar if str(inventario.id_registro_doc_ultimo_movimiento) != str(
            entrada_almacen.id_entrada_almacen) or str(inventario.tipo_doc_ultimo_movimiento) != str(tipo_doc_ultimo_movimiento)]
        id_bien_items_actualizables = [
            item.id_bien.id_bien for item in items_actualizables]
        item_data_por_actualizar = [
            item for item in data if item['id_bien'] in id_bien_items_actualizables]

        for item in item_data_por_actualizar:
            # SE ACTUALIZA EN CATALOGO BIENES
            catalogo_bien_instance_actualizar = catalogo_bienes_fijos_actualizar.filter(
                id_bien=item['id_bien']).first()
            item['id_porcentaje_iva'] = item['porcentaje_iva']
            serializer_catalogo_bien = CatalogoBienesActivoFijoPutSerializer(
                catalogo_bien_instance_actualizar, data=item)
            serializer_catalogo_bien.is_valid(raise_exception=True)
            serializer_catalogo_bien.save()

            descripcion_item_actualizado = {
                'nombre': serializer_catalogo_bien.data['nombre']}

            # SE ACTUALIZA EN INVENTARIO
            inventario_instance_actualizar = inventario_fijos_actualizar.filter(
                id_bien=item['id_bien']).first()
            serializer_inventario = SerializerUpdateInventariosActivosFijos(
                inventario_instance_actualizar, data=item)
            serializer_inventario.is_valid(raise_exception=True)
            serializer_inventario.save()

            previous_item_actualizado = copy.copy(item_instance)

            # SE ACTUALIZA ITEM ENTRADA
            item_instance = items_entrada_actualizar.filter(
                id_item_entrada_almacen=item['id_item_entrada_almacen']).first()
            
            serializer_item = SerializerUpdateItemEntradaActivosFijos(
                item_instance, data=item)
            serializer_item.is_valid(raise_exception=True)
            serializer_item.save()

            items_guardados.append(serializer_item.data)

            valores_actualizados_detalles.append(
                {'descripcion': descripcion_item_actualizado, 'previous': previous_item_actualizado, 'current': item_instance})

        # ACTUALIZAR ITEMS DE CONSUMO
        items_consumo_actualizar_id_list = [
            item.id_bien.id_bien for item in items_consumo_actualizar_list]
        inventario_consumo_actualizar = Inventario.objects.filter(
            id_bien__in=items_consumo_actualizar_id_list)
        item_data_por_actualizar_consumo = [
            item for item in data if item['id_bien'] in items_consumo_actualizar_id_list]

        for item in item_data_por_actualizar_consumo:
            item_consumo_instance = items_entrada_actualizar.filter(
                id_bien=item['id_bien']).first()

            # CANTIDAD AUMENTA
            if item['cantidad'] >= item_consumo_instance.cantidad:
                inventario_instance_actualizar = inventario_consumo_actualizar.filter(
                    id_bien=item['id_bien'], id_bodega=item['id_bodega']).first()

                if item['id_bodega'] == inventario_instance_actualizar.id_bodega.id_bodega:
                    # SE ACTUALIZA EN INVENTARIO
                    item_instance = items_entrada_actualizar.filter(
                        id_item_entrada_almacen=item['id_item_entrada_almacen']).first()

                    item['cantidad_entrante_consumo'] = inventario_instance_actualizar.cantidad_entrante_consumo + \
                        abs((item_instance.cantidad - item['cantidad']))
                    serializer_inventario = SerializerUpdateInventariosConsumo(
                        inventario_instance_actualizar, data=item)
                    serializer_inventario.is_valid(raise_exception=True)
                    serializer_inventario.save()

                    bien_actualizado = bienes_existe.filter(
                        id_bien=item['id_bien']).first()
                    descripcion_item_actualizado = {
                        'nombre': bien_actualizado.nombre}
                    previous_item_actualizado = copy.copy(item_instance)

                    # SE ACTUALIZA ITEM ENTRADA
                    serializer_item = SerializerItemEntradaConsumoPut(
                        item_instance, data=item)
                    serializer_item.is_valid(raise_exception=True)
                    serializer_item.save()

                    items_guardados.append(serializer_item.data)

                    valores_actualizados_detalles.append(
                        {'descripcion': descripcion_item_actualizado, 'previous': previous_item_actualizado, 'current': item_instance})

                else:
                    pass
            # CANTIDAD REDUCE
            else:
                if item['cantidad'] < item_consumo_instance.cantidad:
                    valor_minimo_posible = UtilAlmacen.get_valor_minimo_entradas(item_consumo_instance.id_bien.id_bien, item_consumo_instance.id_bodega.id_bodega, item_consumo_instance.id_entrada_almacen.id_entrada_almacen)
                    if item['cantidad'] < valor_minimo_posible:
                        raise PermissionDenied('No puede reducir la cantidad del bien ' + item_consumo_instance.id_bien.nombre + ' hasta la cantidad ingresada. La cantidad mínima posible a la que puede quedar es ' + valor_minimo_posible)
            
        # SE ACTUALIZA VALOR TOTAL ENTRADA MODIFICADO
        entrada_almacen.valor_total_entrada = valor_total_entrada

        # VALIDACIÓN PERSONA ACTUALIZA
        persona_actualiza = request.user.persona
        if (persona_actualiza.id_persona != entrada_almacen.id_creador.id_persona):
            entrada_almacen.id_persona_ult_act_dif_creador = persona_actualiza
            entrada_almacen.fecha_ultima_actualizacion_diferente_creador = datetime.now()

        entrada_almacen.save()

        descripcion = {"numero_entrada_almacen": str(
            entrada_almacen.numero_entrada_almacen), "fecha_entrada": str(entrada_almacen.fecha_entrada)}
        direccion = Util.get_client_ip(request)

        # AUDITORIAS
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 34,
            "cod_permiso": "AC",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_maestro": valores_actualizados_maestro,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success':True, 'detail':'Actualizado exitosamente', 'data': items_guardados}, status=status.HTTP_201_CREATED)

class GetTiposEntradas(generics.ListAPIView):
    serializer_class = TiposEntradasSerializer
    queryset = TiposEntradas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = self.serializer_class(self.queryset.all(), many=True)
        return Response({'success':True, 'detail':'Se encontraron los siguientes tipos de entrada', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetEntradas(generics.ListAPIView):
    serializer_class = EntradaSerializer
    queryset = EntradasAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id_entrada = request.query_params.get('id_entrada')

        # SI NO ENVIAN EL ID_ENTRADA SIGNIFICA QUE QUIEREN LISTAR TODAS LAS ENTRADAS
        if not id_entrada:
            entradas = EntradasAlmacen.objects.all()
            serializer = self.serializer_class(entradas, many=True)
            return Response({'success':True, 'detail':'Obtenido exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)

        # SI NO EXISTE EL ID_ENTRADA ENVIADO
        entrada_instance = EntradasAlmacen.objects.filter(
            id_entrada_almacen=id_entrada).first()
        if not entrada_instance:
            raise NotFound('No se encontró ninguna entrada con el parámetro ingresado')

        # SERIALIZAR LAS INSTANCIAS DE LOS ITEMS DE LA ENTRADA ENVIADA
        items_entrada_instance = ItemEntradaAlmacen.objects.filter(
            id_entrada_almacen=entrada_instance.id_entrada_almacen)
        serializer_items = ItemEntradaSerializer(
            items_entrada_instance, many=True)
        serializer = self.serializer_class(entrada_instance)

        entrada = {'info_entrada': serializer.data,
                   'info_items_entrada': serializer_items.data}
        return Response({'success':True, 'detail':'Búsqueda exitosa', 'data': entrada}, status=status.HTTP_200_OK)


class UpdateItemsEntrada(generics.UpdateAPIView):
    serializer_class = ItemEntradaSerializer
    queryset = ItemEntradaAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_entrada):
        data = request.data
        entrada_almacen = EntradasAlmacen.objects.filter(
            id_entrada_almacen=id_entrada).first()
        if not entrada_almacen:
            raise NotFound('La entrada ingresada no existe')

        # VALIDACIÓN DE QUE TODOS LOS ID_ITEMS ENVIADOS EXISTAN
        items_actualizar = [item['id_item_entrada_almacen']
                            for item in data if item['id_item_entrada_almacen'] != None]
        items_entrada_actualizar = ItemEntradaAlmacen.objects.filter(
            id_item_entrada_almacen__in=items_actualizar)
        if len(set(items_actualizar)) != len(items_entrada_actualizar):
            raise ValidationError('Todos los id_items enviados deben existir')

        # VALIDACIÓN QUE LAS CANTIDADES ENVIADAS DEBEN SER MAYORES A 0
        cantidades_list = [item['cantidad'] for item in data if item['cantidad']
                           == None or item['cantidad'] == "" or item['cantidad'] == 0]
        if cantidades_list:
            raise ValidationError('Todos las cantidades enviadas deben ser mayores a cero')

        # VALIDACIÓN QUE EL NÚMERO DE POSICIÓN SEA ÚNICO EN LA ENTRADA
        numero_posicion = [item['numero_posicion'] for item in data]
        if len(numero_posicion) != len(set(numero_posicion)):
            raise ValidationError('Todos los numero de posición deben ser únicos')

        # VALIDAR QUE EL ID_ENTRADA SEA EL MISMO
        items_entrada_id_list = [item['id_entrada_almacen'] for item in data]
        if len(set(items_entrada_id_list)) != 1:
            raise ValidationError('Debe validar que los items de las entradas pertenezcan a una misma entrada')
        else:
            if items_entrada_id_list[0] != int(id_entrada):
                raise ValidationError('El id_entrada de los items de la petición debe ser igual al enviado en url')

        # VALIDACIÓN DE EXISTENCIA DE UNIDADES MEDIDAS VIDA UTIL
        unidades_medida_vida_util_list = [item['id_unidad_medida_vida_util']
                                          for item in data if item['id_unidad_medida_vida_util'] != None]
        unidades_medida_vida_util_existe = UnidadesMedida.objects.filter(
            id_unidad_medida__in=unidades_medida_vida_util_list)
        if unidades_medida_vida_util_existe.count() != len(set(unidades_medida_vida_util_list)):
            raise ValidationError('Una o varias unidades de medida que está asociando en los items no existen')

        # VALIDACIÓN DE EXISTENCIA DE BODEGAS
        bodegas_list = [item['id_bodega'] for item in data]
        bodegas_existe = Bodegas.objects.filter(id_bodega__in=bodegas_list)
        if bodegas_existe.count() != len(set(bodegas_list)):
            raise ValidationError('Una o varias bodegas que están asociando en los items no existen')

        # VALIDACIÓN DE EXISTENCIA PORCENTAJES IVA
        porcentajes_iva_list = [item['porcentaje_iva'] for item in data]
        porcentajes_iva_existe = PorcentajesIVA.objects.filter(
            id_porcentaje_iva__in=porcentajes_iva_list)
        if porcentajes_iva_existe.count() != len(set(porcentajes_iva_list)):
            raise ValidationError('Uno o varios porcentajes iva que están asociando en los items no existen')

        # VALIDACIÓN DE EXISTENCIA BIENES Y BIENES PADRE
        bienes_list = [item['id_bien']
                       for item in data if item['id_bien'] != None]
        bienes_padre_list = [item['id_bien_padre']
                             for item in data if item['id_item_entrada_almacen'] == None and item['id_bien_padre'] != None]
        bienes_list.extend(bienes_padre_list)
        bienes_existe = CatalogoBienes.objects.filter(id_bien__in=bienes_list)
        if bienes_existe.count() != len(set(bienes_list)):
            raise ValidationError('Uno o varios bienes que están asociando en los items no existen')

        # CONOCER LOS QUE SE VAN A CREAR
        items_por_crear = [
            item for item in data if item['id_item_entrada_almacen'] == None]

        # CONOCER LOS QUE EXISTEN Y NO SE VAN A ACTUALIZAR
        items_existen_sin_actualizar = ItemEntradaAlmacen.objects.filter(
            id_entrada_almacen=id_entrada).exclude(id_item_entrada_almacen__in=items_actualizar)

        # VALIDACIÓN QUE EL DOC_IDENTIFICADOR SEA ÚNICO EN LA ENTRADA
        doc_identificadores_existentes = [
            item.doc_identificador_bien for item in items_existen_sin_actualizar if item.doc_identificador_bien != None]
        docs_identificadores_list = [item['doc_identificador_bien']
                                     for item in data if item['doc_identificador_bien'] != None]
        doc_identificadores_existentes.extend(docs_identificadores_list)
        if len(set(doc_identificadores_existentes)) != len(doc_identificadores_existentes):
            raise ValidationError('Todos los documentos identificadores deben ser únicos')
        if len(docs_identificadores_list) != len(set(docs_identificadores_list)):
            raise ValidationError('Todos los documentos identificadores deben ser únicos')

        # TOTAL VALOR ENTRADA
        valor_total_items_actualizar_list = [
            float(item.valor_total_item) for item in items_entrada_actualizar]
        valor_total_item_existen_list = [
            float(item.valor_total_item) for item in items_existen_sin_actualizar]
        valor_total_item_crear_list = [
            float(item['valor_total_item']) for item in items_por_crear]
        valor_total_entrada = valor_total_items_actualizar_list + \
            valor_total_item_existen_list + valor_total_item_crear_list
        valor_total_entrada = sum(valor_total_entrada)

        # SEPARAR LO QUE SE CREA EN ACTIVOS FIJOS Y DE CONSUMO
        items_activos_fijos_crear_list = [
            item for item in items_por_crear if item['id_bien_padre'] != None and item['id_bien'] == None]
        items_consumo_crear_list = [
            item for item in items_por_crear if item['id_bien_padre'] == None and item['id_bien'] != None]

        # OBTENER TIPO DOC ULTIMO MOVIMIENTO DE ENTRADA
        tipo_doc_ultimo_movimiento = ''
        match entrada_almacen.id_tipo_entrada.cod_tipo_entrada:
            case 1:
                tipo_doc_ultimo_movimiento = 'E_CPR'
            case 2:
                tipo_doc_ultimo_movimiento = 'E_DON'
            case 3:
                tipo_doc_ultimo_movimiento = 'E_RES'
            case 4:
                tipo_doc_ultimo_movimiento = 'E_CPS'
            case 5:
                tipo_doc_ultimo_movimiento = 'E_CMD'
            case 6:
                tipo_doc_ultimo_movimiento = 'E_CNV'
            case 7:
                tipo_doc_ultimo_movimiento = 'E_EMB'
            case 8:
                tipo_doc_ultimo_movimiento = 'E_INC'

        # VARIABLES AUDITORIAS
        valores_creados_detalles = []
        valores_actualizados_detalles = []

        # CREACIÓN ACTIVOS FIJOS
        items_guardados = []
        for item in items_activos_fijos_crear_list:
            id_bien_padre = item.get('id_bien_padre')
            doc_identificador_bien = item.get('doc_identificador_bien')
            id_porcentaje_iva = item.get('porcentaje_iva')
            cantidad_vida_util = item.get('cantidad_vida_util')
            id_unidad_medida_vida_util = item.get('id_unidad_medida_vida_util')
            valor_residual = item.get('valor_residual')
            tiene_hoja_vida = item.get('tiene_hoja_vida')
            id_bodega = item.get('id_bodega')
            valor_total_item = item.get('valor_total_item')
            cod_estado = item.get('cod_estado')

            cod_estado_instance = EstadosArticulo.objects.filter(cod_estado=cod_estado).first()

            # CREACIÓN DE UN ITEM ACTIVO FIJO EN BASE A CAMPOS HEREDADOS DEL PADRE
            bien_padre = CatalogoBienes.objects.filter(
                id_bien=id_bien_padre).first()
            bien_padre_serializado = CatalogoBienesSerializer(bien_padre)

            # ASIGNACIÓN DEL ÚLTIMO NÚMERO DEL ELEMENTO
            ultimo_numero_elemento = CatalogoBienes.objects.filter(Q(codigo_bien=bien_padre.codigo_bien) & ~Q(
                nro_elemento_bien=None)).order_by('-nro_elemento_bien').first()
            numero_elemento = 1
            if ultimo_numero_elemento:
                numero_elemento = ultimo_numero_elemento.nro_elemento_bien + 1

            # ASIGNACIÓN DE INFORMACIÓN PARA LA CREACIÓN DEL ELEMENTO
            data_create = bien_padre_serializado.data
            data_create['nro_elemento_bien'] = numero_elemento
            data_create['doc_identificador_nro'] = doc_identificador_bien
            data_create['id_porcentaje_iva'] = id_porcentaje_iva
            data_create['cantidad_vida_util'] = cantidad_vida_util
            data_create['id_unidad_medida_vida_util'] = id_unidad_medida_vida_util
            data_create['valor_residual'] = valor_residual
            data_create['tiene_hoja_vida'] = tiene_hoja_vida
            data_create['id_bien_padre'] = id_bien_padre
            del data_create['id_bien']
            del data_create['maneja_hoja_vida']
            del data_create['visible_solicitudes']
            serializer = CatalogoBienesSerializer(data=data_create, many=False)
            serializer.is_valid(raise_exception=True)
            elemento_creado = serializer.save()

            # REGISTRAR LA ENTRADA EN INVENTARIO
            bodega = Bodegas.objects.filter(id_bodega=id_bodega).first()

            registro_inventario = Inventario.objects.create(
                id_bien=elemento_creado,
                id_bodega=bodega,
                cod_tipo_entrada=entrada_almacen.id_tipo_entrada,
                fecha_ingreso=entrada_almacen.fecha_entrada.date(),
                id_persona_origen=entrada_almacen.id_proveedor,
                numero_doc_origen=entrada_almacen.numero_entrada_almacen,
                valor_ingreso=valor_total_item,
                ubicacion_en_bodega=True,
                cod_estado_activo=cod_estado_instance,
                fecha_ultimo_movimiento=datetime.now(),
                tipo_doc_ultimo_movimiento=tipo_doc_ultimo_movimiento,
                id_registro_doc_ultimo_movimiento=entrada_almacen.id_entrada_almacen
            )
            if tiene_hoja_vida == True:
                if bien_padre.cod_tipo_activo:
                    match bien_padre.cod_tipo_activo.cod_tipo_activo:
                        case 'Com':
                            create_hoja_vida = HojaDeVidaComputadores.objects.create(
                                id_articulo=elemento_creado
                            )
                        case 'Veh':
                            create_hoja_vida = HojaDeVidaVehiculos.objects.create(
                                id_articulo=elemento_creado
                            )
                        case 'OAc':
                            create_hoja_vida = HojaDeVidaOtrosActivos.objects.create(
                                id_articulo=elemento_creado
                            )
            item['id_bien'] = elemento_creado.id_bien
            serializador_item_entrada = SerializerItemEntradaActivosFijos(
                data=item, many=False)
            serializador_item_entrada.is_valid(raise_exception=True)
            serializador_item_entrada.save()
            items_guardados.append(serializador_item_entrada.data)
            valores_creados_detalles.append({'nombre': elemento_creado.nombre})

        # CREACIÓN DE CONSUMO
        for item in items_consumo_crear_list:
            id_bien_ = item.get('id_bien')
            cantidad = item.get('cantidad')
            id_bodega = item.get('id_bodega')

            # REALIZAR EL GUARDADO DE LOS ITEMS TIPO BIEN CONSUMO EN INVENTARIO
            bodega = Bodegas.objects.filter(id_bodega=id_bodega).first()

            # CREA EL BIEN CONSUMO EN INVENTARIO O MODIFICA LA CANTIDAD POR BODEGA
            bien = CatalogoBienes.objects.filter(id_bien=id_bien_).first()
            id_bien_inventario = Inventario.objects.filter(
                id_bien=bien.id_bien, id_bodega=bodega.id_bodega).first()

            # SUMA EL REGISTRO SI ESTABA ESE BIEN EN ESA BODEGA EN INVENTARIO
            if id_bien_inventario:
                if id_bien_inventario.cantidad_entrante_consumo != None:
                    suma = id_bien_inventario.cantidad_entrante_consumo + cantidad
                    id_bien_inventario.cantidad_entrante_consumo = suma
                    id_bien_inventario.save()
                else:
                    id_bien_inventario.cantidad_entrante_consumo = cantidad
                    id_bien_inventario.save()
            else:
                registro_inventario = Inventario.objects.create(
                    id_bien=bien,
                    id_bodega=bodega,
                    cod_tipo_entrada=entrada_almacen.id_tipo_entrada,
                    cantidad_entrante_consumo=cantidad,
                    fecha_ingreso=entrada_almacen.fecha_entrada.date()
                )
            serializador_item_entrada_consumo = SerializerItemEntradaConsumo(
                data=item, many=False)
            serializador_item_entrada_consumo.is_valid(raise_exception=True)
            serializador_item_entrada_consumo.save()
            items_guardados.append(serializador_item_entrada_consumo.data)

            valores_creados_detalles.append({'nombre': bien.nombre})

        # SEPARAR LO QUE SE ACTUALIZA EN ACTIVOS FIJOS Y DE CONSUMO
        items_activos_fijos_actualizar_list = [
            item for item in items_entrada_actualizar if item.id_bien.cod_tipo_bien == 'A']
        items_consumo_actualizar_list = [
            item for item in items_entrada_actualizar if item.id_bien.cod_tipo_bien == 'C']

        # ACTUALIZAR ACTIVOS FIJOS
        items_activos_fijos_actualizar_id_list = [
            item.id_bien.id_bien for item in items_activos_fijos_actualizar_list]
        catalogo_bienes_fijos_actualizar = CatalogoBienes.objects.filter(
            id_bien__in=items_activos_fijos_actualizar_id_list)
        inventario_fijos_actualizar = Inventario.objects.filter(
            id_bien__in=items_activos_fijos_actualizar_id_list)
        items_actualizables = [inventario for inventario in inventario_fijos_actualizar if str(inventario.id_registro_doc_ultimo_movimiento) == str(
            entrada_almacen.id_entrada_almacen) and str(inventario.tipo_doc_ultimo_movimiento) == str(tipo_doc_ultimo_movimiento)]
        items_no_actualizables = [inventario for inventario in inventario_fijos_actualizar if str(inventario.id_registro_doc_ultimo_movimiento) != str(
            entrada_almacen.id_entrada_almacen) or str(inventario.tipo_doc_ultimo_movimiento) != str(tipo_doc_ultimo_movimiento)]
        id_bien_items_actualizables = [
            item.id_bien.id_bien for item in items_actualizables]
        item_data_por_actualizar = [
            item for item in data if item['id_bien'] in id_bien_items_actualizables]

        for item in item_data_por_actualizar:
            # SE ACTUALIZA EN CATALOGO BIENES
            catalogo_bien_instance_actualizar = catalogo_bienes_fijos_actualizar.filter(
                id_bien=item['id_bien']).first()
            item['id_porcentaje_iva'] = item['porcentaje_iva']
            serializer_catalogo_bien = CatalogoBienesActivoFijoPutSerializer(
                catalogo_bien_instance_actualizar, data=item)
            serializer_catalogo_bien.is_valid(raise_exception=True)
            serializer_catalogo_bien.save()

            descripcion_item_actualizado = {
                'nombre': serializer_catalogo_bien.data['nombre']}

            # SE ACTUALIZA EN INVENTARIO
            inventario_instance_actualizar = inventario_fijos_actualizar.filter(
                id_bien=item['id_bien']).first()
            serializer_inventario = SerializerUpdateInventariosActivosFijos(
                inventario_instance_actualizar, data=item)
            serializer_inventario.is_valid(raise_exception=True)
            serializer_inventario.save()

            previous_item_actualizado = copy.copy(item_instance)

            # SE ACTUALIZA ITEM ENTRADA
            item_instance = items_entrada_actualizar.filter(
                id_item_entrada_almacen=item['id_item_entrada_almacen']).first()
            serializer_item = SerializerUpdateItemEntradaActivosFijos(
                item_instance, data=item)
            serializer_item.is_valid(raise_exception=True)
            serializer_item.save()

            items_guardados.append(serializer_item.data)

            valores_actualizados_detalles.append(
                {'descripcion': descripcion_item_actualizado, 'previous': previous_item_actualizado, 'current': item_instance})

        # ACTUALIZAR ITEMS DE CONSUMO
        items_consumo_actualizar_id_list = [
            item.id_bien.id_bien for item in items_consumo_actualizar_list]
        inventario_consumo_actualizar = Inventario.objects.filter(
            id_bien__in=items_consumo_actualizar_id_list)
        item_data_por_actualizar_consumo = [
            item for item in data if item['id_bien'] in items_consumo_actualizar_id_list]

        for item in item_data_por_actualizar_consumo:
            item_consumo_instance = items_entrada_actualizar.filter(
                id_bien=item['id_bien']).first()

            # CANTIDAD AUMENTA
            if item['cantidad'] >= item_consumo_instance.cantidad:
                inventario_instance_actualizar = inventario_consumo_actualizar.filter(
                    id_bien=item['id_bien'], id_bodega=item['id_bodega']).first()

                if item['id_bodega'] == inventario_instance_actualizar.id_bodega.id_bodega:
                    # SE ACTUALIZA EN INVENTARIO
                    item_instance = items_entrada_actualizar.filter(
                        id_item_entrada_almacen=item['id_item_entrada_almacen']).first()

                    item['cantidad_entrante_consumo'] = inventario_instance_actualizar.cantidad_entrante_consumo + \
                        abs((item_instance.cantidad - item['cantidad']))
                    serializer_inventario = SerializerUpdateInventariosConsumo(
                        inventario_instance_actualizar, data=item)
                    serializer_inventario.is_valid(raise_exception=True)
                    serializer_inventario.save()

                    bien_actualizado = bienes_existe.filter(
                        id_bien=item['id_bien']).first()
                    descripcion_item_actualizado = {
                        'nombre': bien_actualizado.nombre}
                    previous_item_actualizado = copy.copy(item_instance)

                    # SE ACTUALIZA ITEM ENTRADA
                    serializer_item = SerializerItemEntradaConsumoPut(
                        item_instance, data=item)
                    serializer_item.is_valid(raise_exception=True)
                    serializer_item.save()

                    items_guardados.append(serializer_item.data)

                    valores_actualizados_detalles.append(
                        {'descripcion': descripcion_item_actualizado, 'previous': previous_item_actualizado, 'current': item_instance})

                else:
                    pass
            # CANTIDAD REDUCE
            else:
                pass

        # SE ACTUALIZA VALOR TOTAL ENTRADA MODIFICADO
        entrada_almacen.valor_total_entrada = valor_total_entrada

        # VALIDACIÓN PERSONA ACTUALIZA
        persona_actualiza = request.user.persona
        if (persona_actualiza.id_persona != entrada_almacen.id_creador.id_persona):
            entrada_almacen.id_persona_ult_act_dif_creador = persona_actualiza
            entrada_almacen.fecha_ultima_actualizacion_diferente_creador = datetime.now()

        entrada_almacen.save()

        descripcion = {"numero_entrada_almacen": str(
            entrada_almacen.numero_entrada_almacen), "fecha_entrada": str(entrada_almacen.fecha_entrada)}
        direccion = Util.get_client_ip(request)

        # AUDITORIAS
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 34,
            "cod_permiso": "AC",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

        return Response({'success':True, 'detail':'Actualizado exitosamente', 'data': items_guardados}, status=status.HTTP_201_CREATED)


class AnularEntrada(generics.UpdateAPIView):
    serializer_class = EntradaSerializer
    queryset = EntradasAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_entrada):
        datos_ingresados = request.data

        entrada_anular = EntradasAlmacen.objects.filter(
            id_entrada_almacen=id_entrada).first()
        items_entrada = ItemEntradaAlmacen.objects.filter(
            id_entrada_almacen=id_entrada)
        if not entrada_anular:
            raise ValidationError('No se encontro una entrada asociada al ID que ingresó')
        if entrada_anular.entrada_anulada == True:
            raise ValidationError('Esta entrada ya ha sido anulada')

        if not items_entrada:
            raise ValidationError('No hay items asociados a la entrada')

        activos_fijos = [
            i.id_bien.id_bien for i in items_entrada if i.id_bien.cod_tipo_bien == 'A']
        bienes = CatalogoBienes.objects.filter(Q(id_bien__in=activos_fijos))
        codigos_bienes = [i.codigo_bien for i in bienes]
        bienes_consumo = [
            i.id_bien.id_bien for i in items_entrada if i.id_bien.cod_tipo_bien == 'C']

        for i in activos_fijos:
            aux = Inventario.objects.filter(id_bien=i).first()
            if not aux:
                raise ValidationError('Uno de los items no tiene registro en iventairo')
            hdv_computadores = HojaDeVidaComputadores.objects.filter(
                id_articulo=i).first()
            hdv_vehivulos = HojaDeVidaVehiculos.objects.filter(
                id_articulo=i).first()
            hdv_otro_activos = HojaDeVidaOtrosActivos.objects.filter(
                id_articulo=i).first()
            if aux.id_registro_doc_ultimo_movimiento != entrada_anular.id_entrada_almacen or aux.cod_tipo_entrada != entrada_anular.id_tipo_entrada:
                raise ValidationError('Uno de los items de la entrada a anular ya registra movimientos posteriores')
            if hdv_computadores or hdv_vehivulos or hdv_otro_activos:
                raise ValidationError('Uno de los items de la entrada a anular ya tiene hoja de vida, no se pueden anular entradas con items que tengan hoja de vida')
        instancia_items_entrada_eliminar = ItemEntradaAlmacen.objects.filter(
            Q(id_bien__in=activos_fijos) & Q(id_entrada_almacen=id_entrada))
        instancia_inventario_eliminar = Inventario.objects.filter(Q(id_bien__in=activos_fijos) & Q(
            id_registro_doc_ultimo_movimiento=id_entrada) & Q(cod_tipo_entrada=entrada_anular.id_tipo_entrada))
        instancia_elementos = CatalogoBienes.objects.filter(
            Q(codigo_bien__in=codigos_bienes) & ~Q(nro_elemento_bien=None))
        entrada_anular.justificacion_anulacion = datos_ingresados['justificacion_anulacion']
        entrada_anular.fecha_anulacion = datetime.now()
        entrada_anular.id_persona_anula = request.user.persona
        entrada_anular.entrada_anulada = True
        valores_eliminados_detalles = [
            {'nombre': i.nombre} for i in instancia_elementos]
        entrada_anular.save()
        instancia_items_entrada_eliminar.delete()
        instancia_inventario_eliminar.delete()
        instancia_elementos.delete()

        descripcion = {"numero_entrada_almacen": str(
            entrada_anular.numero_entrada_almacen), "fecha_entrada": str(entrada_anular.fecha_entrada)}
        direccion = Util.get_client_ip(request)

        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 34,
            "cod_permiso": "BO",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        return Response({'success':True, 'detail':'Solicitud anulada exitosamente'}, status=status.HTTP_201_CREATED)

