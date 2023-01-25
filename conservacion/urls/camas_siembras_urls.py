from django.urls import path
from conservacion.views import camas_siembras_views as views

urlpatterns = [
    path('crear-camas/', views.CrearCamasGerminacion.as_view(), name='tipo-vivero'),
]