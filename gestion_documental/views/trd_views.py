import json
from transversal.serializers.organigrama_serializers import UnidadesGetSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db.models import Q
import copy
from django.db import transaction
from datetime import datetime
from rest_framework import generics
from rest_framework.response import Response
from gestion_documental.models.plantillas_models import PlantillasDoc
from gestion_documental.models.tca_models import TablasControlAcceso
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from gestion_documental.serializers.trd_serializers import (
    BuscarTipologiaSerializer,
    BusquedaTRDNombreVersionSerializer,
    ConfigTipologiasDocAgnoSerializer,
    ConsecPorNivelesTipologiasDocAgnoSerializer,
    CrearTipologiaDocumentalSerializer,
    GetHistoricoTRDSerializer,
    ModificarTRDNombreVersionSerializer,
    ModificarTipologiaDocumentalSerializer,
    ReanudarTrdSerializer,
    RetornarDatosTRDSerializador,
    TipologiasDocumentalesSerializer,
    TRDSerializer,
    TRDPostSerializer,
    TRDPutSerializer,
    TRDFinalizarSerializer,
    FormatosTiposMedioSerializer,
    FormatosTiposMedioPostSerializer,
    SeriesSubSeriesUnidadesOrgTRDSerializer,
    SeriesSubSeriesUnidadesOrgTRDPutSerializer,
    TipologiasDocumentalesPutSerializer,
    GetSeriesSubSUnidadOrgTRDSerializer,
    TipologiasSeriesSubSUnidadOrgTRDSerializer
)
from gestion_documental.serializers.ccd_serializers import (
    CCDSerializer
)

from gestion_documental.models.ccd_models import (
    CatalogosSeriesUnidad,
    CuadrosClasificacionDocumental,
    SeriesDoc
)
from transversal.models.organigrama_models import (
    Organigramas,
    UnidadesOrganizacionales
)
from gestion_documental.models.trd_models import (
    ConfigTipologiasDocAgno,
    ConsecPorNivelesTipologiasDocAgno,
    TablaRetencionDocumental,
    TipologiasDoc,
    SeriesSubSUnidadOrgTRDTipologias,
    FormatosTiposMedio,
    CatSeriesUnidadOrgCCDTRD,
    FormatosTiposMedioTipoDoc,
    HistoricosCatSeriesUnidadOrgCCDTRD,
    TiposMediosDocumentos,
    
)

#CREAR TIPOLOGIA DOCUMENTAL

class CrearTipologiaDocumental(generics.CreateAPIView):
    serializer_class = CrearTipologiaDocumentalSerializer
    queryset = TipologiasDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        data = request.data
        
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        tipologia = serializador.save()
        
        id_lista_formatos = data["formatos"]
        id_cod_tipo_medio = data["cod_tipo_medio_doc"]
        
        if not id_lista_formatos:
            raise ValidationError('Se debe asociar minimo un formato a la tipología.')
        
        id_lista_formatos=set(id_lista_formatos) #eliminar los duplicados de una lista enviada por el usuario "Formatos" ejm:[10,25,10]
        formatos = FormatosTiposMedio.objects.filter(id_formato_tipo_medio__in=id_lista_formatos)
        
        if len(id_lista_formatos) != len(formatos) :#"len" es para contar el numero de elementos del campo formatos (del campo del usuario) de la lista.
            raise ValidationError('Verifique que todos los formatos existan.')

        tipo_medio = formatos.filter(cod_tipo_medio_doc=id_cod_tipo_medio) if id_cod_tipo_medio!='H' else formatos.filter(cod_tipo_medio_doc__in=['E','F'])
        
        if len(tipo_medio) != len(formatos):
            raise ValidationError('Verifique que los formatos existan en relacion con el tipo de medio.')

        if formatos:
            for formato in formatos:
                FormatosTiposMedioTipoDoc.objects.create(
                    id_tipologia_doc = tipologia, 
                    id_formato_tipo_medio = formato)
                        

        return Response({'success':True, 'detail':'Se creo correctamente'}, status=status.HTTP_200_OK)
    
       
        #formatos = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=id_formato_tipo_medio).first()
        
        #VALIDAR QUE LOS FORMATOS PERTENEZCAN AL TIPO DE MEDIO INDICADO
        
        
        
        # for tipologia in data:
        #     if tipologia['cod_tipo_medio_doc'] == 'E' or tipologia['cod_tipo_medio_doc']== 'F':
        #         formatos_actuales = TiposMediosDocumentos.objects.filter(cod_tipo_medio_doc=tipologia['cod_tipo_medio_doc'])
        #         formatos_actuales_list = [formato.id_formato_tipo_medio for formato in formatos_actuales]
        #         if not set(tipologia['formatos']).issubset(formatos_actuales_list):
        #             return Response({'success':False, 'detail':'Debe asignar formatos que correspondan al tipo medio elegido'}, status=status.HTTP_400_BAD_REQUEST)


#EDITAR UNA TIPOLOGIA DOCUMENTAL
class ModificarTipologiaDocumental(generics.UpdateAPIView):
    serializer_class = ModificarTipologiaDocumentalSerializer
    queryset = TipologiasDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
        data = request.data
        
        #VALIDAR DE QUE LA TIPOLOGIA EXISTA EN LA TABLA T208Id_TipologiaDoc
        
        tipologias = TipologiasDoc.objects.filter(id_tipologia_documental=pk).first()
        
        #item_ya_usado = TipologiasDocumentales.objects.filter(id_tipologia_documental=pk, item_ya_usado=True).first()
        
        if not tipologias:
            raise ValidationError('No existe la Tipologia ingresada')        
        
        #EL NOMBRE DE LA TIPOLOGIA SOLO SE PUEDE EDITAR SI EL CAMPO ITEM_YA_USADO ESTA EN FALSE
        if tipologias.item_ya_usado==True:
            if tipologias.nombre != data['nombre']:
                raise ValidationError('No se puede actualizar el nombre de una Tipologia que esta siendo usada.')
            elif tipologias.activo != data['activo']:
                raise ValidationError('No se puede actualizar el estado de una Tipologia que esta siendo usada.')    
        

        if tipologias.activo==True:
            if 'activo' in data:
                if data['activo']==False:
                    plantillas_asociadas_tiplogia=PlantillasDoc.objects.filter(id_tipologia_doc_trd=tipologias.id_tipologia_documental)
                    for x in plantillas_asociadas_tiplogia:
                        #print (x)
                        nombre_tipologia=x.id_tipologia_doc_trd.nombre
                        x.id_tipologia_doc_trd=None
                        x.otras_tipologias=nombre_tipologia
                        x.asociada_a_tipologia_doc_trd=False
                        x.save()
            
        serializador = self.serializer_class(tipologias,data=data)
        serializador.is_valid(raise_exception=True)
        tipologia = serializador.save()
        
        
        id_lista_formatos = data['formatos']
        id_cod_tipo_medio = data['cod_tipo_medio_doc']
        
        if not id_lista_formatos:
            raise ValidationError('Los campos de los formatos no pueden quedar vacios.')
        if not id_cod_tipo_medio:
            raise ValidationError('Los campos del tipo medio doc no pueden quedar vacios.')
        
        desactivar_tipologia = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_tipologia_doc=pk,activo=True,id_catserie_unidadorg_ccd_trd__id_trd__fecha_retiro_produccion=None).first()
        serializer = RetornarDatosTRDSerializador(desactivar_tipologia)  
        
        if desactivar_tipologia and not data['activo']:
            try:
                raise PermissionDenied('La Tipologia no se puede desactivar si se esta usando en una TRD.')
            except PermissionDenied as e:
                return Response({'success':False, 'detail':'La Tipologia no se puede desactivar si se esta usando en una TRD.', 'data':serializer.data}, status=status.HTTP_403_FORBIDDEN)
                
        id_lista_formatos = set(id_lista_formatos) #el "SET" elimina los valores repetidos enviados por el usuario ejm:[10,10,25] y solo deja el primero
        
        formatos = FormatosTiposMedio.objects.filter(id_formato_tipo_medio__in = id_lista_formatos) #"IN" para traer la lista de datos.
        if len(id_lista_formatos) != len(formatos): #"LEN" para ir contando uno por uno el numero de elementos de la lista [10,15,25]
            raise ValidationError('Verifique que los formatos ingresados para su modificación existan.')
        
        tipo_medio = formatos.filter(cod_tipo_medio_doc = id_cod_tipo_medio) if id_cod_tipo_medio != 'H' else formatos.filter(cod_tipo_medio_doc__in=['E','F'])
        
        if len(tipo_medio) != len(formatos):
            raise ValidationError('Verifique que los formatos a modificar pertenezcan al tipo de medio elegido.')
        
        #VALIDAR QUE SE CREEN LAS NUEVAS RELACIONES EN LA TABLA 217 CUANDO MODIFICAN CAMPOS DE LOS FORMATOS ejm:[10,20] nuevo:[10,20,23], se debe de crear la nueva relacion con el codigo 23
       
        formatosactuales = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=pk)
        list_id_formatos_formatosactuales = formatosactuales.values_list('id_formato_tipo_medio__id_formato_tipo_medio', flat=True)#values_list = traer una lista de valores
        
        formatos_eliminar = formatosactuales.exclude(id_formato_tipo_medio__in=id_lista_formatos) #forma de poder ingresar los nuevos datos registrador por el usuario exluyendo los datos que ya existen.
        # list_id_formatos_formatosactuales = [formatoactual.id_formato_tipo_medio.id_formato_tipo_medio for formatoactual in formatosactuales] # list comprehension = ?
        if formatos_eliminar:
            formatos_eliminar.delete()
        
        #poder crear los nuevos registros en la tabla 217 con los nuevos formatos enviados por el usuario.
        for formato in id_lista_formatos:
            if formato not in list_id_formatos_formatosactuales:
                FormatosTiposMedioTipoDoc.objects.create(
                    id_tipologia_doc = tipologia, 
                    id_formato_tipo_medio = formatos.filter(id_formato_tipo_medio=formato).first()
                )              
        return Response({'success':True, 'detail':'Se Realizo la modificación solicitada.'}, status=status.HTTP_200_OK)
    
