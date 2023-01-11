from django.urls import path
from conservacion.views import choices_views as views

urlpatterns = [
    # Choices
    path('tipo-vivero/', views.TipoViveroChoices.as_view(), name='tipo-vivero'),
    path('origen-recursos-vivero/', views.OrigenRecursosViveroChoices.as_view(), name='origen-recursos-vivero'),
    path('cod-etapa-lote/', views.CodEtapaLoteChoices.as_view(), name='cod-etapa-lote'),
]