from django.urls import path

from gestion_documental.views import reporte_de_documentacion_permisos_views as views


urlpatterns = [
    #ReportePermisosUndsOrgActualesSerieExpCCDGet
     path('trd/get/',views.TRDCCDOrganigramaGet .as_view(), name='listas-trd-activos-produccion'),
     path('seccion-subseccion/get/<str:trd>/',views.UnidadesSeccionSubseccionGet .as_view(), name='listas-trd-seccion-subseccion'),
     path('reporte-permisos-unds-org-actuales-serie-exp-CCD/get/<str:cat>/',views.ReportePermisosUndsOrgActualesSerieExpCCDGet .as_view(), name='listas-trd-seccion-subseccion'),
     #path('reporte-denegacion-permisos/get/<str:uni>/',views.DenegacionPermisosGetByUnidadView .as_view(), name='listas-trd-seccion-subseccion'),
     path('reporte-permisos-no-propios/get/<str:uni>/',views.PermisosExpedientesNoPropios .as_view(), name='listas-trd-seccion-subseccion'),
     ]#