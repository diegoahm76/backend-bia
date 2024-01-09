#EnviarCorreoView
from django.urls import path
from transversal.views import sms_views as views

urlpatterns = [
    path('envio_sms/', views.EnviarSMSView.as_view(), name='envio-sms'),
]