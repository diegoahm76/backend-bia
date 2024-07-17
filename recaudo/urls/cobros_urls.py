from django.urls import path
from recaudo.views import cobros_views as views

urlpatterns = [
    path('carteras/', views.CarteraGeneralView.as_view(), name='carteras-todos'),
    path('filtrar-carteras/', views.CarteraDeudoresView.as_view(), name='carteras-por-deudores'),
    path('carteras-tua/', views.VistaCarteraTuaView.as_view(), name='carteras-tua'),
    path('info-tua/<str:id_expediente>/', views.InfoTuaView.as_view(), name='info-tua'),


    path('conceptos-contables/', views.ConceptoContableGetView.as_view(), name='conceptos-contables'),
    path('etapas-proceso/', views.EtapasGetView.as_view(), name='etapas-proceso'),
    path('tipos-atributos/', views.TiposAtributosGetView.as_view(), name='tipos-atributos'),
    path('sub-etapas/<str:id_etapa>/', views.SubEtapasGetView.as_view(), name='categorias-atributos'),
    path('rangos-edad/', views.RangosGetView.as_view(), name='rangos-edad'),

]
