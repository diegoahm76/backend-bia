from django.urls import path
from gestion_documental.views import activacion_ccd_views as views

urlpatterns = [
    
    # ACTIVACION CCD
    path('get-ccd-actual/get/', views.CCDActualGetView.as_view(), name='ccd-actual-get'),
    path('get-ccd-terminado-by-organigrama/<str:id_organigrama>/', views.CCDTerminadoByOrganigramaGetListView.as_view(), name='ccd-terminado-by-organigrama'),



]