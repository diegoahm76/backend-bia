from django.urls import path
from gestion_documental.views import permisos_views as views

urlpatterns = [
    path('busqueda-ccd/get/', views.BusquedaCCDPermisosGetView.as_view(),name='buscar-ccd-permisos'),
    path('unidades-ccd/get/<str:id_organigrama>/', views.UnidadesCCDGetView.as_view(),name='unidades-ccd-permisos'),
    path('serie-subserie-unidad-ccd/get/', views.SerieSubserieUnidadCCDGetView.as_view(),name='serie-subserie-unidad-ccd-permisos'),
    path('unidades-hijas-ccd/get/<str:id_unidad_organizacional>/', views.UnidadesHijasCCDGetView.as_view(),name='unidades-hijas-ccd-permisos'),
]
