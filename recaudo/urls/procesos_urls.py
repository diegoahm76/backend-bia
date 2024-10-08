from django.urls import path
from recaudo.views import procesos_views as views
from recaudo.views import facilidades_pagos_views as f_views

urlpatterns = [
    path('etapas/', views.EtapasProcesoView.as_view(), name='etapas-proceso-todos'),
    path('tipos-atributos/', views.TiposAtributosView.as_view(), name='tipos-etapas-todos'),
    path('actualizar-tipos-atributos/<int:tipo>/', views.ActualizarTiposAtributosView.as_view(), name='tipos-etapas-actualizar'),
    path('eliminar-tipos-atributos/<int:tipo>/', views.EliminarTiposAtributosView.as_view(), name='tipos-etapas-eliminar'),
    path('atributos/<int:etapa>/', views.AtributosEtapasView.as_view(), name='atributos-etapas-todos'),
    path('flujos/', views.FlujoProcesoView.as_view(), name='flujos-todos'),
    path('grafica/', views.GraficaView.as_view(), name='grafica-flujo'),
    path('valores-proceso/<int:proceso>/', views.ValoresProcesoView.as_view(), name='valores-por-proceso'),
    path('valores-proceso/', views.ValoresProcesoView.as_view(), name='crear-valores-proceso'),
    path('actualizar-etapa-proceso/<int:proceso>/', views.ActualizarEtapaProceso.as_view(), name='actualiza-etapa-de-un-proceso'),
    path('procesos-sin-finalizar/', views.ProcesosView.as_view(), name='procesos-sin-finalizar'),
    path('procesos/', views.ProcesosGeneralView.as_view(), name='procesos'),
    path('procesos/<int:proceso>/', views.ProcesosGetGeneralView.as_view(), name='procesos'),
    path('crear-proceso/', views.ProcesosView.as_view(), name='crear-proceso'),
    path('actualizar-proceso/<int:pk>/', views.UpdateProcesosView.as_view(), name='actualizar-etapa-proceso'),
    path('actualizar-categoria-proceso/<int:pk>/', views.UpdateCategoriaProcesosView.as_view(), name='actualizar-categoria-proceso'),
    path('atributos/', views.AtributosEtapasView.as_view(), name='atributos-etapas-agregar'),
    path('atributos/<int:pk>/', views.AtributosEtapasView.as_view(), name='atributos-etapas-editar'),
    path('eliminar-atributos-etapa/<int:etapa>/<int:categoria>/', views.DeleteAtributosEtapasView.as_view(), name='eliminar-atributos-etapas'),
    path('avaluos-bienes/', f_views.AvaluoCreateView.as_view(), name='avaluos-bienes'),
    path('categoria-atributos/', views.CategoriaAtributoView.as_view(), name='categoria-atributos'),
    path('categoria-atributos/<int:pk>/', views.CategoriaAtributoView.as_view(), name='categoria-atributos'),
    path('etapas-filtrado/', views.EtapasFiltradoView.as_view(), name='categoria-atributos'),
    path('categoria-por-etapas/<int:pk>/', views.CategoriasEtapasFiltradoView.as_view(), name='categoria-etapas-atributos'),
    path('eliminar-etapa/<int:etapa>/', views.DeleteEtapaView.as_view(), name='eliminar-etapas-por-id'),
    path('eliminar-categoria/<int:categoria>/', views.DeleteCategoriaAtributoView.as_view(), name='eliminar-etapas-por-id'),
    path('eliminar-atributo/<int:pk>/', views.DeleteAtributosView.as_view(), name='eliminar-atributo'),

]
