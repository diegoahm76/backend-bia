from django.urls import path
from almacen.views import despachos_viveros_views as views

urlpatterns = [
    path('crear-despacho-bienes-de-consumo/', views.CreateDespachoMaestroVivero.as_view(), name='crear-despacho-bienes-de-consumo')
]
