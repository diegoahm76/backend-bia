from django.urls import path
from recaudo.views import choices_views as views

urlpatterns = [
    path('pagos-tipo-id/',views.PagosTipoId.as_view(), name='pagos-tipo-id'),
]