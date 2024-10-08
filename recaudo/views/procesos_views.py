from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.utils import UtilsGestor
from recaudo.models.procesos_models import (
    EtapasProceso,
    TiposAtributos,
    AtributosEtapas,
    FlujoProceso,
    ValoresProceso,
    Procesos,
    CategoriaAtributo,
    Bienes,
    Avaluos
)
from recaudo.serializers.procesos_serializers import (
    EtapasProcesoSerializer,
    TiposAtributosSerializer,
    AtributosEtapasSerializer,
    FlujoProcesoSerializer,
    FlujoProcesoPostSerializer,
    ValoresProcesoSerializer,
    ValoresProcesoPostSerializer,
    ValoresProcesoPutSerializer,
    ProcesosSerializer,
    ProcesosPostSerializer,
    AtributosEtapasPostSerializer,
    CategoriaAtributoSerializer
)
from recaudo.models.base_models import TiposBien

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
import datetime
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.generics import get_object_or_404

from seguridad.permissions.permissions_recaudo import PermisoActualizarEtapasProcesoRentas, PermisoCrearFlujoProcesoRecaudo

class EtapasProcesoView(generics.ListAPIView):
    queryset = EtapasProceso.objects.all()
    serializer_class = EtapasProcesoSerializer
    #permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        method = self.request.method
        if method == 'POST':
            permissions.append(PermisoActualizarEtapasProcesoRentas())
        return permissions

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TiposAtributosView(generics.ListAPIView):
    queryset = TiposAtributos.objects.all()
    serializer_class = TiposAtributosSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActualizarTiposAtributosView(generics.ListAPIView):
    queryset = TiposAtributos.objects.all()
    serializer_class = TiposAtributosSerializer
    #permission_classes = [IsAuthenticated]

    def post(self, request, tipo):
        tipo_actual = TiposAtributos.objects.filter(pk=tipo)
        if len(tipo_actual) == 1:
            tipo_actual = tipo_actual.get()
            tipo_actual.tipo = request.data.get('tipo') if request.data.get('tipo') is not None else tipo_actual.tipo
            tipo_actual.notificacion = request.data.get('notificacion') if request.data.get('notificacion') is not None else tipo_actual.notificacion
            tipo_actual.save()
            return Response({'success': True, 'data': 'Tipo de atributo actualizado con exito.'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'data': 'No existe el tipo con el id enviado.'}, status=status.HTTP_200_OK)


class EliminarTiposAtributosView(generics.ListAPIView):
    queryset = TiposAtributos.objects.all()
    serializer_class = TiposAtributosSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, tipo):
        tipo_actual = TiposAtributos.objects.filter(pk=tipo)
        if len(tipo_actual) == 1:
            tipo_actual = tipo_actual.get()
            tipo_actual.delete()
            return Response({'success': True, 'data': 'Tipo de atributo eliminado con exito.'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'data': 'No existe el tipo con el id enviado.'}, status=status.HTTP_200_OK)


