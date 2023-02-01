from django.urls import path
from conservacion.views import camas_siembras_views as views

urlpatterns = [
    path('camas-germinacion/<str:id_vivero_procesar>/', views.CamasGerminacion.as_view(), name='camas-germinacion'),
    path('siembra/create/', views.CreateSiembraView.as_view(), name='crear-siembra'),
    path('siembra/get-viveros/', views.FilterViverosByNombreAndMunicipio.as_view(), name='get-numero-lote'),
    path('siembra/get-material-vegetal/', views.GetBienSembradoView.as_view(), name='get-material-vegetal'),
    path('siembra/get-camas-germinacion/', views.GetCamasGerminaciones.as_view(), name='get-camas-germinacion'),

                                                                                
                                                                                 
                                                                        ]