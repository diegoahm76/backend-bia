from django.urls import path
from almacen.views import bienes_views as views

urlpatterns = [
    #Catalogo Bienes
    path('catalogo-bienes/get-list/',views.GetCatalogoBienesList.as_view(),name='catalogo-bienes-get-list'),
    path('catalogo-bienes/delete/<str:id_bien>/',views.DeleteNodos.as_view(),name='catalogo-bienes-delete'),
    path('catalogo-bienes/get-element-by-nodo/<str:id_nodo>/',views.GetElementosByIdNodo.as_view(),name='catalogo-bienes-get-element-by-nodo'),
    path('catalogo-bienes/create/', views.CreateCatalogoDeBienes.as_view(), name='catalogo-bienes-create'),

]
