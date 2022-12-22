from django.urls import path
from almacen.views import hoja_de_vida_views as views

urlpatterns = [
    # HOJAS DE VIDA COMPUTADORES
    path('computadores/create/',views.CreateHojaDeVidaComputadores.as_view(),name='hdv-computadores-create'),
    path('computadores/update/<str:pk>/',views.UpdateHojaDeVidaComputadores.as_view(),name='hdv-computadores-update'),
    path('computadores/delete/<str:pk>/',views.DeleteHojaDeVidaComputadores.as_view(),name='hdv-computadores-delete'),
    path('computadores/get-by-id/<str:pk>/',views.GetHojaDeVidaComputadoresById.as_view(),name='hdv-computadores-get'),
    path('computadores/get-by-id-bien/<str:id_bien>/',views.GetHojaDeVidaComputadoresByIdBien.as_view(),name='hdv-computadores-get-bien'),
    
    # HOJAS DE VIDA VEHICULOS
    path('vehiculos/create/',views.CreateHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-create'),
    path('vehiculos/update/<str:pk>/',views.UpdateHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-update'),
    path('vehiculos/delete/<str:pk>/',views.DeleteHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-delete'),
    path('vehiculos/get-by-id/<str:pk>/',views.GetHojaDeVidaVehiculosById.as_view(),name='hdv-vehiculos-get'),
    path('vehiculos/get-by-id-bien/<str:id_bien>/',views.GetHojaDeVidaVehiculosByIdBien.as_view(),name='hdv-vehiculos-get-bien'),
    
    # HOJAS DE VIDA OTROS ACTIVOS
    path('otros/create/',views.CreateHojaDeVidaOtros.as_view(),name='hdv-otros-create'),
    path('otros/update/<str:pk>/',views.UpdateHojaDeVidaOtrosActivos.as_view(),name='hdv-otros-update'),
    path('otros/delete/<str:pk>/',views.DeleteHojaDeVidaOtrosActivos.as_view(),name='hdv-otros-delete'),
    path('otros/get-by-id/<str:pk>/',views.GetHojaDeVidaOtrosActivosById.as_view(),name='hdv-otros-get'),
    path('otros/get-by-id-bien/<str:id_bien>/',views.GetHojaDeVidaOtrosActivosByIdBien.as_view(),name='hdv-otros-get-bien'),
]