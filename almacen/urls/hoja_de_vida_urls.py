from django.urls import path
from almacen.views import hoja_de_vida_views as views

urlpatterns = [
    # UNIDADES ORGANIZACIONALES
    path('computadores/delete/<str:pk>/',views.DeleteHojaDeVidaComputadores.as_view(),name='hdv-computadores-delete'),
    path('vehiculos/delete/<str:pk>/',views.DeleteHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-delete'),
    path('otros/delete/<str:pk>/',views.DeleteHojaDeVidaOtrosActivos.as_view(),name='hdv-otros-delete'),
    path('computadores/create/',views.CreateHojaDeVidaComputadores.as_view(),name='hdv-computador-create'),
    path('vehiculos/create/',views.CreateHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-create'),
    path('otros/create/',views.CreateHojaDeVidaOtros.as_view(),name='hdv-otros-create'),
    path('computadores/update/<str:pk>/',views.UpdateHojaDeVidaComputadores.as_view(),name='hdv-computador-update'),
    path('vehiculos/update/<str:pk>/',views.UpdateHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-update'),
    path('otros/update/<str:pk>/',views.UpdateHojaDeVidaOtrosActivos.as_view(),name='hdv-otros-update'),
]