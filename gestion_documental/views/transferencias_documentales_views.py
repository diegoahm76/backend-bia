from datetime import datetime, timedelta
from django.forms import ValidationError
from rest_framework import generics,status
from rest_framework.response import Response
from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD
from gestion_documental.models.expedientes_models import ExpedientesDocumentales, IndicesElectronicosExp
from django.db.models import Q

from gestion_documental.models.transferencias_documentales_models import TransferenciasDocumentales
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD
from gestion_documental.serializers.transferencias_documentales_serializers import ExpedienteSerializer, HistoricoTransferenciasSerializer, UnidadesOrganizacionalesSerializer
from seguridad.signals.roles_signals import IsAuthenticated
from transversal.models.organigrama_models import UnidadesOrganizacionales
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

    def get(self, request):
        try:
            id_persona_logueada = request.user.id_persona
            expediente = request.query_params.get('expediente', None)
            permisos = {}
            permisos['consulta'] = False
            permisos['descarga'] = False
            if expediente:
                persona_logueada = Personas.objects.all().filter(id_persona = id_persona_logueada).first()
                if expediente['id_und_org_oficina_respon_actual'] == persona_logueada.es_unidad_organizacional_actual_id:
                    permisos['consulta'] = True
                    permisos['descarga'] = True

                else:
                    ctrlAccesoClasificacionExpCCD = CtrlAccesoClasificacionExpCCD.objects.all().filter(id_cat_serie_und_org_ccd = expediente['id_cat_serie_und_org_ccd_trd_prop']).first()
                    if ctrlAccesoClasificacionExpCCD:
                        if ctrlAccesoClasificacionExpCCD.entidad_entera_consultar or ctrlAccesoClasificacionExpCCD.entidad_entera_descargar:
                            permisos['consulta'] = ctrlAccesoClasificacionExpCCD.entidad_entera_consultar
                            permisos['descarga'] = ctrlAccesoClasificacionExpCCD.entidad_entera_descargar
                        else:
                            pass
                    else:
                        pass

            else:
                raise ValidationError("error': 'El expediente es necesario para obtener los permisos.")
            
            return Response({'success':True, 'detail':'Permisos de la persona logueada', 'data':permisos},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


