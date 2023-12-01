from recaudo.views import RegistrosConfiguracion_viwes  as viwes
from django.urls import path

# urls
urlpatterns = [
        path('registrosconfiguracion/get/', viwes.Vista_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
        path('registrosconfiguracion/post/', viwes.Crear_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
        path('registrosconfiguracion/put/<str:pk>/', viwes.Actualizar_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
        path('registrosconfiguracion/delete/<str:pk>/', viwes.Borrar_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
    ]

