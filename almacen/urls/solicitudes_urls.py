from django.urls import path
from almacen.views import solicitudes_views as views

urlpatterns = [
    path('crear-solicitud-bienes-de-consumo/', views.CreateSolicitud.as_view(), name='crear-solicitud-bienes-de-consumo'),
    path('search-bienes-solicitud/', views.SearchVisibleBySolicitud.as_view(), name='search-bienes-solicitud'),
    path('get-orgchart-tree/<str:pk>/', views.get_orgchart_tree, name='get-orgchart-tree'),
]