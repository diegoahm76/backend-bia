from django.urls import path
from almacen.views import despachos_views as views

urlpatterns = [
    path('crear-despacho-bienes-de-consumo/', views.CreateDespachoMaestro.as_view(), name='crear-despacho-bienes-de-consumo'),
    path('get-solicitudes-aprobados-abiertos/', views.SearchSolicitudesAprobadasYAbiertos.as_view(), name='get-solicitudes-aprobados-abiertos'),
    path('cerrar-solicitud-debido-inexistencia/<str:id_solicitud>/', views.CerrarSolicitudDebidoInexistenciaView.as_view(), name='cerrar-solicitud-debido-inexistencia'),

    path('search-bien-inventario/', views.SearchBienInventario.as_view(), name='search-bien-inventario'),
    path('search-bienes-inventario/', views.SearchBienesInventario.as_view(), name='search-bienes-inventario'),
    path('get-despacho-consumo-by-numero-despacho/', views.GetDespachoConsumoByNumeroDespacho.as_view(), name='get-despacho-consumo-by-numero-despacho'),
    path('filter-despacho-consumo/', views.FiltroDespachoConsumo.as_view(), name='filter-despacho-consumo'),
]