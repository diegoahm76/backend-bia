from django.urls import path
from gestion_documental.views import ctrl_acceso_views as views

urlpatterns = [
    # Ctrl Acceso Clasificacion Exp
    path('get/', views.CtrlAccesoGetView.as_view(), name='ctrl-acceso-get'),
    path('put/', views.CtrlAccesoPutView.as_view(), name='ctrl-acceso-put'),
]