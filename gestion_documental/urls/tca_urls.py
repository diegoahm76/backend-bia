from django.urls import path
from gestion_documental.views import tca_views as views

urlpatterns = [
    path('unidades/get/<str:pk>/', views.GetUnidadesbyCCD.as_view(), name='update-tipologias-doc'),
    
    # Tabla de Control de Acceso
    path('create/', views.PostTablaControlAcceso.as_view(),name='create-tca'),
    path('update/<str:pk>/', views.UpdateTablaControlAcceso.as_view(), name='update-tca'),
]