#ELIMINAR TIPOLOGIA DOCUMENTAL

class EliminarTipologiaDocumental(generics.DestroyAPIView):
    serializer_class = CrearTipologiaDocumentalSerializer
    queryset = TipologiasDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        tipologia = TipologiasDoc.objects.filter(id_tipologia_documental=pk).first()
        
        if tipologia:
            if not tipologia.item_ya_usado:
                tipologia.delete()
                return Response({'success':True, 'detail':'Registro se elimino correctamente.'}, status=status.HTTP_200_OK)
            else:
                raise ValidationError('No se puede eliminar una tipologia que se ecuentre siendo usada.')
                #raise NotFound('No se puede eliminar una tipologia que se ecuentre siendo usada.')
        else:
            raise ValidationError('No existe la tipologia indicada a eliminar.')
             #raise NotFound('No existe la tipologia indicada a eliminar.')

            #raise ValidationError('No se puede eliminar una tipologia que se ecuentre siendo usada.')


#BUSCAR TIPOLOGIA

class BuscarTipologia(generics.ListAPIView):
    serializer_class = BuscarTipologiaSerializer
    queryset = TipologiasDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        nombre_tipologia = request.query_params.get('nombre')
        buscar_tipologia = self.queryset.filter(nombre__icontains=nombre_tipologia) if nombre_tipologia else self.queryset.all()
        serializador = self.serializer_class(buscar_tipologia,many=True,context={'request':request})
        
        return Response({'succes':True, 'detail':'Se encontraron las siguientes tipologias','data':serializador.data}, status=status.HTTP_200_OK)
            

#BUSQUEDA DE TRD POR NOMBRE Y VERSIÓN

class BusquedaTRDNombreVersion(generics.ListAPIView):
    serializer_class = BusquedaTRDNombreVersionSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
        filter={}
        
        for key, value in request.query_params.items():
            if key in ['nombre','version']:
                if value != '':
                    filter[key+'__icontains'] = value
         
         
        trd = self.queryset.all().filter(**filter)
        serializador = self.serializer_class(trd,many=True)
                         
        return Response({'succes':True, 'detail':'Se encontraron las siguientes TRD por Nombre y Versión','data':serializador.data}, status=status.HTTP_200_OK)

class GetHistoricoTRD(generics.ListAPIView):
    serializer_class = GetHistoricoTRDSerializer
    queryset = HistoricosCatSeriesUnidadOrgCCDTRD.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        id_trd = request.query_params.get('id_trd')
        queryset = self.queryset.all()
        
        if id_trd:
            queryset = queryset.filter(id_catserie_unidadorg_ccd_trd__id_trd=id_trd)
            
        serializador = self.serializer_class(queryset, many=True)
                         
        return Response({'succes':True, 'detail':'Se encontró el siguiente histórico','data':serializador.data}, status=status.HTTP_200_OK)

#MODIFICAR TDR NOMBRE Y VERSION

class ModificarNombreVersionTRD(generics.UpdateAPIView):
    serializer_class = ModificarTRDNombreVersionSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,id_trd):
        data = request.data
        
        #SE VALIDA DE QUE LA TRD A MODIFICAR EXISTA
        
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        
        if not trd:
            raise ValidationError('No existe la TRD ingresada')
        
        if trd.fecha_terminado:
            raise ValidationError('No se puede editar una TRD Finalizada.')
        
        
        serializador = self.serializer_class(trd,data=data)
        serializador.is_valid(raise_exception=True)
        trd = serializador.save()
        
        
        return Response({'succes':True, 'detail':'Se realizo la Modidificación Solicitada.'}, status=status.HTTP_200_OK)

class GetTipologiasDocumentales(generics.ListAPIView):
    serializer_class = TipologiasDocumentalesSerializer
    queryset = TipologiasDoc.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_trd):
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        if trd:
            tipologias = TipologiasDoc.objects.filter(id_trd=id_trd, activo=True).values()
            if not tipologias:
                return Response({'success':True, 'detail':'No se encontraron tipologías para el TRD', 'data':tipologias}, status=status.HTTP_200_OK)
            for tipologia in tipologias:
                formatos_tipologias = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=tipologia['id_tipologia_documental'])
                formatos_tipologias_list = [formato_tipologia.id_formato_tipo_medio.id_formato_tipo_medio for formato_tipologia in formatos_tipologias]
                formatos = FormatosTiposMedio.objects.filter(id_formato_tipo_medio__in=formatos_tipologias_list).values()
                tipologia['formatos'] = formatos
                
            return Response({'success':True, 'detail':'Se encontraron las siguientes tipologías para el TRD', 'data':tipologias}, status=status.HTTP_200_OK)
        else:
            raise NotFound('Debe consultar por un TRD válido')

class GetFormatosTipologiasDocumentales(generics.ListAPIView):
    serializer_class = FormatosTiposMedioSerializer
    queryset = FormatosTiposMedioTipoDoc.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_tipologia_documental):
        formatos_tipologias = self.queryset.filter(id_tipologia_doc=id_tipologia_documental)
        formatos_tipos_medio= [formato_tipo_medio.id_formato_tipo_medio for formato_tipo_medio in formatos_tipologias]
        formatos_tipologias_serializer = self.serializer_class(formatos_tipos_medio, many=True)
            
        return Response({'success':True, 'detail':'Se encontraron los siguientes formatos para la tipología elegida', 'data':formatos_tipologias_serializer.data}, status=status.HTTP_200_OK)

#----------------------------------------------------------------------------------------------------------------#

