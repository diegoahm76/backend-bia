from django.urls import path
from almacen.views import bienes_views as views

urlpatterns = [
    path('create-catalogo-bienes/', views.CreateCatalogoDeBienes.as_view(), name='')
]