class AtributosEtapasView(generics.ListAPIView):
    queryset = AtributosEtapas.objects.all()
    serializer_class = AtributosEtapasSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, etapa):
        queryset = AtributosEtapas.objects.filter(id_etapa=etapa)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AtributosEtapasPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, etapa):
        atributo = AtributosEtapas.objects.filter(pk=etapa).get()
        serializer = AtributosEtapasPostSerializer(atributo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAtributosEtapasView(generics.ListAPIView):
    queryset = AtributosEtapas.objects.all()
    serializer_class = AtributosEtapasSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, etapa, categoria):
        queryset = AtributosEtapas.objects.filter(id_etapa=etapa).filter(id_categoria=categoria)
        queryset.delete()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class DeleteAtributosView(generics.ListAPIView):
    queryset = AtributosEtapas.objects.all()
    serializer_class = AtributosEtapasSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = AtributosEtapas.objects.filter(pk=pk)
        queryset.delete()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class FlujoProcesoView(generics.ListAPIView):
    queryset = FlujoProceso.objects.all()
    serializer_class = FlujoProcesoSerializer
    #permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        method = self.request.method
        if method == 'POST':
            permissions.append(PermisoCrearFlujoProcesoRecaudo())
        return permissions

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FlujoProcesoPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GraficaView(generics.ListAPIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        querysetEtapas = EtapasProceso.objects.all()
        querysetFlujos = FlujoProceso.objects.all()
        nuevasEtapas = []
        nuevoFlujo = []
        for item in querysetEtapas:
            nuevasEtapas.append({'id': item.pk, 'data': {'id': item.pk, 'etapa': item.etapa, 'descripcion': item.descripcion}})
        for item in querysetFlujos:
            data = {'fecha_flujo': item.fecha_flujo, 'descripcion': item.descripcion, 'requisitos': item.requisitos}
            nuevoFlujo.append({'id': item.pk, 'source': item.id_etapa_origen.pk, 'target': item.id_etapa_destino.pk, 'data': data})
        response = {
            'nodes': nuevasEtapas,
            'edges': nuevoFlujo
        }
        return Response(response, status=status.HTTP_200_OK)


class ValoresProcesoView(generics.ListAPIView):
    queryset = ValoresProceso.objects.all()
    serializer_class = ValoresProcesoSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, proceso):
        queryset = ValoresProceso.objects.filter(id_proceso=proceso)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        data._mutable=True
        archivo_soporte = request.FILES.get('documento')

        # CREAR ARCHIVO EN T238
        if archivo_soporte:
            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "ValoresProcesoRecaudo")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['documento'] = archivo_creado_instance.id_archivo_digital
        
        serializer = ValoresProcesoPostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, proceso):
        data = request.data
        data._mutable=True
        archivo_soporte = request.FILES.get('documento')

        valores = ValoresProceso.objects.filter(pk=proceso).get()

        # ACTUALIZAR ARCHIVO
        if archivo_soporte:
            if valores.documento:
                valores.documento.ruta_archivo.delete()
                valores.documento.delete()

            archivo_creado = UtilsGestor.create_archivo_digital(archivo_soporte, "ValoresProcesoRecaudo")
            archivo_creado_instance = ArchivosDigitales.objects.filter(id_archivo_digital=archivo_creado.get('id_archivo_digital')).first()
            
            data['documento'] = archivo_creado_instance.id_archivo_digital
        # elif not archivo_soporte and valores.documento:
        #     valores.documento.ruta_archivo.delete()
        #     valores.documento.delete()

        serializer = ValoresProcesoPutSerializer(valores, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActualizarEtapaProceso(generics.ListAPIView):
    serializer_class = ProcesosSerializer
    permission_classes = [IsAuthenticated, PermisoActualizarEtapasProcesoRentas]

    def get(self, request, proceso):
        procesoFilter = Procesos.objects.filter(pk=proceso).filter(fin__isnull=True)
        if len(procesoFilter) == 0:
            return Response({'success': False, 'detail': 'No existen etapas sin finalizar en el proceso con el id enviado'}, status=status.HTTP_200_OK)
        else:
            procesoActual = procesoFilter.get()
            procesoActual.fin = datetime.date.today()
            procesoActual.save()
            flujo_siguiente = FlujoProceso.objects.filter(id_etapa_origen=procesoActual.id_etapa.pk)
            if len(flujo_siguiente) == 0:
                serializer = self.serializer_class(procesoActual, many=False)
                return Response({'success': True, 'detail': 'Esta era la ultima etapa en el flujo, fecha fin actualizada correctamente', 'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                flujo_nuevo = flujo_siguiente.first()
                proceso_nuevo = Procesos(
                    id_cartera=procesoActual.id_cartera,
                    id_etapa=flujo_nuevo.id_etapa_destino,
                    id_funcionario=procesoActual.id_funcionario,
                    id_categoria=procesoActual.id_categoria,
                    inicio=datetime.date.today()
                )
                proceso_nuevo.save()
                serializer = self.serializer_class(proceso_nuevo, many=False)
                return Response({'success': True, 'detail': 'Se creo la siguiente etapa de manera exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)


class ProcesosView(generics.ListAPIView):
    queryset = Procesos.objects.filter(fin__isnull=True)
    serializer_class = ProcesosSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProcesosPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProcesosView(generics.ListAPIView):
    queryset = Procesos.objects.all()
    serializer_class = ProcesosSerializer
    #permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        id_etapa = request.data['id_etapa']
        etapa = EtapasProceso.objects.filter(pk=id_etapa)
        proceso = Procesos.objects.filter(pk=pk)
        if len(proceso) == 1:
            if len(etapa) == 1:
                proceso = proceso.get()
                etapa = etapa.get()
                proceso.id_etapa = etapa
                proceso.save()
                return Response({'success': True, 'data': 'La etapa del proceso se ha actualizado con exito'}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'data': 'No existe la etapa con el id enviado'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'data': 'No existe el proceso con el id enviado'}, status=status.HTTP_400_BAD_REQUEST)



class UpdateCategoriaProcesosView(generics.ListAPIView):
    queryset = Procesos.objects.all()
    serializer_class = ProcesosSerializer

    def post(self, request, pk):
        
        id_categoria_nuevo = int(request.data.get('id_categoria'))
        if not id_categoria_nuevo:
            raise ValidationError("Es necesario el id de la categoria")
    
        try:
            categoria_seleccionada = CategoriaAtributo.objects.get(id=id_categoria_nuevo)
        except CategoriaAtributo.DoesNotExist:
            raise NotFound("No se encontro categoria ingresada")
        
        proceso = get_object_or_404(Procesos, pk=pk)

        if proceso:
            id_categoria_actual = proceso.id_categoria.id
            orden_categoria_actual = proceso.id_categoria.orden
            nombre_categoria_actual = proceso.id_categoria.categoria

            if orden_categoria_actual > int(categoria_seleccionada.orden):
                return Response({'success': False, 'data': f'No se permite cambiar a una etapa anterior,Actualmente estas en  {nombre_categoria_actual}'}, status=status.HTTP_400_BAD_REQUEST)
            elif id_categoria_nuevo == id_categoria_actual:
                return Response({'success': False, 'data': f'La etapa seleccionada es igual a la que está actualmente en curso'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                categoria = get_object_or_404(CategoriaAtributo, pk=id_categoria_nuevo)
                proceso.id_categoria = categoria
                proceso.save()
                return Response({'success': True, 'data': 'La categoría del proceso se ha actualizado con éxito'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'data': 'No existe el proceso con el id enviado'}, status=status.HTTP_400_BAD_REQUEST)


class ProcesosGeneralView(generics.ListAPIView):
    queryset = Procesos.objects.all()
    serializer_class = ProcesosSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ProcesosGetGeneralView(generics.ListAPIView):
    queryset = Procesos.objects.all()
    serializer_class = ProcesosSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, proceso):
        queryset = Procesos.objects.filter(pk=proceso)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    
# class AvaluosBienesView(generics.CreateAPIView):
#     serializer_class = AvaluosSerializer
    
#     def post(self, request):
#         data = request.data
#         serializer = self.serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'success': True, 'detail':'Se agregar los avaluos del bien que da el deudor', 'data':serializer.data},status=status.HTTP_200_OK)


class CategoriaAtributoView(generics.ListAPIView):
    queryset = CategoriaAtributo.objects.all()
    serializer_class = CategoriaAtributoSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        categoria = CategoriaAtributo.objects.filter(pk=pk).get()
        serializer = CategoriaAtributoSerializer(categoria, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
    def delete(self, request, pk):
        try:
            categoria = CategoriaAtributo.objects.get(pk=pk)
        except CategoriaAtributo.DoesNotExist:
            return Response({'success': False, 'error': 'La categoría no existe'}, status=status.HTTP_404_NOT_FOUND)

        categoria.delete()
        return Response({'success': True, 'message': 'Categoría eliminada exitosamente'}, status=status.HTTP_200_OK)
class EtapasFiltradoView(generics.ListAPIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        etapas = AtributosEtapas.objects.all()
        etapasGeneral = []
        etapasLista = []
        etapasNombres = []

        for etapa in etapas:
            etapasNombres.append(etapa.id_etapa.etapa)
            etapasLista.append(
                {
                    'etapa_general': etapa.id_etapa,
                    'etapa': etapa.id_etapa.etapa,
                    'categoria_general': etapa.id_categoria,
                    'categoria': etapa.id_categoria.categoria
                }
            )

        for etapa in etapasNombres:
            categorias = []
            etapa_general = {}
            for item in etapasLista:
                if etapa == item['etapa']:
                    etapa_general = EtapasProcesoSerializer(item['etapa_general']).data
                    categorias.append(CategoriaAtributoSerializer(item['categoria_general']).data)

            categorias_vistas = set()

            nueva_lista = []

            for elemento in categorias:
                categoria = elemento["categoria"]

                if categoria not in categorias_vistas:
                    nueva_lista.append(elemento)
                    categorias_vistas.add(categoria)
            categorias = nueva_lista
            etapasGeneral.append(
                {
                    'etapa': etapa_general,
                    'subetapas': categorias
                }
            )

        return Response({'success': True, 'data': etapasGeneral}, status=status.HTTP_200_OK)


class CategoriasEtapasFiltradoView(generics.ListAPIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        etapaGeneral = AtributosEtapas.objects.filter(pk=pk)

        if len(etapaGeneral):
            etapaG = etapaGeneral.get()
            etapas = AtributosEtapas.objects.all()
            etapasGeneral = []
            etapasLista = []
            etapasNombres = []

            for etapa in etapas:
                etapasNombres.append(etapa.id_etapa.etapa)
                etapasLista.append(
                    {
                        'etapa_general': etapa.id_etapa,
                        'etapa': etapa.id_etapa.etapa,
                        'categoria_general': etapa.id_categoria,
                        'categoria': etapa.id_categoria.categoria
                    }
                )

            for etapa in etapasNombres:
                categorias = []
                for item in etapasLista:
                    if etapa == etapaG.id_etapa.etapa:
                        categorias.append(CategoriaAtributoSerializer(item['categoria_general']).data)
                if len(categorias) > 0:
                    categorias_vistas = set()

                    nueva_lista = []

                    for elemento in categorias:
                        categoria = elemento["categoria"]

                        if categoria not in categorias_vistas:
                            nueva_lista.append(elemento)
                            categorias_vistas.add(categoria)

                    etapasGeneral = nueva_lista

            return Response({'success': True, 'data': etapasGeneral}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'data': 'No existe la etapa con el id enviado'}, status=status.HTTP_200_OK)


class DeleteEtapaView(generics.ListAPIView):
    queryset = EtapasProceso.objects.all()
    serializer_class = EtapasProcesoSerializer
    permission_classes = [IsAuthenticated, PermisoActualizarEtapasProcesoRentas]

    def get(self, request, etapa):
        queryset = EtapasProceso.objects.filter(id=etapa)
        queryset.delete()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class DeleteCategoriaAtributoView(generics.ListAPIView):
    queryset = CategoriaAtributo.objects.all()
    serializer_class = CategoriaAtributoSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, categoria):
        queryset = CategoriaAtributo.objects.filter(id=categoria)
        queryset.delete()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)