#Series SubSeries Unidades Organizacionales TRD
class CreateSerieSubSeriesUnidadesOrgTRD(generics.CreateAPIView):
    serializer_class = SeriesSubSeriesUnidadesOrgTRDSerializer
    queryset = CatSeriesUnidadOrgCCDTRD.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, id_trd):
        data_entrante = request.data
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        tipologias = request.data.get('tipologias')

        if trd:
            serializador = self.serializer_class(data=data_entrante, many=False)
            serializador.is_valid(raise_exception=True)
            
            cod_disposicion_final = serializador.validated_data.get('cod_disposicion_final')
            digitalizacion_dis_final = serializador.validated_data.get('digitalizacion_dis_final')
            tiempo_retencion_ag = serializador.validated_data.get('tiempo_retencion_ag')
            tiempo_retencion_ac = serializador.validated_data.get('tiempo_retencion_ac')
            descripcion_procedimiento = serializador.validated_data.get('descripcion_procedimiento')
            id_cat_serie_und = serializador.validated_data.get('id_cat_serie_und')
            id_trd_validated = serializador.validated_data.get('id_trd') #YA EL ID SE ESTA ENVIANDO EN LA URL
            
            #VALIDACION DE NO ASIGNAR UNA SERIE SUBSERIE UNIDAD TRD A OTRA TRD

            if int(id_trd) != id_trd_validated.id_trd:
                raise ValidationError('El id de la TRD enviado debe ser el mismo id que se ingreso en la URL.')    

            #VALIDACION ENVIO COMPLETO DE LA INFORMACION

            if cod_disposicion_final and digitalizacion_dis_final!=None and tiempo_retencion_ag and tiempo_retencion_ac and descripcion_procedimiento != None:
                tipologias_instance = TipologiasDoc.objects.filter(id_tipologia_documental__in = tipologias)
                if len(tipologias) != tipologias_instance.count():
                    raise ValidationError('Todas las tipologias selecionadas deben existir')
                
                #VALIDAR QUE SE ELIJA UNA SERIE SUBSERIE UNIDAD VALIDA, SEGÚN LA TRD ELEGIDA
            
                serie_subserie_unidad = []
                serie_subserie_unidad.append(id_cat_serie_und.id_cat_serie_und)
                series_trd = list(SeriesDoc.objects.filter(id_ccd = trd.id_ccd))
                series_id = [serie.id_serie_doc for serie in series_trd]
                series_subseries_unidades_org_ccd = CatalogosSeriesUnidad.objects.filter(id_catalogo_serie__id_serie_doc__in = series_id)
                series_subseries_unidades_org_ccd_id = [serie.id_cat_serie_und for serie in series_subseries_unidades_org_ccd]
                if not set(serie_subserie_unidad).issubset(set(series_subseries_unidades_org_ccd_id)):
                    raise ValidationError('Debe elegir una serie subserie unidad asociada al CCD que tiene la TRD enviada en la URL.')
                serializado = serializador.save()
                
                
                #CREACIÓN DE LA SERIE SUBSERIE UNIDAD TRD TIPOLOGIA
  
                for tipologia in tipologias_instance:
                    SeriesSubSUnidadOrgTRDTipologias.objects.create(
                        id_catserie_unidadorg_ccd_trd = serializado,
                        id_tipologia_doc = tipologia)
                    
                    #PARA PONER EN TRUE T208itemYaUsado cuando es asignado en la tripleta
                    if not tipologia.item_ya_usado:
                        tipologia.item_ya_usado = True
                        tipologia.save()
                        
                        
                descripcion = {'Nombre':str(trd.nombre), 'Versión':str(trd.version)}    
                valores_creados_detalles = [
                    {
                        'NombreUnidad':serializado.id_cat_serie_und.id_unidad_organizacional.nombre, 
                        'NombreSerie':serializado.id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre
                    }
                ]
                
                if serializado.id_cat_serie_und.id_catalogo_serie.id_subserie_doc:
                    valores_creados_detalles[0]['NombreSubserie'] = serializado.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre
                
                direccion=Util.get_client_ip(request)
                auditoria_data = {
                    "id_usuario" : request.user.id_usuario,
                    "id_modulo" : 29,
                    "cod_permiso": "AC",
                    "subsistema": 'GEST',
                    "dirip": direccion,
                    "descripcion": descripcion,
                    "valores_creados_detalles": valores_creados_detalles,
                }
                Util.save_auditoria_maestro_detalle(auditoria_data)            
                    

                return Response({'succes':True, 'detail':'Creación exitosa','data': serializador.data}, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError('Debe enviar todas las especificaciones diligenciadas y asociar mínimo una tipología.')
        else:
            raise NotFound('No existe Tabla de Retención Documental (TRD) con el parámetro ingresado')



@api_view(['POST'])
def uploadDocument(request, id_serie_subserie_uniorg_trd):
    ssuorg_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_serie_subs_unidadorg_trd=id_serie_subserie_uniorg_trd).first()
    if ssuorg_trd:
        if ssuorg_trd.id_trd.actual:
            ssuorg_trd.ruta_archivo_cambio = request.FILES.get('document')
            ssuorg_trd.save()
            return Response({'success':True, 'detail':'Documento cargado correctamente'}, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied('El documento solo debe ser subido cuando se realizan cambios a una trd actual')
    else:
        raise NotFound('No se encontró ninguna ssuorg-trd con el parámetro ingresado')


class UpdateSerieSubSeriesUnidadesOrgTRD(generics.UpdateAPIView):
    serializer_class = SeriesSubSeriesUnidadesOrgTRDPutSerializer
    queryset = CatSeriesUnidadOrgCCDTRD.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_serie_subs_unidadorg_trd):
        data_entrante = request.data
        persona_usuario_logeado = request.user.persona
        serie_subs_unidadorg_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_catserie_unidadorg=id_serie_subs_unidadorg_trd).first()
        previous = copy.copy(serie_subs_unidadorg_trd)
        
        
        tipologias = request.data.get('tipologias')
        tipologias = json.loads(tipologias)
        tipologias_list = [tipologia['id_tipologia_documental'] for tipologia in tipologias]
        
        previous_serie_subs_unidad_org_trd = copy.copy(serie_subs_unidadorg_trd)


        if serie_subs_unidadorg_trd:
            #SI LA TRD NO ES ACTUAL Y NO TIENE FECHA RETIRO PRODUCCIÓN ACTUALIZA SERIE SUBSERIE SIN HISTORICO
            if serie_subs_unidadorg_trd.id_trd.actual == False and serie_subs_unidadorg_trd.id_trd.fecha_retiro_produccion == None and serie_subs_unidadorg_trd.id_trd.fecha_terminado == None:
                if data_entrante.get("justificacion_cambio") and data_entrante.get("justificacion_cambio") != "":
                    #raise ValidationError('NO se puede guardar la justificacion del cambio si la TRD no es la actual.'
                    data_entrante["justificacion_cambio"] = None
                    
                if data_entrante.get("ruta_archivo_cambio") and data_entrante.get("ruta_archivo_cambio") != "":
                    data_entrante["ruta_archivo_cambio"] = None
                
                serializador = self.serializer_class(serie_subs_unidadorg_trd, data=data_entrante, many=False)
                serializador.is_valid(raise_exception=True)

                cod_disposicion_final = serializador.validated_data.get('cod_disposicion_final')
                digitalizacion_dis_final = serializador.validated_data.get('digitalizacion_dis_final')
                tiempo_retencion_ag = serializador.validated_data.get('tiempo_retencion_ag')
                tiempo_retencion_ac = serializador.validated_data.get('tiempo_retencion_ac')
                descripcion_procedimiento = serializador.validated_data.get('descripcion_procedimiento')
                

                #SI ENVIAN TODAS LAS ESPECIFICACIONES DILIGENCIADAS
                if cod_disposicion_final and digitalizacion_dis_final!=None and tiempo_retencion_ag and tiempo_retencion_ac and descripcion_procedimiento and tipologias:
                    tipologias_instance = TipologiasDoc.objects.filter(id_tipologia_documental__in=tipologias_list)

                    #VALIDACION SI ENVIAN TIPOLOGIAS QUE NO SON DE LA MISMA TRD O QUE NO EXISTEN
                    if len(tipologias) != tipologias_instance.count():
                        #return Response({'success':False, 'detail':'Todas las tipologias seleccionadas deben existir y deben estar relacionadas a la TRD elegida'}, status=status.HTTP_400_BAD_REQUEST)
                        raise ValidationError('Todas las tipologias seleccionadas deben de existir y deben de estar relacionadas a la TRD elegida.')

                    #ELIMINA TODAS LAS TIPOLOGIAS QUE NO HAYA ENVIADO AL MOMENTO DE ACTUALIZAR
                    serie_subserie_unidad_tipologias = SeriesSubSUnidadOrgTRDTipologias.objects.filter(Q(id_catserie_unidadorg_ccd_trd=id_serie_subs_unidadorg_trd) & ~Q(id_tipologia_doc__in=tipologias_list))
                    serie_subserie_unidad_tipologias.delete()

                    serializado = serializador.save()
                    
                    #VERIFICA QUE NO EXISTA EN SSUTRD-TIPOLOGIAS Y CREA LA CONEXIÓN
                    for tipologia in tipologias:
                        serie_tipologia_instance = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_catserie_unidadorg_ccd_trd=id_serie_subs_unidadorg_trd, id_tipologia_doc=tipologia['id_tipologia_documental']).first()
                        tipologia_instance_create = TipologiasDoc.objects.filter(id_tipologia_documental=tipologia['id_tipologia_documental']).first()
                        if not serie_tipologia_instance:
                            SeriesSubSUnidadOrgTRDTipologias.objects.create(
                                id_catserie_unidadorg_ccd_trd = serie_subs_unidadorg_trd,
                                id_tipologia_doc = tipologia_instance_create)
                        # else:
                        #     if serie_tipologia_instance.activo != tipologia['activo']:
                        #         if tipologia['activo'] == True and not tipologia_instance_create.activo:
                        #             raise PermissionDenied('No se puede activar la relacion asociada a la tipologia '+tipologia_instance_create.nombre+', ya que esta se encuentra inactiva.')
                                
                        #         serie_tipologia_instance.activo = tipologia['activo']
                        #         serie_tipologia_instance.save()
                        #PARA CUANDO SE UTILICE UNA TIPOLOGIA Y ESTA ESTE EN FALSE EN EL CAMPO T208itemYaUsado este en False, se pase a True      
                        if not tipologia_instance_create.item_ya_usado:
                            tipologia_instance_create.item_ya_usado = True
                            tipologia_instance_create.save()
                    
                    
                    descripcion = {'Nombre':str(serie_subs_unidadorg_trd.id_trd.nombre), 'Versión':str(serie_subs_unidadorg_trd.id_trd.version)}    
                    valores_actualizados_detalles = [
                        {
                            'previous':previous,'current':serie_subs_unidadorg_trd,
                            'descripcion': {
                                'NombreUnidad':serie_subs_unidadorg_trd.id_cat_serie_und.id_unidad_organizacional.nombre, 
                                'NombreSerie':serie_subs_unidadorg_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre
                            }
                        }
                    ]
                    if serie_subs_unidadorg_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc:
                        valores_actualizados_detalles[0]['NombreSubserie'] = serie_subs_unidadorg_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre
                        
                    direccion=Util.get_client_ip(request)
                    auditoria_data = {
                        "id_usuario" : request.user.id_usuario,
                        "id_modulo" : 29,
                        "cod_permiso": "AC",
                        "subsistema": 'GEST',
                        "dirip": direccion,
                        "descripcion": descripcion,
                        "valores_actualizados_detalles": valores_actualizados_detalles,
                    }
                    Util.save_auditoria_maestro_detalle(auditoria_data)  
                    
                    
                                
                    return Response({'success':True, 'detail':'Actualización realizada correctamente', 'data': serializador.data}, status=status.HTTP_201_CREATED)

                else:
                    #return Response({'success':False, 'detail':'Debe enviar todas las especificaciones y tipologias diligenciadas o todas las especificaciones y tipologias vacias'}, status=status.HTTP_400_BAD_REQUEST)
                    raise ValidationError('Se deben enviar todas las especificaciones y tipologias diligenciadas')
                

            # SI LA TRD A MODIFICAR ES LA ACTUAL, GENERA HISTORICOS Y ASIGNA NUEVAS TIPOLOGIAS
            elif serie_subs_unidadorg_trd.id_trd.actual == True:
                serializador = self.serializer_class(serie_subs_unidadorg_trd, data=data_entrante, many=False)
                serializador.is_valid(raise_exception=True)

                cod_disposicion_final = serializador.validated_data.get('cod_disposicion_final')
                digitalizacion_dis_final = serializador.validated_data.get('digitalizacion_dis_final')
                tiempo_retencion_ag = serializador.validated_data.get('tiempo_retencion_ag')
                tiempo_retencion_ac = serializador.validated_data.get('tiempo_retencion_ac')
                descripcion_procedimiento = serializador.validated_data.get('descripcion_procedimiento')
                justificacion_cambio = serializador.validated_data.get('justificacion_cambio')
                

               #SI ENVIAN TODA LA INFORMACIÓN DILIGENCIADA
                if cod_disposicion_final and digitalizacion_dis_final == True or digitalizacion_dis_final == False and tiempo_retencion_ag and tiempo_retencion_ac and descripcion_procedimiento and justificacion_cambio:
                    tipologias_instance = TipologiasDoc.objects.filter(id_tipologia_documental__in=tipologias_list)
                 
                    
                    #VALIDA QUE LAS TIPOLOGIAS SELECCIONADAS EXISTAN
                    if len(tipologias) != tipologias_instance.count():
                        #return Response({'success':False, 'detail':'Todas las tipologias seleccionadas deben existir y deben estar relacionadas a la TRD elegida'}, status=status.HTTP_400_BAD_REQUEST)
                        raise ValidationError('Todas las tipologias seleccionadas deben de existir y deben de estar relacionadas a la TRD elegida.')
                    
                    
                    
                    #VALIDA QUE LA TIPOLOGIA SELECCIONADA ESTÉ ACTIVA
                    for tipologia in tipologias_instance:
                        if tipologia.activo == False:
                            #return Response({'success':False, 'detail':'Todas las tipologias seleccionadas deben estar activas para poder asignarlas'}, status=status.HTTP_400_BAD_REQUEST)
                            raise ValidationError('Todas las tipologias seleccionadas deben estar activas para poder asignarlas.')
           

                    campos_actualizados = Util.comparacion_campos_actualizados(data_entrante,serie_subs_unidadorg_trd)
                    print(campos_actualizados)
                    if campos_actualizados: 
                        if not data_entrante.get("justificacion_cambio") or (data_entrante.get("justificacion_cambio") and data_entrante.get("justificacion_cambio") == ''):
                            raise ValidationError('No se puede Actualizar sin una justificacion del cambio.')
                
                        if not data_entrante.get("ruta_archivo_cambio"):
                            raise ValidationError('No se puede Actualizar si no carga el archivo justificando el cambio.')
                       
                        #CREA EL HISTORICO
                        HistoricosCatSeriesUnidadOrgCCDTRD.objects.create(
                            id_catserie_unidadorg_ccd_trd = previous_serie_subs_unidad_org_trd,                        
                            cod_disposicion_final = previous_serie_subs_unidad_org_trd.cod_disposicion_final,                        
                            digitalizacion_disp_final = previous_serie_subs_unidad_org_trd.digitalizacion_dis_final,                        
                            tiempo_retencion_ag = previous_serie_subs_unidad_org_trd.tiempo_retencion_ag,
                            tiempo_retencion_ac = previous_serie_subs_unidad_org_trd.tiempo_retencion_ac,                        
                            descripcion_procedimiento = previous_serie_subs_unidad_org_trd.descripcion_procedimiento,                        
                            justificacion = previous_serie_subs_unidad_org_trd.justificacion_cambio,
                            ruta_archivo = previous_serie_subs_unidad_org_trd.ruta_archivo_cambio,
                            id_persona_cambia = persona_usuario_logeado
                        )
                        
                    #GUARDA LA INFORMACIÓN ENVIADA  
                    serializado = serializador.save()

                    #CREA LA CONEXIÓN EN LA TABLA SSUTRD-TIPOLOGIA SI NO EXISTE
                    for tipologia in tipologias:
                        serie_tipologia_instance = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_catserie_unidadorg_ccd_trd=id_serie_subs_unidadorg_trd, id_tipologia_doc=tipologia['id_tipologia_documental']).first()
                        tipologia_instance_create = TipologiasDoc.objects.filter(id_tipologia_documental=tipologia['id_tipologia_documental']).first()
                        if not serie_tipologia_instance:
                            SeriesSubSUnidadOrgTRDTipologias.objects.create(
                                id_catserie_unidadorg_ccd_trd = serie_subs_unidadorg_trd,
                                id_tipologia_doc = tipologia_instance_create)
                        else:
                            if serie_tipologia_instance.activo != tipologia['activo']:
                                
                                if tipologia['activo'] == True and not tipologia_instance_create.activo:
                                    raise PermissionDenied('No se puede activar la relacion asociada a la tipologia '+tipologia_instance_create.nombre+', ya que esta se encuentra inactiva.')
                                
                                serie_tipologia_instance.activo = tipologia['activo']
                                serie_tipologia_instance.save()                                
                                
                        #PARA CUANDO SE UTILICE UNA TIPOLOGIA Y ESTA ESTE EN FALSE EN EL CAMPO T208itemYaUsado este en False, se pase a True      
                        if not tipologia_instance_create.item_ya_usado:
                            tipologia_instance_create.item_ya_usado = True
                            tipologia_instance_create.save()
                        
                    descripcion = {'Nombre':str(serie_subs_unidadorg_trd.id_trd.nombre), 'Versión':str(serie_subs_unidadorg_trd.id_trd.version)}    
                    valores_actualizados_detalles = [
                        {
                            'previous':previous,'current':serie_subs_unidadorg_trd
                        }
                    ]
                    direccion=Util.get_client_ip(request)
                    auditoria_data = {
                        "id_usuario" : request.user.id_usuario,
                        "id_modulo" : 29,
                        "cod_permiso": "AC",
                        "subsistema": 'GEST',
                        "dirip": direccion,
                        "descripcion": descripcion,
                        "valores_actualizados_detalles": valores_actualizados_detalles,
                    }
                    Util.save_auditoria_maestro_detalle(auditoria_data)  
                            
                    
                    
                    # for tipologia in tipologias_instance:                          
                    #     tipologia_existente = SeriesSubSUnidadOrgTRDTipologias.objects.filter(Q(id_catserie_unidadorg_ccd_trd=serie_subs_unidadorg_trd.id_catserie_unidadorg) & Q(id_tipologia_doc=tipologia.id_tipologia_documental)).first()
                    #     if not tipologia_existente:
                    #         SeriesSubSUnidadOrgTRDTipologias.objects.create(
                    #             id_catserie_unidadorg_ccd_trd = serie_subs_unidadorg_trd,
                    #             id_tipologia_doc = tipologia)

                    return Response({'success':True, 'detail':'Actualización exitosa de la TRD Actual', 'data': serializador.data}, status=status.HTTP_201_CREATED)
                else:
                    #return Response({'success':False, 'detail':'Para modificar una trd actual se debe completar toda la información'}, status=status.HTTP_400_BAD_REQUEST)
                    raise ValidationError('Para modificar una TRD actual se debe de completar toda la información')
            else:
                raise PermissionDenied('No puede realizar esta acción si la TRD se encuentra terminada o retirada de producción.')
                # return Response({'success':False, 'detail':'Test'})
        else:
            #return Response({'success':False, 'detail':'No existe ninguna Serie Subserie Unidad TRD con el parámetro ingresado')
            raise ValidationError('No existe ninguna Serie Subserie Unidad TRD con los parametros ingresados')

