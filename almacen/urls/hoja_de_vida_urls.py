from django.urls import path
from almacen.views import hoja_de_vida_views as views

urlpatterns = [
    # UNIDADES ORGANIZACIONALES
    path('computadores/delete/<str:pk>/',views.DeleteHojaDeVidaComputadores.as_view(),name='hdv-computadores-delete'),
    path('vehiculos/delete/<str:pk>/',views.DeleteHojaDeVidaVehiculos.as_view(),name='hdv-vehiculos-delete'),
    path('otros/delete/<str:pk>/',views.DeleteHojaDeVidaOtrosActivos.as_view(),name='hdv-otros-delete'),
    path('computador/create/',views.CreateHojaDeVidaComputadores.as_view(),name='hdv-computador-create')
]