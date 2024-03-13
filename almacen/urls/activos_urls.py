from django.urls import path
from almacen.views import activos_views as views




urlpatterns = [
    

    #Baja_Activos
    path('busqueda-avanzada-bienes/get/',views.BuscarBien.as_view(),name='busqueda-avanzada-bien'),
    path('crear-baja-activos/create/',views.RegistrarBajaCreateView.as_view(),name='crear-baja-activo'),
    path('restablecer-consecutivo/get/',views.UltimoConsecutivoView.as_view(),name='consecutivo-baja-activo'),
    path('actualizar-baja-activos/update/<int:pk>/', views.ActualizarBajaActivosView.as_view(), name='actualizar-baja-activo'),
    path('eliminar-baja-activos/<int:pk>/', views.BorrarBajaActivosView.as_view(), name='borrar-baja-activos'),
    path('info-baja-activos/get/<int:consecutivo>/', views.BajaActivosPorConsecutivo.as_view(), name='baja-activos-consecutivo'),
    path('bajas-activos/get/', views.ListarBajasActivosView.as_view(), name='listar_bajas_activos'),




]
