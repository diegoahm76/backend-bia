from django.urls import path
from gestion_documental.views import activacion_ccd_views as views

urlpatterns = [
    
    # ACTIVACION CCD
    path('get-ccd-actual/get/', views.CCDActualGetView.as_view(), name='ccd-actual-get'),
    path('get-ccd-posibles/', views.GetCCDPosiblesActivar.as_view(), name='ccd-posibles-activar'),
    path('activar-ccd/', views.CCDCambioActualPut.as_view(), name='activar-ccd'),
    



]