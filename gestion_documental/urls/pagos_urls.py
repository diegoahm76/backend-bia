from django.urls import path

from gestion_documental.views import pagos_views as views


urlpatterns = [
    path('iniciar/',views.IniciarPagoView.as_view(), name='iniciar-pago'),
    path('verificar/',views.VerificarPagoView.as_view(), name='verificar-pago'),
]