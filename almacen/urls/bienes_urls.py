from django.urls import path
from almacen.views import bienes_views as views

urlpatterns = [
    #Catalogo Bienes
    path('catalogo-bienes/get-list/',views.GetCatalogoBienesList.as_view(),name='catalogo-bienes-get-list'),
    path('catalogo-bienes/delete/<str:id_bien>/',views.DeleteNodos.as_view(),name='catalogo-bienes-delete'),
    path('catalogo-bienes/get-element-by-id-nodo/<str:id_nodo>/',views.GetElementosByIdNodo.as_view(),name='catalogo-bienes-get-element-by-nodo'),
    #path('catalogo-bienes/create/', views.CreateCatalogoDeBienes.as_view(), name='catalogo-bienes-create'),
    path('catalogo-bienes/get-by-nro-identificador/',views.SearchArticuloByDocIdentificador.as_view(),name='get-by-nro-identificador'),
    path('catalogo-bienes/get-by-nombre-nroidentificador/',views.SearchArticulosByNombreDocIdentificador.as_view(),name='get-by-nombre-nroidentificador'),
    path('catalogo-bienes/validar-codigo/<str:nivel>/<str:codigo_bien>/',views.ValidacionCodigoBien.as_view(),name='validar-codigo'),
    
    #Catalogo Bienes yo
    path('catalogo-bienes/create/', views.CatalogoBienesCreate.as_view(), name='catalogo-bienes-create'),

    #Entradas
    path('entradas/tipos-entradas/', views.GetTiposEntradas.as_view(), name='tipos-entrada'),
    path('entradas/create/', views.CreateEntradaandItemsEntrada.as_view(), name='entrada-create'),
    path('entradas/get-list/', views.GetEntradas.as_view(), name='entrada-get-list'),
    path('entradas/update/<str:id_entrada>/', views.UpdateEntrada.as_view(), name='entrada-update'),
    path('entradas/search-bienes/', views.SearchArticulos.as_view(), name='catalogo-bienes-search-bienes'),
    # path('entradas/items/delete/', views.DeleteItemsEntrada.as_view(), name='item-entrada-delete'),
    path('entradas/get-numero_entrada/', views.GetNumeroEntrada.as_view(), name='get_numero_entrada'),
    # path('entradas/items/update/<str:id_entrada>/', views.UpdateItemsEntrada.as_view(), name='item-entrada-update'),
    path('entradas/anular/<str:id_entrada>/', views.AnularEntrada.as_view(), name='entrada-entrada'),
    path('entradas/get-by-codigo/', views.GetCatalogoBienesByCodigo.as_view(), name='catalogo-bienes-codigo-get'),
]
