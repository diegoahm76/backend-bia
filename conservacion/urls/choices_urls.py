from django.urls import path
from conservacion.views import choices_views as views

urlpatterns = [
    # Choices
    path('tipo-vivero/', views.TipoViveroChoices.as_view(), name='tipo-vivero'),
    path('origen-recursos-vivero/', views.OrigenRecursosViveroChoices.as_view(), name='origen-recursos-vivero'),
    path('tipo_incidencia/', views.TipoIncidencia.as_view(), name='tipo-incidencia'),
    path('cod-etapa-lote/', views.CodEtapaLoteChoices.as_view(), name='cod-etapa-lote'),
    path('estado-aprobacion/', views.EstadoAprobacion.as_view(), name='estado-aprobacion'),
    path('tipo-baja/', views.TipoBaja.as_view(), name='estado-aprobacion'),
    path('tipo-bien/', views.TipoBien.as_view(), name='tipo-bien'),
]