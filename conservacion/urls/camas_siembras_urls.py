from django.urls import path
from conservacion.views import camas_siembras_views as views

urlpatterns = [
    path('camas-germinacion/<str:id_vivero_procesar>/', views.CamasGerminacion.as_view(), name='camas-germinacion'),
]