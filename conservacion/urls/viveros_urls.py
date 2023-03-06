from django.urls import path
from conservacion.views import viveros_views as views

urlpatterns = [
    # Viveros
    path('create/', views.CreateViveros.as_view(), name='vivero-create'),
    path('update/<str:id_vivero_ingresado>/', views.UpdateViveros.as_view(), name='vivero-update'),
    path('delete/<int:id_vivero>/', views.DeleteVivero.as_view(), name='delete-vivero'),
    path('abrir-cerrar/<str:id_vivero>/', views.AbrirCerrarVivero.as_view(), name='abrir-cerrar-vivero'),
    path('cuarentena/<str:id_vivero>/', views.UpdateViveroCuarentena.as_view(),name='update-vivero-cuarentena'),
    path('desactivar/<str:id_vivero>/', views.DesactivarActivarViveroView.as_view(),name='desactivar-vivero'),
    path('tipificacion/<str:id_bien>/', views.TipificacionBienConsumoVivero.as_view(),name='tipificacion-bien-vivero'),
    path('get-by-id/<str:pk>/', views.GetViveroByPk.as_view(),name='viveros-get-by-id'),
    path('get-by-nombre-municipio/cuarentena/', views.FilterViverosByNombreAndMunicipioForCuarentena.as_view(),name='get-by-nombre-municipio-cuarentena'),
    path('get-by-nombre-municipio/apertura-cierre/', views.FilterViverosByNombreAndMunicipioForAperturaCierres.as_view(),name='get-by-nombre-municipio-apertura-cierre'),
    path('get-by-nombre-municipio/', views.FilterViverosByNombreAndMunicipio.as_view(),name='get-by-nombre-municipio'),
    path('historial-viverista-by-vivero/<str:id_vivero>/',views.HistorialViveristaByVivero.as_view(),name='historial-viverista-by-vivero'),
    path('viverista-actual-by-id-vivero/<str:id_vivero>/',views.GetViveristaActual.as_view(),name='viverista-actual-by-id-vivero'),
    path('get-persona-viverista-nuevo-lupa/',views.GetPersonaFiltro.as_view(),name='get-persona-viverista-nuevo-lupa'),
    path('get-persona-viverista-nuevo-by-numero-documento/',views.GetPersonaByNumeroDocumento.as_view(),name='get-persona-viverista-nuevo-by-numero-documento'),
    path('asignacion-viverista/<str:id_vivero>/',views.GuardarAsignacionViverista.as_view(),name='asignacion-viverista')
    
]