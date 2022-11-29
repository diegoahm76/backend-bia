from django.urls import path
from almacen.views import bienes_views as views

urlpatterns = [
    #Catalogo Bienes
    path('catalogo-bienes/get-list/',views.GetCatalogoBienesList.as_view(),name='catalogo-bienes-get-list'),
    path('catalogo-bienes/delete/<str:id_bien>/',views.DeleteNodos.as_view(),name='catalogo-bienes-delete'),

]
