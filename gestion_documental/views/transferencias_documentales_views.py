from datetime import datetime, timedelta
from django.forms import ValidationError
from rest_framework import generics,status
from rest_framework.response import Response
from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD
from gestion_documental.models.expedientes_models import ExpedientesDocumentales, IndicesElectronicosExp
from django.db.models import Q
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD

from gestion_documental.models.transferencias_documentales_models import TransferenciasDocumentales
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD
from gestion_documental.serializers.transferencias_documentales_serializers import ExpedienteSerializer, HistoricoTransferenciasSerializer, UnidadesOrganizacionalesSerializer
from seguridad.signals.roles_signals import IsAuthenticated
from transversal.models.organigrama_models import NivelesOrganigrama, Organigramas, UnidadesOrganizacionales
from transversal.models.personas_models import Personas

class GetUnidadesOrganizacionales(generics.ListAPIView):
    serializer_class = UnidadesOrganizacionalesSerializer

    def get(self, request):
        unidades = UnidadesOrganizacionales.objects.all()
        serializador = self.serializer_class(unidades, many = True)
        return Response({'success':True, 'detail':'Se encontraron las siguientes unidades organizacionales', 'data':serializador.data},status=status.HTTP_200_OK)


class GetHistoricoTransferencias(generics.ListAPIView):
    serializer_class = HistoricoTransferenciasSerializer
    queryset = TransferenciasDocumentales.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            filter = {}
            for key,value in request.query_params.items():
                if key in ['cod_tipo_transferencia','id_unidad_org_propietaria','fecha_transferenciaExp','id_persona_transfirio']:
                    if key == "fecha_transferenciaExp":
                        if value != "":
                            filter[key+'__contains'] = value
                    else:
                        if value != "":
                            filter[key] = value

            transferencias = self.queryset.filter(**filter)
            serializador = self.serializer_class(transferencias, many = True)
            return Response({'success':True, 'detail':'Se encontraron las siguientes transferencias', 'data':serializador.data},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetExpedientesATransferir(generics.ListAPIView):
    serializer_class = ExpedienteSerializer
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            tipo_transferencia = request.query_params.get('tipo_transferencia', None)
            id_unidad_organizacional = request.query_params.get('id_unidad_organizacional', None)
            cod_disposicion_final = request.query_params.get('cod_disposicion_final', None)

            condiciones = Q(estado = "C")
            if id_unidad_organizacional:
                condiciones &= ~Q(id_und_seccion_propietaria_serie=id_unidad_organizacional)
            expedientes_filtrados = self.queryset.filter(condiciones)
            expedientes_transferir = self.get_expedientes_transferir(expedientes_filtrados, tipo_transferencia, cod_disposicion_final)
            serializador = self.serializer_class(expedientes_transferir, many = True)
            return Response({'success':True, 'detail':'Se encontraron los siguientes expedientes para transferir', 'data':serializador.data},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)   
    
    def get_expedientes_transferir(self, expedientes, tipo_transferencia, cod_disposicion_final):
        expedientes_transferir = []
        fecha_actual = datetime.now()
        for expediente in expedientes:
            catSeriesUnidadOrgCCDTRD = CatSeriesUnidadOrgCCDTRD.objects.all().filter(id_catserie_unidadorg = expediente.id_cat_serie_und_org_ccd_trd_prop_id).first()
            indicesElectronicosExp = IndicesElectronicosExp.objects.all().filter(id_expediente_doc = expediente.id_expediente_documental).first()
            
            if cod_disposicion_final and catSeriesUnidadOrgCCDTRD.cod_disposicion_final_id != cod_disposicion_final:
                continue

            if tipo_transferencia == "P":
                tiempo_retencion = expediente.fecha_cierre_reapertura_actual + timedelta(days=catSeriesUnidadOrgCCDTRD.tiempo_retencion_ag)
                if fecha_actual > tiempo_retencion and indicesElectronicosExp.abierto == False:
                    expedientes_transferir.append(expediente)
            else:
                transferencia_documental = TransferenciasDocumentales.objects.all().filter(id_expedienteDoc = expediente.id_expediente_documental).first()
                if transferencia_documental:
                    tiempo_retencion = transferencia_documental.fecha_transferenciaExp + timedelta(days=catSeriesUnidadOrgCCDTRD.tiempo_retencion_ac)
                    if fecha_actual > tiempo_retencion and indicesElectronicosExp.abierto == False and expediente.cod_etapa_de_archivo_actual_exped == "C":
                        expedientes_transferir.append(expediente)

        return expedientes_transferir
    
class GetPermisosUsuario(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset_unidades = UnidadesOrganizacionales.objects.all()
    def get(self, request):
        try:
            id_persona_logueada = request.user.id_persona
            expediente = request.query_params.get('expediente', None)
            permisos = {}
            permisos['consulta'] = False
            permisos['descarga'] = False
            if expediente:
                persona_logueada = Personas.objects.all().filter(id_persona = id_persona_logueada).first()
                unidad_persona_logueada = self.queryset_unidades.filter(id_unidad_organizacional = persona_logueada.es_unidad_organizacional_actual_id).first()
                organigrama_actual = Organigramas.objects.all().filter(actual = True).first()

                if organigrama_actual.id_organigrama == unidad_persona_logueada.id_organigrama_id:
                    if expediente['id_und_org_oficina_respon_actual'] == persona_logueada.es_unidad_organizacional_actual_id:
                        permisos['consulta'] = True
                        permisos['descarga'] = True

                    else:
                        permisos = self.validaciones_ctrl_acceso_clasificacionExp_CCD(expediente, unidad_persona_logueada, organigrama_actual)
                    
                    if permisos['consultar'] is False and permisos['descarga'] is False:
                        permisos = self.validacion_permisos_unds_org_actuales(expediente, unidad_persona_logueada.id_unidad_organizacional)
                else:
                   raise ValidationError("error': 'La unidad a la que pertenece el usuario logueado no es del organigrama actual.") 

            else:
                raise ValidationError("error': 'El expediente es necesario para obtener los permisos.")
            
            return Response({'success':True, 'detail':'Permisos de la persona logueada', 'data':permisos},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def validaciones_ctrl_acceso_clasificacionExp_CCD(self, expediente, unidad_persona_logueada, organigrama_actual):
        permisos = {}
        catSeriesUnidadOrgCCDTRD = CatSeriesUnidadOrgCCDTRD.objects.all().filter(id_catserie_unidadorg = expediente['id_cat_serie_und_org_ccd_trd_prop']).first()
        ctrlAccesoClasificacionExpCCD = CtrlAccesoClasificacionExpCCD.objects.all().filter(id_cat_serie_und_org_ccd = catSeriesUnidadOrgCCDTRD.id_cat_serie_und).first()
        if ctrlAccesoClasificacionExpCCD:
            permisos = self.validaciones_ctrl_acceso_clasificacionExp_CCD_existe(ctrlAccesoClasificacionExpCCD, unidad_persona_logueada, expediente, organigrama_actual)
        else:
            pass
            
        return permisos
    
    def validaciones_ctrl_acceso_clasificacionExp_CCD_existe(self, ctrlAccesoClasificacionExpCCD, unidad_persona_logueada, expediente, organigrama_actual):
        permisos = {}
        entidadEnteraConsultarDescargar = True if ctrlAccesoClasificacionExpCCD.entidad_entera_consultar is True or ctrlAccesoClasificacionExpCCD.entidad_entera_descargar is True else False
        if entidadEnteraConsultarDescargar:
                permisos['consulta'] = ctrlAccesoClasificacionExpCCD.entidad_entera_consultar
                permisos['descarga'] = ctrlAccesoClasificacionExpCCD.entidad_entera_descargar
        else:
            if unidad_persona_logueada.cod_agrupacion_documental:
                und_seccion_propietaria_serie = self.queryset_unidades.filter(id_unidad_organizacional = expediente['id_und_seccion_propietaria_serie']).first()
                
                #Validación 1
                permisos = self.validate_seccionActualResponsable(ctrlAccesoClasificacionExpCCD, und_seccion_propietaria_serie, unidad_persona_logueada)
                
                #Validación 2
                if permisos['consulta'] is False or permisos['descarga'] is False:
                    permisos = self.validate_seccionRaizOrgActual(ctrlAccesoClasificacionExpCCD, unidad_persona_logueada, permisos)
                
                #Validación 3
                if permisos['consulta'] is False or permisos['descarga'] is False:
                    permisos = self.validate_seccionesActualesNivel(ctrlAccesoClasificacionExpCCD, und_seccion_propietaria_serie, organigrama_actual.id_organigrama, unidad_persona_logueada.id_nivel_organigrama_id, permisos)
            
            #Validación 4
            if permisos['consulta'] is False or permisos['descarga'] is False:
                permisos = self.validate_unidadesHijas(expediente['id_und_org_oficina_respon_actual'], und_seccion_propietaria_serie, permisos)
        
        return permisos
        
    def validate_seccionActualResponsable(self, ctrlAccesoClasificacionExpCCD, und_seccion_propietaria_serie, unidad_persona_logueada):
        permisos = {}
        permisos['consulta'] = False
        permisos['descarga'] = False
        validacionSeccionActualResponsable = True if und_seccion_propietaria_serie and und_seccion_propietaria_serie.id_unidad_org_actual_admin_series == unidad_persona_logueada.id_unidad_organizacional else False

        if validacionSeccionActualResponsable is True:
            permisos['consulta'] = ctrlAccesoClasificacionExpCCD.seccion_actual_respon_serie_doc_consultar
            permisos['descarga'] = ctrlAccesoClasificacionExpCCD.seccion_actual_respon_serie_doc_descargar

        return permisos
    
    def validate_seccionRaizOrgActual(self, ctrlAccesoClasificacionExpCCD, unidad_persona_logueada, permisos):
        #TODO: CUADRAR PARA QUE SI YA TENGO UNO DE LOS PERMISOS EN TRUE NO SE PIERDA ESTE DATO SINO QUE SOLO SE SETEE EL FALSE
        permisos = {}
        permisos['consulta'] = False
        permisos['descarga'] = False

        if unidad_persona_logueada.unidad_raiz is True:
            permisos['consulta'] = ctrlAccesoClasificacionExpCCD.seccion_raiz_organi_actual_consultar
            permisos['descarga'] = ctrlAccesoClasificacionExpCCD.seccion_raiz_organi_actual_descargar

        return permisos
    
    def validate_seccionesActualesNivel(self, ctrlAccesoClasificacionExpCCD, und_seccion_propietaria_serie, id_organigrama, id_nivel_organigrama_persona_logueada, permisos):
        #TODO: CUADRAR PARA QUE SI YA TENGO UNO DE LOS PERMISOS EN TRUE NO SE PIERDA ESTE DATO SINO QUE SOLO SE SETEE EL FALSE
        permisos = {}
        permisos['consulta'] = False
        permisos['descarga'] = False
        
        und_org_actual_admin_series = self.queryset_unidades.filter(id_unidad_organizacional = und_seccion_propietaria_serie.id_unidad_org_actual_admin_series).first()
        nivel_organigrama_actual_admin_series = NivelesOrganigrama.objects.all().filter(id_nivel_organigrama = und_org_actual_admin_series.id_nivel_organigrama_id).first()
        nivel_organigrama_persona_logueada = NivelesOrganigrama.objects.all().filter(id_nivel_organigrama = id_nivel_organigrama_persona_logueada).first()
        nivel_igual_superior = True if nivel_organigrama_persona_logueada.orden_nivel <= nivel_organigrama_actual_admin_series.orden_nivel else False
        nivel_inferior = True if nivel_organigrama_persona_logueada.orden_nivel > nivel_organigrama_actual_admin_series.orden_nivel else False
        
        
        if nivel_igual_superior is True or nivel_inferior is True:
            consultar = True if ctrlAccesoClasificacionExpCCD.secciones_actuales_mismo_o_sup_nivel_respon_consulta is True or ctrlAccesoClasificacionExpCCD.secciones_actuales_inf_nivel_respon_consultar else False
            descargar = True if ctrlAccesoClasificacionExpCCD.secciones_actuales_mismo_o_sup_nivel_respon_descargar is True or ctrlAccesoClasificacionExpCCD.secciones_actuales_inf_nivel_respon_descargar is True else False
            permisos['consulta'] = consultar
            permisos['descarga'] = descargar

        return permisos
    
    def validate_unidadesHijas(self, id_und_org_oficina_respon_actual, und_seccion_propietaria_serie, permisos):
        #TODO: Validación pendiente
        #TODO: CUADRAR PARA QUE SI YA TENGO UNO DE LOS PERMISOS EN TRUE NO SE PIERDA ESTE DATO SINO QUE SOLO SE SETEE EL FALSE
        pass

    def validacion_permisos_unds_org_actuales(self, expediente, id_unidad_organizacional_persona_logueada):
        permisos = {}
        catSeriesUnidadOrgCCDTRD = CatSeriesUnidadOrgCCDTRD.objects.all().filter(id_catserie_unidadorg = expediente['id_cat_serie_und_org_ccd_trd_prop'])
        permisosUndsOrgActualesSerieExpCCD = PermisosUndsOrgActualesSerieExpCCD.objects.all().filter(id_cat_serie_und_org_ccd = catSeriesUnidadOrgCCDTRD.id_cat_serie_und_id, id_und_organizacional_actual = id_unidad_organizacional_persona_logueada).first()
        permisos['consulta'] = permisosUndsOrgActualesSerieExpCCD.consultar_expedientes_no_propios
        permisos['descarga'] = permisosUndsOrgActualesSerieExpCCD.descargar_expedientes_no_propios

        return permisos
        


