from django.urls import path
from conservacion.views import incidencias_views as views

urlpatterns = [
    path('get-material-vegetal-by-codigo-bien/<str:id_vivero>/',views.GetMaterialVegetalByCodigo.as_view(),name='get-material-vegetal-by-codigo-bien'),
    path('get-material-vegetal-by-lupa/<str:id_vivero>/',views.GetMaterialVegetalByLupa.as_view(),name='get-material-vegetal-by-codigo-bien'),
    path('get-bienes-mezclas-by-lupa/<str:id_vivero>/',views.GetElementoYMezclaByLupa.as_view(),name='get-bienes-mezclas-by-lupa'),
    path('get-bienes-insumo-by-codigo/<str:id_vivero>/',views.GetElementosInsumoByCodigo.as_view(),name='get-bienes-insumo-by-codigo'),
    path('get-consumo-by-incidencia/<str:id_incidencia>/',views.GetConsumoIncidenciaByidIncidencia.as_view(),name='get-consumo-by-incidencia'),
    path('get-incidencia-by-vivero/<str:id_vivero>/',views.GetIncidenciasByVivero.as_view(),name='get-incidencia-by-vivero'),
    path('create-incidencias/<str:id_vivero>/',views.GuardarIncidencia.as_view(),name='create-incidencia'),
    path('anulacion-incidencias/<str:id_incidencias_mat_vegetal>/',views.AnulacionIncidencia.as_view(),name='anulacion-incidencias'),
    path('actualizacion-incidencias/<str:id_incidencias_mat_vegetal>/',views.ActualizacionIncidencia.as_view(),name='actualizacion-incidencias')
]
