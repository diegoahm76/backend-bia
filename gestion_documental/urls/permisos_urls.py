from django.urls import path
from gestion_documental.views import permisos_views as views

urlpatterns = [
    path('busqueda-ccd/get/', views.BusquedaCCDPermisosGetView.as_view(),name='buscar-ccd-permisos'),
    path('unidades-ccd/get/<str:id_organigrama>/', views.UnidadesCCDGetView.as_view(),name='unidades-ccd-permisos'),
    path('serie-subserie-unidad-ccd/get/', views.SerieSubserieUnidadCCDGetView.as_view(),name='serie-subserie-unidad-ccd-permisos'),
    path('unidades-permisos/get/<str:id_cat_serie_und>/', views.UnidadesPermisosGetView.as_view(),name='unidades-permisos-get'),
    path('unidades-permisos/put/<str:id_cat_serie_und>/', views.UnidadesPermisosPutView.as_view(),name='unidades-permisos-put'),
]
