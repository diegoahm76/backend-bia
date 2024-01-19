from django.urls import path
from transversal.views import activacion_organigrama_views as views

urlpatterns = [
 
    # ACTIVACION ORGANIGRAMA

    path('get-organigrama-actual/', views.OrganigramaActualGetView.as_view(), name='get-organigrama-actual'),
    path('get-organigramas-posibles/', views.OrganigramasPosiblesGetListView.as_view(), name='get-organigrama-posibles'),
    #path('activar-organigrama/', views.OrganigramaCambioActualPutView.as_view(), name='activar-organigrama'),


]