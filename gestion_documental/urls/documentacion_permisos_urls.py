from django.urls import path

from gestion_documental.views import reporte_de_documentacion_permisos_views as views


urlpatterns = [
    #UnidadesSeccionSubseccionGet
     path('trd/get/',views.TRDCCDOrganigramaGet .as_view(), name='listas-trd-activos-produccion'),
     path('seccion-subseccion/get/<str:trd>/',views.UnidadesSeccionSubseccionGet .as_view(), name='listas-trd-seccion-subseccion'),
     ]