from django.urls import path
from almacen.views import solicitudes_views as views

urlpatterns = [
    path('search-bienes-solicitud/', views.SearchVisibleBySolicitud.as_view(), name='search-bienes-solicitud'),

]