class ReanudarTRD(generics.RetrieveUpdateAPIView):
    serializer_class = ReanudarTrdSerializer
    queryset = TablaRetencionDocumental.objects.all()
    
    def put(self,request,id_trd):
        
        trd = TablaRetencionDocumental.objects.filter(id_trd = id_trd).first()
        
        if not trd:
            raise NotFound('No existe la TRD Ingresada.')
        
        if trd.fecha_terminado == None:
            raise PermissionDenied('La TRD debe de estar Finalizada para su Reanudación.')
        
        if trd.fecha_retiro_produccion != None:
            raise PermissionDenied('La TRD no puede tener Fecha Retiro de Producción.')
        
        if trd.actual == True:
            raise ValidationError('La TRD no puede ser la Actual')
        
        tca_activo = TablasControlAcceso.objects.filter(id_trd = id_trd).first()
        
        if tca_activo:
            raise NotFound('El TRD ya esta siendo utilizado en un TCA.')
        
        trd.fecha_terminado = None
        
        trd.save()
        
        return Response({'succes':True, 'detail':'Se ha Reanudado con exito la TRD Seleccionada.'}, status=status.HTTP_200_OK)


# class EliminarCatSerieUndOrgCCDTRD218(generics.DestroyAPIView):
    
#     serializer_class = EliminarCatSerieUndOrgCCDTRD218Serializer
#     queryset = CatSeriesUnidadOrgCCDTRD.objects.all()
    
#     def delete(self, request,pk):
        
#         eliminar_relacion = CatSeriesUnidadOrgCCDTRD.objects.filter(id_catserie_unidadorg=pk).first()
        
#         if eliminar_relacion:
#             if not eliminar_relacion.id_trd.fecha_terminado:
#                 eliminar_relacion.delete()
#                 return Response({'succes':True, 'detail':'Se Elimino la Relacion seleccionada Correctamente.'})
#             else:
#                 raise PermissionDenied('No se puede Eliminar la Relación Seleccionada.')
#         else:
#             raise ValidationError('No Existe la Relación que desea Eliminar.')

class EliminarSerieUnidadTRD(generics.RetrieveDestroyAPIView):
    serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
    queryset = CatSeriesUnidadOrgCCDTRD.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,id_serie):
        eliminar_catalogo_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_catserie_unidadorg=id_serie).first()
        
        if eliminar_catalogo_trd:
            if eliminar_catalogo_trd.id_trd.actual == True:
                raise PermissionDenied('No se puede realizar la acción solicitada si la TRD se encuentra siendo la actual.')
            if eliminar_catalogo_trd.id_trd.fecha_terminado != None:
                raise ValidationError('No se puede realizar la acción solicitada si la TRD se encuentra Finalizada.')
            eliminar_catalogo_trd.delete()
            
            descripcion = {'Nombre':str(eliminar_catalogo_trd.id_trd.nombre), 'Versión':str(eliminar_catalogo_trd.id_trd.version)}    
            valores_eliminados_detalles = [
                {
                    'NombreUnidad':eliminar_catalogo_trd.id_cat_serie_und.id_unidad_organizacional.nombre, 
                    'NombreSerie':eliminar_catalogo_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.nombre
                }
            ]
            if eliminar_catalogo_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc:
                valores_eliminados_detalles[0]['NombreSubserie'] = eliminar_catalogo_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.nombre
                    
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 29,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_eliminados_detalles": valores_eliminados_detalles,
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)  
    
 
            return Response({'succes':True, 'detail':'Se ha Eliminado Exitosamente el registro del catalogo de TRD.'}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('No se encontró ninguna serie con el parametro Ingresado.')

# class DeleteSerieSubserieUnidadTRD(generics.RetrieveDestroyAPIView):
#     serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
#     queryset = CatSeriesUnidadOrgCCDTRD.objects.all()
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, id_ssuorg_trd):
#         serie_ss_uniorg_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_catserie_unidadorg=id_ssuorg_trd).first()
#         if serie_ss_uniorg_trd:
#             if serie_ss_uniorg_trd.id_trd.actual == True:
#                 #return Response({'success':False, 'detail':'No se pueden realizar ninguna acción sobre las Series')
#                 raise PermissionDenied('No se puede realizar ninguna acción sobre la serie Ingresada siendo la Actual.')
#             # serie_ss_uniorg_trd_tipologias = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_tipologia_catserie_unidad_ccd_trd=serie_ss_uniorg_trd)
#             # serie_ss_uniorg_trd_tipologias.delete()
#             serie_ss_uniorg_trd.delete()
#             return Response({'success':True, 'detail':'Eliminado exitosamente'}, status=status.HTTP_200_OK)
#         else:
#             #return Response({'success':False, 'detail':'No se encontró ninguna Serie Subserie Unidad TRD con el parámetro ingresado'}, status.HTTP_404_NOT_FOUND)
#             raise ValidationError('No se encontró ninguna Serie con el parámetro Ingresado')



#Tabla de Retencion Documental

class GetTablaRetencionDocumental(generics.ListAPIView):
    serializer_class = TRDSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

