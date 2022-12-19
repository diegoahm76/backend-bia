from django.urls import path
from gestion_documental.views import finalizar_views as views

urlpatterns = [
    # FINALIZAR ROGANIGRAMA, CCD Y TRD
    path('',views.Activar.as_view(),name='activar'),
    path('get-ccd-terminados-by-org/<str:id_organigrama>/', views.GetCCDTerminadoByORG.as_view(), name='ccd-terminados-get-by-org'),
    path('get-trd-terminados-by-ccd/<str:id_ccd>/', views.GetTRDTerminadoByCCD.as_view(), name='trd-terminados-get-by-ccd'),
    path('get-tca-terminados-by-ccd/<str:id_ccd>/', views.GetTCATerminadoByCCD.as_view(), name='tca-terminados-get-by-ccd')
]