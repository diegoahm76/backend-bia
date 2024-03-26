

from django.urls import path
from gestion_documental.views import reporte_indices_PQRSDF_views as views

urlpatterns = [
    # Tabla de Control de Acceso
    path('reporte_general/get/', views.ReporteIndicesTodosGet.as_view(), name='reporte-pqrsdf-general'),
    path('reporte_sedes/get/', views.ReporteIndicesSucursalesGet.as_view(), name='reporte-pqrsdf-sedes'),
    path('reporte/sedes/tipo/get/',views.ReporteIndicesSucursalesTiposPQRSDFGet.as_view(),name='reporte-pqrsdf-sedes-tipo'),
    path('reporte/tipos/sedes/get/',views.ReporteIndicesTiposSucursalesPQRSDFGet.as_view(),name='reporte-pqrsdf-sedes-tipo'),
    #ReporteIndicesUnidadPQRSDFGet
    path('reporte_unidad/get/', views.ReporteIndicesUnidadPQRSDFGet.as_view(), name='reporte-pqrsdf-unidad'),
    #

]