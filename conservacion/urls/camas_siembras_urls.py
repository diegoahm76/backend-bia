from django.urls import path
from conservacion.views import camas_siembras_views as views

urlpatterns = [
    #CAMAS DE GERMINACIÓN
    path('camas-germinacion/<str:id_vivero_procesar>/', views.CamasGerminacion.as_view(), name='camas-germinacion'),
    
    #SIEMBRAS
    path('siembra/create/', views.CreateSiembraView.as_view(), name='crear-siembra'),
    path('siembra/get-viveros/', views.FilterViverosByNombreAndMunicipioView.as_view(), name='get-numero-lote'),
    path('siembra/get-material-vegetal/', views.GetBienSembradoView.as_view(), name='get-material-vegetal'),
    path('siembra/get-camas-germinacion/', views.GetCamasGerminacionesView.as_view(), name='get-camas-germinacion'),
    path('siembra/get/<str:id_siembra>/', views.GetSiembrasView.as_view(), name='get-siembra'),
    path('siembra/get-bienes-por-consumir/<str:id_vivero>/<str:codigo_bien>/', views.GetBienesPorConsumirView.as_view(), name='get-bienes-por-consumir'),
    path('siembra/get-bienes-por-consumir-lupa/<str:id_vivero>/', views.GetBusquedaBienesConsumidos.as_view(), name='get-bienes-por-consumir'),
    path('siembra/bienes-consumidos/create/<str:id_siembra>/', views.CreateBienesConsumidosView.as_view(), name='create-bienes-consumidos'),
    
]