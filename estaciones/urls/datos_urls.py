from django.urls import path
from estaciones.views import datos_views as views

urlpatterns = [
    # Datos
    path('consultar-datos-id/<str:pk>/',
         views.ConsultarDatosId.as_view(), name='consultardatosid'),
    path('consultar-datos-fecha/<str:pk>/<str:fecha_inicial>/<str:fecha_final>/',
         views.ConsultarDatosFecha.as_view(), name='consultar-datos-fecha'),
    path('consultar-datos-reporte/<str:pk>/<str:mes>/',
         views.ConsultarDatosReportes.as_view(), name='consultar-datos-reporte'),
    path('consultar-datos-id-primeros/<str:pk>/',
         views.ConsultarDatosIdPrimerosDatos.as_view(), name='consultardatosidprimerosdatos'),
]
