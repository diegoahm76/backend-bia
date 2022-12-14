from django.urls import path
from almacen.views import hoja_de_vida_views as views

urlpatterns = [
    # UNIDADES ORGANIZACIONALES
    path('computadores/delete/<str:pk>/',views.DeleteHojaDeVidaComputadores.as_view(),name='hdv-computadores-delete'),
    path('vehiculos/delete/<str:pk>/',views.DeleteHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-delete'),
    path('otros/delete/<str:pk>/',views.DeleteHojaDeVidaOtrosActivos.as_view(),name='hdv-otros-delete'),
    path('computadores/create/',views.CreateHojaDeVidaComputadores.as_view(),name='hdv-computadores-create'),
    path('vehiculos/create/',views.CreateHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-create'),
    path('otros/create/',views.CreateHojaDeVidaOtros.as_view(),name='hdv-otros-create'),
    path('computadores/update/<str:pk>/',views.UpdateHojaDeVidaComputadores.as_view(),name='hdv-computadores-update'),
    path('vehiculos/update/<str:pk>/',views.UpdateHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-update'),
    path('otros/update/<str:pk>/',views.UpdateHojaDeVidaOtrosActivos.as_view(),name='hdv-otros-update'),
    path('computadores/get-by-id/<str:pk>/',views.GetHojaDeVidaComputadoresById.as_view(),name='hdv-computadores-get'),
    path('vehiculos/get-by-id/<str:pk>/',views.GetHojaDeVidaVehiculosById.as_view(),name='hdv-vehiculos-get'),
    path('otros/get-by-id/<str:pk>/',views.GetHojaDeVidaOtrosActivosById.as_view(),name='hdv-otros-get'),
    path('get-by-nro-identificador/',views.SearchArticuloByDocIdentificador.as_view(),name='get-by-nro-identificador'),
    path('get-by-nombre-nroidentificador/',views.SearchArticulosByNombreDocIdentificador.as_view(),name='get-by-nombre-nroidentificador'),
]