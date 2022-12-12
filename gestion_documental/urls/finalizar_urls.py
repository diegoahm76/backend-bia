from django.urls import path
from gestion_documental.views import finalizar_views as views

urlpatterns = [
    # FINALIZAR ROGANIGRAMA, CCD Y TRD
    path('',views.Activar.as_view(),name='activar'),
    path('get-ccd-terminados/<str:id_organigrama>/', views.GetCCDTerminadoByPk.as_view(), name='ccd-terminados-get-by-id'),
    path('get-trd-terminados/<str:id_ccd>/', views.GetTRDTerminadoByPk.as_view(), name='trd-terminados-get-by-id'),
    path('get-tca-terminados/<str:id_ccd>/', views.GetTCATerminadoByPk.as_view(), name='tca-terminados-get-by-id')
]