import copy
from datetime import datetime, timedelta
import json
from django.forms import ValidationError, model_to_dict
from django.db.models import Q
from django.db import transaction

from rest_framework import generics,status
from rest_framework.response import Response

from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD
from gestion_documental.models.expedientes_models import ExpedientesDocumentales, IndicesElectronicosExp
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.tca_models import CatSeriesUnidadOrgCCD_TRD_TCA
from gestion_documental.models.transferencias_documentales_models import TransferenciaExpediente, TransferenciasDocumentales
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD
from gestion_documental.serializers.expedientes_serializers import EliminacionAnexosSerializer
from gestion_documental.serializers.transferencias_documentales_serializers import CrearTransferenciaSerializer, ExpedienteSerializer, HistoricoTransferenciasSerializer, UnidadesOrganizacionalesSerializer, UpdateExpedienteSerializer
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied

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
                if key in ['cod_tipo_transferencia','fecha_transferenciaExp','id_persona_transfirio']:
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

class GetExpedientesTransferidos(generics.ListAPIView):
    serializer_class = ExpedienteSerializer
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_transferencia_documental):
        expedientes_transferidos = TransferenciaExpediente.objects.filter(id_transferencia_documental=id_transferencia_documental).values_list('id_expediente_documental', flat=True)
        if not expedientes_transferidos:
            raise NotFound('No se encontraron los expedientes transferidos para la transferencia elegida')
        expedientes_transferidos = self.queryset.filter(id_expediente_documental__in=list(expedientes_transferidos))
        serializador = self.serializer_class(expedientes_transferidos, many=True)
        return Response({'success':True, 'detail':'Se encontraron los siguientes expedientes para la transferencia elegida', 'data':serializador.data},status=status.HTTP_200_OK)

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
                condiciones &= Q(id_und_seccion_propietaria_serie=id_unidad_organizacional)
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
            catSeriesUnidadOrgCCDTRD = expediente.id_cat_serie_und_org_ccd_trd_prop
            indicesElectronicosExp = IndicesElectronicosExp.objects.all().filter(id_expediente_doc=expediente.id_expediente_documental).first()
            
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
    def get(self, request, id_expediente):
        try:
            id_persona_logueada = request.user.persona_id
            permisos = {}
            permisos['consulta'] = False
            permisos['descarga'] = False
            if id_expediente:
                expediente = ExpedientesDocumentales.objects.all().filter(id_expediente_documental = id_expediente).first()
                persona_logueada = Personas.objects.all().filter(id_persona = id_persona_logueada).first()
                unidad_persona_logueada = self.queryset_unidades.filter(id_unidad_organizacional = persona_logueada.id_unidad_organizacional_actual_id).first()
                organigrama_actual = Organigramas.objects.all().filter(actual = True).first()

                if organigrama_actual.id_organigrama == unidad_persona_logueada.id_organigrama_id:
                    if expediente.id_und_org_oficina_respon_actual_id == persona_logueada.id_unidad_organizacional_actual_id:
                        permisos['consulta'] = True
                        permisos['descarga'] = True

                    else:
                        permisos = self.validaciones_ctrl_acceso_clasificacionExp_CCD(expediente, unidad_persona_logueada)
                    
                    if permisos['consulta'] is False or permisos['descarga'] is False:
                        permisos = self.validacion_permisos_unds_org_actuales(expediente, unidad_persona_logueada.id_unidad_organizacional, permisos)
                else:
                   raise ValidationError("error': 'La unidad a la que pertenece el usuario logueado no es del organigrama actual.") 

            else:
                raise ValidationError("error': 'El expediente es necesario para obtener los permisos.")
            
            return Response({'success':True, 'detail':'Permisos de la persona logueada', 'data':permisos},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def validaciones_ctrl_acceso_clasificacionExp_CCD(self, expediente, unidad_persona_logueada):
        permisos = {}
        catSeriesUnidadOrgCCDTRD = CatSeriesUnidadOrgCCDTRD.objects.all().filter(id_catserie_unidadorg = expediente.id_cat_serie_und_org_ccd_trd_prop_id).first()
        ctrlAccesoClasificacionExpCCD = CtrlAccesoClasificacionExpCCD.objects.all().filter(id_cat_serie_und_org_ccd = catSeriesUnidadOrgCCDTRD.id_cat_serie_und_id).first()
        if ctrlAccesoClasificacionExpCCD:
            permisos = self.validaciones_ctrl_acceso_clasificacionExp_CCD_existe(ctrlAccesoClasificacionExpCCD, unidad_persona_logueada, expediente)
        else:
            permisos['consulta'] = False
            permisos['descarga'] = False
            id_ccd = catSeriesUnidadOrgCCDTRD.id_trd.id_ccd_id
            catSeriesUnidadOrgCCD_TRD_TCA = CatSeriesUnidadOrgCCD_TRD_TCA.objects.all().filter(id_cat_serie_und_ccd_trd = catSeriesUnidadOrgCCDTRD.id_catserie_unidadorg).first()

            if id_ccd and catSeriesUnidadOrgCCD_TRD_TCA:
                ctrlAccesoClasificacionExpCCD = CtrlAccesoClasificacionExpCCD.objects.all().filter(id_ccd = id_ccd, cod_clasificacion_exp = catSeriesUnidadOrgCCD_TRD_TCA.cod_clas_expediente_id).first()
                if ctrlAccesoClasificacionExpCCD:
                    permisos = self.validaciones_ctrl_acceso_clasificacionExp_CCD_existe(ctrlAccesoClasificacionExpCCD, unidad_persona_logueada, expediente)
        return permisos
    
    def validaciones_ctrl_acceso_clasificacionExp_CCD_existe(self, ctrlAccesoClasificacionExpCCD, unidad_persona_logueada, expediente):
        permisos = {}
        entidadEnteraConsultarDescargar = True if ctrlAccesoClasificacionExpCCD.entidad_entera_consultar is True or ctrlAccesoClasificacionExpCCD.entidad_entera_descargar is True else False
        if entidadEnteraConsultarDescargar:
                permisos['consulta'] = ctrlAccesoClasificacionExpCCD.entidad_entera_consultar
                permisos['descarga'] = ctrlAccesoClasificacionExpCCD.entidad_entera_descargar
        else:
            if unidad_persona_logueada.cod_agrupacion_documental:
                und_seccion_propietaria_serie = self.queryset_unidades.filter(id_unidad_organizacional = expediente.id_und_seccion_propietaria_serie_id).first()
                
                #Validación 1
                permisos = self.validate_seccionActualResponsable(ctrlAccesoClasificacionExpCCD, und_seccion_propietaria_serie, unidad_persona_logueada)
                
                #Validación 2
                if permisos['consulta'] is False or permisos['descarga'] is False:
                    permisos = self.validate_seccionRaizOrgActual(ctrlAccesoClasificacionExpCCD, unidad_persona_logueada, permisos)
                
                #Validación 3
                if permisos['consulta'] is False or permisos['descarga'] is False:
                    permisos = self.validate_seccionesActualesNivel(ctrlAccesoClasificacionExpCCD, und_seccion_propietaria_serie, unidad_persona_logueada.id_nivel_organigrama_id, permisos)
            
            #Validación 4
            if permisos['consulta'] is False or permisos['descarga'] is False:
                permisos = self.validate_unidades_hijas_y_nivel(ctrlAccesoClasificacionExpCCD, expediente.id_und_org_oficina_respon_actual_id, und_seccion_propietaria_serie, unidad_persona_logueada, permisos)
        
        return permisos
        
    def validate_seccionActualResponsable(self, ctrlAccesoClasificacionExpCCD, und_seccion_propietaria_serie, unidad_persona_logueada):
        permisos = {}
        permisos['consulta'] = False
        permisos['descarga'] = False
        validacionSeccionActualResponsable = True if und_seccion_propietaria_serie and und_seccion_propietaria_serie.id_unidad_org_actual_admin_series_id == unidad_persona_logueada.id_unidad_organizacional else False

        if validacionSeccionActualResponsable is True:
            permisos['consulta'] = ctrlAccesoClasificacionExpCCD.seccion_actual_respon_serie_doc_consultar
            permisos['descarga'] = ctrlAccesoClasificacionExpCCD.seccion_actual_respon_serie_doc_descargar

        return permisos
    
    def validate_seccionRaizOrgActual(self, ctrlAccesoClasificacionExpCCD, unidad_persona_logueada, permisos):
        permisos['consulta'] = permisos['consulta'] if permisos['consulta'] is True else False
        permisos['descarga'] = permisos['descarga'] if permisos['descarga'] is True else False

        if unidad_persona_logueada.unidad_raiz is True:
            permisos['consulta'] = ctrlAccesoClasificacionExpCCD.seccion_raiz_organi_actual_consultar if permisos['consulta'] is False else permisos['consulta']
            permisos['descarga'] = ctrlAccesoClasificacionExpCCD.seccion_raiz_organi_actual_descargar if permisos['descarga'] is False else permisos['descarga']

        return permisos
    
    def validate_seccionesActualesNivel(self, ctrlAccesoClasificacionExpCCD, und_seccion_propietaria_serie, id_nivel_organigrama_persona_logueada, permisos):
        permisos['consulta'] = permisos['consulta'] if permisos['consulta'] is True else False
        permisos['descarga'] = permisos['descarga'] if permisos['descarga'] is True else False
        
        und_org_actual_admin_series = self.queryset_unidades.filter(id_unidad_organizacional = und_seccion_propietaria_serie.id_unidad_org_actual_admin_series_id).first()
        nivel_organigrama_actual_admin_series = NivelesOrganigrama.objects.all().filter(id_nivel_organigrama = und_org_actual_admin_series.id_nivel_organigrama_id).first()
        nivel_organigrama_persona_logueada = NivelesOrganigrama.objects.all().filter(id_nivel_organigrama = id_nivel_organigrama_persona_logueada).first()
        nivel_igual_superior = True if nivel_organigrama_persona_logueada.orden_nivel <= nivel_organigrama_actual_admin_series.orden_nivel else False
        nivel_inferior = True if nivel_organigrama_persona_logueada.orden_nivel > nivel_organigrama_actual_admin_series.orden_nivel else False
        
        
        if nivel_igual_superior is True or nivel_inferior is True:
            consultar = True if ctrlAccesoClasificacionExpCCD.secciones_actuales_mismo_o_sup_nivel_respon_consulta is True or ctrlAccesoClasificacionExpCCD.secciones_actuales_inf_nivel_respon_consultar is True else permisos['consulta']
            descargar = True if ctrlAccesoClasificacionExpCCD.secciones_actuales_mismo_o_sup_nivel_respon_descargar is True or ctrlAccesoClasificacionExpCCD.secciones_actuales_inf_nivel_respon_descargar is True else permisos['descarga']
            permisos['consulta'] = consultar
            permisos['descarga'] = descargar

        return permisos
    
    def validate_unidades_hijas_y_nivel(self, ctrlAccesoClasificacionExpCCD, id_und_org_oficina_respon_actual, und_seccion_propietaria_serie, unidad_persona_logueada, permisos):
        permisos['consulta'] = permisos['consulta'] if permisos['consulta'] is True else False
        permisos['descarga'] = permisos['descarga'] if permisos['descarga'] is True else False

        und_org_oficina_respon_actual = self.queryset_unidades.filter(id_unidad_organizacional = id_und_org_oficina_respon_actual).first()
        nivel_organigrama_actual_resp_act = NivelesOrganigrama.objects.all().filter(id_nivel_organigrama = und_org_oficina_respon_actual.id_nivel_organigrama_id).first()
        nivel_organigrama_persona_logueada = NivelesOrganigrama.objects.all().filter(id_nivel_organigrama = unidad_persona_logueada.id_nivel_organigrama_id).first()
        nivel_igual_superior = True if nivel_organigrama_persona_logueada.orden_nivel <= nivel_organigrama_actual_resp_act.orden_nivel else False
        nivel_inferior = True if nivel_organigrama_persona_logueada.orden_nivel > nivel_organigrama_actual_resp_act.orden_nivel else False
        
        validar_nivel = nivel_igual_superior is True or nivel_inferior is True
        validate_und_hijas = self.validate_unidades_hijas(und_seccion_propietaria_serie.id_unidad_organizacional, unidad_persona_logueada.id_unidad_organizacional)
        
        if validar_nivel is True and validate_und_hijas is True:
            consultar = True if ctrlAccesoClasificacionExpCCD.unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_consultar is True or ctrlAccesoClasificacionExpCCD.unds_org_sec_respon_inf_nivel_resp_exp_consultar is True else permisos['consulta']
            descargar = True if ctrlAccesoClasificacionExpCCD.unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_descargar is True or ctrlAccesoClasificacionExpCCD.unds_org_sec_respon_inf_nivel_resp_exp_descargar is True else permisos['descarga']
            permisos['consulta'] = consultar
            permisos['descarga'] = descargar
            
    
        return permisos
    
    def validate_unidades_hijas(self, id_unidad_org_padre, id_und_org_hijo):
        validate = False
        if id_und_org_hijo:
            hijo = self.queryset_unidades.filter(id_unidad_organizacional = id_und_org_hijo).first()
            if hijo.id_unidad_org_padre and hijo.id_unidad_org_padre_id == id_unidad_org_padre:
                validate = True
            else:
                self.validate_unidades_hijas(id_unidad_org_padre, hijo.id_unidad_org_padre_id)
        return validate

    def validacion_permisos_unds_org_actuales(self, expediente, id_unidad_organizacional_persona_logueada, permisos):
        catSeriesUnidadOrgCCDTRD = CatSeriesUnidadOrgCCDTRD.objects.all().filter(id_catserie_unidadorg = expediente.id_cat_serie_und_org_ccd_trd_prop_id).first()
        permisosUndsOrgActualesSerieExpCCD = PermisosUndsOrgActualesSerieExpCCD.objects.all().filter(id_cat_serie_und_org_ccd = catSeriesUnidadOrgCCDTRD.id_cat_serie_und_id, id_und_organizacional_actual = id_unidad_organizacional_persona_logueada).first()
        
        if permisosUndsOrgActualesSerieExpCCD:
            permisos['consulta'] = permisosUndsOrgActualesSerieExpCCD.consultar_expedientes_no_propios if permisos['consulta'] is False else permisos['consulta']
            permisos['descarga'] = permisosUndsOrgActualesSerieExpCCD.descargar_expedientes_no_propios if permisos['descarga'] is False else permisos['descarga']

        return permisos
    
class CreateTransferencia(generics.CreateAPIView):
    serializer_class = CrearTransferenciaSerializer
    serializer_expediente_class = UpdateExpedienteSerializer
    serializer_class_anexos = EliminacionAnexosSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                expedientes = request.data.get('expedientes', [])
                cod_tipo_transferencia = request.data.get('cod_tipo_transferencia')
                anexos = request.data.get('anexos')
                fecha_actual = datetime.now()
                
                output_data = {}

                if expedientes:
                    transferencia = self.create_transferencia_documental(cod_tipo_transferencia, request.user.persona_id, fecha_actual, len(expedientes))
                    output_data = model_to_dict(transferencia)
                    output_data['expedientes'] = []
                    for expediente in expedientes:
                        expediente_bd = ExpedientesDocumentales.objects.all().filter(id_expediente_documental=expediente).first()
                        if not expediente_bd:
                            raise ValidationError('El expediente no existe')
                        transferencia_exp = TransferenciaExpediente.objects.create(
                            id_transferencia_documental = transferencia,
                            id_expediente_documental = expediente_bd
                        )
                        output_data['expedientes'].append(model_to_dict(transferencia_exp))
                    
                    anexos = self.create_anexos(anexos, transferencia)
                    output_data['anexos'] = anexos
                else:
                    raise ValidationError('Los expedientes son necesarios para crear las transferencias')
                
                return Response({'success':True, 'detail':'Los expedientes seleccionados han sido transferidos correctamente', 'data':output_data},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create_transferencia_documental(self, cod_tipo_transferencia, id_persona_guarda, fecha_actual, nro_expedientes_transferidos):
        crear_transferencia = self.set_data_tipo_primaria(cod_tipo_transferencia, id_persona_guarda, fecha_actual, nro_expedientes_transferidos)
        serializer = self.serializer_class(data=crear_transferencia)
        serializer.is_valid(raise_exception=True)
        transferencia = serializer.save()
        return transferencia
    
    def create_anexos(self, anexos, transferencia):
        serializer_anexos_data = []
        if anexos:
            for anexo in anexos:
                data_anexo = {}
                data_anexo['id_transferencia_documental'] = transferencia.id_transferencia_documental
                data_anexo['id_documento_archivo_exp'] = anexo
                
                serializer_anexos = self.serializer_class_anexos(data=data_anexo)
                serializer_anexos.is_valid(raise_exception=True)
                serializer_anexos.save()
                
                serializer_anexos_data.append(serializer_anexos.data)
        return serializer_anexos_data
    
    def set_data_tipo_primaria(self, cod_tipo_transferencia, id_persona_guarda, fecha_actual, nro_expedientes_transferidos):
        crear_transferencia = {}
        crear_transferencia['id_persona_transfirio'] = id_persona_guarda
        crear_transferencia['cod_tipo_transferencia'] = cod_tipo_transferencia
        crear_transferencia['fecha_transferenciaExp'] = fecha_actual
        crear_transferencia['nro_expedientes_transferidos'] = nro_expedientes_transferidos
        return crear_transferencia
    
    def update_expediente(self, expediente, cod_tipo_transferencia, fecha_actual):
        expediente_instance = copy.copy(expediente)
        
        expediente.cod_etapa_de_archivo_actual_exped = "C" if cod_tipo_transferencia == "P" else "H"
        expediente.fecha_paso_a_archivo_central = fecha_actual
        expediente.ubicacion_fisica_esta_actualizada = False
            
        expediente_dic = model_to_dict(expediente)
        serializer = self.serializer_expediente_class(expediente_instance, data=expediente_dic)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        


