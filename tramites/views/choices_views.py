from tramites.choices.cod_tipo_operacion_tramite_choices import cod_tipo_operacion_tramite_CHOICES
from tramites.choices.cod_calendario_habiles_choices import cod_calendario_habiles_CHOICES
from tramites.choices.cod_tipo_permiso_ambiental_choices import cod_tipo_permiso_ambiental_CHOICES
from tramites.choices.estado_solicitud_tramite_choices import estado_solicitud_tramite_CHOICES

from rest_framework.views import APIView
from rest_framework.response import Response

class CodTipoOperacionTramiteChoices(APIView):
    def get(self,request):
        choices = cod_tipo_operacion_tramite_CHOICES
        return Response(choices)

class CodCalendarioHabilesChoices(APIView):
    def get(self,request):
        choices = cod_calendario_habiles_CHOICES
        return Response(choices)

class CodTipoPermisoAmbientalChoices(APIView):
    def get(self,request):
        choices = cod_tipo_permiso_ambiental_CHOICES
        return Response(choices)
    
class EstadoSolicitudTramite(APIView):
    def get(self,request):
        choices = estado_solicitud_tramite_CHOICES
        return Response(choices)