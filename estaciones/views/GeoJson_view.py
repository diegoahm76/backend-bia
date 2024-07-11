import json
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from recurso_hidrico.views.zonas_hidricas_views import FuncionesAuxiliares
from tramites.models import SolicitudesTramites, PermisosAmbientales, PermisosAmbSolicitudesTramite

class GeoJsonConcesionAguasSuperficialesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        tramites = PermisosAmbSolicitudesTramite.objects.filter(id_permiso_ambiental__cod_tipo_permiso_ambiental = 'DA')

        GeoJson_list = []

        for tramite in tramites:
            tramite_sasoftco = FuncionesAuxiliares.get_tramite_sasoftco(tramite)

            if tramite_sasoftco:
                GeoJson = {
                    "Feature": tramite.id_permiso_ambiental.get_cod_tipo_permiso_ambiental_display(),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [tramite_sasoftco['longitud'], tramite_sasoftco['latitud']]
                    },
                    "properties": {
                        "municipio": tramite_sasoftco['Mun_fuente'],
                        "tipo_determinante": tramite.id_permiso_ambiental.nombre,
                        "tipo_elementos_proteccion": tramite_sasoftco['tipo'],
                        "nombre_geografico": tramite.fecha_creacion,
                        "area": tramite.estado,
                        #"latitud": tramite_sasoftco['latitud'],
                        #"longitud": tramite_sasoftco['longitud'],
                        "expediente": tramite_sasoftco['NumExp'],
                        "usuario": tramite.id_usuario.username,
                        "resolucion": tramite_sasoftco['NumResol'],
                        "fecha_resolucion": tramite_sasoftco['Fecha_Resolu'],
                        "estado": tramite.id_permiso_ambiental.estado,
                    }
                }