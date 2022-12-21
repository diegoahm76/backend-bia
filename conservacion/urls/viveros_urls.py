from django.urls import path
from conservacion.views import viveros_views as views

urlpatterns = [
    # Viveros
    path('create/', views.CreateViveros.as_view(), name='vivero-create'),
    path('delete/<str:id_vivero>/', views.DeleteVivero.as_view(), name='delete-vivero'),
    path('abrir-cerrar/<str:id_vivero>/', views.AbrirCerrarVivero.as_view(), name='abrir-cerrar-vivero'),
    path('get-by-id/<str:pk>/', views.GetViveroByPk.as_view(),name='viveros-get-by-id'),
    path('get-by-nombre-municipio/cuarentena/', views.FilterViverosByNombreAndMunicipioForCuarentena.as_view(),name='get-by-nombre-municipio-cuarentena'),
    path('get-by-nombre-municipio/apertura-cierre/', views.FilterViverosByNombreAndMunicipioForAperturaCierres.as_view(),name='get-by-nombre-municipio-apertura-cierre'),
]