from datetime import datetime, timedelta
from rest_framework import generics,status
from rest_framework.response import Response
from gestion_documental.models.expedientes_models import ExpedientesDocumentales, IndicesElectronicosExp
from django.db.models import Q

from gestion_documental.models.transferencias_documentales_models import TransferenciasDocumentales
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD
from gestion_documental.serializers.transferencias_documentales_serializers import ExpedienteSerializer, HistoricoTransferenciasSerializer, UnidadesOrganizacionalesSerializer
from seguridad.signals.roles_signals import IsAuthenticated
from transversal.models.organigrama_models import UnidadesOrganizacionales

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

            condiciones = Q(estado = "C")
            if id_unidad_organizacional:
                condiciones &= ~Q(id_und_seccion_propietaria_serie=id_unidad_organizacional)
            expedientes_filtrados = self.queryset.filter(condiciones)
            expedientes_transferir = self.get_expedientes_transferir(expedientes_filtrados, tipo_transferencia)
            serializador = self.serializer_class(expedientes_transferir, many = True)
            return Response({'success':True, 'detail':'Se encontraron los siguientes expedientes para transferir', 'data':serializador.data},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def get_expedientes_transferir(self, expedientes, tipo_transferencia):
        expedientes_transferir = []
        fecha_actual = datetime.now()
        for expediente in expedientes:
            catSeriesUnidadOrgCCDTRD = CatSeriesUnidadOrgCCDTRD.objects.all().filter(id_catserie_unidadorg = expediente.id_cat_serie_und_org_ccd_trd_prop_id).first()
            indicesElectronicosExp = IndicesElectronicosExp.objects.all().filter(id_expediente_doc = expediente.id_expediente_documental).first()
            if tipo_transferencia == "P":
                tiempo_retencion = expediente.fecha_apertura_expediente + timedelta(days=catSeriesUnidadOrgCCDTRD.tiempo_retencion_ag)
                if fecha_actual > tiempo_retencion and indicesElectronicosExp.abierto == False:
                    expedientes_transferir.append(expediente)
            else:
                tiempo_retencion = expediente.fecha_apertura_expediente + timedelta(days=catSeriesUnidadOrgCCDTRD.tiempo_retencion_ac)
                if fecha_actual > tiempo_retencion and indicesElectronicosExp.abierto == False and expediente.cod_etapa_de_archivo_actual_exped == "C":
                    expedientes_transferir.append(expediente)

        return expedientes_transferir
