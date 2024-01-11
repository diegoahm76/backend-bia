from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# IMPORT LISTS
from tramites.lists.cod_tipo_operacion_tramite_list import cod_tipo_operacion_tramite_LIST
from tramites.lists.cod_tipo_predio_list import cod_tipo_predio_LIST
from tramites.lists.cod_clasificacion_territorial_list import cod_clasificacion_territorial_LIST
from tramites.lists.cod_tipo_calidad_persona_list import cod_tipo_calidad_persona_LIST
from tramites.lists.cod_tipo_permiso_ambiental_list import cod_tipo_permiso_ambiental_LIST
from tramites.lists.cod_tipo_desistimiento_list import cod_tipo_desistimiento_LIST
from tramites.lists.cod_tipo_solicitud_al_requerimiento_list import cod_tipo_solicitud_al_requerimiento_LIST
from tramites.lists.cod_calendario_habiles_list import cod_calendario_habiles_LIST
from tramites.lists.cod_tipo_solicitud_juridica_list import cod_tipo_solicitud_juridica_LIST
from tramites.lists.cod_estado_solicitud_juridica_list import cod_estado_solicitud_juridica_LIST
from gestion_documental.choices.tipo_radicado_choices import cod_tipos_radicados_LIST

class GetListCodTipoOperacionTramite(APIView):
    def get(self, request):
        return Response(cod_tipo_operacion_tramite_LIST, status=status.HTTP_200_OK)
    
class GetListCodTipoPredio(APIView):
    def get(self, request):
        return Response(cod_tipo_predio_LIST, status=status.HTTP_200_OK)
    
class GetListCodClasificacionTerritorial(APIView):
    def get(self, request):
        return Response(cod_clasificacion_territorial_LIST, status=status.HTTP_200_OK)
    
class GetListCodTipoCalidadPersona(APIView):
    def get(self, request):
        return Response(cod_tipo_calidad_persona_LIST, status=status.HTTP_200_OK)
    
class GetListCodTipoPermisoAmbiental(APIView):
    def get(self, request):
        return Response(cod_tipo_permiso_ambiental_LIST, status=status.HTTP_200_OK)
    
class GetListCodTipoDesistimiento(APIView):
    def get(self, request):
        return Response(cod_tipo_desistimiento_LIST, status=status.HTTP_200_OK)
    
class GetListCodTipoSolicitudAlRequerimiento(APIView):
    def get(self, request):
        return Response(cod_tipo_solicitud_al_requerimiento_LIST, status=status.HTTP_200_OK)
    
class GetListCodCalendarioHabiles(APIView):
    def get(self, request):
        return Response(cod_calendario_habiles_LIST, status=status.HTTP_200_OK)
    
class GetListCodTipoSolicitudJuridica(APIView):
    def get(self, request):
        return Response(cod_tipo_solicitud_juridica_LIST, status=status.HTTP_200_OK)
    
class GetListCodEstadoSolicitudJuridica(APIView):
    def get(self, request):
        return Response(cod_estado_solicitud_juridica_LIST, status=status.HTTP_200_OK)
    
class GetListTiposRadicado(APIView):
    def get(self, request):
        return Response(cod_tipos_radicados_LIST, status=status.HTTP_200_OK)