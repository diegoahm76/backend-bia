from django.urls import path
from gestion_documental.views import finalizar_views as views

urlpatterns = [
    # FINALIZAR ROGANIGRAMA, CCD Y TRD
    path('',views.Activar.as_view(),name='activar'),
    path('get-ccd-terminados/<str:pk>/', views.GetCCDTerminadoByPk.as_view(), name='ccd-terminados-get-by-id'),
    path('get-trd-terminados/<str:pk>/', views.GetTRDTerminadoByPk.as_view(), name='trd-terminados-get-by-id')
]