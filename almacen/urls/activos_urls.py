from django.urls import path
from almacen.views import activos_views as views




urlpatterns = [
    

    #Baja_Activos
    path('busqueda-avanzada-bienes/get/',views.BuscarBien.as_view(),name='busqueda-avanzada-bien'),
    path('crear-baja-activos/create/',views.RegistrarBajaCreateView.as_view(),name='crear-baja-activo'),











]
