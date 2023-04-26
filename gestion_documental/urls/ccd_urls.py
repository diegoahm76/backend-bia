from django.urls import path
from gestion_documental.views import ccd_views as views

urlpatterns = [
    # Cuadros de Clasificación Documental
    path('create/', views.CreateCuadroClasificacionDocumental.as_view(),name='create-ccd'),
    path('update/<str:pk>/', views.UpdateCuadroClasificacionDocumental.as_view(),name='update-ccd'),
    path('get-list/', views.GetCuadroClasificacionDocumental.as_view(),name='get-list-ccd'),
    path('get-terminados/', views.GetCCDTerminado.as_view(),name='get-terminados-ccd'),
    path('finish/<str:pk>/', views.FinalizarCuadroClasificacionDocumental.as_view(),name='finish-ccd'),
    path('resume/<str:pk>/', views.ReanudarCuadroClasificacionDocumental.as_view(),name='resume-ccd'),
    path('get-busqueda/', views.BusquedaCCD.as_view(),name='buscar-ccd'),

    # Series
    path('series/create/',views.CreateSeriesDoc.as_view(),name='create-series-ccd'),
    path('series/update/<str:id_serie_doc>/',views.UpdateSeriesDoc.as_view(),name='update-series-ccd'),
    path('series/delete/<str:id_serie_doc>/',views.DeleteSeriesDoc.as_view(),name='delete-series-ccd'),
    path('series/get-by-id/<str:id_serie_doc>/',views.GetSeriesById.as_view(),name='get-series-by-id'),
    path('series/get-by-filters/<str:id_ccd>/',views.GetSeriesByFilters.as_view(),name='get-series-by-filters'),
    path('series/get-by-id-ccd/<str:id_ccd>/',views.GetSeriesByIdCCD.as_view(),name='get-series-by-id-ccd'),
    path('series/get-independent/<str:id_ccd>/',views.GetSeriesIndependent.as_view(),name='get-series-independent'),

    # SUBSERIES
    path('subseries/create/', views.CreateSubseriesDoc.as_view(), name='create-subseries-ccd'),
    path('subseries/update/<str:id_subserie_doc>/', views.UpdateSubseriesDoc.as_view(), name='update-subseries-ccd'),
    path('subseries/delete/<str:id_subserie_doc>/', views.DeleteSubseriesDoc.as_view(), name='delete-subseries-ccd'),
    path('subseries/get-by-id/<str:id_subserie_doc>/', views.GetSubseriesById.as_view(),name='get-subseries-by-id'),
    path('subseries/get-by-id-serie-doc/<str:id_serie_doc>/', views.GetSubseriesByIdSerieDoc.as_view(),name='get-subseries-id-serie-doc'),
    
    # CATALOGOS
    path('catalogo/serie-subserie/create/',views.CreateCatalogoSerieSubserie.as_view(),name='create-cat-serie-subserie'),
    path('catalogo/serie-subserie/delete/<str:id_catalogo_serie>/',views.DeleteCatalogoSerieSubserie.as_view(),name='delete-cat-serie-subserie'),
    path('catalogo/serie-subserie/get-by-id-ccd/<str:id_ccd>/',views.GetCatalogoSerieSubserieByIdCCD.as_view(),name='create-cat-serie-subserie'),
    path('catalogo/unidad/update/<str:id_ccd>/',views.UpdateCatalogoUnidad.as_view(),name='update-cat-unidad'),
    path('catalogo/unidad/get-by-id-ccd/<str:id_ccd>/',views.GetCatalogoSeriesUnidadByIdCCD.as_view(),name='get-cat-unidad-by-id-ccd'),
    
    # Asignaciones
    # path('asignar/create/<str:id_ccd>/',views.AsignarSeriesYSubseriesAUnidades.as_view(),name='asignar-series-documentales'),
    # path('asignar/get/<str:id_ccd>/',views.GetAsignaciones.as_view(),name='asignar-series-documentales')
]
