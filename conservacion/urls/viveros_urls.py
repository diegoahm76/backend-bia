from django.urls import path
from conservacion.views import viveros_views as views

urlpatterns = [
    # Viveros
    path('create/', views.CreateViveros.as_view(), name='vivero-create'),
    path('update/<str:id_vivero_ingresado>/', views.UpdateViveros.as_view(), name='vivero-update'),
    path('delete/<str:id_vivero>/', views.DeleteVivero.as_view(), name='delete-vivero'),
    path('abrir-cerrar/<str:id_vivero>/', views.AbrirCerrarVivero.as_view(), name='abrir-cerrar-vivero'),
    path('cuarentena/<str:id_vivero>/', views.UpdateViveroCuarentena.as_view(),name='update-vivero-cuarentena'),
    path('desactivar/<str:id_vivero>/', views.DesactivarViveroView.as_view(),name='desactivar-vivero'),
    path('tipificacion/<str:id_bien>/', views.TipificacionBienConsumoVivero.as_view(),name='tipificacion-bien-vivero'),
    path('get-by-id/<str:pk>/', views.GetViveroByPk.as_view(),name='viveros-get-by-id'),
    path('get-by-nombre-municipio/cuarentena/', views.FilterViverosByNombreAndMunicipioForCuarentena.as_view(),name='get-by-nombre-municipio-cuarentena'),
    path('get-by-nombre-municipio/apertura-cierre/', views.FilterViverosByNombreAndMunicipioForAperturaCierres.as_view(),name='get-by-nombre-municipio-apertura-cierre'),
    path('get-by-nombre-municipio/', views.FilterViverosByNombreAndMunicipio.as_view(),name='get-by-nombre-municipio'),
    
]