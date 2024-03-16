from almacen.choices.estados_articulo_choices import estados_articulo_CHOICES
from almacen.choices.magnitudes_choices import magnitudes_CHOICES
from almacen.choices.tipo_combustible_choices import tipo_combustible_CHOICES
from almacen.choices.tipo_documento_choices import tipo_documento_CHOICES
from almacen.choices.tipo_mantenimiento_choices import tipo_mantenimiento_CHOICES
from almacen.choices.tipo_vehiculo_choices import tipo_vehiculo_CHOICES
from almacen.choices.cod_tipo_bien_choices import cod_tipo_bien_CHOICES
from almacen.choices.tipo_doc_ultimo_choices import tipo_doc_ultimo_CHOICES
from almacen.choices.metodos_valoracion_articulos_choices import metodos_valoracion_articulos_CHOICES
from almacen.choices.tipos_activo_choices import tipos_activo_CHOICES
from almacen.choices.tipos_depreciacion_activos_choices import tipos_depreciacion_activos_CHOICES
from almacen.choices.estado_aprobacion_choices import estado_aprobacion_CHOICES
from almacen.choices.cod_tipo_elemento_vivero_choices import cod_tipo_elemento_vivero_CHOICES
from almacen.choices.estado_solicitud_choices import estado_solicitud_CHOICES
from almacen.choices.tipo_conductor_choices import tipo_conductor_CHOICES
from almacen.choices.estado_solicitud_activo_choices import estado_solicitud_activo_CHOICES
from almacen.choices.estado_aprobacion_activo_choices import estado_aprobacion_activo_CHOICES
from almacen.choices.estado_despacho_choices import estado_despacho_CHOICES

tipo_conductor_CHOICES
from rest_framework.views import APIView
from rest_framework.response import Response
    
class EstadosArticuloChoices(APIView):
    def get(self,request):
        choices = estados_articulo_CHOICES
        return Response(choices)

class MagnitudesChoices(APIView):
    def get(self,request):
        choices = magnitudes_CHOICES
        return Response(choices)

class TipoCombustibleChoices(APIView):
    def get(self,request):
        choices = tipo_combustible_CHOICES
        return Response(choices)

class TipoDocumentoChoices(APIView):
    def get(self,request):
        choices = tipo_documento_CHOICES
        return Response(choices)

class TipoMantenimientoChoices(APIView):
    def get(self,request):
        choices = tipo_mantenimiento_CHOICES
        return Response(choices)

class TipoVehiculoChoices(APIView):
    def get(self,request):
        choices = tipo_vehiculo_CHOICES
        return Response(choices)

class TipoBienChoices(APIView):
    def get(self,request):
        choices = cod_tipo_bien_CHOICES
        return Response(choices)

class TipoDocUltimoChoices(APIView):
    def get(self,request):
        choices = tipo_doc_ultimo_CHOICES
        return Response(choices)

class MetodoValoracionChoices(APIView):
    def get(self,request):
        choices = metodos_valoracion_articulos_CHOICES
        return Response(choices)

class TipoActivoChoices(APIView):
    def get(self,request):
        choices = tipos_activo_CHOICES
        return Response(choices)

class TipoDepreciacionActivos(APIView):
    def get(self,request):
        choices = tipos_depreciacion_activos_CHOICES
        return Response(choices)

class EstadoAprobacionChoices(APIView):
    def get(self,request):
        choices = estado_aprobacion_CHOICES
        return Response(choices)

class CodTipoElementoViveroChoices(APIView):
    def get(self,request):
        choices = cod_tipo_elemento_vivero_CHOICES
        return Response(choices)
    

class EstadoSolicitudChoices(APIView):
    def get(self,request):
        choices = estado_solicitud_CHOICES
        return Response(choices)
    
class TipoConductorChoices(APIView):
    def get(self,request):
        choices = tipo_conductor_CHOICES
        return Response(choices)
    
class EstadoSolicitudActivo(APIView):
    def get(self,request):
        choices = estado_solicitud_activo_CHOICES
        return Response(choices)
    

class EstadoAprobacionActivo(APIView):
    def get(self,request):
        choices = estado_aprobacion_activo_CHOICES
        return Response(choices)
    

class EstadoDespacho(APIView):
    def get(self,request):
        choices = estado_despacho_CHOICES
        return Response(choices)