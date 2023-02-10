from django.urls import path
from conservacion.views import bajas_views as views

urlpatterns = [
    path('crear-bajas-vivero/', views.CreateBajasVivero.as_view(), name='crear-bajas-vivero'),
    path('actualizar-bajas-vivero/', views.ActualizarBajasVivero.as_view(), name='actualizar-bajas-vivero'),
    path('anualar-bajas-vivero/<str:id_baja_anular>/', views.AnularBajasVivero.as_view(), name='anular-bajas-vivero'),
    path('get-viveros/', views.GetVivero.as_view(), name='get-viveros'),
    path('get-baja-by-numero-baja/<str:nro_baja>/', views.GetBajasParaAnulacionPorNumeroBaja.as_view(), name='get-baja-by-numero-baja'),
    path('get-bienes-bajas/<str:codigo_entrante>/<str:vivero_origen>/', views.GetBienesBajas.as_view(), name='get-bienes_bajas'),
    path('busqueda-avanzada-bienes-bajas/<str:vivero_origen>/', views.BusquedaAvanzadaBienesBajas.as_view(), name='busqueda-avanzada-bienes-bajas'),
]