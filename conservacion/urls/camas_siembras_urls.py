from django.urls import path
from conservacion.views import camas_siembras_views as views

urlpatterns = [
    #CAMAS DE GERMINACIÓN
    path('camas-germinacion/<str:id_vivero_procesar>/', views.CamasGerminacion.as_view(), name='camas-germinacion'),
    
    #SIEMBRAS
    path('siembra/create/', views.CreateSiembraView.as_view(), name='crear-siembra'),
    path('siembra/update/<str:id_siembra>/', views.UpdateSiembraView.as_view(), name='update-siembra'),
    path('siembra/delete/<str:id_siembra>/', views.DeleteSiembraView.as_view(), name='delete-siembra'),
    # path('siembra/bienes-consumidos/create/<str:id_siembra>/', views.CreateBienesConsumidosView.as_view(), name='create-bienes-consumidos'),
    path('siembra/bienes-consumidos/update/<str:id_siembra>/', views.UpdateBienConsumidoView.as_view(), name='update-bienes-consumidos-siembra'),
    path('siembra/bienes-consumidos/delete/<str:id_siembra>/', views.DeleteBienesConsumidosView.as_view(), name='delete-bienes-consumidos-siembra'),

    path('siembra/get-viveros/', views.FilterViverosByNombreAndMunicipioView.as_view(), name='get-numero-lote'),
    path('siembra/get/', views.GetSiembrasView.as_view(), name='get-siembras'),
    path('siembra/get-material-vegetal/', views.GetBienSembradoView.as_view(), name='get-bien-sembrado'),
    path('siembra/get-bienes-consumidos/<str:id_siembra>/', views.GetBienesConsumidosSiembraView.as_view(), name='get-bienes-consumidos-siembra'),
    path('siembra/get-camas-germinacion/<str:id_vivero>/', views.GetCamasGerminacionesView.as_view(), name='get-camas-germinacion'),
    path('siembra/get-camas-germinacion-siembra/<str:id_vivero>/', views.GetCamasGerminacionesByIdVivero.as_view(), name='get-camas-germinacion-siembra'),
    path('siembra/get-camas-germinacion-list/', views.GetCamasGerminacionList.as_view(), name='siembraget-camas-germinacion-list'),
    path('siembra/get/<str:id_siembra>/', views.GetSiembrasView.as_view(), name='get-siembra'),
    path('siembra/get-bienes-por-consumir/<str:id_vivero>/<str:codigo_bien>/', views.GetBienesPorConsumirView.as_view(), name='get-bienes-por-consumir'),
    path('siembra/get-bienes-por-consumir-lupa/<str:id_vivero>/', views.GetBusquedaBienesConsumidosView.as_view(), name='get-bienes-por-consumir'),
]