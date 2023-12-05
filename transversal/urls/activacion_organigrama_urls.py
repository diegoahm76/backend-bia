from django.urls import path
from transversal.views import activacion_organigrama_views as views

urlpatterns = [

        # ACTIVACION ORGANIGRAMA
    path('get-ccd-terminados-by-org/<str:id_organigrama>/', views.GetCCDTerminadoByORG.as_view(), name='ccd-terminados-get-by-org'),
    path('get-organigrama-actual/', views.ObtenerOrganigramaActual.as_view(), name='get-organigrama-actual'),
    path('get-organigramas-posibles/', views.ObtenerOrganigramasPosibles.as_view(), name='get-organigrama-posibles'),
    path('change-actual-organigrama/', views.CambioDeOrganigramaActual.as_view(), name='change-actual-organigrama'),

]