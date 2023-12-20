#EnviarCorreoView
from django.urls import path
from transversal.views import email_views as views

urlpatterns = [


    path('envio_email/', views.EnviarCorreoView.as_view(), name='envio-email'),
]