class GetTablaRetencionDocumentalTerminados(generics.ListAPIView):
    serializer_class = TRDSerializer
    queryset = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))
    permission_classes = [IsAuthenticated]

    def get(self,request):
        trd_terminados = self.queryset.all()
        serializer = self.serializer_class(trd_terminados, many=True)
        return Response({'success':True, 'detail':'Se encontraron los siguientes TRD terminados', 'data':serializer.data}, status=status.HTTP_200_OK)

class PostTablaRetencionDocumental(generics.CreateAPIView):
    serializer_class = TRDPostSerializer
    queryset = TablaRetencionDocumental
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
            
        serializer.is_valid(raise_exception=True)

        #Validación de seleccionar solo ccd terminados
        ccd = serializer.validated_data.get('id_ccd')
        ccd_instance = CuadrosClasificacionDocumental.objects.filter(id_ccd=ccd.id_ccd).first()
        if ccd_instance:
            if ccd_instance.fecha_terminado == None:
                raise PermissionDenied('No se pueden seleccionar Cuadros de Clasificación Documental que no estén terminados')

            serializado = serializer.save()

            #Auditoria Crear Tabla de Retención Documental
            usuario = request.user.id_usuario
            descripcion = {"Nombre": str(serializado.nombre), "Versión": str(serializado.version)}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 29,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
            }
            Util.save_auditoria(auditoria_data)

            return Response({'success':True, 'detail':'TRD creada exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError('No existe un Cuadro de Clasificación Documental con el id_ccd enviado')

class UpdateTablaRetencionDocumental(generics.RetrieveUpdateAPIView):
    serializer_class = TRDPutSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            trd = TablaRetencionDocumental.objects.get(id_trd=pk)
            previoud_trd = copy.copy(trd)
            pass
        except:
            raise NotFound('No existe ninguna Tabla de Retención Documental con los parámetros ingresados')

        if trd.fecha_terminado:
            raise PermissionDenied('No se puede actualizar una TRD terminada')

        serializer = self.serializer_class(trd, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pass
        except:
            raise ValidationError('Validar data enviada, el nombre y la versión son requeridos y deben ser únicos')
        serializer.save()

        # AUDITORIA DE UPDATE DE TRD
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        descripcion = {'Nombre':str(previoud_trd.nombre), 'Versión':str(previoud_trd.version)}
        valores_actualizados={'previous':previoud_trd, 'current':trd}
        auditoria_data = {
            'id_usuario': user_logeado,
            'id_modulo': 29,
            'cod_permiso': 'AC',
            'subsistema': 'GEST',
            'dirip': dirip,
            'descripcion': descripcion,
            'valores_actualizados': valores_actualizados
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success':True, 'detail':'Tabla de Retención Documental actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
class GetFormatosTiposMedioByParams(generics.ListAPIView):
    serializer_class = FormatosTiposMedioSerializer
    queryset = FormatosTiposMedio.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cod_tipo_medio = request.query_params.get('cod-tipo-medio')
        nombre = request.query_params.get('nombre')

        if cod_tipo_medio == '':
            cod_tipo_medio = None
        if nombre == '':
            nombre = None

        if not cod_tipo_medio and not nombre:
            raise NotFound('Debe ingresar los parámetros de búsqueda')

        filter={}
        
        for key,value in request.query_params.items():
            if key in ['cod-tipo-medio','nombre']:
                if key == 'nombre':
                    filter[key+'__icontains'] = value
                elif key == 'cod-tipo-medio':
                    filter['cod_tipo_medio_doc'] = value
                else:
                    if value != '':
                        filter[key]=value
        
        formatos_tipos_medio = FormatosTiposMedio.objects.filter(**filter).filter(activo=True)
        serializador = self.serializer_class(formatos_tipos_medio, many=True)
        if formatos_tipos_medio:
            return Response({'success':True, 'detail':'Se encontró la siguiente información', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No se encontró ningún resultado')

class GetFormatosTiposMedioByCodTipoMedio(generics.ListAPIView):
    serializer_class = FormatosTiposMedioSerializer
    queryset = FormatosTiposMedio.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, cod_tipo_medio_doc):
        if cod_tipo_medio_doc == 'H':
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(activo=True)
        else:
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc=cod_tipo_medio_doc, activo=True)

        serializador = self.serializer_class(formatos_tipos_medio, many=True)
        if serializador:
            return Response({'success':True, 'detail':'Se encontró la siguiente información', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No se encontró ningún resultado')

class RegisterFormatosTiposMedio(generics.CreateAPIView):
    serializer_class =  FormatosTiposMedioPostSerializer
    queryset = FormatosTiposMedio.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        
        data = request.data
        
        if data['cod_tipo_medio_doc'] != "E" and data['cod_tipo_medio_doc'] !="F":
            raise ValidationError('El codigo tipo medio ingresado no es valido para crear.')
        if data['cod_tipo_medio_doc'] == "E":
            if data['control_tamagno_max']:
                print('control acceso')
                if not data['tamagno_max_mb']:
                    raise ValidationError('el tamaño maximo es requerido.') 
                else:
                    if data['tamagno_max_mb'] <= 0:
                        raise ValidationError('el tamaño maximo debe ser mayor a 0.')
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success':True, 'detail':'Se ha creado el Formato Tipo Medio exitosamente.','data':serializador.data}, status=status.HTTP_201_CREATED)

#ACTUALIZAR FORMATOS TIPO MEDIO
class UpdateFormatosTiposMedio(generics.RetrieveUpdateAPIView):
    serializer_class = FormatosTiposMedioPostSerializer
    queryset = FormatosTiposMedio.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data=request.data
        formato_tipo_medio = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=pk).first()
        previus = copy.copy(formato_tipo_medio)
        if formato_tipo_medio:
            if  formato_tipo_medio.registro_precargado:
                if 'nombre' in data and  previus.nombre != data['nombre']:
                    raise ValidationError('No se puede cambiar el nombre de un registro precargado.')
                if  'cod_tipo_medio_doc' in data and previus.cod_tipo_medio_doc != data['cod_tipo_medio_doc']:
                    raise ValidationError('No se puede cambiar el codigo de un registro precargado.')
            if data['cod_tipo_medio_doc'] == "E":
                    
                if not data['tamagno_max_mb']:
                    raise ValidationError('el tamaño maximo es requerido.') 
            else:
                if data['tamagno_max_mb'] <= 0:
                    raise ValidationError('el tamaño maximo debe ser mayor a 0.')
            serializer = self.serializer_class(formato_tipo_medio, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success':True, 'detail':'Registro actualizado exitosamente','data':serializer.data}, status=status.HTTP_201_CREATED)

        else:
            raise NotFound('No existe el formato tipo medio')

class DeleteFormatosTiposMedio(generics.DestroyAPIView):
    serializer_class = FormatosTiposMedioPostSerializer
    queryset = FormatosTiposMedio.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        formato_tipo_medio = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=pk).first()
        if formato_tipo_medio:
            pass
            if not formato_tipo_medio.registro_precargado:
                if formato_tipo_medio.item_ya_usado:
                    raise PermissionDenied('Este formato tipo medio ya está siendo usado, no se pudo eliminar')

                formato_tipo_medio.delete()
                return Response({'success':True, 'detail':'Este formato tipo medio ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('No puedes eliminar un formato tipo medio precargado')
        else:
            raise NotFound('No existe el formato tipo medio')

class CambiosPorConfirmar(generics.UpdateAPIView):
    serializer_class = SeriesSubSeriesUnidadesOrgTRDPutSerializer
    queryset = SeriesSubSUnidadOrgTRDTipologias.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_trd):
        confirm = request.query_params.get('confirm')
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        if trd:
            if trd.actual:
                if trd.cambios_por_confirmar:
                    series_sub_unidades_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_trd=id_trd)
                    series_sub_unidades_trd_list = [serie_sub_unidad_trd.id_serie_subs_unidadorg_trd for serie_sub_unidad_trd in series_sub_unidades_trd]
                    formatos_tipo_medio = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd__in=series_sub_unidades_trd_list)
                    tipologias_list = [formato_tipo_medio.id_tipologia_doc.id_tipologia_documental for formato_tipo_medio in formatos_tipo_medio]
                    tipologias_trd = TipologiasDoc.objects.filter(id_trd=id_trd)
                    tipologias_trd_list = [tipologia.id_tipologia_documental for tipologia in tipologias_trd]

                    if not set(tipologias_trd_list).issubset(tipologias_list):
                        tipologias_faltan = TipologiasDoc.objects.filter(id_trd=id_trd).exclude(id_tipologia_documental__in=tipologias_list)
                        if confirm == 'true':
                            tipologias_faltan.delete()
                            trd.cambios_por_confirmar = False
                            trd.save()
                            return Response({'success':True, 'detail':'Se han eliminado las tipologias no usadas y se confirmaron cambios'}, status=status.HTTP_200_OK)
                        else:
                            try:
                                raise PermissionDenied('Tiene tipologias pendientes por usar')
                            except PermissionDenied as e:
                                return Response({'success':False, 'detail':'Tiene tipologias pendientes por usar', 'data':tipologias_faltan.values()}, status=status.HTTP_403_FORBIDDEN)
                    else:
                        trd.cambios_por_confirmar = False
                        trd.save()
                        return Response({'success':True, 'detail':'Está usando todas las tipologias, se han confirmado cambios'}, status=status.HTTP_200_OK)
                else:
                    raise PermissionDenied('No tiene cambios por confirmar')
            else:
                raise PermissionDenied('No puede realizar esta acción porque no es el TRD actual')
        else:
            raise NotFound('El TRD no existe')

# class GetSeriesSubSUnidadOrgTRD(generics.ListAPIView):
#     serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
#     queryset = CatSeriesUnidadOrgCCDTRD.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, id_trd):
        
#         #VALIDACIÓN SI EXISTE LA TRD ENVIADA
#         series_subseries_unidad_org_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_trd=id_trd)
#         if not series_subseries_unidad_org_trd:
#             return Response({'success':False, 'detail':'No se encontró la TRD')
        
#         ids_serie_subs_unidad_org_trd = [i.id_serie_subs_unidadorg_trd for i in series_subseries_unidad_org_trd]
#         result = []
#         for i in ids_serie_subs_unidad_org_trd:
#             main_detail = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd = i).first()
#             serializer_ssutrdtipo = GetSeriesSubSUnidadOrgTRDTipologiasSerializer(main_detail, many=False)
#             detalle_serie_subs_unidad_org_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_serie_subs_unidadorg_trd = serializer_ssutrdtipo.data['id_serie_subserie_unidadorg_trd']).first()
#             serializer_ssutrd = GetSeriesSubSUnidadOrgTRDSerializer(detalle_serie_subs_unidad_org_trd, many=False)
#             detalle_tipologias = TipologiasDocumentales.objects.filter(id_tipologia_documental = serializer_ssutrdtipo.data['id_tipologia_doc']).first()
#             serializer_tipologias = GetTipologiasDocumentalesSerializer(detalle_tipologias, many=False)

#             data = serializer_ssutrdtipo.data
#             data['id_serie_subserie_unidadorg_trd'] = serializer_ssutrd.data
#             data['id_tipologia_doc'] = serializer_tipologias.data
#             result.append(data)
            
#         return Response({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data': result}, status=status.HTTP_200_OK)

class GetSeriesSubSUnidadOrgTRD(generics.ListAPIView):
    serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id_trd):
        queryset = CatSeriesUnidadOrgCCDTRD.objects.filter(id_trd=id_trd).order_by('id_catserie_unidadorg')
        
        #VALIDACIÓN SI EXISTE LA TRD ENVIADA
        if not queryset:
            raise NotFound('No se encontró ningún registro del cátalogo de TRD ingresada')  
        
        serializer = self.serializer_class(queryset, many=True, context={'request':request})
        return Response({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class GetTipologiasSeriesSubSUnidadOrgTRD(generics.ListAPIView):
    serializer_class = TipologiasSeriesSubSUnidadOrgTRDSerializer
    queryset = SeriesSubSUnidadOrgTRDTipologias.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_catserie_unidadorg):
        tipologias_catalogo_trd = self.queryset.filter(id_catserie_unidadorg_ccd_trd=id_catserie_unidadorg)
        tipologias_catalogo_serializer = self.serializer_class(tipologias_catalogo_trd, many=True)
            
        return Response({'success':True, 'detail':'Se encontraron las siguientes tipologias para el registro del catalogo TRD elegido', 'data':tipologias_catalogo_serializer.data}, status=status.HTTP_200_OK)
  
class DesactivarTipologiaActual(generics.UpdateAPIView):
    serializer_class = TipologiasDocumentalesPutSerializer
    queryset = TipologiasDoc.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_tipologia):
        persona = request.user.persona
        tipologia = TipologiasDoc.objects.filter(id_tipologia_documental=id_tipologia).first()
        justificacion = request.data.get('justificacion_desactivacion')
        if tipologia:
            trd = TablaRetencionDocumental.objects.filter(id_trd=tipologia.id_trd.id_trd).first()
            if trd.actual:
                if not tipologia.activo:
                    raise PermissionDenied('La tipologia ya se encuentra desactivada')
                if not justificacion:
                    raise ValidationError('Debe ingresar la justificación para desactivar la tipología')
                
                tipologia.activo = False
                tipologia.fecha_desactivacion = datetime.now()
                tipologia.justificacion_desactivacion = justificacion
                tipologia.id_persona_desactiva = persona
                tipologia.save()
                return Response({'success':True, 'detail':'Se ha desactivado la tipologia indicada'}, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('No puede realizar esta acción porque no es el TRD actual')
        else:
            raise NotFound('La tipologia ingresada no existe')

class FinalizarTRD(generics.RetrieveUpdateAPIView):
    serializer_class = TRDFinalizarSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        trd = self.queryset.filter(id_trd=pk).first()
        if not trd:
            raise NotFound('No se encontró la TRD elegida')
        
        if trd.fecha_terminado:
            raise ValidationError('No puede finalizar una TRD que ya se encuentra finalizada')
        if trd.fecha_retiro_produccion:
            raise ValidationError('No puede finalizar una TRD que haya sido retirada de producción')
        if trd.actual:
            raise ValidationError('No puede finalizar una TRD actual')
        
        existencia_catalogo_ccd = CatalogosSeriesUnidad.objects.filter(id_catalogo_serie__id_serie_doc__id_ccd=trd.id_ccd).values_list('id_cat_serie_und', flat=True)
        existencia_catalogo_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_trd=trd.id_trd).values_list('id_cat_serie_und', flat=True)
        
        if len(existencia_catalogo_ccd) != len(existencia_catalogo_trd):
            raise PermissionDenied('No puede finalizar la TRD elegida porque no todos los registros del catalogo de la CCD están relacionadas en el catalogo de la TRD')
        
        trd.fecha_terminado = datetime.now()
        trd.save()
        
        return Response({'success':True, 'detail':'Se ha finalizado correctamente la TRD'}, status=status.HTTP_200_OK)
    


############################################# CRUD DE CONFIGURACION DE TIPOLOGIA DOCUMENTAL #############################################################

class ListarTipologiasdocumentales(generics.ListAPIView):
    queryset = TipologiasDoc.objects.filter(activo=True).order_by('nombre')
    serializer_class = TipologiasDocumentalesSerializer
    permission_classes = [IsAuthenticated]

#////////////////////////////////////////////////////////////////////////////////////////////////////
class CrearConfigurarTipologiaEmpresa(generics.CreateAPIView):
    serializer_class = ConsecPorNivelesTipologiasDocAgnoSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        maneja_consecutivo = data.get('maneja_consecutivo', False)
        current_year = datetime.now().year
        fecha_ultima_config = datetime.now()
        # Procesa los datos para agregar un documento de archivo expediente
        user = request.user
        persona_logueada = user.persona

        if not persona_logueada.id_unidad_organizacional_actual:
            raise ValidationError("No tiene permiso para realizar esta acción")

        if datetime.now().month > 7:
            next_year = current_year + 1
        else:
            next_year = current_year

        tipologia_id = data.get('id_tipologia_doc')

        # Verificar si la tipología ya fue configurada
        if ConsecPorNivelesTipologiasDocAgno.objects.filter(
            id_config_tipologia_doc_agno__id_tipologia_doc=tipologia_id,
            id_config_tipologia_doc_agno__agno_tipologia=current_year
        ).exists():
            raise ValidationError('La tipología documental ya fue configurada')

        try:
            tipologia = TipologiasDoc.objects.get(id_tipologia_documental=tipologia_id)
        except TipologiasDoc.DoesNotExist:
            raise NotFound('La tipología ingresada no existe')

        with transaction.atomic():
            if maneja_consecutivo:
                if 'nivel_consecutivo' not in data:
                    return Response({
                        'success': False,
                        'detail': 'El campo nivel_consecutivo es obligatorio si se maneja el consecutivo.',
                    }, status=status.HTTP_400_BAD_REQUEST)

                nivel_consecutivo = data['nivel_consecutivo']

                if nivel_consecutivo == 'EM':
                    if 'valor_inicial' not in data or 'cantidad_digitos' not in data:
                        return Response({
                            'success': False,
                            'detail': 'Valor Inicial y Cantidad de Dígitos son campos obligatorios para Nivel Empresa.',
                        }, status=status.HTTP_400_BAD_REQUEST)

                    valor_inicial = data['valor_inicial']
                    cantidad_digitos = data['cantidad_digitos']

                    if not (isinstance(valor_inicial, int) and valor_inicial > 0) or not (1 <= cantidad_digitos <= 20):
                        return Response({
                            'success': False,
                            'detail': 'Valor Inicial debe ser un entero mayor a 0 y Cantidad de Dígitos debe estar entre 1 y 20.',
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # Crear o actualizar la configuración de consecutivo en ConfigTipologiasDocAgno
                    config_tipologia, created = ConfigTipologiasDocAgno.objects.get_or_create(
                        agno_tipologia=current_year,
                        id_tipologia_doc=tipologia,
                        maneja_consecutivo=maneja_consecutivo,
                        defaults={
                            'cod_nivel_consecutivo': nivel_consecutivo,
                            'item_ya_usado': False,
                        }
                    )

                    # Crear o actualizar la configuración de consecutivo en ConsecPorNivelesTipologiasDocAgno
                    consec_por_niveles, _ = ConsecPorNivelesTipologiasDocAgno.objects.get_or_create(
                        id_config_tipologia_doc_agno=config_tipologia,
                        defaults={
                            'consecutivo_inicial': valor_inicial,
                            'cantidad_digitos': cantidad_digitos,
                            'item_ya_usado': False,
                            'consecutivo_actual': valor_inicial - 1,
                            'id_persona_ult_config_implemen': persona_logueada,  # Asignar la instancia de Personas
                        }
                    )
                else:
                    return Response({
                        'success': False,
                        'detail': 'Opción de Nivel de Consecutivo no válida.',
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                config_tipologia, created = ConfigTipologiasDocAgno.objects.get_or_create(
                    agno_tipologia=current_year,
                    id_tipologia_doc=tipologia,
                    maneja_consecutivo=maneja_consecutivo,
                    defaults={'item_ya_usado': False}
                )

                consec_por_niveles, _ = ConsecPorNivelesTipologiasDocAgno.objects.get_or_create(
                    id_config_tipologia_doc_agno=config_tipologia,
                    defaults={
                        'consecutivo_inicial': None,
                        'cantidad_digitos': None,
                        'item_ya_usado': False,
                        'consecutivo_actual': None,
                        'id_persona_ult_config_implemen': persona_logueada,
                    }
                )

            # Formatear T247consecutivoInicial y T247consecutivoActual con ceros a la izquierda
            t247_consecutivo_inicial = str(consec_por_niveles.consecutivo_inicial).zfill(cantidad_digitos)
            t247_consecutivo_actual = str(consec_por_niveles.consecutivo_actual).zfill(cantidad_digitos)


            nombre_persona_config = ""
            if persona_logueada.primer_nombre:
                nombre_persona_config += persona_logueada.primer_nombre

            if persona_logueada.segundo_nombre:
                nombre_persona_config += " " + persona_logueada.segundo_nombre

            if persona_logueada.primer_apellido:
                nombre_persona_config += " " + persona_logueada.primer_apellido

            if persona_logueada.segundo_apellido:
                nombre_persona_config += " " + persona_logueada.segundo_apellido


            response_data = {
                "T246IdConfigTipologiaDocAgno": config_tipologia.id_config_tipologia_doc_agno,
                "T246agnoTipologia": current_year,
                "T246Id_TipologiaDoc": tipologia_id,
                "T246manejaConsecutivo": maneja_consecutivo,
                "T246codNivelDelConsecutivo": config_tipologia.cod_nivel_consecutivo,
                "T246itemYaUsado": config_tipologia.item_ya_usado,
                "T247IdConsecPorNiveles_TipologiasDocAgno": consec_por_niveles.id_consec_nivel_tipologias_doc_agno,
                "T247Id_ConfigTipologiaDocAgno": config_tipologia.id_config_tipologia_doc_agno,
                "T247Id_UnidadOrganizacional": None,
                "T247consecutivoInicial": valor_inicial,
                "T247cantidadDigitos": consec_por_niveles.cantidad_digitos,
                "T247itemYaUsado": consec_por_niveles.item_ya_usado,
                "T247Id_PersonaUltConfigImplemen": persona_logueada.id_persona,  # Asignar el ID de la persona logueada
                "Persona_ult_config_implemen": nombre_persona_config,
                "T247fechaUltConfigImplemen": fecha_ultima_config,
                "T247consecutivoActual":consec_por_niveles.consecutivo_actual,
                "T247consecutivoActualAMostrar": t247_consecutivo_actual,
                

            }

            return Response({
                'success': True,
                'detail': 'Se ha configurado la tipología documental con éxito',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
        
#///////////////////////////////////////////////////////////////////////////////////////////////

class ConfigurarTipologiaSS(generics.CreateAPIView):
    serializer_class = ConsecPorNivelesTipologiasDocAgnoSerializer  # Asegúrate de usar el serializador correcto
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        maneja_consecutivo = data.get('maneja_consecutivo', False)
        current_year = datetime.now().year
        fecha_ultima_config = datetime.now()

        user = request.user
        persona_logueada = user.persona

        if not persona_logueada.id_unidad_organizacional_actual:
            raise ValidationError("No tiene permiso para realizar esta acción")

        if datetime.now().month > 7:
            next_year = current_year + 1
        else:
            next_year = current_year

        tipologia_id = data.get('id_tipologia_doc')

        # Verificar si la tipología ya fue configurada
        if ConsecPorNivelesTipologiasDocAgno.objects.filter(
            id_config_tipologia_doc_agno__id_tipologia_doc=tipologia_id,
            id_config_tipologia_doc_agno__agno_tipologia=current_year
        ).exists():
            raise ValidationError('La tipología documental ya fue configurada')

        try:
            tipologia = TipologiasDoc.objects.get(id_tipologia_documental=tipologia_id)
        except TipologiasDoc.DoesNotExist:
            raise NotFound('La tipología ingresada no existe')

        with transaction.atomic():
            if maneja_consecutivo:
                if 'nivel_consecutivo' not in data:
                    return Response({
                        'success': False,
                        'detail': 'El campo nivel_consecutivo es obligatorio si se maneja el consecutivo.',
                    }, status=status.HTTP_400_BAD_REQUEST)

                nivel_consecutivo = data['nivel_consecutivo']

                if nivel_consecutivo == 'SS':
                    # Validar datos requeridos para Nivel SS
                    if 'valor_inicial' not in data or 'cantidad_digitos' not in data or 'prefijo_consecutivo' not in data:
                        return Response({
                            'success': False,
                            'detail': 'Valor Inicial, Cantidad de Dígitos y Prefijo Consecutivo son campos obligatorios para Nivel SS.',
                        }, status=status.HTTP_400_BAD_REQUEST)

                    valor_inicial = data['valor_inicial']
                    cantidad_digitos = data['cantidad_digitos']
                    prefijo_consecutivo = data['prefijo_consecutivo']

                    # Validar prefijo único para la misma tipología y sección en la TRD actual
                    if ConsecPorNivelesTipologiasDocAgno.objects.filter(
                        id_config_tipologia_doc_agno__id_tipologia_doc=tipologia_id,
                        consecutivo_inicial__isnull=False,
                        prefijo_consecutivo=prefijo_consecutivo
                    ).exists():
                        raise ValidationError('El prefijo ya está siendo utilizado en otra sección/subsección para la misma tipología.')

                    # Crear o actualizar la configuración de consecutivo en ConfigTipologiasDocAgno
                    config_tipologia, created = ConfigTipologiasDocAgno.objects.get_or_create(
                        agno_tipologia=current_year,
                        id_tipologia_doc=tipologia,
                        maneja_consecutivo=maneja_consecutivo,
                        defaults={
                            'cod_nivel_consecutivo': nivel_consecutivo,
                            'item_ya_usado': False,
                        }
                    )

                    # Crear o actualizar la configuración de consecutivo en ConsecPorNivelesTipologiasDocAgno
                    consec_por_niveles, _ = ConsecPorNivelesTipologiasDocAgno.objects.get_or_create(
                        id_config_tipologia_doc_agno=config_tipologia,
                        defaults={
                            'consecutivo_inicial': valor_inicial,
                            'cantidad_digitos': cantidad_digitos,
                            'item_ya_usado': False,
                            'consecutivo_actual': valor_inicial - 1,
                            'prefijo_consecutivo': prefijo_consecutivo,
                            'id_persona_ult_config_implemen': persona_logueada,
                        }
                    )
                else:
                    return Response({
                        'success': False,
                        'detail': 'Opción de Nivel de Consecutivo no válida.',
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                config_tipologia, created = ConfigTipologiasDocAgno.objects.get_or_create(
                    agno_tipologia=current_year,
                    id_tipologia_doc=tipologia,
                    maneja_consecutivo=maneja_consecutivo,
                    defaults={'item_ya_usado': False}
                )

                consec_por_niveles, _ = ConsecPorNivelesTipologiasDocAgno.objects.get_or_create(
                    id_config_tipologia_doc_agno=config_tipologia,
                    defaults={
                        'consecutivo_inicial': None,
                        'cantidad_digitos': None,
                        'item_ya_usado': False,
                        'consecutivo_actual': None,
                        'prefijo_consecutivo': None,
                        'id_persona_ult_config_implemen': persona_logueada,
                    }
                )

            # Formatear T247consecutivoInicial y T247consecutivoActual con ceros a la izquierda
            t247_consecutivo_inicial = str(consec_por_niveles.consecutivo_inicial).zfill(cantidad_digitos)
            t247_consecutivo_actual = str(consec_por_niveles.consecutivo_actual).zfill(cantidad_digitos)

            nombre_persona_config = ""
            if persona_logueada.primer_nombre:
                nombre_persona_config += persona_logueada.primer_nombre

            if persona_logueada.segundo_nombre:
                nombre_persona_config += " " + persona_logueada.segundo_nombre

            if persona_logueada.primer_apellido:
                nombre_persona_config += " " + persona_logueada.primer_apellido

            if persona_logueada.segundo_apellido:
                nombre_persona_config += " " + persona_logueada.segundo_apellido

            response_data = {
                "T246IdConfigTipologiaDocAgno": config_tipologia.id_config_tipologia_doc_agno,
                "T246agnoTipologia": current_year,
                "T246Id_TipologiaDoc": tipologia_id,
                "T246manejaConsecutivo": maneja_consecutivo,
                "T246codNivelDelConsecutivo": config_tipologia.cod_nivel_consecutivo,
                "T246itemYaUsado": config_tipologia.item_ya_usado,
                "T247IdConsecPorNiveles_TipologiasDocAgno": consec_por_niveles.id_consec_nivel_tipologias_doc_agno,
                "T247Id_ConfigTipologiaDocAgno": config_tipologia.id_config_tipologia_doc_agno,
                "T247Id_UnidadOrganizacional": None,  # PEDIENTE
                "T247consecutivoInicial": valor_inicial,
                "T247cantidadDigitos": consec_por_niveles.cantidad_digitos,
                "T247itemYaUsado": consec_por_niveles.item_ya_usado,
                "T247Id_PersonaUltConfigImplemen": persona_logueada.id_persona,
                "Persona_ult_config_implemen": nombre_persona_config,
                "T247fechaUltConfigImplemen": fecha_ultima_config,
                "T247consecutivoActual":consec_por_niveles.consecutivo_actual,
                "T247consecutivoActualAMostrar": t247_consecutivo_actual,
                "T247prefijoConsecutivo": prefijo_consecutivo,
                "prefijoConsecutivoAMosotrar": f"{prefijo_consecutivo}-{t247_consecutivo_actual}",  
            }

            return Response({
                'success': True,
                'detail': 'Se ha configurado la tipología documental con éxito',
                'data': response_data
            }, status=status.HTTP_201_CREATED)

#///////////////////////////////////////////////////////////////////////////////////////////////       


class CrearConfigurarTipologia(generics.CreateAPIView):
    serializer_class = ConfigTipologiasDocAgnoSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Obtener los datos enviados por el usuario
        data = request.data
        
        # Verificar si el usuario seleccionó "Maneja Consecutivo"
        maneja_consecutivo = data.get('maneja_consecutivo', False)

         # Si "maneja_consecutivo" es True, retornar una respuesta de error
        if maneja_consecutivo:
            raise ValidationError('El campo "maneja_consecutivo" no puede ser True')

        # Obtener el año actual
        current_year = datetime.now().year

        # Lógica para determinar si el año siguiente debe ser utilizado
        if datetime.now().month > 7:
            next_year = current_year + 1
        else:
            next_year = current_year

        # Obtener el ID de la tipología proporcionado
        tipologia_id = data.get('tipologia')

        # Verificar si la tipología ya fue configurada
        if ConfigTipologiasDocAgno.objects.filter(agno_tipologia=current_year, id_tipologia_doc=tipologia_id).exists():
            raise ValidationError('La tipología documental ya fue configurada')

        # Verificar si el registro ya existe, y si es así, actualizarlo
        config_tipologia, created = ConfigTipologiasDocAgno.objects.get_or_create(
            agno_tipologia=current_year,
            id_tipologia_doc_id=tipologia_id,  # Usar el campo de relación directamente
            defaults={'maneja_consecutivo': maneja_consecutivo}
        )

        # Si el registro ya existía, actualizar los campos
        if not created:
            config_tipologia.maneja_consecutivo = maneja_consecutivo
            config_tipologia.save()

        # Generar la respuesta
        response_data = {
            "T246IdConfigTipologiaDocAgno": config_tipologia.id_config_tipologia_doc_agno,
            "T246agnoTipologia": current_year,
            "T246Id_TipologiaDoc": tipologia_id,
            "T246manejaConsecutivo": maneja_consecutivo,
            "T246codNivelDelConsecutivo": None,
            "T246itemYaUsado": False
        }

        return Response({
            'success': True,
            'detail': 'Se ha configurado la tipología documental con éxito',
            'data': response_data
        }, status=status.HTTP_201_CREATED)




class ListaConfiguraciones(generics.ListAPIView):
    serializer_class = ConfigTipologiasDocAgnoSerializer

    def get_queryset(self):
        return ConfigTipologiasDocAgno.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ConfigTipologiasDocAgnoSerializer(queryset, many=True)
        user = request.user
        persona_logueada = user.persona
        # Puedes ajustar este bloque según tu modelo y lógica
        data = []
        for config_tipologia in queryset:
            try:
                consec_por_niveles = ConsecPorNivelesTipologiasDocAgno.objects.get(
                    id_config_tipologia_doc_agno=config_tipologia
                )
            except ConsecPorNivelesTipologiasDocAgno.DoesNotExist:
                consec_por_niveles = None

            nombre_persona_config = ""
            if consec_por_niveles and consec_por_niveles.id_persona_ult_config_implemen:
                nombre_persona_config = (
                    f"{consec_por_niveles.id_persona_ult_config_implemen.primer_apellido} "
                    f"{consec_por_niveles.id_persona_ult_config_implemen.segundo_apellido}"
                )

            t247_consecutivo_actual = (
                str(consec_por_niveles.consecutivo_actual).zfill(consec_por_niveles.cantidad_digitos)
                if consec_por_niveles and consec_por_niveles.consecutivo_actual is not None
                else None
            )

            item = {
                "T246IdConfigTipologiaDocAgno": config_tipologia.id_config_tipologia_doc_agno,
                "T246agnoTipologia": config_tipologia.agno_tipologia,
                "T246Id_TipologiaDoc": config_tipologia.id_tipologia_doc.id_tipologia_documental,
                "T246manejaConsecutivo": config_tipologia.maneja_consecutivo,
                "T246codNivelDelConsecutivo": config_tipologia.cod_nivel_consecutivo,
                "T246itemYaUsado": config_tipologia.item_ya_usado,
                "T247IdConsecPorNiveles_TipologiasDocAgno": (
                    consec_por_niveles.id_consec_nivel_tipologias_doc_agno
                    if consec_por_niveles
                    else None
                ),
                "T247Id_ConfigTipologiaDocAgno": config_tipologia.id_config_tipologia_doc_agno,
                "T247Id_UnidadOrganizacional": (
                    consec_por_niveles.id_unidad_organizacional.id_unidad_organizacional
                    if consec_por_niveles and consec_por_niveles.id_unidad_organizacional
                    else None
                ),
                "T247consecutivoInicial": (
                    consec_por_niveles.consecutivo_inicial if consec_por_niveles else None
                ),
                "T247cantidadDigitos": (
                    consec_por_niveles.cantidad_digitos if consec_por_niveles else None
                ),
                "T247itemYaUsado": (
                    consec_por_niveles.item_ya_usado if consec_por_niveles else None
                ),
                "T247Id_PersonaUltConfigImplemen": (
                    consec_por_niveles.id_persona_ult_config_implemen.id_persona
                    if consec_por_niveles and consec_por_niveles.id_persona_ult_config_implemen
                    else None
                ),
                "Persona_ult_config_implemen": nombre_persona_config,
                "T247fechaUltConfigImplemen": (
                    consec_por_niveles.fecha_ult_config_implemen if consec_por_niveles else None
                ),
                "T247consecutivoActualAMostrar": t247_consecutivo_actual,
                "T247Id_UnidadOrganizacional": (
                    consec_por_niveles.id_unidad_organizacional.id_unidad_organizacional
                    if consec_por_niveles and consec_por_niveles.id_unidad_organizacional
                    else None
                ),

                "T247prefijoConsecutivo": consec_por_niveles.prefijo_consecutivo,
                "prefijoConsecutivoAMosotrar": f"{consec_por_niveles.prefijo_consecutivo}-{t247_consecutivo_actual}", 
            }
            data.append(item)

        return Response({
            'success': True,
            'detail': 'Lista de configuraciones',
            'data': data
        })


class ListaConfiguracionesPorAgnoYTipologia(generics.ListAPIView):
    serializer_class = ConfigTipologiasDocAgnoSerializer

    def get_queryset(self):
        # Obtener parámetros de la solicitud
        agno_tipologia = self.request.query_params.get('agno_tipologia', None)
        id_tipologia_doc = self.request.query_params.get('id_tipologia_doc', None)

        # Validar que se proporcionen ambos parámetros
        if not agno_tipologia or not id_tipologia_doc:
            raise ValidationError("Se deben proporcionar 'agno_tipologia' y 'id_tipologia_doc' en los parámetros de la solicitud.")

        try:
            # Obtener la configuración según los parámetros proporcionados
            queryset = ConfigTipologiasDocAgno.objects.filter(
                agno_tipologia=agno_tipologia,
                id_tipologia_doc=id_tipologia_doc
            )
        except ConfigTipologiasDocAgno.DoesNotExist:
            queryset = []

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = ConfigTipologiasDocAgnoSerializer(queryset, many=True)

            data = []
            for config_tipologia in queryset:
                tipo_configuracion = config_tipologia.cod_nivel_consecutivo
                id_tipologia = config_tipologia.id_tipologia_doc.id_tipologia_documental if config_tipologia.id_tipologia_doc else None
                nombre_tipologia = config_tipologia.id_tipologia_doc.nombre if config_tipologia.id_tipologia_doc else None

                if tipo_configuracion is None:
                    # Caso 1
                    item = {
                        "id_config_tipologia_doc_agno":config_tipologia.id_config_tipologia_doc_agno,
                        "tipo_configuracion": tipo_configuracion,
                        "agno_tipologia": config_tipologia.agno_tipologia,
                        "id_tipologia": id_tipologia,
                        "nombre_tipologia": nombre_tipologia
                    }
                    
                elif tipo_configuracion == "EM":
                    # Caso 2
                    consec_por_niveles = ConsecPorNivelesTipologiasDocAgno.objects.filter(
                        id_config_tipologia_doc_agno=config_tipologia
                    ).first()

                    id_tipologia = config_tipologia.id_tipologia_doc.id_tipologia_documental if config_tipologia.id_tipologia_doc else None
                    nombre_tipologia = config_tipologia.id_tipologia_doc.nombre if config_tipologia.id_tipologia_doc else None

                    # Verifica y concatena solo campos no nulos
                    nombre_persona_config = " ".join(filter(None, [
                        consec_por_niveles.id_persona_ult_config_implemen.primer_nombre,
                        consec_por_niveles.id_persona_ult_config_implemen.segundo_nombre,
                        consec_por_niveles.id_persona_ult_config_implemen.primer_apellido,
                        consec_por_niveles.id_persona_ult_config_implemen.segundo_apellido
                    ])) if consec_por_niveles and consec_por_niveles.id_persona_ult_config_implemen else ""


                    t247_consecutivo_actual = (
                        str(consec_por_niveles.consecutivo_actual).zfill(consec_por_niveles.cantidad_digitos)
                        if consec_por_niveles and consec_por_niveles.consecutivo_actual is not None
                        else None
                    )

                    item = {

                        "id_config_tipologia_doc_agno":config_tipologia.id_config_tipologia_doc_agno,
                        "id_tipologia": id_tipologia,
                        "nombre_tipologia": nombre_tipologia,
                        "agno_tipologia": config_tipologia.agno_tipologia,
                        "tipo_configuracion": tipo_configuracion,
                        "consecutivo_inicial": consec_por_niveles.consecutivo_inicial,
                        "cantidad_digitos": consec_por_niveles.cantidad_digitos,
                        "T247Id_PersonaUltConfigImplemen": (
                            consec_por_niveles.id_persona_ult_config_implemen.id_persona
                            if consec_por_niveles and consec_por_niveles.id_persona_ult_config_implemen
                            else None
                        ),
                        "Persona_ult_config_implemen": nombre_persona_config,
                        "T247fechaUltConfigImplemen": (
                            consec_por_niveles.fecha_ult_config_implemen if consec_por_niveles else None
                        ),
                        "consecutivo_final": t247_consecutivo_actual,
                        "fecha_consecutivo_final": (
                            consec_por_niveles.fecha_consecutivo_actual if consec_por_niveles else None
                        ),
                    }
                elif tipo_configuracion == "SS":
                    # Caso 3
                    item = {"tipo_configuracion": tipo_configuracion}
                else:
                    # Otros casos, si es necesario
                    item = {"tipo_configuracion": "Otro"}

                data.append(item)

            return Response({
                'success': True,
                'detail': 'Lista de configuraciones',
                'data': data
            })
        except Exception as e:
            return Response({
                'success': False,
                'detail': str(e),
                'data': []
            })


class GetActualSeccionSubsecciones(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    
    def get(self, request):
        trd_actual = TablaRetencionDocumental.objects.filter(actual=True).first()
        if not trd_actual:
            raise NotFound('No existe aún una TRD actual')
        id_organigrama = trd_actual.id_ccd.id_organigrama.id_organigrama

        unidades = UnidadesOrganizacionales.objects.filter(Q(id_organigrama=id_organigrama) & Q(activo=True) & ~Q(cod_agrupacion_documental=None))
        serializer = self.serializer_class(unidades, many=True)
        return Response({'success':True, 'detail':'Se encontraron las siguientes unidades', 'data':serializer.data}, status=status.HTTP_200_OK)