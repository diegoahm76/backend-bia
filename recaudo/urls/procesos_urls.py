from django.urls import path
from recaudo.views import procesos_views as views

urlpatterns = [
    path('etapas/', views.EtapasProcesoView.as_view(), name='etapas-proceso-todos'),
    path('tipos-atributos/', views.TiposAtributosView.as_view(), name='tipos-etapas-todos'),
    path('atributos/<int:etapa>/', views.AtributosEtapasView.as_view(), name='atributos-etapas-todos'),
    path('flujos/', views.FlujoProcesoView.as_view(), name='flujos-todos'),
    path('grafica/', views.GraficaView.as_view(), name='grafica-flujo'),
    path('valores-proceso/<int:proceso>/', views.ValoresProcesoView.as_view(), name='valores-por-proceso'),
    path('valores-proceso/', views.ValoresProcesoView.as_view(), name='crear-valores-proceso'),
    path('actualizar-etapa-proceso/<int:proceso>/', views.ActualizarEtapaProceso.as_view(), name='actualiza-etapa-de-un-proceso'),
]
