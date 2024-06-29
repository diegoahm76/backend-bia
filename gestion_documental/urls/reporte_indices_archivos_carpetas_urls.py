from django.urls import path
from gestion_documental.views import reporte_indices_archivos_carpetas_views as views

urlpatterns = [
    # Tabla de Control de Acceso
    path('reporte_general/get/', views.ReporteIndicesTodosGet.as_view(), name='reporte-general-get'),
    path('sedes/get/', views.SucursalesEmpresasGet.as_view(), name='sedes-post'),
    path('reporte_sede/get/', views.ReporteIndicesSedesGet.as_view(), name='reportes-sedes-get'),
    path('unidades/get/', views.UnidadesOrganigramaActualGet.as_view(), name='unidades-get'),
    path('grupos/get/<str:uni>/',views.UnidadesGruposGet.as_view(),name='grupos-get'),
    path('catalogos/get/<str:uni>/', views.SerieSubserioUnidadGet.as_view(), name='catalogos-get'),
    path('reporte_unidad/get/<str:uni>/', views.ReporteUnidadGet.as_view(), name='reporte-unidad-get'),
    path('reporte_unidad_total/get/<str:uni>/', views.ReporteUnidadTotalUnidadGet.as_view(), name='reporte-unidad-total-get'),
    path('reporte_unidad_oficina/get/<str:uni>/', views.ReporteUnidadOficinaGet.as_view(), name='reporte-unidad-oficina-get'),
    

]