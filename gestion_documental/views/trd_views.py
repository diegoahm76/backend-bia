from rest_framework import status
from django.db.models import Q
import copy
from datetime import datetime
from rest_framework import generics
from rest_framework.response import Response
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from gestion_documental.serializers.trd_serializers import (
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
    GetSeriesSubSUnidadOrgTRDSerializer
)
from gestion_documental.serializers.ccd_serializers import (
    CCDSerializer
)

from gestion_documental.models.ccd_models import (
    SeriesSubseriesUnidadOrg,
    CuadrosClasificacionDocumental,
    SeriesDoc
)
from almacen.models.organigrama_models import (
    Organigramas
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental,
    TipologiasDocumentales,
    SeriesSubSUnidadOrgTRDTipologias,
    FormatosTiposMedio,
    SeriesSubSUnidadOrgTRD,
    FormatosTiposMedioTipoDoc,
    HistoricosSerieSubSeriesUnidadOrgTRD,
)

class UpdateTipologiasDocumentales(generics.UpdateAPIView):
    serializer_class = TipologiasDocumentalesPutSerializer
    queryset = TipologiasDocumentales.objects.all()

    def put(self, request, id_trd):
        data = request.data
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        confirm = request.query_params.get('confirm')
        if trd:
            if not trd.fecha_terminado and not trd.fecha_retiro_produccion:
                if data:
                    # VALIDAR QUE EL ID_TRD SEA EL MISMO
                    trd_list = [tipologia['id_trd'] for tipologia in data]
                    if len(set(trd_list)) != 1:
                        return Response({'success':False, 'detail':'Debe validar que las tipologias pertenezcan a un mismo TRD'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if trd_list[0] != int(id_trd):
                            return Response({'success':False, 'detail':'El id trd de la petición debe ser igual al enviado en url'}, status=status.HTTP_400_BAD_REQUEST)

                    # VALIDAR QUE LOS CODIGOS SEAN UNICOS
                    codigos_list = [tipologia['codigo'] for tipologia in data]
                    if len(codigos_list) != len(set(codigos_list)):
                        return Response({'success':False, 'detail':'Debe validar que los códigos de las tipologias sean únicos'}, status=status.HTTP_400_BAD_REQUEST)

                    # VALIDAR QUE LOS NOMBRES SEAN UNICOS
                    nombres_list = [tipologia['nombre'] for tipologia in data]
                    if len(nombres_list) != len(set(nombres_list)):
                        return Response({'success':False, 'detail':'Debe validar que los nombres de las tipologias sean únicos'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDAR QUE LOS FORMATOS NO ESTÉN VACÍOS
                    formatos_list = [tipologia['formatos'] for tipologia in data]
                    formatos_empty = any(sublist == [] for sublist in formatos_list)
                    if formatos_empty:
                        return Response({'success':False, 'detail':'Debe asignar formatos para el tipo de medio de cada tipologia'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDAR QUE LOS FORMATOS EXISTAN
                    formatos_actuales = FormatosTiposMedio.objects.filter(activo=True)
                    formatos_actuales_list = [formato.id_formato_tipo_medio for formato in formatos_actuales]
                    formatos_flat_list = set([item for sublist in formatos_list for item in sublist])
                    if not formatos_flat_list.issubset(formatos_actuales_list):
                        return Response({'success':False, 'detail':'Debe asignar formatos que existan'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDAR QUE LOS FORMATOS PERTENEZCAN AL TIPO MEDIO INDICADO
                    for tipologia in data:
                        if tipologia['cod_tipo_medio_doc'] == 'E' or tipologia['cod_tipo_medio_doc'] == 'F':
                            formatos_actuales = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc=tipologia['cod_tipo_medio_doc'])
                            formatos_actuales_list = [formato.id_formato_tipo_medio for formato in formatos_actuales]
                            if not set(tipologia['formatos']).issubset(formatos_actuales_list):
                                return Response({'success':False, 'detail':'Debe asignar formatos que correspondan al tipo medio elegido'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # CREAR TIPOLOGIAS
                    tipologias_create = list(filter(lambda tipologia: tipologia['id_tipologia_documental'] == None, data))
                    tipologias_id_create = []
                    if tipologias_create:
                        # CREAR RELACIONES CON FORMATOS
                        for tipologia in tipologias_create:
                            serializer = self.serializer_class(data=tipologia)
                            serializer.is_valid(raise_exception=True)
                            serializador = serializer.save()
                            tipologias_id_create.append(serializador.id_tipologia_documental)
                            for formato in tipologia['formatos']:
                                formato_instance = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=formato).first()
                                FormatosTiposMedioTipoDoc.objects.create(
                                    id_tipologia_doc=serializador,
                                    id_formato_tipo_medio=formato_instance
                                )
                        # CAMBIOS POR CONFIRMAR TRUE SI ES TRD ACTUAL
                        if trd.actual:
                            trd.cambios_por_confirmar = True
                            trd.save()

                    # ACTUALIZAR TIPOLOGIAS
                    tipologias_update = list(filter(lambda tipologia: tipologia['id_tipologia_documental'] != None, data))
                    if tipologias_update:
                        for tipologia in tipologias_update:
                            tipologia_existe = TipologiasDocumentales.objects.filter(id_tipologia_documental=tipologia['id_tipologia_documental']).first()
                            if tipologia_existe:
                                if tipologia_existe.cod_tipo_medio_doc != tipologia['cod_tipo_medio_doc']:
                                    formato_tipologia_existe = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=tipologia['id_tipologia_documental'])
                                    formato_tipologia_existe.delete()
                                
                                if not trd.actual:    
                                    serializer = self.serializer_class(tipologia_existe, data=tipologia)
                                    serializer.is_valid(raise_exception=True)
                                    serializador = serializer.save()
                                
                                # ACTUALIZAR FORMATOS
                                for formato in tipologia['formatos']:
                                    formato_tipologia_existe = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=tipologia['id_tipologia_documental'], id_formato_tipo_medio=formato)
                                    tipologia_actualizada = TipologiasDocumentales.objects.filter(id_tipologia_documental=tipologia['id_tipologia_documental']).first()
                                    if not formato_tipologia_existe:
                                        formato_instance = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=formato).first()
                                        FormatosTiposMedioTipoDoc.objects.create(
                                            id_tipologia_doc=tipologia_actualizada,
                                            id_formato_tipo_medio=formato_instance
                                        )
                                    formato_tipologia_eliminar = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=tipologia['id_tipologia_documental']).exclude(id_formato_tipo_medio__in=tipologia['formatos'])
                                    formato_tipologia_eliminar.delete()

                    # ELIMINAR TIPOLOGIAS
                    lista_tipologia_id = [tipologia['id_tipologia_documental'] for tipologia in tipologias_update]
                    lista_tipologia_id.extend(tipologias_id_create)
                    tipologias_eliminar = TipologiasDocumentales.objects.filter(id_trd=id_trd).exclude(id_tipologia_documental__in=lista_tipologia_id)
                    
                    if tipologias_eliminar and trd.actual:
                        return Response({'success':False, 'detail':'No puede eliminar tipologias para una TRD actual. Intente desactivar'})
                    
                    # VALIDAR QUE NO SE ESTÉN USANDO LAS TIPOLOGIAS A ELIMINAR
                    tipologias_eliminar_id = [tipologia.id_tipologia_documental for tipologia in tipologias_eliminar]
                    serie_subserie_unidad_tipologia = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_tipologia_doc__in=tipologias_eliminar_id)
                    if serie_subserie_unidad_tipologia:
                        if confirm == 'true':
                            serie_subserie_unidad_tipologia.delete()
                        else:
                            return Response({'success':False, 'detail':'Una o varias tipologias a eliminar ya están asociadas al TRD', 'data':serie_subserie_unidad_tipologia.values()}, status=status.HTTP_403_FORBIDDEN)
                    
                    tipologias_eliminar.delete()

                    return Response({'success':True, 'detail':'Se ha realizado cambios con las tipologias'}, status=status.HTTP_201_CREATED)
                else:
                    # VALIDAR QUE NO SE ESTÉN USANDO LAS TIPOLOGIAS A ELIMINAR
                    tipologias_eliminar = TipologiasDocumentales.objects.filter(id_trd=id_trd)
                    
                    if tipologias_eliminar and trd.actual:
                        return Response({'success':False, 'detail':'No puede eliminar tipologias para una TRD actual. Intente desactivar'})
                    
                    tipologias_eliminar_id = [tipologia.id_tipologia_documental for tipologia in tipologias_eliminar]
                    serie_subserie_unidad_tipologia = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_tipologia_doc__in=tipologias_eliminar_id)
                    if serie_subserie_unidad_tipologia:
                        if confirm == 'true':
                            serie_subserie_unidad_tipologia.delete()
                        else:
                            return Response({'success':False, 'detail':'Una o varias tipologias a eliminar ya están asociadas al TRD', 'data':serie_subserie_unidad_tipologia.values()}, status=status.HTTP_403_FORBIDDEN)

                    tipologias_eliminar.delete()

                    return Response({'success':True, 'detail':'Se han eliminado todas las tipologias'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'success':False, 'detail':'El TRD ya está terminado o fue retirado de producción, por lo cual no es posible realizar acciones sobre las tipologias'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success':False, 'detail':'El TRD no existe'}, status=status.HTTP_404_NOT_FOUND)

class GetTipologiasDocumentales(generics.ListAPIView):
    serializer_class = TipologiasDocumentalesSerializer
    queryset = TipologiasDocumentales.objects.all()

    def get(self, request, id_trd):
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        if trd:
            tipologias = TipologiasDocumentales.objects.filter(id_trd=id_trd, activo=True).values()
            if not tipologias:
                return Response({'success':True, 'detail':'No se encontraron tipologías para el organigrama', 'data':tipologias}, status=status.HTTP_200_OK)
            for tipologia in tipologias:
                formatos_tipologias = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=tipologia['id_tipologia_documental'])
                formatos_tipologias_list = [formato_tipologia.id_formato_tipo_medio.id_formato_tipo_medio for formato_tipologia in formatos_tipologias]
                formatos = FormatosTiposMedio.objects.filter(id_formato_tipo_medio__in=formatos_tipologias_list).values()
                tipologia['formatos'] = formatos
                
            return Response({'success':True, 'detail':'Se encontraron las siguientes tipologías para el organigrama', 'data':tipologias}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'Debe consultar por un TRD válido'}, status=status.HTTP_404_NOT_FOUND)


#Series SubSeries Unidades Organizacionales TRD
class CreateSerieSubSeriesUnidadesOrgTRD(generics.CreateAPIView):
    serializer_class = SeriesSubSeriesUnidadesOrgTRDSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()

    def post(self, request, id_trd):
        data_entrante = request.data
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        tipologias = request.data.get('tipologias')

        if trd:
            serializador = self.serializer_class(data=data_entrante, many=False)
            serializador.is_valid(raise_exception=True)

            id_trd_validated = serializador.validated_data.get('id_trd')
            id_serie_subserie_unidad = serializador.validated_data.get('id_serie_subserie_doc')
            cod_disposicion_final = serializador.validated_data.get('cod_disposicion_final')
            digitalizacion_dis_final = serializador.validated_data.get('digitalizacion_dis_final')
            tiempo_retencion_ag = serializador.validated_data.get('tiempo_retencion_ag')
            tiempo_retencion_ac = serializador.validated_data.get('tiempo_retencion_ac')
            descripcion_procedimiento = serializador.validated_data.get('descripcion_procedimiento')

            #VALIDACION DE NO ASIGNAR UNA SERIE SUBSERIE UNIDAD TRD A OTRA TRD
            if int(id_trd) != id_trd_validated.id_trd:
                return Response({'success': False, 'detail': 'El id_trd enviado debe ser el mismo que el ingresado en la url'}, status=status.HTTP_400_BAD_REQUEST)

            #VALIDACION ENVIO VACIO DE LA INFORMACION
            if not cod_disposicion_final and not digitalizacion_dis_final and not tiempo_retencion_ag and not tiempo_retencion_ac and not descripcion_procedimiento:
                serializador.save()
                return Response({'success': True, 'detail': 'Creación exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)

            #VALIDACION ENVIO COMPLETO DE LA INFORMACION
            elif cod_disposicion_final and digitalizacion_dis_final and tiempo_retencion_ag and tiempo_retencion_ac and descripcion_procedimiento != None:
                tipologias_instance = TipologiasDocumentales.objects.filter(id_tipologia_documental__in=tipologias, id_trd=id_trd)
                if len(tipologias) != tipologias_instance.count():
                    return Response({'success': False, 'detail': 'Todas las tipologias seleccionadas deben existir y deben estar relacionadas a la TRD elegida'}, status=status.HTTP_400_BAD_REQUEST)

                #VALIDAR QUE SE ELIJA UNA SERIE SUBSERIE UNIDAD VALIDA, SEGÚN LA TRD ELEGIDA
                serie_subserie_unidad = []
                serie_subserie_unidad.append(id_serie_subserie_unidad.id_serie_subserie_doc)
                series_trd = list(SeriesDoc.objects.filter(id_ccd=trd.id_ccd))
                series_id = [serie.id_serie_doc for serie in series_trd]
                series_subseries_unidades_org_ccd = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc__in=series_id)
                series_subseries_unidades_org_ccd_id = [serie.id_serie_subserie_doc for serie in series_subseries_unidades_org_ccd]
                if not set(serie_subserie_unidad).issubset(set(series_subseries_unidades_org_ccd_id)):
                    return Response({'success': False, 'detail': 'Debe elegir una serie subserie unidad asociada al ccd que tiene la trd enviada en la url'}, status=status.HTTP_400_BAD_REQUEST)

                serializado = serializador.save()

                #CREACIÓN DE LA SERIE SUBSERIE UNIDAD TRD TIPOLOGIA
                for tipologia in tipologias_instance:
                    SeriesSubSUnidadOrgTRDTipologias.objects.create(
                        id_serie_subserie_unidadorg_trd = serializado,
                        id_tipologia_doc = tipologia
                    )
                return Response({'success': True, 'detail': 'Creación exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'detail': 'Debe enviar todas las especificaciones diligenciadas o todas las especificaciones vacias'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'detail': 'No existe ninguna Tabla de Retención Documental con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])
# def uploadDocument(request, id_serie_subserie_uniorg_trd):
#     ssuorg_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd=id_serie_subserie_uniorg_trd).first()
#     if ssuorg_trd:
#         if ssuorg_trd.id_trd.actual:
#             return Response({'success': False, 'detail': ''})
#         ssuorg_trd.ruta_archivo_cambio = request.FILES.get('document')
#         ssuorg_trd.save()
#     else:
#         return Response({'success': False, 'detail': 'No se encontró ninguna ssuorg-trd con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

#     return Response({'success': True, 'detail': 'Documento cargado correctamente'}, status=status.HTTP_201_CREATED)

class UpdateSerieSubSeriesUnidadesOrgTRD(generics.CreateAPIView):
    serializer_class = SeriesSubSeriesUnidadesOrgTRDPutSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_serie_subs_unidadorg_trd):
        data_entrante = request.data
        persona_usuario_logeado = request.user.persona
        serie_subs_unidadorg_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd=id_serie_subs_unidadorg_trd).first()
        tipologias = request.data.get('tipologias')
        previous_serie_subs_unidad_org_trd = copy.copy(serie_subs_unidadorg_trd)

        if serie_subs_unidadorg_trd:
            #SI LA TRD NO ES ACTUAL Y NO TIENE FECHA RETIRO PRODUCCIÓN ACTUALIZA SERIE SUBSERIE SIN HISTORICO
            if serie_subs_unidadorg_trd.id_trd.actual == False and serie_subs_unidadorg_trd.id_trd.fecha_retiro_produccion == None:
                serializador = self.serializer_class(serie_subs_unidadorg_trd, data=data_entrante, many=False)
                serializador.is_valid(raise_exception=True)

                cod_disposicion_final = serializador.validated_data.get('cod_disposicion_final')
                digitalizacion_dis_final = serializador.validated_data.get('digitalizacion_dis_final')
                tiempo_retencion_ag = serializador.validated_data.get('tiempo_retencion_ag')
                tiempo_retencion_ac = serializador.validated_data.get('tiempo_retencion_ac')
                descripcion_procedimiento = serializador.validated_data.get('descripcion_procedimiento')

                #SI ENVIAN TODAS LAS ESPECIFICACIONES VACIAS
                if not cod_disposicion_final and not digitalizacion_dis_final and not tiempo_retencion_ag and not tiempo_retencion_ac and not descripcion_procedimiento and not tipologias:
                    serializador.save()

                    #ELIMINA TODAS LAS TIPOLOGIAS ASOCIADAS A ESA SSU-TRD
                    series_unidades_tipologias = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd=id_serie_subs_unidadorg_trd)
                    series_unidades_tipologias.delete()
                    return Response({'success': True, 'detail': 'Actualización exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)

                #SI ENVIAN TODAS LAS ESPECIFICACIONES DILIGENCIADAS
                elif cod_disposicion_final and digitalizacion_dis_final and tiempo_retencion_ag and tiempo_retencion_ac and descripcion_procedimiento and tipologias:
                    tipologias_instance = TipologiasDocumentales.objects.filter(id_tipologia_documental__in=tipologias, id_trd=serie_subs_unidadorg_trd.id_trd.id_trd)

                    #VALIDACION SI ENVIAN TIPOLOGIAS QUE NO SON DE LA MISMA TRD O QUE NO EXISTEN
                    if len(tipologias) != tipologias_instance.count():
                        return Response({'success': False, 'detail': 'Todas las tipologias seleccionadas deben existir y deben estar relacionadas a la TRD elegida'}, status=status.HTTP_400_BAD_REQUEST)

                    #ELIMINA TODAS LAS TIPOLOGIAS QUE NO HAYA ENVIADO AL MOMENTO DE ACTUALIZAR
                    serie_subserie_unidad_tipologias = SeriesSubSUnidadOrgTRDTipologias.objects.filter(Q(id_serie_subserie_unidadorg_trd=id_serie_subs_unidadorg_trd) & ~Q(id_tipologia_doc__in=tipologias))
                    serie_subserie_unidad_tipologias.delete()

                    serializado = serializador.save()
                    
                    #VERIFICA QUE NO EXISTA EN SSUTRD-TIPOLOGIAS Y CREA LA CONEXIÓN
                    for tipologia in tipologias:
                        serie_tipologia_instance = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd=id_serie_subs_unidadorg_trd, id_tipologia_doc=tipologia)
                        tipologia_instance_create = TipologiasDocumentales.objects.filter(id_tipologia_documental=tipologia).first()
                        if not serie_tipologia_instance:
                            SeriesSubSUnidadOrgTRDTipologias.objects.create(
                                id_serie_subserie_unidadorg_trd = serie_subs_unidadorg_trd,
                                id_tipologia_doc = tipologia_instance_create
                            )
                    return Response({'success': True, 'detail': 'Actualización exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)

                else:
                    return Response({'success': False, 'detail': 'Debe enviar todas las especificaciones y tipologias diligenciadas o todas las especificaciones y tipologias vacias'}, status=status.HTTP_400_BAD_REQUEST)
            
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
                    tipologias_instance = TipologiasDocumentales.objects.filter(id_tipologia_documental__in=tipologias, id_trd=serie_subs_unidadorg_trd.id_trd.id_trd)
                    tipologias_instance_list = [tipologia.id_tipologia_documental for tipologia in tipologias_instance]
                    
                    #VALIDA QUE LAS TIPOLOGIAS SELECCIONADAS TENGAN LA MISMA TRD COMO PADRE
                    if tipologias and not tipologias_instance_list:
                        return Response({'success': False, 'detail': 'La tipologia seleccionada no hace parte de las disponibles'}, status=status.HTTP_400_BAD_REQUEST)
                    if not set(tipologias).issubset(set(tipologias_instance_list)):
                        return Response({'success': False, 'detail': 'Alguna de las tipologias seleccionadas no hacen parte de las disponibles'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    #VALIDA QUE LA TIPOLOGIA SELECCIONADA ESTÉ ACTIVA
                    for tipologia in tipologias_instance:
                        if tipologia.activo == False:
                            return Response({'success': False, 'detail': 'Todas las tipologias seleccionadas deben estar activas para poder asignarlas'}, status=status.HTTP_400_BAD_REQUEST)

                    #GUARDA LA INFORMACIÓN ENVIADA  
                    serializado = serializador.save()

                    #CREA LA CONEXIÓN EN LA TABLA SSUTRD-TIPOLOGIA SI NO EXISTE
                    for tipologia in tipologias_instance:
                        tipologia_existente = SeriesSubSUnidadOrgTRDTipologias.objects.filter(Q(id_serie_subserie_unidadorg_trd=serie_subs_unidadorg_trd.id_serie_subs_unidadorg_trd) & Q(id_tipologia_doc=tipologia.id_tipologia_documental)).first()
                        if not tipologia_existente:
                            SeriesSubSUnidadOrgTRDTipologias.objects.create(
                                id_serie_subserie_unidadorg_trd = serie_subs_unidadorg_trd,
                                id_tipologia_doc = tipologia
                            )

                    #CREA EL HISTORICO
                    HistoricosSerieSubSeriesUnidadOrgTRD.objects.create(
                        id_serie_subs_unidadorg_trd = previous_serie_subs_unidad_org_trd,
                        cod_disposicion_final = previous_serie_subs_unidad_org_trd.cod_disposicion_final,
                        digitalizacion_disp_final = previous_serie_subs_unidad_org_trd.digitalizacion_dis_final,
                        tiempo_retencion_ag = previous_serie_subs_unidad_org_trd.tiempo_retencion_ag,
                        tiempo_retencion_ac = previous_serie_subs_unidad_org_trd.tiempo_retencion_ac,
                        descripcion_procedimiento = previous_serie_subs_unidad_org_trd.descripcion_procedimiento,
                        justificacion = previous_serie_subs_unidad_org_trd.justificacion_cambio,
                        id_persona_cambia = persona_usuario_logeado
                    )

                    return Response({'success': True, 'detail': 'Actualización exitosa de la TRD Actual', 'data': serializador.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success': False, 'detail': 'Para modificar una trd actual se debe completar toda la información'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'detail': 'No existe ninguna Serie Subserie Unidad TRD con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)


class DeleteSerieSubserieUnidadTRD(generics.RetrieveDestroyAPIView):
    serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()

    def delete(self, request, id_ssuorg_trd):
        serie_ss_uniorg_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd=id_ssuorg_trd).first()
        if serie_ss_uniorg_trd:
            if serie_ss_uniorg_trd.id_trd.actual == True:
                return Response({'success': False, 'detail': 'No se pueden realizar acciones sobre las Series'})
            serie_ss_uniorg_trd_tipologias = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd=serie_ss_uniorg_trd)
            serie_ss_uniorg_trd_tipologias.delete()
            serie_ss_uniorg_trd.delete()
            return Response({'success': True, 'detail': 'Eliminado exitosamente'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'success': False, 'detail': 'No se encontró ninguna Serie Subserie Unidad TRD con el parámetro ingresado'}, status.HTTP_404_NOT_FOUND)



#Tabla de Retencion Documental

class GetTablaRetencionDocumental(generics.ListAPIView):
    serializer_class = TRDSerializer
    queryset = TablaRetencionDocumental.objects.all()

class GetTablaRetencionDocumentalTerminados(generics.ListAPIView):
    serializer_class = TRDSerializer
    queryset = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

class PostTablaRetencionDocumental(generics.CreateAPIView):
    serializer_class = TRDPostSerializer
    queryset = TablaRetencionDocumental
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pass
        except:
            return Response({'success': False, 'detail': 'Valide la información ingresada, el id_ccd es requerido, el nombre y la versión son requeridos y deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)

        #Validación de seleccionar solo ccd terminados
        ccd = serializer.validated_data.get('id_ccd')
        ccd_instance = CuadrosClasificacionDocumental.objects.filter(id_ccd=ccd.id_ccd).first()
        if ccd_instance:
            if ccd_instance.fecha_terminado == None:
                return Response({'success': False, 'detail': 'No se pueden seleccionar Cuadros de Clasificación Documental que no estén terminados'}, status=status.HTTP_403_FORBIDDEN)

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

            return Response({'success': True, 'detail': 'TRD creada exitosamente'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'No existe un Cuadro de Clasificación Documental con el id_ccd enviado'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'success': False, 'detail': 'No existe ninguna Tabla de Retención Documental con los parámetros ingresados'}, status=status.HTTP_404_NOT_FOUND)

        if trd.fecha_terminado:
            return Response({'success': False,'detail': 'No se puede actualizar una TRD terminada'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(trd, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pass
        except:
            return Response({'success': False, 'detail': 'Validar data enviada, el nombre y la versión son requeridos y deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        # AUDITORIA DE UPDATE DE CCD
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        descripcion = {'nombre':str(previoud_trd.nombre), 'version':str(previoud_trd.version)}
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

        return Response({'success': True, 'detail': 'Tabla de Retención Documental actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)

# class FinalizarTablaRetencionDocumental(generics.RetrieveUpdateAPIView):
#     serializer_class = TRDFinalizarSerializer
#     queryset = TablaRetencionDocumental

#     def put(self, request, id_trd):
#         trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
#         if trd:
#             if trd.fecha_terminado == None:
#                 #Obtiene el id de las tipologias existentes relacionadas a la TRD
#                 tipologias = TipologiasDocumentales.objects.filter(id_trd=id_trd)
#                 tipologias_list = [tipologia.id_tipologia_documental for tipologia in tipologias]

#                 #Obtiene el id de la seriesubserieunidad existentes relacionadas con el ccd asociado a la TRD
#                 ccd_trd = CuadrosClasificacionDocumental.objects.get(id_ccd=trd.id_ccd.id_ccd)
#                 series_ccd_trd = SeriesDoc.objects.filter(id_ccd=ccd_trd.id_ccd)
#                 series_ccd_trd_list = [serie.id_serie_doc for serie in series_ccd_trd]
#                 serie_subserie_unidadorg = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc__in=series_ccd_trd_list)
#                 serie_subserie_unidadorg_list = [serie.id_serie_subserie_doc for serie in serie_subserie_unidadorg]


#                 # Busqueda mediante la tipologia, valor clave que contiene la trd directa
#                 serie_subserie_tipologia_list = SeriesSubSeriesUnidadesTipologias.objects.filter(id_tipologia_documental__in=tipologias_list)

#                 #Id de conexiones de ccd conectadas en TRD
#                 series_unidades_asignacion_list = [serie.id_serie_subserie_doc.id_serie_subserie_doc for serie in serie_subserie_tipologia_list]

#                 #Id de tipologias relacionadas conectadas
#                 tipologias_asignacion_list = [serie.id_tipologia_documental.id_tipologia_documental for serie in serie_subserie_tipologia_list]

#                 #Valida que lo existente asociado a esa trd esté asociado en la tabla intermedia
#                 if not set(tipologias_list).issubset(tipologias_asignacion_list):
#                     tipologias_difference_list = [tipologia for tipologia in tipologias_list if tipologia not in tipologias_asignacion_list]
#                     tipologias_difference_instance = TipologiasDocumentales.objects.filter(id_tipologia_documental__in=tipologias_difference_list).values()
#                     return Response({'success': False, 'detail': 'Debe asociar todas las tipologias de esta TRD', 'Tipologias sin asignar':tipologias_difference_instance}, status=status.HTTP_400_BAD_REQUEST)


#                 if not set(serie_subserie_unidadorg_list).issubset(series_unidades_asignacion_list):
#                     serie_subser_unidad_difference_list = [serie_sub_uni for serie_sub_uni in serie_subserie_unidadorg_list if serie_sub_uni not in series_unidades_asignacion_list]
#                     serie_sub_unidad_difference_instance = SeriesSubseriesUnidadOrg.objects.filter(id_serie_subserie_doc__in=serie_subser_unidad_difference_list).values()
#                     return Response({'success': False, 'detail': 'Debe asociar todas las series subseries unidades del CCD asociado a esta TRD', 'Series Subseries Unidades sin asignar': serie_sub_unidad_difference_instance}, status=status.HTTP_400_BAD_REQUEST)

#                 #Poner Fecha Terminado
#                 trd.fecha_terminado = datetime.now()
#                 trd.save()
#                 return Response({'success': True, 'detail': 'Finalizado el CCD'}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({'success': False, 'detail': 'Ya se encuentra finalizado esta TRD'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({'success': False, 'detail': 'No se encontró ninguna TRD con estos parámetros'}, status=status.HTTP_404_NOT_FOUND)
class GetCCDTerminadoByPk(generics.ListAPIView):
    serializer_class = CCDSerializer
    queryset = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

    def get(self, request, pk):
        orgamigrama = Organigramas.objects.filter(id_organigrama = pk).first()
        if not orgamigrama:
            return Response({'success': False, 'detail': 'El organigrama ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)

        if orgamigrama.fecha_terminado == None or orgamigrama.fecha_retiro_produccion != None:
            return Response({'success': False, 'detail': 'El organigrama ingresado ya está retirado o no está terminado'}, status=status.HTTP_400_BAD_REQUEST)
        ccds = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None)).filter(id_organigrama = int(orgamigrama.id_organigrama)).values()
        return Response({'success': True, 'detail': 'CCD', 'data': ccds}, status=status.HTTP_201_CREATED)

class GetTRDTerminadoByPk(generics.ListAPIView):
    serializer_class = TRDSerializer
    queryset = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

    def get(self, request, pk):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_organigrama = pk).first()
        if not ccd:
            return Response({'success': False, 'detail': 'El ccd ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)

        if ccd.fecha_terminado == None or ccd.fecha_retiro_produccion != None:
            return Response({'success': False, 'detail': 'El ccd ingresado ya está retirado o no está terminado'}, status=status.HTTP_400_BAD_REQUEST)
        trds = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None)).filter(id_ccd = int(ccd.id_ccd)).values()
        return Response({'success': True, 'detail': 'CCD', 'data': trds}, status=status.HTTP_201_CREATED)

class Activar(generics.UpdateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class =TRDSerializer
    queryset=TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request):
        json_recibido = request.data
        if not json_recibido:
            return Response({'success': False, 'detail': 'Ingrese información'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['id_organigrama'] == '' or json_recibido['id_organigrama'] == None:
            return Response({'success': False, 'detail': 'Ingrese un organigrama'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['id_ccd'] == '' or json_recibido['id_ccd'] == None:
            return Response({'success': False, 'detail': 'Ingrese cuadro de clasificación documental'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['id_trd'] == '' or json_recibido['id_trd'] == None:
            return Response({'success': False, 'detail': 'Ingrese tabla de retención documental'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['justificacion'] == '' or json_recibido['justificacion'] == None:
            return Response({'success': False, 'detail': 'Ingrese justificación'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['archivo'] == '' or json_recibido['archivo'] == None:
            return Response({'success': False, 'detail': 'Ingrese archivo'}, status=status.HTTP_400_BAD_REQUEST)
        #VALIDAR LA EXISTENCIA DE LOS DATOS
        organigrama = Organigramas.objects.filter(~Q(fecha_terminado=None) & Q(fecha_retiro_produccion=None)).filter(id_organigrama = json_recibido['id_organigrama']).first()
        if not organigrama:
            return Response({'success': False, 'detail': 'El organigrama ingresado no se puede activar'}, status=status.HTTP_400_BAD_REQUEST)
        ccd = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado=None) & Q(fecha_retiro_produccion=None)).filter(id_ccd = json_recibido['id_ccd']).first()
        if not ccd:
            return Response({'success': False, 'detail': 'El CCD ingresado no se puede activar'}, status=status.HTTP_400_BAD_REQUEST)
        trd = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado=None) & Q(fecha_retiro_produccion=None)).filter(id_trd = json_recibido['id_trd']).first()
        if not trd:
            return Response({'success': False, 'detail': 'La TRD ingresada no se puede activar'}, status=status.HTTP_400_BAD_REQUEST)
        #VALIDAR LA RELACION DE LA CCD CON EL ORGANIGRAMA, Y DE LA CCD CON LA TRD
        if ccd.id_organigrama.id_organigrama != organigrama.id_organigrama:
            return Response({'success': False, 'detail': 'El organigrama ingresado no tiene relación con el ccd ingresado'}, status=status.HTTP_400_BAD_REQUEST)
        if trd.id_ccd.id_ccd != ccd.id_ccd:
            return Response({'success': False, 'detail': 'El ccd ingresado no tiene relación con la trd ingresada'}, status=status.HTTP_400_BAD_REQUEST)
        #CONSULTAR LA PREEXISTENCIA DE DE TABLAS ACTIVADAS
        trd_a_remplazar=TablaRetencionDocumental.objects.filter(actual=True).first()
        ccd_a_remplazar=CuadrosClasificacionDocumental.objects.filter(actual=True).first()
        organigrama_a_remplazar=Organigramas.objects.filter(actual=True).first()

        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        previous_remplazante_trd=copy.copy(trd)
        previous_a_remplazar_trd=copy.copy(trd_a_remplazar)
        previous_remplazante_ccd=copy.copy(ccd)
        previous_a_remplazar_ccd=copy.copy(ccd_a_remplazar)
        previous_remplazante_org=copy.copy(organigrama)
        previous_a_remplazar_org=copy.copy(organigrama_a_remplazar)

        if trd_a_remplazar and ccd_a_remplazar and organigrama_a_remplazar:
            if organigrama.actual == True and ccd.actual == True and trd.actual == True:
                return Response({'success': False, 'detail': 'Esta combinación ya se encuentra activa'}, status=status.HTTP_400_BAD_REQUEST)
            if  organigrama.actual == False and ccd.actual == False and trd.actual == False:
                organigrama_a_remplazar.actual =  False
                organigrama.actual = True
                ccd_a_remplazar.actual = False
                ccd.actual = True
                trd_a_remplazar.actual = False
                trd.actual =True
                organigrama.fecha_puesta_produccion = datetime.now()
                ccd.fecha_puesta_produccion = datetime.now()
                trd.fecha_puesta_produccion = datetime.now()
                organigrama.justificacion_nueva_version = json_recibido['justificacion']
                ccd.justificacion = json_recibido['justificacion']
                trd.justificacion = json_recibido['justificacion']
                organigrama_a_remplazar.fecha_retiro_produccion = datetime.now()
                ccd_a_remplazar.fecha_retiro_produccion = datetime.now()
                trd_a_remplazar.fecha_retiro_produccion = datetime.now()
                organigrama.ruta_resolucion = json_recibido['archivo']
                ccd.ruta_soporte = json_recibido['archivo']
                trd.ruta_soporte = json_recibido['archivo']
                trd_a_remplazar.save()
                trd.save()
                ccd_a_remplazar.save()
                ccd.save()
                organigrama_a_remplazar.save()
                organigrama.save()

                #auditoria organigrama desactivado
                descripcion = {"nombre":str(organigrama_a_remplazar.nombre),"versión":str(organigrama_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_org, 'current':organigrama_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 16,'cod_permiso': 'AC','subsistema': 'TRSV','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria CCD desactivado
                descripcion = {"nombre":str(ccd_a_remplazar.nombre),"versión":str(ccd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_ccd, 'current':ccd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD desactivado
                descripcion = {"nombre":str(trd_a_remplazar.nombre),"versión":str(trd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_trd, 'current':trd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                #auditoria organigrama activado
                descripcion = {"nombre":str(organigrama.nombre),"versión":str(organigrama.version)}
                valores_actualizados={'previous':previous_remplazante_org, 'current':organigrama}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 16,'cod_permiso': 'AC','subsistema': 'TRSV','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria CCD activado
                descripcion = {"nombre":str(ccd.nombre),"versión":str(ccd.version)}
                valores_actualizados={'previous':previous_remplazante_ccd, 'current':ccd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD activado
                descripcion = {"nombre":str(trd.nombre),"versión":str(trd.version)}
                valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                return Response({'success': True, 'detail': 'Activación exitosa'}, status=status.HTTP_201_CREATED)

            if organigrama.actual == True and ccd.actual == False and trd.actual == False:
                ccd_a_remplazar.actual = False
                ccd.actual = True
                trd_a_remplazar.actual = False
                trd.actual =True
                ccd.fecha_puesta_produccion = datetime.now()
                trd.fecha_puesta_produccion = datetime.now()
                ccd.justificacion = json_recibido['justificacion']
                trd.justificacion = json_recibido['justificacion']
                ccd_a_remplazar.fecha_retiro_produccion = datetime.now()
                trd_a_remplazar.fecha_retiro_produccion = datetime.now()
                ccd.ruta_soporte = json_recibido['archivo']
                trd.ruta_soporte = json_recibido['archivo']
                trd_a_remplazar.save()
                trd.save()
                ccd_a_remplazar.save()
                ccd.save()

                 #auditoria CCD desactivado
                descripcion = {"nombre":str(ccd_a_remplazar.nombre),"versión":str(ccd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_ccd, 'current':ccd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD desactivado
                descripcion = {"nombre":str(trd_a_remplazar.nombre),"versión":str(trd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_trd, 'current':trd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria CCD activado
                descripcion = {"nombre":str(ccd.nombre),"versión":str(ccd.version)}
                valores_actualizados={'previous':previous_remplazante_ccd, 'current':ccd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD activado
                descripcion = {"nombre":str(trd.nombre),"versión":str(trd.version)}
                valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                return Response({'success': True, 'detail': 'Activación exitosa'}, status=status.HTTP_201_CREATED)

            if organigrama.actual == True and ccd.actual == True and trd.actual == False:
                trd_a_remplazar.actual = False
                trd.actual =True
                trd.fecha_puesta_produccion = datetime.now()
                trd.justificacion = json_recibido['justificacion']
                trd_a_remplazar.fecha_retiro_produccion = datetime.now()
                trd.ruta_soporte = json_recibido['archivo']
                trd_a_remplazar.save()
                trd.save()

                 #auditoria TRD desactivado
                descripcion = {"nombre":str(trd_a_remplazar.nombre),"versión":str(trd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_trd, 'current':trd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD activado
                descripcion = {"nombre":str(trd.nombre),"versión":str(trd.version)}
                valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                return Response({'success': True, 'detail': 'Activación exitosa'}, status=status.HTTP_201_CREATED)

            return Response({'success': False, 'detail': 'No se pudo llevar a cabo la activación. Contraste la información ingresada con la que está en la base de datos'}, status=status.HTTP_400_BAD_REQUEST)

        if (trd_a_remplazar == None) and (ccd_a_remplazar == None) and (organigrama_a_remplazar == None):
                organigrama.actual = True
                ccd.actual = True
                trd.actual =True
                organigrama.fecha_puesta_produccion = datetime.now()
                ccd.fecha_puesta_produccion = datetime.now()
                trd.fecha_puesta_produccion = datetime.now()
                organigrama.justificacion_nueva_version = json_recibido['justificacion']
                ccd.justificacion = json_recibido['justificacion']
                trd.justificacion = json_recibido['justificacion']
                organigrama.ruta_resolucion = json_recibido['archivo']
                ccd.ruta_soporte = json_recibido['archivo']
                trd.ruta_soporte = json_recibido['archivo']
                trd.save()
                ccd.save()
                organigrama.save()

                #auditoria organigrama activado
                descripcion = {"nombre":str(organigrama.nombre),"versión":str(organigrama.version)}
                valores_actualizados={'previous':previous_remplazante_org, 'current':organigrama}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 16,'cod_permiso': 'AC','subsistema': 'TRSV','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria CCD activado
                descripcion = {"nombre":str(ccd.nombre),"versión":str(ccd.version)}
                valores_actualizados={'previous':previous_remplazante_ccd, 'current':ccd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD activado
                descripcion = {"nombre":str(trd.nombre),"versión":str(trd.version)}
                valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                return Response({'success': True, 'detail': 'Activación exitosa'}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'detail': 'Error de base de datos'}, status=status.HTTP_400_BAD_REQUEST)


class GetFormatosTiposMedioByParams(generics.ListAPIView):
    serializer_class = FormatosTiposMedioSerializer
    queryset = FormatosTiposMedio.objects.all()

    def get(self, request):
        cod_tipo_medio = request.query_params.get('cod-tipo-medio')
        nombre = request.query_params.get('nombre')

        if cod_tipo_medio == '':
            cod_tipo_medio = None
        if nombre == '':
            nombre = None

        if not cod_tipo_medio and not nombre:
            return Response({'success':False, 'detail':'Debe ingresar los parámetros de búsqueda'}, status=status.HTTP_404_NOT_FOUND)

        if cod_tipo_medio and nombre:
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc=cod_tipo_medio, nombre__icontains=nombre, activo=True)
            serializador = self.serializer_class(formatos_tipos_medio, many=True)
            if formatos_tipos_medio:
                return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'No se encontró ningún resultado'}, status=status.HTTP_404_NOT_FOUND)

        if cod_tipo_medio and not nombre:
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc=cod_tipo_medio, activo=True)
            serializador = self.serializer_class(formatos_tipos_medio, many=True)
            if formatos_tipos_medio:
                return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'No se encontró ningún resultado'}, status=status.HTTP_404_NOT_FOUND)

        if not cod_tipo_medio and nombre:
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(nombre__icontains=nombre, activo=True)
            serializador = self.serializer_class(formatos_tipos_medio, many=True)
            if formatos_tipos_medio:
                return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'No se encontró ningún resultado'}, status=status.HTTP_404_NOT_FOUND)

class GetFormatosTiposMedioByCodTipoMedio(generics.ListAPIView):
    serializer_class = FormatosTiposMedioSerializer
    queryset = FormatosTiposMedio.objects.all()

    def get(self, request, cod_tipo_medio_doc):
        if cod_tipo_medio_doc == 'H':
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(activo=True)
        else:
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc=cod_tipo_medio_doc, activo=True)

        serializador = self.serializer_class(formatos_tipos_medio, many=True)
        if serializador:
            return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No se encontró ningún resultado'}, status=status.HTTP_404_NOT_FOUND)

class RegisterFormatosTiposMedio(generics.CreateAPIView):
    serializer_class =  FormatosTiposMedioPostSerializer
    queryset = FormatosTiposMedio.objects.all()

    def post(self, request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success':True, 'detail':'Se creado el Formato Tipo Medio'}, status=status.HTTP_201_CREATED)

class UpdateFormatosTiposMedio(generics.RetrieveUpdateAPIView):
    serializer_class = FormatosTiposMedioPostSerializer
    queryset = FormatosTiposMedio.objects.all()

    def put(self, request, pk):
        formato_tipo_medio = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=pk).first()

        if formato_tipo_medio:
            if not formato_tipo_medio.registro_precargado:
                if formato_tipo_medio.item_ya_usado:
                    return Response({'success':False, 'detail':'Este formato tipo medio ya está siendo usado, por lo cual no es actualizable'}, status=status.HTTP_403_FORBIDDEN)

                serializer = self.serializer_class(formato_tipo_medio, data=request.data, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':True, 'detail':'Registro actualizado exitosamente'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'detail': 'No puede actualizar un formato tipo medio precargado'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No existe el formato tipo medio'}, status=status.HTTP_404_NOT_FOUND)

class DeleteFormatosTiposMedio(generics.DestroyAPIView):
    serializer_class = FormatosTiposMedioPostSerializer
    queryset = FormatosTiposMedio.objects.all()

    def delete(self, request, pk):
        formato_tipo_medio = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=pk).first()
        if formato_tipo_medio:
            pass
            if not formato_tipo_medio.registro_precargado:
                if formato_tipo_medio.item_ya_usado:
                    return Response({'success':False, 'detail':'Este formato tipo medio ya está siendo usado, no se pudo eliminar'}, status=status.HTTP_403_FORBIDDEN)

                formato_tipo_medio.delete()
                return Response({'success': True, 'detail': 'Este formato tipo medio ha sido eliminado exitosamente'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'success': False, 'detail': 'No puedes eliminar un formato tipo medio precargado'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail':'No existe el formato tipo medio'}, status=status.HTTP_404_NOT_FOUND)

class CambiosPorConfirmar(generics.UpdateAPIView):
    serializer_class = SeriesSubSeriesUnidadesOrgTRDPutSerializer
    queryset = SeriesSubSUnidadOrgTRDTipologias.objects.all()

    def put(self, request, id_trd):
        confirm = request.query_params.get('confirm')
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        if trd:
            if trd.actual:
                if trd.cambios_por_confirmar:
                    series_sub_unidades_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_trd=id_trd)
                    series_sub_unidades_trd_list = [serie_sub_unidad_trd.id_serie_subs_unidadorg_trd for serie_sub_unidad_trd in series_sub_unidades_trd]
                    formatos_tipo_medio = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd__in=series_sub_unidades_trd_list)
                    tipologias_list = [formato_tipo_medio.id_tipologia_doc.id_tipologia_documental for formato_tipo_medio in formatos_tipo_medio]
                    tipologias_trd = TipologiasDocumentales.objects.filter(id_trd=id_trd)
                    tipologias_trd_list = [tipologia.id_tipologia_documental for tipologia in tipologias_trd]

                    if not set(tipologias_trd_list).issubset(tipologias_list):
                        tipologias_faltan = TipologiasDocumentales.objects.filter(id_trd=id_trd).exclude(id_tipologia_documental__in=tipologias_list)
                        if confirm == 'true':
                            tipologias_faltan.delete()
                            trd.cambios_por_confirmar = False
                            trd.save()
                            return Response({'success': True, 'detail': 'Se han eliminado las tipologias no usadas y se confirmaron cambios'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'success': False, 'detail': 'Tiene tipologias pendientes por usar', 'data':tipologias_faltan.values()}, status=status.HTTP_403_FORBIDDEN)
                    else:
                        trd.cambios_por_confirmar = False
                        trd.save()
                        return Response({'success': True, 'detail': 'Está usando todas las tipologias, se han confirmado cambios'}, status=status.HTTP_200_OK)
                else:
                    return Response({'success': False, 'detail': 'No tiene cambios por confirmar'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'success':False, 'detail':'No puede realizar esta acción porque no es el TRD actual'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success':False, 'detail':'El TRD no existe'}, status=status.HTTP_404_NOT_FOUND)

class GetSeriesSubSUnidadOrgTRD(generics.ListAPIView):
    serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()
    
    def get(self, request, pk):
        id_trd_a_consultar1 = pk
        series_subseries_unidad_org_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_trd = id_trd_a_consultar1).values()
        if not series_subseries_unidad_org_trd:
            return Response({'success': False, 'detail': 'No se encontró la TRD'}, status=status.HTTP_403_FORBIDDEN)
        
        ids_serie_subs_unidad_org_trd = [i['id_serie_subs_unidadorg_trd'] for i in series_subseries_unidad_org_trd]
        #print(ids_serie_subs_unidad_org_trd)
        result = []
        for i in ids_serie_subs_unidad_org_trd:
            main_detail = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd = i).values().first()
            detalle_serie_subs_unidad_org_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd = main_detail['id_serie_subserie_unidadorg_trd_id']).values().first()
            detalle_tipologias = TipologiasDocumentales.objects.filter(id_tipologia_documental = main_detail['id_tipologia_doc_id']).values().first()
            main_detail['id_serie_subserie_unidadorg_trd_id'] = detalle_serie_subs_unidad_org_trd
            main_detail['id_tipologia_doc_id'] = detalle_tipologias
            result.append(main_detail)
            
            
        return Response({'success': True, 'Tabla': result}, status=status.HTTP_204_NO_CONTENT)

class GetSeriesSubSUnidadOrgTRDByPk(generics.ListAPIView):
    serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()
    
    def get(self, request, pk):
        pk_a_consultar1 = pk
        serie_subseries_unidad_org = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd = pk_a_consultar1).values()
        if not serie_subseries_unidad_org:
            return Response({'success': False, 'detail': 'No se encontró información relacionada a ese id'}, status=status.HTTP_403_FORBIDDEN)
        
        ids_serie_subs_unidad_org_trd = [i['id_serie_subs_unidadorg_trd'] for i in serie_subseries_unidad_org]
        #print(ids_serie_subs_unidad_org_trd)
        result = []
        for i in ids_serie_subs_unidad_org_trd:
            main_detail = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd = i).values().first()
            detalle_serie_subs_unidad_org_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd = main_detail['id_serie_subserie_unidadorg_trd_id']).values().first()
            detalle_tipologias = TipologiasDocumentales.objects.filter(id_tipologia_documental = main_detail['id_tipologia_doc_id']).values().first()
            main_detail['id_serie_subserie_unidadorg_trd_id'] = detalle_serie_subs_unidad_org_trd
            main_detail['id_tipologia_doc_id'] = detalle_tipologias
            result.append(main_detail)
            
            
        return Response({'success': True, 'Tabla': result}, status=status.HTTP_204_NO_CONTENT)

class DesactivarTipologiaActual(generics.UpdateAPIView):
    serializer_class = TipologiasDocumentalesPutSerializer
    queryset = TipologiasDocumentales.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_tipologia):
        persona = request.user.persona
        tipologia = TipologiasDocumentales.objects.filter(id_tipologia_documental=id_tipologia).first()
        justificacion = request.data.get('justificacion_desactivacion')
        if tipologia:
            trd = TablaRetencionDocumental.objects.filter(id_trd=tipologia.id_trd.id_trd).first()
            if trd.actual:
                if not tipologia.activo:
                    return Response({'success':False, 'detail':'La tipologia ya se encuentra desactivada'}, status=status.HTTP_403_FORBIDDEN)
                if not justificacion:
                    return Response({'success':False, 'detail':'Debe ingresar la justificación para desactivar la tipología'}, status=status.HTTP_400_BAD_REQUEST)
                
                tipologia.activo = False
                tipologia.fecha_desactivacion = datetime.now()
                tipologia.justificacion_desactivacion = justificacion
                tipologia.id_persona_desactiva = persona
                tipologia.save()
                return Response({'success': True, 'detail': 'Se ha desactivado la tipologia indicada'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'No puede realizar esta acción porque no es el TRD actual'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success':False, 'detail':'La tipologia ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)

class finalizarTRD(generics.UpdateAPIView):
    serializer_class = TRDFinalizarSerializer
    queryset = TablaRetencionDocumental.objects.all()
    
    def put(self, request, pk):
        trd_ingresada = pk
        confirm = request.query_params("confirm")
        trd = TablaRetencionDocumental.objects.filter(id_trd = trd_ingresada).first()
        series_subseries_unidad_org_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd = trd_ingresada).values()
        for i in series_subseries_unidad_org_trd:
            if i['cod_disposicion_final'] == None and i['digitalizacion_dis_final'] == None and i['tiempo_retencion_ag'] == None and i['tiempo_retencion_ac'] == None:
                return Response({'success': False, 'detail': 'No se encontró información relacionada a ese id'}, status=status.HTTP_403_FORBIDDEN)
            if i['digitalizacion_dis_final'] == None: 
                return Response({'success': False, 'detail': 'No se encontró información relacionada a ese id'}, status=status.HTTP_403_FORBIDDEN)
            if i['tiempo_retencion_ag'] == None:
                return Response({'success': False, 'detail': 'No se encontró información relacionada a ese id'}, status=status.HTTP_403_FORBIDDEN)
            if i['tiempo_retencion_ac'] == None:
                return Response({'success': False, 'detail': 'No se encontró información relacionada a ese id'}, status=status.HTTP_403_FORBIDDEN)
        ids_series_subseries_unidad_org_trd = [i['id_serie_subs_unidadorg_trd'] for i in series_subseries_unidad_org_trd]
        
        
        
        
        
         
