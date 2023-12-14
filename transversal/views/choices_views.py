from transversal.choices.agrupacion_documental_choices import agrupacion_documental_CHOICES
from transversal.choices.tipo_unidad_choices import tipo_unidad_CHOICES
from transversal.choices.departamentos_choices import departamentos_CHOICES
from transversal.choices.municipios_choices import municipios_CHOICES
from transversal.choices.paises_choices import paises_CHOICES
from transversal.choices.indicativo_paises_choices import indicativo_paises_CHOICES
from transversal.choices.sexo_choices import sexo_CHOICES
from transversal.choices.estado_civil_choices import estado_civil_CHOICES
from transversal.choices.tipo_documento_choices import tipo_documento_CHOICES
from transversal.choices.tipo_persona_choices import tipo_persona_CHOICES
from transversal.choices.cod_naturaleza_empresa_choices import cod_naturaleza_empresa_CHOICES
from transversal.choices.tipo_direccion_choices import tipo_direccion_CHOICES

from rest_framework.views import APIView
from rest_framework.response import Response

class TipoUnidadChoices(APIView):
    def get(self,request):
        choices = tipo_unidad_CHOICES
        return Response(choices)

class AgrupacionDocumentalChoices(APIView):
    def get(self,request):
        choices = agrupacion_documental_CHOICES
        return Response(choices)
    
class DepartamentosChoices(APIView):
    def get(self,request):
        choices = departamentos_CHOICES
        return Response(choices)
    
class MunicipiosChoices(APIView):
    def get(self,request):
        choices = municipios_CHOICES
        return Response(choices)
    
class PaisesChoices(APIView):
    def get(self,request):
        choices = paises_CHOICES
        return Response(choices)

class IndicativoPaisesChoices(APIView):
    def get(self,request):
        choices = indicativo_paises_CHOICES
        return Response(choices)

class SexoChoices(APIView):
    def get(self,request):
        choices = sexo_CHOICES
        return Response(choices)
    
class EstadoCivilChoices(APIView):
    def get(self,request):
        choices = estado_civil_CHOICES
        return Response(choices) 

class TipoDocumentoChoices(APIView):
    def get(self,request):
        choices = tipo_documento_CHOICES
        return Response(choices)

class TipoPersonaChoices(APIView):
    def get(self,request):
        choices = tipo_persona_CHOICES
        return Response(choices)

class CodNaturalezaEmpresaChoices(APIView):
    def get(self,request):
        choices = cod_naturaleza_empresa_CHOICES
        return Response(choices)

class TipoDireccionChoices(APIView):
    def get(self,request):
        choices = tipo_direccion_CHOICES
        return Response(choices)